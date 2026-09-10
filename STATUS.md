# STATUS — 현황 보드

> 매주 월요일 갱신. 최신 상태만 남기고 지난 내용은 지웁니다 (이력은 git log에 있습니다).
> 마지막 갱신: 2026-09-10 (한울)

## 목표

- 산출물: 4페이지 short paper (workshop 또는 Findings)
- 목표 일정: 초고 2~3주 (≈ 9월 말)
- 타겟 venue: [?] PrivateNLP / TrustNLP / FinNLP 중 데드라인 확인 후 결정 → ADR 예정

## 마일스톤

| # | 마일스톤 | 상태 | 담당 | 메모 |
|---|---|---|---|---|
| M0 | 선행연구 조사 + 포지셔닝 확정 | ✅ 완료 | 한울 | `docs/related_work.md`, ADR-0001 |
| M1 | 택소노미 v1 (Legal / Identifiability, 법령 매핑) | 🔶 초안 완료, 리뷰 대기 | 한울 → 성현 리뷰 | `taxonomy/taxonomy.yaml` v1.1-draft (36 카테고리 + 변형 축 T0~T4), ADR-0004 |
| M2 | 합성 코퍼스 생성 파이프라인 + 샘플 100건 | 🔲 | [?] | 생성 모델 결정 필요 (ADR 예정) |
| M3 | 평가 스크립트 (스팬 F1 / 비식별화 지표 / 일관성) | 🔲 | [?] | TAB 지표 채택 |
| M4 | 리더보드 실험 (API + 한국어 로컬 LLM) | 🔲 | [?] | 모델 리스트 확정 필요 |
| M5 | figure + 분석 | 🔲 | [?] | |
| M6 | 논문 초고 (Overleaf) | 🔲 | [?] | |

## 이번 주 할 일

- [x] 택소노미 초안 (법령 조문 매핑) — `taxonomy/taxonomy.yaml`, `taxonomy.md`
- [x] Thunder-DeID·KDPII·ko-pii 매핑표 — `taxonomy/mapping_prior_work.md`
- [ ] **성현 리뷰**: 택소노미 금융 현실성 + ADR-0004 열린 질문 6개 (dob_age·IP tier, 상담내용 경계, 직원 이름, 변형 분포, T4 포함 여부)
- [ ] 변형 연산 26개 중 STT 재현(hangul_digits·chunk_split)은 실제 콜센터 STT 산출물 샘플 형태를 성현님께 확인
- [ ] 금융분야 가명·익명처리 안내서 PDF 본문 직접 확인 (식별자/속성정보 표) — 자동 파싱 실패
- [ ] 어노테이션 가이드라인 초안 (특히 consultation_content, life_event)
- [ ] 타겟 venue 데드라인 조사
- [ ] Overleaf 프로젝트 생성 + submodule 연결

## 막힌 것 / 결정 필요

- 합성 데이터 생성 모델 선택 (API·로컬 모두 가능, 리더보드에 generator 표기 규칙) → ADR-0002 예정
- ADR-0004 택소노미 설계 accepted 여부 (열린 질문 6개)
- 리더보드 모델 리스트 (한국어 로컬 LLM 후보: HyperCLOVA X, EXAONE, Kanana … [?] 확인 필요)

## 최근 결정

- ADR-0004 택소노미 v1 설계 proposed (2026-09-10)
- ADR-0001 프레이밍 A 채택 (2026-09-08)
