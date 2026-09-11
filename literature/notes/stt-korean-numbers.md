# 한국 콜센터 STT 전사에서 숫자·식별자가 나타나는 형태 — 조사 노트

- 조사일 2026-09-11. 용도: `taxonomy.yaml: variation.stt_profile`의 근거. 합성 상담 전사(cs_transcript) 생성 정책을 실제 상용 STT 출력 분포에 맞추기 위함.
- **[?]** = 1차 출처 미확인. 주입률 수치는 측정값이 아니라 설계 선택.

## 1. 결론 먼저

1. **상용 한국어 STT는 대부분 아라비아 숫자를 출력한다.** 리턴제로는 ITN(`use_itn`) 기본 true, CLOVA·Google은 숫자 변환을 끌 수 없고, Azure ko-KR은 display form 지원, Whisper도 대체로 숫자. → 합성 전사 기본은 `010-1234-5678`, `3200만원` 형태.
2. **한글 발음전사도 실재한다.** KsponSpeech `(3학년)/(삼 학년)` 이중전사, AI Hub 고객응대 코퍼스의 `directText`(발음전사)/`standardText`(표준·숫자) 쌍, KT API 샘플 `육 년 전`. → 20% 정도는 `공일공 일이삼사 오육칠팔` 형태.
3. **STT 단에서 한국어 PII를 마스킹하는 상용 엔진은 없다.** AWS Transcribe PII redaction은 ko-KR 미지원(영·스·프·독·이·포만), Azure MaskedITN은 비속어용, CLOVA/리턴제로는 파라미터 없음. 마스킹은 전부 다운스트림 regex+NER → **한글 숫자·분할 발화는 마스킹을 통과한다.** 이것이 벤치마크의 가장 현실적인 누출 시나리오.
4. 구어 구분자는 `에`(리턴제로 ITN 예시가 하이픈으로 변환)와 `다시`(국어원: dash의 일본식 표현). 0은 `공`·`영` 모두 허용(국어원), 실무는 `공` 우세.

## 2. 벤더별 ITN 동작

| 엔진 | 숫자 출력 | 근거 |
|---|---|---|
| 리턴제로 RTZR/VITO | `use_itn` 기본 true. 「영어/숫자/단위 등에 해당하는 표현을 한글이 아닌 보다 가독성 높은 표기로 변환」. 예: `일 오 칠 칠 에 일공공일번으로` → `1577-1001 번으로`; `최대 삼천 이백만원까지` → `최대 3200만원까지`; `일 이 삼 번을` → `1 2 3 번을` (단일 숫자는 공백 유지) | https://developers.rtzr.ai/docs/stt-file/itn/ ; 파라미터 목록 https://developers.rtzr.ai/docs/stt-file/ (`use_itn`, `use_disfluency_filter`, `use_profanity_filter`, `use_diarization`, `use_paragraph_splitter`, `domain`, `keywords`) |
| Naver CLOVA Speech | 숫자 변환 스위치 없음. 문서 예시 `"5천 원이에요"` — 숫자+한글 단위 혼합이 기본 | https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-longsentence (파라미터: language, completion, wordAlignment, fullText, noiseFiltering, boostings, forbiddens, diarization, sed, format) |
| Google Cloud STT | 숫자 변환 자동, 비활성화 옵션 없음 | https://discuss.google.dev/t/speech-to-text-unexpected-transcribing-numbers-as-digits/181656 |
| Azure Speech | Lexical / ITN / MaskedITN / Display 4형 병행. ko-KR display format 지원 | https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-speech-to-text-short |
| OpenAI Whisper | 아라비아 숫자 전사 지원 확인; 「아라비아 숫자로 구성된 개인식별 정보의 경우 인식율을 높이기 위한 후처리가 필요」. 전화번호를 `010`, `1234`, `5678` 토큰으로 분리 | https://www.comworld.co.kr/news/articleView.html?idxno=50818 ; https://velog.io/@ledu202/Faster-Whisper로-오디오-속-개인정보-찾아-지우기 |
| KT AI API (2022 규격) | 샘플 출력 `육 년 전 사하라 사막에서` — 한글 숫자, ITN 파라미터 없음 [?] 현재 동작 | https://cloud.kt.com/download/KT_AI_API_standard_v1.1.pdf |
| Kakao i / Brity / NUGU / LG CNS | 공개 문서에 숫자 포맷 정보 없음 [?] | — |
| NeMo ITN | `inverse_normalize.py` lang 선택지에 `ko` 존재, 문서 매트릭스에는 없음 (성숙도 [?]) | https://github.com/NVIDIA/NeMo-text-processing/blob/main/nemo_text_processing/inverse_text_normalization/inverse_normalize.py |
| ETRI K-STW (학술) | 한자어 수사→아라비아, 고유어 1~10은 단어 유지; 숫자 토큰 정확도 84.91% | https://ksp.etri.re.kr/ksp/article/file/68666.pdf |

