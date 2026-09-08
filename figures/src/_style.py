"""공용 figure 스타일. 모든 figure 스크립트는 이 모듈을 import 합니다.

사용:
    from _style import setup, COL_W, DBL_W, save
    setup()
    fig, ax = plt.subplots(figsize=(COL_W, COL_W * 0.7))
    ...
    save(fig, "fig2_subjects_curve")
"""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parents[1] / "out"
COL_W = 3.3   # 단일 컬럼 폭 (inch, ACL)
DBL_W = 7.0   # 더블 컬럼 폭

# 색: 흑백 인쇄에서도 구분되도록 명도 차이를 둔 팔레트
PALETTE = ["#1f3a5f", "#4f7cac", "#9ec1e6", "#c9a227", "#8c8c8c"]
MODEL_TYPE_COLORS = {"api": "#1f3a5f", "local": "#c9a227", "rule": "#8c8c8c"}


def setup() -> None:
    mpl.rcParams.update({
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "pdf.fonttype": 42,   # 폰트 임베딩 (Type 42) — 학회 PDF 검사 통과용
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def save(fig, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.pdf")
    fig.savefig(OUT_DIR / f"{name}.png", dpi=200)
    plt.close(fig)
    print(f"saved {OUT_DIR / name}.{{pdf,png}}")
