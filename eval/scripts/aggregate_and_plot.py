"""Aggregate recommendation-judge outputs across the 5-paper pilot and produce plots.

Reads:  eval/judgements/*.json
Writes: eval/figures/per_paper_totals.png
        eval/figures/per_dimension_heatmap.png
        eval/figures/social_optimiser_vs_algorithmselector.png
        eval/figures/summary.json  (raw aggregates)
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent.parent
JUDGEMENTS_DIR = REPO / "eval" / "judgements"
FIGURES_DIR = REPO / "eval" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

DIMENSIONS = ["method_family", "formulation", "depth", "implementation", "clarity"]
DIMENSION_LABELS = ["Method\nfamily", "Formulation", "Algorithmic\ndepth", "Implementation", "Stakeholder\nclarity"]

# AlgorithmSelector baseline from EVAL_TEST_5PAPERS.md — 0/5 exact, 0/5 partial on this exact paper set.
# Express that as a per-paper total-score estimate for plotting: 0/20 exact-match-only view.
ALGORITHM_SELECTOR_BASELINE = {
    "paper_01": 0,
    "paper_02": 0,
    "paper_03": 0,
    "paper_04": 0,
    "paper_05": 0,
}


def load_judgements() -> dict[str, list[dict]]:
    """Group judgement JSONs by paper_id."""
    by_paper: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(JUDGEMENTS_DIR.glob("*.json")):
        with path.open() as f:
            entry = json.load(f)
        by_paper[entry["paper_id"]].append(entry)
    return dict(by_paper)


def per_paper_totals(by_paper: dict[str, list[dict]]) -> dict[str, dict]:
    """Mean and range of total scores per paper across runs."""
    out = {}
    for paper_id, runs in by_paper.items():
        totals = [r["total"] for r in runs]
        out[paper_id] = {
            "mean_total": float(np.mean(totals)),
            "min_total": int(np.min(totals)),
            "max_total": int(np.max(totals)),
            "n_runs": len(totals),
            "method_named_first_run": runs[0].get("method_named", ""),
            "gold_family": runs[0].get("gold_family", ""),
            "flags_union": sorted({flag for r in runs for flag in r.get("failure_modes", [])}),
        }
    return out


def per_dimension_means(by_paper: dict[str, list[dict]]) -> dict[str, dict[str, float]]:
    """Mean score per (paper, dimension)."""
    out: dict[str, dict[str, float]] = {}
    for paper_id, runs in by_paper.items():
        out[paper_id] = {}
        for dim in DIMENSIONS:
            vals = [r["scores"][dim] for r in runs]
            out[paper_id][dim] = float(np.mean(vals))
    return out


def plot_per_paper_totals(totals: dict[str, dict]) -> None:
    papers = sorted(totals)
    means = [totals[p]["mean_total"] for p in papers]
    mins = [totals[p]["min_total"] for p in papers]
    maxs = [totals[p]["max_total"] for p in papers]
    err_low = [m - lo for m, lo in zip(means, mins)]
    err_high = [hi - m for m, hi in zip(means, maxs)]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(papers, means, yerr=[err_low, err_high], capsize=6, color="#2b6cb0", alpha=0.85, label="social_optimiser")
    ax.axhline(20, linestyle="--", color="gray", alpha=0.6, linewidth=1)
    ax.text(len(papers) - 0.5, 20.3, "perfect (20/20)", color="gray", fontsize=9, ha="right")
    ax.set_ylabel("Judge total score (0–20)")
    ax.set_ylim(0, 22)
    ax.set_title("social_optimiser — 5-paper pilot, judge scores per paper")
    for i, p in enumerate(papers):
        n = totals[p]["n_runs"]
        ax.text(i, means[i] + 0.4 + err_high[i], f"n={n}", ha="center", fontsize=9, color="#2b6cb0")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "per_paper_totals.png", dpi=140)
    plt.close(fig)


def plot_per_dimension_heatmap(per_dim: dict[str, dict[str, float]]) -> None:
    papers = sorted(per_dim)
    matrix = np.array([[per_dim[p][d] for d in DIMENSIONS] for p in papers])

    fig, ax = plt.subplots(figsize=(8, 4 + 0.3 * len(papers)))
    im = ax.imshow(matrix, cmap="YlGnBu", vmin=0, vmax=4, aspect="auto")
    ax.set_xticks(range(len(DIMENSIONS)))
    ax.set_xticklabels(DIMENSION_LABELS, fontsize=10)
    ax.set_yticks(range(len(papers)))
    ax.set_yticklabels(papers, fontsize=10)
    for i, _ in enumerate(papers):
        for j, _ in enumerate(DIMENSIONS):
            val = matrix[i, j]
            color = "white" if val < 2.2 else "#1a365d"
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", color=color, fontsize=10)
    fig.colorbar(im, ax=ax, label="Mean score (0–4)")
    ax.set_title("Per-dimension score — social_optimiser 5-paper pilot")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "per_dimension_heatmap.png", dpi=140)
    plt.close(fig)


def plot_vs_algorithmselector(totals: dict[str, dict]) -> None:
    papers = sorted(totals)
    so_means = [totals[p]["mean_total"] for p in papers]
    # AlgorithmSelector was scored on exact-match-only (0/1) on this test set. All 5 were misses.
    # For visual comparison on a common 0-20 scale, we use the same judge rubric's "method_family" dim
    # baseline: exact-match = 4, partial = 2, miss = 0, applied only to that dimension and scaled to 20
    # as a reference. That gives AlgorithmSelector a 0 on method_family for all 5 -> 0/20 reference.
    as_means = [ALGORITHM_SELECTOR_BASELINE[p] * 5 for p in papers]  # 0/4 -> 0/20

    x = np.arange(len(papers))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, so_means, width, color="#2b6cb0", label="social_optimiser", alpha=0.9)
    ax.bar(x + width / 2, as_means, width, color="#c53030", label="AlgorithmSelector baseline", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(papers)
    ax.set_ylabel("Judge total score (0–20)")
    ax.set_ylim(0, 22)
    ax.set_title("social_optimiser vs AlgorithmSelector — same 5-paper test set")
    ax.legend(loc="upper right")
    ax.axhline(20, linestyle="--", color="gray", alpha=0.4, linewidth=1)
    for i, p in enumerate(papers):
        ax.text(x[i] - width / 2, so_means[i] + 0.3, f"{so_means[i]:.0f}", ha="center", fontsize=9, color="#2b6cb0")
        ax.text(x[i] + width / 2, as_means[i] + 0.3, f"{as_means[i]:.0f}", ha="center", fontsize=9, color="#c53030")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "social_optimiser_vs_algorithmselector.png", dpi=140)
    plt.close(fig)


def main() -> None:
    by_paper = load_judgements()
    if not by_paper:
        print(f"No judgements found at {JUDGEMENTS_DIR}.")
        return

    totals = per_paper_totals(by_paper)
    per_dim = per_dimension_means(by_paper)

    summary = {
        "per_paper_totals": totals,
        "per_dimension_means": per_dim,
        "algorithm_selector_baseline_note": "All 5 papers scored 0 on exact-match in EVAL_TEST_5PAPERS.md",
    }
    with (FIGURES_DIR / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    plot_per_paper_totals(totals)
    plot_per_dimension_heatmap(per_dim)
    plot_vs_algorithmselector(totals)

    print("Aggregates and plots written to:", FIGURES_DIR)
    print("Summary:")
    for p, t in sorted(totals.items()):
        flags = ", ".join(t["flags_union"]) if t["flags_union"] else "none"
        print(f"  {p}: mean={t['mean_total']:.1f}/20  n={t['n_runs']}  flags=[{flags}]")
        print(f"    recommended: {t['method_named_first_run'][:100]}...")


if __name__ == "__main__":
    main()
