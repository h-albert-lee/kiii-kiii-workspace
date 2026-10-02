"""Plot frozen ADR-0038 paired results; no inference, rescoring or new intervals."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
TABLES = ROOT / "experiments/results/analyses/1001-completed-manuscript-v1/tables"
PIN = PAPER / "notes/analysis-inputs.json"


def main():
    pins = json.loads(PIN.read_text())
    for rel, expected in pins["sha256"].items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen manuscript input changed: {rel}")
    with (TABLES / "paired.csv").open(newline="") as f:
        paired = list(csv.DictReader(f))
    with (TABLES / "summary.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 25 and len(paired) == 10
    lookup = {(r["model"], r["condition"]): r for r in rows}
    labels = {
        "kakaocorp/kanana-2-3b-instruct": "Kanana-2-3B",
        "Qwen/Qwen3.5-9B": "Qwen3.5-9B",
        "kakaocorp/kanana-1.5-8b-instruct-2505": "Kanana-1.5-8B*",
        "LGAI-EXAONE/EXAONE-4.5-33B": "EXAONE-4.5-33B",
        "Qwen/Qwen3-30B-A3B": "Qwen3-30B-A3B",
        "google/gemma-4-E2B-it": "Gemma-4-E2B",
        "google/gemma-4-E4B-it": "Gemma-4-E4B",
        "google/gemma-4-12B-it": "Gemma-4-12B",
        "google/gemma-4-26B-A4B-it": "Gemma-4-26B-A4B",
        "google/gemma-4-31B-it": "Gemma-4-31B (FP8)",
    }
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.18), sharey=True,
                             gridspec_kw={"width_ratios": [1, 1]})
    for i, row in enumerate(paired):
        model = row["model"]
        full = lookup[model, "full_context_targeted"]
        local = lookup[model, "local_window"]
        assert full["documents"] == local["documents"] == row["documents"]
        x, lo, hi = (100 * float(row[k]) for k in ("delta_f1", "ci_low", "ci_high"))
        axes[0].errorbar(x, i, xerr=[[x-lo], [hi-x]], fmt="o", markersize=4,
                         capsize=2, color="#20678A", linewidth=1.1)
        d = 100 * (float(full["detection_f1"]) - float(local["detection_f1"]))
        axes[1].plot(d, i, "s", markersize=4, color="#9B4E30")
    for ax, title in zip(axes, ["Strict F1: paired 95% intervals", "D-F1: point differences only"]):
        ax.axvline(0, color="#555555", linestyle="--", linewidth=.8)
        ax.set_title(title, fontsize=8.5, pad=8)
        ax.grid(axis="y", alpha=.15)
        ax.set_xlabel("Full minus local (F1 points)")
    axes[0].set_yticks(range(len(paired)), [labels[r["model"]] for r in paired])
    axes[0].invert_yaxis()
    axes[0].set_xlim(-2.55, 1.05)
    axes[1].set_xlim(-8.1, .6)
    axes[0].set_xticks([-2, -1, 0, 1])
    axes[1].set_xticks([-8, -6, -4, -2, 0])
    fig.subplots_adjust(left=.24, right=.98, top=.88, bottom=.16, wspace=.23)
    fig.savefig(PAPER / "figures/context-contrasts.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(PAPER / "figures/context-contrasts.png", dpi=180)
    print("Plotted 10 frozen pairs; D intervals were not computed or implied.")


if __name__ == "__main__":
    main()
