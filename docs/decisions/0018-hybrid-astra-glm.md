# ADR-0018: GLM 완료본 유지, 미완료 계획 Astra/GLM 병렬 배정

- 날짜: 2026-09-20
- 상태: accepted
- 대체: ADR-0016의 Astra 단일 생성기로 전체 재생성 해석

사용자가 GLM 완료본을 다시 만들지 않고 다른 계획을 Astra에 배정하며 GLM도 병렬로 계속하라고 명시했다. 720개 계획 중 GLM 통과본 140개를 유지한다. 미완료 580개를 문서 유형·길이·T-level·주체 수로 정렬하여 교대로 배정해 Astra 290개와 GLM 290개로 나눈다. 원래 doc_id와 seed를 유지하고 allocation.json으로 중복·누락 여부를 확인한다.

`data/corpus/main-720-v2/hybrid-0920-03`에 배정 계획을 보존한다. GLM은 동시 4개, 스트리밍, 65,536 출력 상한으로 새 실행한다. 과거 비용·불확실 예약 $23.97330718를 Mango 전체 $150 한도에 이월한다. 과거 중단은 출력 한도/서버 오류로 기록되어 있으며 노트북 덮개가 원인이라고 단정하지 않는다.

Astra는 `gpt-6-astra`, reasoning_effort=low, compose_v7, max_completion_tokens=32000, 공식 OpenAI Batch를 사용한다. 최초 문서 유형별 10건, 이후 최대 40건씩 제출한다. 묶음마다 완성·자동 검증 통과율 80% 이상 및 첫 묶음의 실제 장문 통과를 확인한다. 실패는 보존하며 임의로 GLM 계획과 교체하거나 중복 제출하지 않는다. 품질 게이트 실패 시 별도 점검한다.

OpenAI 예산은 $100로 분리한다. 입력 UTF-8 바이트 수+여유분을 입력 최대 추정 토큰으로, 출력 한도를 출력 최대 토큰으로 예약한다. Batch 입력은 캐시 쓰기 최댓값 $6.25/1M, 출력 $25/1M로 보수적 계산한다. 응답 usage로 정산하되 사용량 미수신은 예약액을 유지하고 중단한다. 실제 청구액과 일치한다고 주장하지 않는다. 현재 API 잔액은 검증하지 않았다.

로컬 실행기가 60초 간격으로 Batch 상태를 확인·수집·검증하고 다음 묶음을 자동 제출한다. 이는 LLM 호출을 만들지 않는다. 제출된 Batch는 OpenAI 서버에서 실행된다. GLM 호출과 다음 Batch 제출/수집은 노트북 실행 상태에 영향을 받는다. 자동화된 Codex 정기 실행은 만들지 않는다.

근거: [Astra 모델/단가](https://developers.openai.com/api/docs/models/gpt-6-astra), [Batch](https://developers.openai.com/api/docs/guides/batch).
