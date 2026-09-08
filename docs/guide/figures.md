# Figure 가이드

## 원칙 하나

**모든 figure는 스크립트로 다시 만들 수 있어야 합니다.** 수치가 바뀌면 스크립트만 다시 돌립니다. 손으로 그린 그림은 없습니다.

## 디렉토리

```
figures/
├── src/
│   ├── fig1_taxonomy.py         ← Figure 1 만드는 스크립트
│   ├── fig2_subjects_curve.py
│   └── _style.py                ← 공용 스타일 (색, 폰트, 크기). 모든 스크립트가 import
└── out/
    ├── fig1_taxonomy.pdf        ← 논문용 (벡터)
    ├── fig1_taxonomy.png        ← 슬라이드/카톡용
    └── ...
```

파일명은 `figN_짧은이름` 으로 통일. 논문에서 번호가 바뀌면 파일명도 바꿉니다.

## 스크립트 규칙

- 입력은 `experiments/results/leaderboard.csv` 또는 `results/*.json`만. 스크립트 안에 숫자를 직접 적지 않습니다.
- `python figures/src/fig2_subjects_curve.py` 한 줄로 `out/`에 pdf와 png가 둘 다 나와야 합니다.
- 스타일은 `_style.py`에서만 정합니다. 개별 스크립트에서 색·폰트를 새로 정하지 않습니다.
- 크기: 단일 컬럼 3.3in, 더블 컬럼 7in (ACL 템플릿 기준). 폰트 8–9pt.

## Overleaf 반영

```bash
scripts/sync_figures.sh
```

`figures/out/*.pdf`를 `paper/figures/`로 복사하고 Overleaf에 push합니다. 실행 전에 `paper/` submodule이 최신인지 확인하세요 (`docs/guide/overleaf.md`).

## 체크리스트 (PR 전)

- [ ] 스크립트만으로 재생성됨
- [ ] 축 라벨·단위·범례 있음
- [ ] 흑백 인쇄해도 구분됨 (색만으로 구분하지 않음)
- [ ] 캡션 초안을 PR 설명에 적었음