## 3. 공개 코퍼스의 숫자 전사 규약

| 코퍼스 | 도메인 | 숫자 규약 | 화자 라벨 | 출처 |
|---|---|---|---|---|
| KsponSpeech (AI Hub 105) | 자유 대화 1,000h | 이중전사 `(철자)/(발음)`: `(70%)/(칠 십 퍼센트)`, `(3학년)/(삼 학년)`, `(7시)/(일곱시)`, `(ARS)/(에이 알 에스)`. 발음전사는 음절 사이 공백. 태그 `/`간투어 `+`반복 `*`불명확 `b/`숨 `n/`잡음 | — | https://www.mdpi.com/2076-3417/10/19/6936/htm ; https://github.com/sooftware/KoSpeech/wiki/Preparation-before-Training |
| 상담 음성 (AI Hub 30711) | 교육·**금융**·텔레마케팅 3,000h | 「이름, 주소, 전화번호, 상황 등은 모두 창작된 것」, 샘플 「민감한 정보는 일부 마스킹(*) 처리」 | 화자 메타 | https://aihub.or.kr/aidata/30711 |
| 민간분야 고객 상담 (AI Hub 71616) | **금융·보험** 포함 3,300h | `directText` 「발화를 기준으로 한 한글 발음전사」 / `standardText` 「이중전사 대치어」(표준어·숫자·영어) | 상담사/고객 | https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71616 (IRB·안심존) |
| 공공분야 고객응대 (AI Hub 71615) | 6분야 3,300h | 동일 directText/standardText | 상담사1, 고객1, 고객2 | https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71615 |
| 민원(콜센터) QA (AI Hub 98) | **금융/보험** 포함 202k 쌍 | 창작 PII | `0: 상담사, 1: 고객` | https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=98 |
| 저음질 전화망 (AI Hub 571) | 6,500h 전화망 잡음 | — | customer/counselor | https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=571 |

리턴제로 벤치마크 CER (상담 음성): Return Zero 3.51%, CLOVA 4.91%, Whisper 7.51%, Google v2 8.37%, ETRI 8.36% — https://github.com/rtzr/Awesome-Korean-Speech-Recognition

## 4. 전화로 숫자 읽는 방식

- 국어원 온라인가나다 (2026-01-06): 「'010'은 '영일영'으로 읽을 수도 있고 '공일공'으로 읽을 수도 있겠습니다. '1234'는 보통 '일이삼사'처럼 개별 숫자로 읽는 듯하며」; 56은 실무상 '오륙'. 공식 규정 없음. https://m.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=326032
- 국어원 @urimal365: 「'다시(ダッシュ)'는 '줄표' 즉 'dash'의 일본식 표현입니다」 — 「공이 다시 일이삼 다시 ~」 질문에 대한 답. https://x.com/urimal365/status/377704686545272832
- `에` 구분자: 리턴제로 ITN 예시 `일 오 칠 칠 에 일공공일` → `1577-1001`.
- 계좌 읽기 그룹핑: 「계좌번호의 -(하이픈) 표시는 사실 전혀 중요하지 않은 표시다」(나무위키). 하이픈 위치에서 끊어 읽는다는 1차 근거는 없음 [?]. 상담사 되읽기·그룹 반복 확인은 관행적으로 가정.
- 하나/둘 고유어 사용 [?] 근거 없음.

## 5. 숫자 관련 STT 오류 유형 (근거 수준 표시)

