"""Rebuild the manuscript overview (vector PDF/SVG and PNG).

python figures/src/fig1_overview.py
Examples: figures/specs/fig1_overview.yaml. Counts: taxonomy/taxonomy.yaml.
This figure contains no measured results.
"""
from collections import Counter
from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "kiii-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
import yaml

from _style import DBL_W, OUT_DIR, FIGURE_COLORS as C, FIGURE_FONTS as F, setup

ROOT = Path(__file__).resolve().parents[2]


def korean_font():
    override = os.environ.get("KIII_KOREAN_FONT")
    if override:
        return font_manager.FontProperties(fname=override)
    bundled = ROOT / "figures/assets/fonts/NanumGothic-Regular.ttf"
    if bundled.exists():
        return font_manager.FontProperties(fname=bundled)
    for name in F["korean_candidates"]:
        try:
            return font_manager.FontProperties(fname=font_manager.findfont(name, fallback_to_default=False))
        except ValueError:
            pass
    raise RuntimeError("Install Noto Sans CJK KR or set KIII_KOREAN_FONT to a Korean font file.")


def main():
    spec = yaml.safe_load((ROOT / "figures/specs/fig1_overview.yaml").read_text())
    taxonomy = yaml.safe_load((ROOT / "taxonomy/taxonomy.yaml").read_text())
    counts = Counter((c["tier"], c["kind"]) for c in taxonomy["categories"])
    assert spec["category"] in {c["id"] for c in taxonomy["categories"]}
    assert [p["level"] for p in spec["panels"]] == ["T0", "T1", "T2", "T3"]
    assert spec["panels"][0]["surface"] == spec["canonical"]
    digits = lambda s: "".join(c for c in s if c.isdigit())
    assert digits(spec["panels"][1]["surface"]) == digits(spec["canonical"])
    assert "".join(digits(t["surface"]) for t in spec["panels"][3]["turns"] if t["target"]) == digits(spec["canonical"])
    setup()
    ko = korean_font()
    w, h = DBL_W * 72, 173
    fig = plt.figure(figsize=(DBL_W, h / 72), facecolor=C["white"])
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, w), ylim=(h, 0))
    ax.set_axis_off()

    def text(x, y, s, size=8, color="ink", weight="normal", ha="left", korean=False, mono=False):
        kwargs = {"fontproperties": ko} if korean else {"fontfamily": F["mono" if mono else "latin"]}
        return ax.text(x, y, s, fontsize=size, color=C[color], weight=weight,
                       ha=ha, va="center", **kwargs)

    def line(x1, y1, x2, y2, color="line", width=.55):
        ax.plot([x1, x2], [y1, y2], color=C[color], lw=width, solid_capstyle="butt")

    def box(x, y, width, height, fill="paper", edge=False):
        ax.add_patch(Rectangle((x, y), width, height, facecolor=C[fill],
                               edgecolor=C["line"] if edge else "none", linewidth=.55))

    text(3, 8, "Same synthetic identifier", size=8.2, weight="bold")
    text(145, 8, spec["canonical"], size=8.2, mono=True, color="accent")
    text(w - 3, 8, "Alternative input forms", size=8, color="muted", ha="right")
    line(3, 20, w-3, 20, color="ink", width=.7)
    gap = 12
    pw = (w - 6 - 3 * gap) / 4
    xs = [3 + i * (pw + gap) for i in range(4)]

    for i, (x, p) in enumerate(zip(xs, spec["panels"])):
        text(x, 33, p["level"], size=10, color="accent", weight="bold")
        text(x + 21, 33, p["title"], size=9, weight="bold")
        text(x, 47, p["context"], size=7.7, color="muted")
        line(x, 57, x + pw, 57)
        text(x, 137, p["note"], size=7.7, color="muted")
        if i < 3:
            line(x + pw + gap/2, 27, x + pw + gap/2, 142)

    # T0/T1 share the same field anchor to isolate separator changes.
    for i in (0, 1):
        x = xs[i]
        box(x, 67, pw, 57, edge=True)
        text(x+7, 79, "연락처", size=8, korean=True)
        text(x+pw-7, 79, "Phone", size=7.5, color="muted", ha="right")
        box(x+6, 91, pw-12, 22, fill="highlight")
        text(x+pw/2, 102, spec["panels"][i]["surface"], size=8.8, mono=True, ha="center", color="accent")

    # T2 is one contiguous wrapped span, not a dialogue split.
    x = xs[2]
    box(x, 67, pw, 57, edge=True)
    box(x+6, 73, pw-12, 31, fill="highlight")
    for row, surface in enumerate(spec["panels"][2]["lines"]):
        text(x+12, 81+15*row, surface, size=9, korean=True, color="accent")
    text(x+7, 115, "= 010 3344 5566", size=7.8, mono=True, color="muted")

    # T3 isolates structural fragmentation using Arabic digits. A/B distinguish
    # speakers in monochrome; the bracket links A's two annotated spans.
    x = xs[3]
    for row, turn in enumerate(spec["panels"][3]["turns"]):
        y = 77 + row * 21
        text(x+3, y, turn["subject"], size=8, weight="bold")
        if turn["target"]:
            box(x+17, y-8, pw-34, 16, fill="highlight")
        text(x+22, y, turn["surface"], size=8.5, korean=not turn["target"],
             mono=turn["target"], color="accent" if turn["target"] else "muted")
    bx = x + pw - 4
    line(bx-8, 77, bx, 77, color="accent", width=.8)
    line(bx, 77, bx, 119, color="accent", width=.8)
    line(bx-8, 119, bx, 119, color="accent", width=.8)

    line(3, 150, w-3, 150, color="ink", width=.65)
    text(3, 163, "Taxonomy", size=8, weight="bold")
    text(59, 163, f"L: {counts['L','identifier']} identifiers + {counts['L','attribute']} attributes", size=8)
    line(267, 156, 267, 170)
    text(279, 163, f"I: {counts['I','attribute']} contextual attributes", size=8, color="context")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUT_DIR / "fig1_overview"
    # Exact physical width: tight cropping would rescale fonts in LaTeX.
    for ext in ("pdf", "svg", "png"):
        fig.savefig(stem.with_suffix("." + ext), dpi=300, bbox_inches=None, pad_inches=0)
    print(f"Saved {stem}.{{pdf,svg,png}}; font={ko.get_file()}")
    plt.close(fig)


if __name__ == "__main__":
    main()
