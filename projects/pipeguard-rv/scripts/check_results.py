#!/usr/bin/env python3
"""Strict checker for cocotb JUnit result files.

cocotb's make flow can exit 0 even when individual tests fail, so every
PipeGuard-RV regression target passes its results.xml files through this
script. It exits non-zero when a file is missing, contains zero test cases,
or reports any failure/error. A one-line summary per file is printed, and
an optional --summary CSV records the counts for reproducibility.

Usage: check_results.py [--summary out.csv] results1.xml [results2.xml ...]
"""
import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def count(path: Path):
    root = ET.parse(path).getroot()
    tests = failed = errored = skipped = 0
    failed_names = []
    for case in root.iter("testcase"):
        tests += 1
        name = case.get("name", "?")
        if case.find("failure") is not None:
            failed += 1
            failed_names.append(name)
        elif case.find("error") is not None:
            errored += 1
            failed_names.append(name)
        elif case.find("skipped") is not None:
            skipped += 1
    return tests, failed, errored, skipped, failed_names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path)
    ap.add_argument("files", nargs="+", type=Path)
    args = ap.parse_args()

    rows, ok = [], True
    tot = [0, 0, 0, 0]
    for f in args.files:
        suite = f.stem
        if not f.is_file():
            print(f"MISSING  {suite}: {f} not found")
            rows.append([suite, "", "", "", "", "MISSING"])
            ok = False
            continue
        t, fl, er, sk, names = count(f)
        passed = t - fl - er - sk
        status = "PASS" if (t > 0 and fl == 0 and er == 0) else "FAIL"
        if status != "PASS":
            ok = False
        extra = f"  failing: {', '.join(names)}" if names else ""
        if t == 0:
            extra = "  (no test cases recorded)"
        print(f"{status:8} {suite}: tests={t} pass={passed} fail={fl} error={er} skip={sk}{extra}")
        rows.append([suite, t, passed, fl + er, sk, status])
        for i, v in enumerate((t, passed, fl + er, sk)):
            tot[i] += v

    print(f"TOTAL    suites={len(args.files)} tests={tot[0]} pass={tot[1]} fail={tot[2]} skip={tot[3]}")
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        with args.summary.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["suite", "tests", "passed", "failed_or_error", "skipped", "status"])
            w.writerows(rows)
            w.writerow(["TOTAL", *tot, "PASS" if ok else "FAIL"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
