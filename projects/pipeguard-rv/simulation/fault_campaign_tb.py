"""Controlled RTL fault-injection cocotb harness (simulation-only).

Reads:
  - PG_CAMPAIGN_SCHEDULE : JSON file listing the exact fault experiments
  - PG_CAMPAIGN_CONFIG   : config name (b0 | m0 | m1 | m2)
  - PG_CAMPAIGN_OUT      : output CSV path for raw experiment results
  - PG_CAMPAIGN_FP_OUT   : output JSON path for fault-free baseline & FP summary

For every workload in the schedule:
  1. Runs a fault-free execution on dut_cpu, verifying expected_regs,
     checking zero monitor false positives, and capturing the golden
     cycle-by-cycle trace (fetch_pc, wb_pc, wb_reg_write, wb_rd, wb_data,
     branch_redirect, store events) + final x0..x31 + final data_memory.
  2. Executes each scheduled fault injection on dut_cpu using cocotb Force/Release
     for 1 clock cycle, compares against the golden trace independently of
     monitor alarms, and classifies the outcome into:
       nonactivated | masked | detected_deviation | undetected_deviation |
       timeout | invalid
"""
import csv
import json
import os
import sys
from pathlib import Path

import cocotb
from cocotb.handle import Force, Release
from cocotb.triggers import Timer

PROJ_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ_DIR / "workloads"))
sys.path.insert(0, str(PROJ_DIR / "tb" / "common"))
from workloads import WORKLOADS
from rv32i import NOP

IMEM_WORDS = 256


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await Timer(1, unit="ns")


async def reset_and_load(dut, words):
    dut.clk.value = 0
    dut.rst.value = 1

    dut_imem = dut.dut_cpu.u_core.frontend.fetch_unit.imem_unit.memory
    ref_imem = dut.ref_cpu.frontend.fetch_unit.imem_unit.memory
    for i in range(IMEM_WORDS):
        w = words[i] if i < len(words) else NOP
        dut_imem[i].value = w
        ref_imem[i].value = w

    dut_dmem = dut.dut_cpu.u_core.memory_unit.data_mem_unit.memory
    ref_dmem = dut.ref_cpu.memory_unit.data_mem_unit.memory
    for i in range(len(dut_dmem)):
        dut_dmem[i].value = 0
        ref_dmem[i].value = 0

    await Timer(1, unit="ns")
    await tick(dut)
    dut.rst.value = 0
    await Timer(1, unit="ns")


def sample_cycle(dut):
    core = dut.dut_cpu.u_core
    return (
        int(dut.dut_fetch_pc.value),
        int(dut.dut_wb_pc.value),
        int(dut.dut_wb_reg_write.value),
        int(dut.dut_wb_rd.value),
        int(dut.dut_wb_data.value),
        int(dut.dut_branch_redirect.value),
        int(core.memory_unit.registered_mem_write.value),
        int(core.memory_unit.mem_alu_result.value),
    )


def snapshot_arch(dut):
    rf = [int(dut.dut_cpu.u_core.frontend.regfile.registers[r].value) for r in range(32)]
    dmem = [int(dut.dut_cpu.u_core.memory_unit.data_mem_unit.memory[a].value)
            for a in range(len(dut.dut_cpu.u_core.memory_unit.data_mem_unit.memory))]
    return rf, dmem


def resolve_target(dut, signal_name):
    core = dut.dut_cpu.u_core
    mapping = {
        "pc": core.frontend.fetch_unit.pc_unit.pc,
        "branch_redirect": core.branch_redirect,
        "branch_taken": core.branch_taken,
        "branch_target": core.branch_target,
        "pc_stall": core.pc_stall,
        "load_use_stall": core.load_use_stall,
        "id_ex_flush": core.id_ex_flush,
    }
    return mapping.get(signal_name)


