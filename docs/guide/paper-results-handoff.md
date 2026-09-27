# 논문 결과표 채우기 — 2026-09-27

논문 본문은 4페이지를 유지하며, 추가 분석표는 부록에 둡니다. 기존 overview 그림과 taxonomy 표는 보존했습니다. 현재 표는 제출용 최종 결과가 아니라 결과를 받아 넣기 위한 초안입니다. `P`는 완료/검증 대기, `--`는 해당 없음이며 0점과 구별합니다.

| 표 / LaTeX label | 위치와 역할 | 채우는 원천 |
|---|---|---|
| Table 2 / `tab:main-results` | 본문: Full/Local strict F1, baseline 문서 F1, LLM 실패율 | 최종 공통 cohort의 result.json `metrics.exact_micro.f1`, `reliability.failure_rate` |
| Table 3 / `tab:taxonomy-results` | 부록: 13조건 × L-identifier/L-attribute/I-attribute의 P/R/F1 | `tier_kind_tlevel`의 TP/FP/FN을 T 전체에 합산 후 P/R/F1 재계산 |
| Table 4 / `tab:paired-context` | 부록: 5개 LLM의 full−local ΔF1, paired bootstrap 95% CI | 동일 문서·프로토콜의 완료 paired 결과; 2,000회, seed 0 |
| Table 5 / `tab:response-diagnostics` | 부록: 완료 4조건의 provisional strict/itemwise/fence/character 점수 | 아래 고정된 보조 분석 JSON. 원래 headline 점수를 대체하지 않음 |

Table 2–4는 아직 모두 P입니다. CPU baseline 전체 릴리스 결과도 최종 LLM 공통 집합과 맞는지 확인한 뒤 넣습니다. 확장 9B/8B는 별도 cohort 감사 대상이며 기존 core 결과와 gate 해시를 수정해 합치지 않습니다. 부분/pilot 점수는 넣지 않습니다. 평균 category F1을 taxonomy-group micro-F1으로 쓰지 않습니다. 숫자는 표시할 때 100배, 원본은 0–1입니다.

Table 5의 실제 수치는 다음 네 `analysis.json`에서 읽어 소수 둘째 자리로 표시했습니다. 입력 SHA와 출력 행은 [검토 기록의 입력 매핑](../reviews/2026-09-27-paper-table-inputs.json)에 있습니다.

- `experiments/results/analyses/0927-response-diagnostics-v1/0925-01-kanana-3b-full/`
- `experiments/results/analyses/0927-response-diagnostics-v1/0925-02-kanana-3b-local/`
- `experiments/results/analyses/0927-response-diagnostics-v1/0925-03-qwen-2b-full/`
- `experiments/results/analyses/0927-response-diagnostics-v1-update-ac25513/0925-06-qwen-4b-local/`

S/I/W는 각 stage의 `metrics.exact_micro.f1`, C는 fence_itemwise의 `metrics.category_character_micro.f1`, W-Prc/W-Rec는 같은 단계 exact precision/recall입니다. Invalid items는 `invalid_item_false_positives`; Strict Fail은 strict `requests_with_errors / requests`입니다. I/W의 exact FP 벌점과 문자 점수의 unanchorable-item 한계는 캡션에 남깁니다. Native 계측/gate 원본이 아직 없으므로 Table 5는 검증된 응답의 사후 진단 snapshot이며 확정 모델 순위가 아닙니다.

문맥 효과 그림을 최종 본문에 넣는다면 Table 4의 검증된 Δ/CI를 사용한 forest plot으로 대체하고 본문 페이지를 다시 확인합니다. 현재는 가상 점·오차막대를 그리지 않았습니다. 사라가 문맥 효과와 오류 해석을 맡고, 실제 추론 담당과 공통 cohort 운영 역할은 기존 배정대로 유지합니다.

편집은 Overleaf 원본에서 코멘트 앵커를 보존하는 작은 변경으로 합니다. Overleaf → GitHub Sync 후 로컬 paper를 fast-forward하고 연구 레포의 submodule 포인터를 갱신합니다. 결과가 새로 도착해도 paper로 무조건 git push하거나 파일 전체를 교체하지 않습니다. 익명 본문/표에는 사람·조직명·식별 가능한 저장소 링크를 넣지 않습니다.

남은 제출 전 작업: native capacity 증빙/공통 집합 확정, 누락 조건 결과 수령, Table 2–4 채우기, paired 해석과 결론 업데이트, 기존 부록 A–C의 TODO 정리, provisional/placeholder 표시 제거 여부 검토. 추가 표와 본문을 계속 누적하지 말고 본문 4페이지 안에서 교체·요약합니다.
