# experiments

실험 설정(`configs/`)과 결과(`results/`). 규칙은 [`docs/guide/experiments.md`](../docs/guide/experiments.md) 한 페이지에 있습니다.

핵심 세 줄:
1. 실행 ID `MMDD-NN`을 config·결과·커밋에 똑같이 씁니다.
2. 결과 json에는 `git_commit`, `data_version`, `prompt_version`이 반드시 있습니다.
3. 논문 수치는 `results/leaderboard.csv`에서만 가져갑니다.
