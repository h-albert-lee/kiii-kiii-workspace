# 결정 기록 (ADR)

"왜 이렇게 했지?"에 답하는 곳입니다. 한 결정 = 한 파일, 번호 순.

## 규칙

- 파일명: `NNNN-짧은-제목.md` (예: `0002-generator-model.md`)
- 한 번 쓴 ADR은 고치지 않습니다. 뒤집으려면 새 ADR을 쓰고 이전 것의 상태를 `superseded by NNNN`으로 바꿉니다.
- 카톡·회의에서 정한 것도 여기 옮겨야 "결정"입니다. 회의록에는 ADR 번호만 링크.
- 길게 쓰지 마세요. 배경 → 결정 → 이유 → 대안 → 영향, 각 2~5줄.

## 목록

| # | 제목 | 상태 | 날짜 |
|---|---|---|---|
| 0001 | 프레이밍 A 채택 — 규제 기반 택소노미 + long-context 벤치마크 | accepted | 2026-09-08 |
| 0002 | 합성 데이터 생성 모델 및 리더보드 제외 규칙 | proposed | — |
| 0003 | 타겟 venue | proposed | — |
| 0004 | 택소노미 v1 설계 — 2 tier × 2 kind, 조문 단위 근거 | proposed | 2026-09-10 |

새 ADR: `cp docs/decisions/0000-template.md docs/decisions/000N-제목.md`
