#!/usr/bin/env python3
"""Compute detection coverage, false-positive rate, and latency metrics from
raw fault-injection campaign CSVs and fault-free JSON logs."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def summarize(raw_csvs, fp_jsons, out_csv: Path, out_json: Path):
    rows = []
    for p in raw_csvs:
        with Path(p).open() as fh:
            rows.extend(csv.DictReader(fh))

    fp_rows = []
    for p in fp_jsons:
        fp_rows.extend(json.loads(Path(p).read_text()))

    def agg(group_rows):
        counts = defaultdict(int)
        latencies = []
        for r in group_rows:
            counts[r["outcome_class"]] += 1
            if r["outcome_class"] == "detected_deviation" and r["detection_latency_cycles"] != "NA":
                latencies.append(int(r["detection_latency_cycles"]))
        rel_total = counts["detected_deviation"] + counts["undetected_deviation"]
        cov = (counts["detected_deviation"] / rel_total) if rel_total > 0 else 0.0
        mean_lat = (sum(latencies) / len(latencies)) if latencies else None
        max_lat = max(latencies) if latencies else None
        return {
            "total_experiments": len(group_rows),
            "nonactivated": counts["nonactivated"],
            "masked": counts["masked"],
            "detected_deviation": counts["detected_deviation"],
            "undetected_deviation": counts["undetected_deviation"],
            "timeout": counts["timeout"],
            "invalid": counts["invalid"],
            "relevant_deviations": rel_total,
            "detection_coverage": round(cov, 6),
            "mean_latency_cycles": round(mean_lat, 4) if mean_lat is not None else None,
            "max_latency_cycles": max_lat,
        }

    by_cfg = defaultdict(list)
    by_cfg_cat = defaultdict(list)
    for r in rows:
        by_cfg[r["config"]].append(r)
        by_cfg_cat[(r["config"], r["fault_category"])].append(r)

    fp_by_cfg = defaultdict(lambda: {"cycles": 0, "fp_cycles": 0, "workloads": 0, "sticky_alarms": 0})
    for r in fp_rows:
        d = fp_by_cfg[r["config"]]
        d["cycles"] += r["cycles"]
        d["fp_cycles"] += r["false_positive_cycles"]
        d["workloads"] += 1
        d["sticky_alarms"] += r["sticky_triggered"]

    summary = {"by_config": {}, "by_config_category": {}}
    csv_rows = []

    for cfg in sorted(by_cfg):
        m = agg(by_cfg[cfg])
        fp = fp_by_cfg[cfg]
        fpr = (fp["fp_cycles"] / fp["cycles"]) if fp["cycles"] > 0 else 0.0
        m["fault_free_cycles"] = fp["cycles"]
        m["false_positive_cycles"] = fp["fp_cycles"]
        m["false_positive_rate"] = round(fpr, 6)
        summary["by_config"][cfg] = m
        csv_rows.append({"config": cfg, "fault_category": "ALL", **m})

    for (cfg, cat) in sorted(by_cfg_cat):
        m = agg(by_cfg_cat[(cfg, cat)])
        summary["by_config_category"][f"{cfg}:{cat}"] = m
        csv_rows.append({"config": cfg, "fault_category": cat, "fault_free_cycles": "",
                         "false_positive_cycles": "", "false_positive_rate": "", **m})

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "config", "fault_category", "total_experiments", "nonactivated", "masked",
        "detected_deviation", "undetected_deviation", "timeout", "invalid",
        "relevant_deviations", "detection_coverage", "mean_latency_cycles",
        "max_latency_cycles", "fault_free_cycles", "false_positive_cycles",
        "false_positive_rate",
    ]
    with out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    out_json.write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", nargs="+", required=True)
    ap.add_argument("--fp", nargs="+", required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    args = ap.parse_args()
    s = summarize(args.raw, args.fp, args.out_csv, args.out_json)
    print(json.dumps(s["by_config"], indent=2))


if __name__ == "__main__":
    main()
