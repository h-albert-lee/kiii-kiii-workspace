# ADR-0002: 합성 데이터 생성 방식 — 슬롯 채우기, 생성 모델, 리더보드 표기

- 상태: accepted
- 날짜: 2026-09-13
- 결정자: 한울
- 관련: ADR-0001, ADR-0004, `docs/generation_design.md`, `taxonomy/taxonomy.yaml`

## 배경

합성 코퍼스는 gold 스팬이 정확해야 벤치마크가 된다. LLM에게 "PII가 든 문서를 쓰고 스팬도 표시해라"고 하면
(a) 체크섬 무효 값(KDPII 카드번호 88% Luhn 불통과), (b) 오프셋 오류, (c) 생성 모델이 자기 문서에서 유리해지는 편향이 생긴다.
또한 ADR-0001에서 생성·평가 모델을 로컬로 한정하지 않기로 했다.

## 결정

1. **슬롯 채우기(slot-filling) 생성.** LLM은 식별자 값을 절대 쓰지 않는다. 문서 텍스트를 `{{person_name:1}}`, `{{bank_account_no:1:bank=신한}}` 같은 **타입 슬롯**과 함께 작성하고, 값은 코드가 채운다.
   - L-identifier 값: `src/generate/identifiers.py`가 체크섬·은행 템플릿으로 생성.
   - L-attribute·I 스팬: LLM이 `[[credit_transaction]]대출 잔액 3,200만 원[[/credit_transaction]]` 형태의 **인라인 태그**로 표시 (값 자체가 자연어라 코드 생성 불가). 태그는 후처리에서 제거되고 오프셋만 남는다.
   - 결과: 식별자 gold는 구성상 정확, 속성 gold는 LLM 표기 + 검증기(태그 균형, 카테고리 존재, 최소 길이) + 파일럿 100건 사람 검수.
2. **변형은 후처리.** 슬롯 값에 `variation.ops`를 코드로 적용(T1·T2 전부, T3 중 anchor_missing·anchor_wrong·table_cell). 발화 간 분할·되읽기·대용 지칭(T3 나머지)은 슬롯 지시자(`{{bank_account_no:1|split=2}}`, `{{person_name:1|coref}}`)로 LLM이 텍스트 구조를 만들고 코드가 값을 배치한다.
3. **생성 모델.** 주 코퍼스 문서 작성은 **frontier API 1종**(gpt-5.6-sol 또는 claude-sonnet-5 — 파일럿에서 한국어 금융 문체 품질로 선택), 검증용 20% 슬라이스는 **로컬 Qwen3.6-35B-A3B**로 동일 프롬프트 생성. 두 슬라이스 간 리더보드 순위 상관을 보고해 생성 모델 편향을 정량화한다.
4. **리더보드 표기.** 생성에 쓴 모델은 리더보드에 올리되 `model_type: generator`로 표기하고 헤드라인 순위 산정에서 제외한다(별도 행). 문서 작성만 했고 식별자 값·변형은 코드가 만들었으므로 편향이 제한적임을 논문에 명시한다.
5. **문서 단위 메타**: `doc_type`, `variation_level`, `num_subjects`, `context_len_bucket`, `generator` 를 반드시 기록. 세 통제 변수(subject 수 × 길이 × T-level)는 생성 시 층화 샘플링한다.
6. **실제 데이터 금지.** 어떤 슬롯 값도 실제 고객 데이터에서 오지 않는다. 이름은 성·이름 사전 조합, 주소는 공개 도로명 사전 + 가짜 번지.

## 이유

- 슬롯 채우기는 SPY·Gretel·CI-Bench가 쓴 방식의 엄격한 버전이며, gold 정확성 논란을 차단한다.
- 식별자 값을 LLM이 만들지 않으므로 생성 모델이 "자기 값"을 알아보는 편향이 없다. 속성 스팬은 남지만 20% 로컬 슬라이스로 측정한다.
- API 모델을 쓰면 문체 다양성과 한국어 금융 문서 현실성이 좋고, 토스 측 제약(외부 API에 PII 금지)은 우리 합성 데이터에는 해당하지 않는다 — 실제 PII가 없다.

## 검토한 대안

- **LLM이 값까지 생성 + 사후 NER 어노테이션** — gold 오류·체크섬 무효·오프셋 불일치. 기각.
- **템플릿만(LLM 없음)** — 다양성 부족, I tier 자연어 스팬 생성 불가. 기각.
- **로컬 모델만으로 생성** — 품질 저하, ADR-0001에서 제한 없기로 결정. 20% 슬라이스로 축소 채택.

## 영향

- `src/generate/`: identifiers, variation, compose(슬롯 프롬프트), fill, validate, run. 스키마는 `docs/generation_design.md`.
- 프롬프트 파일 `src/prompts/compose_v1.txt`. 버전 바꾸면 새 파일.
- 파일럿 100건: 문서유형 10종 × 레벨 4 × subject {1,3,8} 층화. 사람 검수(한울) 후 분포 조정.