| 오류 | 근거 | 설계 반영 |
|---|---|---|
| 유사 발음 치환 (이↔일, 삼↔사, 십↔식) | HCLT 2021 「한국어 음성 인식 시스템의 오류 유형 분류」: 유사 발음·띄어쓰기·기호부착 3대 유형 (숫자 예시 없음 [?]) https://koreascience.kr/article/CFKO202130060561801.page | `stt_digit_error` 3~5%/번호 |
| 탈락 (digit dropping) | Kakao Ent.: 긴 오디오 탈락 오류 27.6% 감소 언급 https://www.ajunews.com/view/20220921095624806 ; Whisper 종성 오류 2.67~4.53% https://www.eksss.org/archive/view_article?pid=pss-18-1-55 | `stt_digit_error` (앞 0 탈락, 한 자리 누락) |
| ITN 부분 적용·오적용 | ETRI ITN 숫자 정확도 84.91%; 리턴제로 `1 2 3 번` 예시 | `mixed_inconsistent` 10%, itn_partial 3% |
| 구분자 잔존 | `에`/`다시`가 전사에 남음 | `separator_artifact` 2% |
| 띄어쓰기·단위 부착 | `5천 원`/`5천원`/`오천 원`, `3 시`/`3시` | unit_spacing_variant 3% |
| 토큰 분할 | Whisper `010` `1234` `5678` | `chunk_split` 강화, `mixed_inconsistent` |

## 6. 금융권 전사 관행

- 화자 라벨: AI Hub 표준 `상담사:` / `고객:`; 벤더 diarization은 숫자 ID(SPEAKER_00) → 역할은 다운스트림 부여.
- 마스킹: AWS Transcribe redaction 지원 언어 목록에 ko-KR 없음 (「Redaction with batch transcriptions is available with English dialects … Spanish … French … German … Italian … Portuguese」) https://docs.aws.amazon.com/transcribe/latest/dg/pii-redaction-batch.html ; Amazon Connect Contact Lens 표에서 ko_KR Redaction 열 공란 https://docs.aws.amazon.com/connect/latest/adminguide/supported-languages.html
- 실무 패턴: post-ITN regex(전화·주민번호)+NER(주소) https://velog.io/@ledu202/… ; Datamaker STT 비식별화 사례 (텍스트 가명처리 + 오디오 묵음) https://www.datamaker.io/ko/blog/articles/review/stt-de-identification
- 금융사 사례: KB국민은행 FCC STT·TA 일 10만 콜 https://www.fetimes.co.kr/news/articleView.html?idxno=107845 ; 신한·부산경남·우리 불완전판매 방지 STT https://www.ddaily.co.kr/page/view/2021042407395429011 ; 삼성생명 STT·TTS 콜센터 https://www.fntimes.com/html/view.php?ud=202403180015337411dd55077bc2_18 ; **토스증권 Amazon Connect/Transcribe** — 민감정보는 Secure IVR(DTMF)로 받아 음성에 안 남김 https://aws.amazon.com/ko/blogs/tech/toss-securities-amazon-connect-migration-journey/ . PII 마스킹 포맷을 공개한 금융사는 없음 [?].

## 7. 설계 반영 (→ `taxonomy.yaml: variation.stt_profile`)

- 숫자 표기: 아라비아(ITN) 70% / 한글 발음 20% / 혼합·불일치(Whisper형) 10%
- 0: 공 80% / 영 20%. 구분자: 에 55% / 다시 35% / 휴지만 10%
- 오류 주입(번호 토큰당): 유사발음·탈락 4%, 구분자 잔존 2%, 단위 띄어쓰기 3%, ITN 부분 적용 3%
- 화자 라벨: 상담사/고객 70%, 화자1/2 20%, 3자 통화 10%. 문장 타임스탬프 30%.
- **pre-masked 20%**: regex 마스킹을 거쳤으나 한글 숫자·분할 발화·고객 원발화가 남은 전사 — 현실의 누출 패턴 재현.
- 새 op: `stt_digit_error`, `separator_artifact` (T2), `agent_readback` (T3: 고객 한글 숫자 ↔ 상담사 아라비아 되읽기, 동일 entity).
