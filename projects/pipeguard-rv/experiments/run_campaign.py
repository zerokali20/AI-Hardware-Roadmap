#!/usr/bin/env python3
"""Orchestrate controlled fault-injection campaigns across B0, M0, M1, and M2."""
import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ_DIR / "workloads"))
from workloads import WORKLOADS
from metrics import summarize


def load_config(path: Path) -> dict:
    text = path.read_text()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def build_schedule(cfg: dict) -> dict:
    rng = random.Random(cfg["seed"])
    n_inj = cfg["injections_per_target_per_workload"]
    experiments = []
    exp_idx = 0

    for wname in cfg["workloads"]:
        w = WORKLOADS[wname]
        # Avoid injecting in cycle 0 (reset boundary) or last 2 cycles (no time to manifest)
        lo, hi = 1, max(2, w["cycles"] - 3)
        for ft in cfg["fault_targets"]:
            for _ in range(n_inj):
                bit_idx = rng.choice(ft["bits"])
                inj_cyc = rng.randint(lo, hi)
                exp_seed = rng.randint(1, 2**31 - 1)
                exp_idx += 1
                experiments.append({
                    "experiment_id": f"{cfg['campaign_name']}_{exp_idx:04d}",
                    "seed": exp_seed,
                    "workload": wname,
                    "fault_category": ft["category"],
                    "fault_target": ft["id"],
                    "signal": ft["signal"],
                    "bit_idx": bit_idx,
                    "inject_cycle": inj_cyc,
                })

    return {
        "campaign_name": cfg["campaign_name"],
        "config_version": cfg["config_version"],
        "seed": cfg["seed"],
        "experiments": experiments,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--configs", nargs="+", help="Override target configs (e.g. b0 m0 m1 m2)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    target_cfgs = args.configs if args.configs else cfg["configs"]
    mode = cfg["campaign_name"]

    schedule = build_schedule(cfg)
    sched_path = PROJ_DIR / "results" / "raw" / f"schedule_{mode}.json"
    sched_path.parent.mkdir(parents=True, exist_ok=True)
    sched_path.write_text(json.dumps(schedule, indent=2))
    print(f"Generated {len(schedule['experiments'])} fault experiments in {sched_path}")

    raw_csvs = []
    fp_jsons = []

    for c in target_cfgs:
        out_csv = PROJ_DIR / "results" / "raw" / f"fault_campaign_{c}_{mode}.csv"
        fp_json = PROJ_DIR / "results" / "raw" / f"fault_free_{c}_{mode}.json"
        env = os.environ.copy()
        env["PG_CAMPAIGN_SCHEDULE"] = str(sched_path)
        env["PG_CAMPAIGN_CONFIG"] = c
        env["PG_CAMPAIGN_OUT"] = str(out_csv)
        env["PG_CAMPAIGN_FP_OUT"] = str(fp_json)

        print(f"=== Running {mode} fault campaign on CONFIG={c} ===")
        subprocess.run(
            ["make", "-C", str(PROJ_DIR / "tb"), f"SUITE=campaign_{c}"],
            env=env,
            check=True,
        )
        subprocess.run(
            ["python3", str(PROJ_DIR / "scripts" / "check_results.py"),
             str(PROJ_DIR / "tb" / "results" / f"campaign_{c}.xml")],
            check=True,
        )
        raw_csvs.append(out_csv)
        fp_jsons.append(fp_json)

    summary_csv = PROJ_DIR / "results" / "processed" / f"campaign_summary_{mode}.csv"
    summary_json = PROJ_DIR / "results" / "processed" / f"campaign_summary_{mode}.json"
    s = summarize(raw_csvs, fp_jsons, summary_csv, summary_json)
    print(f"\n=== Campaign '{mode}' Summary ({summary_csv}) ===")
    print(json.dumps(s["by_config"], indent=2))


if __name__ == "__main__":
    main()