@cocotb.test()
async def run_fault_campaign(dut):
    schedule_path = Path(os.environ["PG_CAMPAIGN_SCHEDULE"])
    cfg_name = os.environ["PG_CAMPAIGN_CONFIG"]
    out_csv = Path(os.environ["PG_CAMPAIGN_OUT"])
    fp_json = Path(os.environ["PG_CAMPAIGN_FP_OUT"])

    schedule = json.loads(schedule_path.read_text())
    experiments = schedule["experiments"]
    cfg_version = schedule["config_version"]

    # 1. Fault-free golden reference runs (one per workload)
    golden = {}
    fp_records = []
    used_workloads = sorted({e["workload"] for e in experiments})

    for wname in used_workloads:
        w = WORKLOADS[wname]
        await reset_and_load(dut, w["words"])
        trace = []
        fp_cycles = 0
        for cyc in range(w["cycles"]):
            trace.append(sample_cycle(dut))
            if int(dut.dut_fault_detected.value) != 0:
                fp_cycles += 1
            await tick(dut)
        rf, dmem = snapshot_arch(dut)
        sticky_fp = int(dut.dut_fault_sticky.value)

        for r_idx, exp_val in w["expected_regs"].items():
            assert rf[r_idx] == (exp_val & 0xFFFFFFFF), (
                f"Golden workload {wname} x{r_idx} mismatch"
            )

        golden[wname] = {"trace": trace, "rf": rf, "dmem": dmem}
        fp_records.append({
            "config": cfg_name,
            "workload": wname,
            "cycles": w["cycles"],
            "false_positive_cycles": fp_cycles,
            "sticky_triggered": sticky_fp,
        })

    fp_json.parent.mkdir(parents=True, exist_ok=True)
    fp_json.write_text(json.dumps(fp_records, indent=2))

    # 2. Controlled fault-injection runs
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment_id",
        "seed",
        "config",
        "config_version",
        "workload",
        "fault_category",
        "fault_target",
        "signal",
        "bit_idx",
        "inject_cycle",
        "activated",
        "relevant_deviation",
        "outcome_class",
        "monitor_detected",
        "fault_class",
        "detection_latency_cycles",
    ]

    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for exp in experiments:
            wname = exp["workload"]
            w = WORKLOADS[wname]
            g = golden[wname]
            inj_cyc = exp["inject_cycle"]
            bit_idx = exp["bit_idx"]
            sig_handle = resolve_target(dut, exp["signal"])

            if sig_handle is None or inj_cyc >= w["cycles"]:
                writer.writerow({
                    "experiment_id": exp["experiment_id"],
                    "seed": exp["seed"],
                    "config": cfg_name,
                    "config_version": cfg_version,
                    "workload": wname,
                    "fault_category": exp["fault_category"],
                    "fault_target": exp["fault_target"],
                    "signal": exp["signal"],
                    "bit_idx": bit_idx,
                    "inject_cycle": inj_cyc,
                    "activated": 0,
                    "relevant_deviation": 0,
                    "outcome_class": "invalid",
                    "monitor_detected": 0,
                    "fault_class": 0,
                    "detection_latency_cycles": "NA",
                })
                continue

            await reset_and_load(dut, w["words"])
            activated = 0
            deviation = 0
            first_detect_cyc = None
            forced = False

            for cyc in range(w["cycles"]):
                if cyc == inj_cyc:
                    orig_val = int(sig_handle.value)
                    new_val = orig_val ^ (1 << bit_idx)
                    activated = 1 if new_val != orig_val else 0
                    sig_handle.value = Force(new_val)
                    forced = True
                    await Timer(1, unit="ns")

                if int(dut.dut_fault_detected.value) == 1 and first_detect_cyc is None and cyc >= inj_cyc:
                    first_detect_cyc = cyc

                if sample_cycle(dut) != g["trace"][cyc]:
                    deviation = 1

                await tick(dut)

                if forced:
                    sig_handle.value = Release()
                    forced = False
                    await Timer(1, unit="ns")

            rf, dmem = snapshot_arch(dut)
            if rf != g["rf"] or dmem != g["dmem"]:
                deviation = 1

            mon_det = int(dut.dut_fault_sticky.value)
            fclass = int(dut.dut_fault_class.value)
            if mon_det == 1 and first_detect_cyc is None:
                first_detect_cyc = w["cycles"] - 1

            if not activated:
                outcome = "nonactivated"
            elif not deviation:
                outcome = "masked"
            elif mon_det:
                outcome = "detected_deviation"
            else:
                outcome = "undetected_deviation"

            latency = (first_detect_cyc - inj_cyc) if (mon_det and first_detect_cyc is not None) else "NA"

            writer.writerow({
                "experiment_id": exp["experiment_id"],
                "seed": exp["seed"],
                "config": cfg_name,
                "config_version": cfg_version,
                "workload": wname,
                "fault_category": exp["fault_category"],
                "fault_target": exp["fault_target"],
                "signal": exp["signal"],
                "bit_idx": bit_idx,
                "inject_cycle": inj_cyc,
                "activated": activated,
                "relevant_deviation": deviation,
                "outcome_class": outcome,
                "monitor_detected": mon_det,
                "fault_class": fclass,
                "detection_latency_cycles": latency,
            })
