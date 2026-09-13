# STATUS — 현황 보드

> 매주 월요일 갱신. 최신 상태만 남기고 지난 내용은 지웁니다 (이력은 git log에 있습니다).
> 마지막 갱신: 2026-09-13 (한울)

## 목표

- 산출물: 4페이지 short paper (workshop 또는 Findings)
- 목표 일정: 초고 2~3주 (≈ 9월 말)
- 타겟 venue: [?] PrivateNLP / TrustNLP / FinNLP 중 데드라인 확인 후 결정 → ADR 예정

## 마일스톤

| # | 마일스톤 | 상태 | 담당 | 메모 |
|---|---|---|---|---|
| M0 | 선행연구 조사 + 포지셔닝 확정 | ✅ 완료 | 한울 | `docs/related_work.md`, ADR-0001 |
| M1 | 택소노미 v1 (Legal / Identifiability, 법령 매핑) | ✅ v1.2 accepted | 한울 | `taxonomy/taxonomy.yaml` (36 카테고리 + 변형 축 T0~T3 + STT 프로필), ADR-0004 |
| M2 | 합성 코퍼스 생성 파이프라인 + 파일럿 100건 | 🔶 파이프라인 스캐폴드 완료 (테스트 9/9), 파일럿 미실행 | 한울 | ADR-0002 슬롯 채우기, `docs/generation_design.md`, `src/generate/` |
| M3 | 평가 스크립트 (스팬 F1 / 비식별화 지표 / 일관성) | 🔲 | [?] | TAB 지표 채택 |
| M4 | 리더보드 실험 (API + 한국어 로컬 LLM) | 🔲 모델 확정 | [?] | ADR-0005, `docs/models.md` 15+4 (ID 검증 완료) |
| M5 | figure + 분석 | 🔲 | [?] | |
| M6 | 논문 초고 (Overleaf) | 🔲 | [?] | |

## 이번 주 할 일

- [x] 택소노미 초안 (법령 조문 매핑) — `taxonomy/taxonomy.yaml`, `taxonomy.md`
- [x] Thunder-DeID·KDPII·ko-pii 매핑표 — `taxonomy/mapping_prior_work.md`
- [x] ADR-0004 accepted (dob_age·IP는 I 유지, 상담내용 운영 규칙, 직원 이름 must_mask)
- [x] 생성 방식 결정 (ADR-0002 슬롯 채우기) + `src/generate` 스캐폴드 + 테스트
- [x] 모델 조사 + 리더보드 확정 (ADR-0005) + 2026-09-13 ID·접근성 재검증 (GPT-5.6, Gemini 3.8 Flash, Qwen3.6; HCX 호출 가능 확인)
- [ ] **파일럿 100건 실행**: `python -m src.generate.run plan --n 100` → compose (API 키 필요) → fill → 한울 검수
- [ ] compose 프롬프트 파일럿 후 튜닝 (슬롯 준수율, 태그 경계)
- [ ] 이름·주소 사전 확장 (현재 시드 수준: 성 20·이름 음절 20·도로 8)
- [ ] `src/eval/metrics.py` — (tier×kind)×T-level 격자, op별 recall, 조각 partial-overlap
- [ ] 금융분야 가명·익명처리 안내서 PDF 본문 직접 확인
- [ ] 타겟 venue 데드라인 조사 → ADR-0003
- [ ] Overleaf 프로젝트 생성 + submodule 연결

## 막힌 것 / 결정 필요

- 파일럿 생성용 API 키 (gpt-5.6-sol / claude-sonnet-5 중 택1)
- **NCP CLOVA Studio 이용 신청 + 서비스 앱 심사 신청** (테스트 키 60K TPM으로는 16k 문서 병목) — 심사 기간 미명시라 빨리
- Upstage 콘솔 가입 (Solar Pro 4, HCX 보험)
- GPU 확보 (80GB 1장) — 로컬 20% 슬라이스 생성 + 오픈 모델 10종 평가
- 타겟 venue (ADR-0003)

## 최근 결정

- ADR-0004 accepted, ADR-0002 생성 방식(슬롯 채우기·API 주생성+로컬 20%), ADR-0005 리더보드 14+4 (2026-09-13)
- T4 encoded 변형 레벨 제외; STT 프로필 자체 조사로 확정 (2026-09-11)
- ADR-0004 택소노미 v1 설계 proposed (2026-09-10)
- ADR-0001 프레이밍 A 채택 (2026-09-08)
