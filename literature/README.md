# literature — 자료조사

## 구성

- `papers.bib` — 공용 bib. **여기가 원본**이고 Overleaf의 `references.bib`로 복사됩니다. bib key는 `저자성-연도-키워드` (예: `hahm2025thunderdeid`).
- `notes/` — 논문 한 편 = 노트 한 파일. `_template.md` 복사해서 씁니다. 파일명은 bib key와 같게.
- 전체 조사 결과와 포지셔닝은 `docs/related_work.md`에 있습니다. 여기 노트는 그 문서의 각주 역할입니다.

## 참고 자료 (조사 보고서)

- `notes/legal-sources-ko.md` — 개인정보보호법·신용정보법·금융실명법·전자금융거래법 조문 원문 인용 + 식별자 형식/체크섬 표. 택소노미 L tier의 근거.
- `notes/prior-pii-schemas.md` — Thunder-DeID·KDPII·Jang 2024·ko-pii·Gretel·ai4privacy·TAB 레이블 체계 전체 추출. 매핑표의 근거.
- `notes/evaluated-models.md` — 선행 PII 벤치마크 12편의 평가 모델 목록 + 2026-09 한국어·오픈 모델 현황·라이선스·GPU 가능 여부. `docs/models.md`의 근거.
- `notes/stt-korean-numbers.md` — 한국어 상용 STT의 숫자 출력(ITN)·공개 코퍼스 전사 규약·구어 구분자·오류 유형·금융권 마스킹 관행. `variation.stt_profile`의 근거.

## 노트 쓰는 기준

읽었으면 씁니다. 다만 "요약"보다 **우리 논문과의 관계**가 중요합니다.
- 우리가 인용할 문장은 무엇인가
- 우리와 어디가 다른가 (리뷰어가 "이거랑 뭐가 달라요?" 물으면 할 답)
- 빌려올 것 (지표, 프로토콜, 표 형식)

## 읽기 큐 (우선순위 순)

| 순서 | 논문 | 왜 | 담당 | 상태 |
|---|---|---|---|---|
| 1 | Thunder-DeID (Findings EMNLP 2025) | 택소노미 tier, 어노테이션 가이드, 지표. 리뷰어 비교 대상 1순위 | 한울 | 🔶 Appendix D 레이블 추출 완료, 본문 정독 필요 |
| 2 | KDPII (IEEE Access 2024) + Zenodo v2 | 한국어 특화 PII 실패 finding. OOD transfer 테스트 후보 | | 🔲 |
| 3 | TAB (CL 2022) | 비식별화 지표 그대로 채택 | | 🔲 |
| 4 | PII-Bench (arXiv 2025) | multi-subject 프로토콜 | | 🔲 |
| 5 | REDACT (arXiv 2026) | tier별 stratified 리포팅 템플릿 | | 🔲 |
| 6 | Pasch & Cha (PrivateNLP 2025) | back-mapping → 일관성 지표 | | 🔲 |
| 7 | 금융분야 가명·익명처리 안내서 + 신용정보법 시행령 | Legal tier 식별자 목록 | 한울 | 🔶 시행령 완료, 안내서 PDF 본문 미확인 |
| 8 | Albanese et al. Anonymous-by-Construction (arXiv 2026) | 가장 가까운 금융 de-ID. surrogate 생성 설계 | | 🔲 |
