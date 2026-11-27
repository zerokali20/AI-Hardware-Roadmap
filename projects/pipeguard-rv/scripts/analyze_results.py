#!/usr/bin/env python3
"""Generate reproducible statistical summaries and all 6 research figures
for PipeGuard-RV from measured fault-campaign and Yosys synthesis outputs.

Figures produced in results/figures/:
  1. fig1_coverage_by_config.png       — Overall detection coverage (B0..M2, N=185)
  2. fig2_coverage_by_category.png     — Coverage by fault category (pc/branch/pipeline)
  3. fig3_false_positive_comparison.png— Fault-free false-positive rate (450 cycles)
  4. fig4_latency_distribution.png     — Detection latency distribution (cycles)
  5. fig5_hardware_overhead.png        — Yosys generic cell overhead vs. B0
  6. fig6_coverage_vs_cost.png         — Coverage vs. hardware cost Pareto trade-off
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CONFIGS = ["b0", "m0", "m1", "m2"]
LABELS = ["B0\n(Baseline)", "M0\n(PC-Only)", "M1\n(Branch)", "M2\n(Pipeline)"]
COLORS = ["#64748b", "#3b82f6", "#f59e0b", "#10b981"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", type=Path, default=Path("."))
    args = ap.parse_args()

    proj = args.proj_dir
    fig_dir = proj / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    camp_json = json.loads((proj / "results" / "processed" / "campaign_summary_full.json").read_text())
    synth_json = json.loads((proj / "results" / "synthesis" / "synth_summary.json").read_text())

    raw_dfs = []
    for c in CONFIGS:
        p = proj / "results" / "raw" / f"fault_campaign_{c}_full.csv"
        if p.is_file():
            raw_dfs.append(pd.read_csv(p))
    raw_df = pd.concat(raw_dfs, ignore_index=True) if raw_dfs else pd.DataFrame()

    plt.rcParams.update({
        "figure.dpi": 150,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.size": 10,
    })

    # 1. Detection coverage by monitoring configuration
    by_cfg = camp_json["by_config"]
    covs = [100.0 * by_cfg[c]["detection_coverage"] for c in CONFIGS]
    rels = [by_cfg[c]["relevant_deviations"] for c in CONFIGS]
    dets = [by_cfg[c]["detected_deviation"] for c in CONFIGS]

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    bars = ax.bar(LABELS, covs, color=COLORS, edgecolor="black", linewidth=0.6)
    for b, d, r, cov in zip(bars, dets, rels, covs):
        ax.text(b.get_x() + b.get_width() / 2, cov + 2.0,
                f"{cov:.1f}%\n({d}/{r})", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Detection Coverage (%)")
    ax.set_title(f"Detection Coverage by Monitor Configuration (Full Campaign, N={rels[0]} relevant deviations)")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig1_coverage_by_config.png")
    plt.close(fig)

    # 2. Detection coverage by fault category
    cats = ["pc", "branch_control", "pipeline_control"]
    cat_labels = [
        f"PC Faults\n(N={camp_json['by_config_category']['b0:pc']['relevant_deviations']})",
        f"Branch Control\n(N={camp_json['by_config_category']['b0:branch_control']['relevant_deviations']})",
        f"Pipeline Control\n(N={camp_json['by_config_category']['b0:pipeline_control']['relevant_deviations']})",
    ]
    x = np.arange(len(cats))
    width = 0.19
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i, c in enumerate(CONFIGS):
        vals = [100.0 * camp_json["by_config_category"][f"{c}:{cat}"]["detection_coverage"] for cat in cats]
        bars = ax.bar(x + (i - 1.5) * width, vals, width, label=c.upper(), color=COLORS[i], edgecolor="black", linewidth=0.5)
        for b, v in zip(bars, vals):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v + 1.8, f"{v:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Detection Coverage (%)")
    ax.set_title("Detection Coverage by Fault Category (Full Campaign)")
    ax.legend(ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig2_coverage_by_category.png")
    plt.close(fig)

    # 3. Fault-free false-positive comparison
    fprs = [100.0 * by_cfg[c]["false_positive_rate"] for c in CONFIGS]
    ff_cyc = [by_cfg[c]["fault_free_cycles"] for c in CONFIGS]
    fp_cyc = [by_cfg[c]["false_positive_cycles"] for c in CONFIGS]

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    bars = ax.bar(LABELS, fprs, color=COLORS, edgecolor="black", linewidth=0.6)
    for b, fp, ff in zip(bars, fp_cyc, ff_cyc):
        ax.text(b.get_x() + b.get_width() / 2, 0.25, f"{fp}/{ff} cyc\n(0.00%)", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, 5.0)
    ax.set_ylabel("False-Positive Rate (%)")
    ax.set_title(f"Fault-Free False-Positive Comparison (8 Workloads, {ff_cyc[0]} cycles/config)")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig3_false_positive_comparison.png")
    plt.close(fig)

    # 4. Detection latency distribution
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    if not raw_df.empty:
        det_df = raw_df[raw_df["outcome_class"] == "detected_deviation"].copy()
        det_df["lat"] = pd.to_numeric(det_df["detection_latency_cycles"], errors="coerce")
        lat_bins = ["0 cyc", "1 cyc", ">=2 cyc"]
        x_l = np.arange(len(lat_bins))
        w_l = 0.24
        for idx, c in enumerate(["m0", "m1", "m2"]):
            sub = det_df[det_df["config"] == c]["lat"].dropna()
            n_det = len(sub)
            c0 = int((sub == 0).sum())
            c1 = int((sub == 1).sum())
            c2 = int((sub >= 2).sum())
            pcts = [100.0 * k / n_det if n_det else 0.0 for k in (c0, c1, c2)]
            bars = ax.bar(x_l + (idx - 1) * w_l, pcts, w_l, label=f"{c.upper()} (n={n_det})",
                          color=COLORS[idx + 1], edgecolor="black", linewidth=0.5)
            for b, cnt, p in zip(bars, (c0, c1, c2), pcts):
                if cnt > 0:
                    ax.text(b.get_x() + b.get_width() / 2, p + 1.8, f"{cnt}\n({p:.0f}%)",
                            ha="center", va="bottom", fontsize=8)
        ax.set_xticks(x_l)
        ax.set_xticklabels(lat_bins)
    ax.set_ylim(0, 118)
    ax.set_ylabel("Share of Detected Faults (%)")
    ax.set_title("Detection Latency Distribution Across Detected Deviations")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "fig4_latency_distribution.png")
    plt.close(fig)

    # 5. Hardware resource overhead comparison
    mon_cells = [synth_json[c]["monitor_module_cells"] for c in CONFIGS]
    delta_cells = [synth_json[c]["delta_total_cells"] for c in CONFIGS]
    ovh_pct = [synth_json[c]["overhead_pct"] for c in CONFIGS]
    logic_ovh_pct = [synth_json[c]["logic_only_overhead_pct"] for c in CONFIGS]

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    x_h = np.arange(len(CONFIGS))
    bars = ax.bar(LABELS, delta_cells, color=COLORS, edgecolor="black", linewidth=0.6)
    for b, dc, pct, lpct in zip(bars, delta_cells, ovh_pct, logic_ovh_pct):
        ax.text(b.get_x() + b.get_width() / 2, dc + 25,
                f"+{dc} cells\n({pct:.2f}% total / {lpct:.2f}% logic)",
                ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, max(delta_cells) * 1.28)
    ax.set_ylabel("Additional Yosys Generic Cells vs. B0")
    ax.set_title("Hardware Resource Overhead vs. B0 (Yosys 0.33, synth -noabc)")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig5_hardware_overhead.png")
    plt.close(fig)

    # 6. Coverage vs. hardware-cost trade-off
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for i, c in enumerate(CONFIGS):
        cost = synth_json[c]["overhead_pct"]
        cov = 100.0 * by_cfg[c]["detection_coverage"]
        ax.scatter(cost, cov, s=110, color=COLORS[i], edgecolor="black", zorder=4)
        ax.annotate(
            f"{c.upper()} ({cov:.1f}%, +{cost:.2f}%)",
            (cost, cov),
            textcoords="offset points",
            xytext=(8, -4 if i == 0 else 6),
            fontsize=9,
        )
    ax.plot([synth_json[c]["overhead_pct"] for c in CONFIGS],
            [100.0 * by_cfg[c]["detection_coverage"] for c in CONFIGS],
            linestyle="--", color="#94a3b8", zorder=2)
    ax.set_xlim(-0.1, max(ovh_pct) + 0.45)
    ax.set_ylim(-5, 100)
    ax.set_xlabel("Total Generic Cell Overhead vs. B0 (%)")
    ax.set_ylabel("Detection Coverage (%, N=185)")
    ax.set_title("Control-Flow Fault Coverage vs. Hardware Overhead Trade-off")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig6_coverage_vs_cost.png")
    plt.close(fig)

    print(f"Generated 6 figures in {fig_dir}")


if __name__ == "__main__":
    main()
