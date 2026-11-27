#!/usr/bin/env python3
"""Parse Yosys stat reports (b0_stat.txt .. m2_stat.txt) into structured CSV/JSON.

Extracts:
  - Total design hierarchy cell counts (total, flip-flops, combinational)
  - Monitor-only module cell counts ($paramod*\\pc_monitor, branch_monitor,
    pipeline_monitor)
  - Core-without-SRAMs reference (excluding instruction_memory and data_memory)
  - Relative overhead vs. B0
"""
import argparse
import csv
import json
import re
from pathlib import Path

FF_PREFIXES = ("$_DFF", "$_SDFF", "$_DFFE", "$_SDFFE", "$_SDFFCE")


def parse_stat_file(path: Path):
    sections = {}
    cur = None
    for line in path.read_text().splitlines():
        m = re.match(r"^===\s+(.+?)\s+===$", line.strip())
        if m:
            cur = m.group(1)
            sections[cur] = {"total": 0, "ff": 0, "comb": 0, "cells": {}}
            continue
        if cur is None:
            continue
        mc = re.match(r"^\s*Number of cells:\s+(\d+)\s*$", line)
        if mc:
            sections[cur]["total"] = int(mc.group(1))
            continue
        mt = re.match(r"^\s*(\$_[A-Z0-9_]+)\s+(\d+)\s*$", line)
        if mt:
            ctype, cnt = mt.group(1), int(mt.group(2))
            sections[cur]["cells"][ctype] = cnt
            if ctype.startswith(FF_PREFIXES):
                sections[cur]["ff"] += cnt
            else:
                sections[cur]["comb"] += cnt
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synth-dir", type=Path, default=Path("results/synthesis"))
    args = ap.parse_args()

    configs = ["b0", "m0", "m1", "m2"]
    summary = {}
    rows = []
    b0_total = None

    for cfg in configs:
        p = args.synth_dir / f"{cfg}_stat.txt"
        if not p.is_file():
            raise FileNotFoundError(f"Missing synthesis stat file: {p}")
        secs = parse_stat_file(p)
        hier = secs["design hierarchy"]

        # Monitor-only section
        mon_sec = {"total": 0, "ff": 0, "comb": 0}
        for name, data in secs.items():
            if any(k in name for k in ("pc_monitor", "branch_monitor", "pipeline_monitor")):
                mon_sec = data
                break

        # Non-memory cells (total minus instruction_memory & data_memory)
        imem_tot = secs.get("instruction_memory", {}).get("total", 0)
        dmem_tot = secs.get("data_memory", {}).get("total", 0)
        logic_only_tot = hier["total"] - imem_tot - dmem_tot

        if cfg == "b0":
            b0_total = hier["total"]
            b0_ff = hier["ff"]
            b0_comb = hier["comb"]
            b0_logic = logic_only_tot

        delta_tot = hier["total"] - b0_total
        ovh_pct = (100.0 * delta_tot / b0_total) if b0_total else 0.0
        logic_ovh_pct = (100.0 * (logic_only_tot - b0_logic) / b0_logic) if b0_logic else 0.0

        rec = {
            "config": cfg,
            "total_cells": hier["total"],
            "ff_cells": hier["ff"],
            "comb_cells": hier["comb"],
            "delta_total_cells": delta_tot,
            "delta_ff_cells": hier["ff"] - b0_ff,
            "delta_comb_cells": hier["comb"] - b0_comb,
            "overhead_pct": round(ovh_pct, 4),
            "monitor_module_cells": mon_sec["total"],
            "monitor_module_ff": mon_sec["ff"],
            "monitor_module_comb": mon_sec["comb"],
            "logic_only_cells_excl_mem": logic_only_tot,
            "logic_only_overhead_pct": round(logic_ovh_pct, 4),
        }
        summary[cfg] = rec
        rows.append(rec)

    out_csv = args.synth_dir / "synth_summary.csv"
    out_json = args.synth_dir / "synth_summary.json"
    with out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    out_json.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
