# Kiii Kiii Taxonomy v1.1-draft — Rationale, Legal Grounding, and the Variation Axis

*Source of truth is `taxonomy.yaml`; this document explains it. English, because it feeds the paper's §2. Korean statute names are kept verbatim. Statute quotations are in `literature/notes/legal-sources-ko.md`.*

## 1. Design in one paragraph

Two tiers, two kinds. **Tier L (Legal)** contains every category that a Korean statute or its enforcement decree *enumerates* as personal (credit) information — we cite the article for each. **Tier I (Identifiability)** contains categories no statute enumerates but which either act as quasi-identifiers (TAB's sense) or, when aggregated, enable profiling and hyper-personalised social engineering against a financial customer. Orthogonally, each category is an **identifier** (a span that alone points at a person or account) or an **attribute** (information about the person). The 2×2 gives: L-identifiers (17) — the must-mask core; L-attributes (7) — 개인신용정보 attributes regulated *when linked* to an identifier; I-attributes (12) — scored for extraction, optional for de-identification. A third, orthogonal axis — **surface-form variation** (§8) — controls how each value appears in text, because canonical numeric identifiers are regex-solvable and the benchmark's difficulty has to come from somewhere else. There are no I-identifiers by construction: if something identifies on its own, Korean law already covers it.

## 2. Why the legal tier is wider than "주민번호·계좌·이름"

The kickoff observation was that industry PII programmes stop at 고유식별정보 + account numbers. The statutes do not. Three findings from the law.go.kr text shape the tier:

1. **신용정보법 §2 1호의2 and 시행령 §2 make the identifier list explicit and long.** Beyond 성명·주소·전화번호 (가목 1), the decree adds 전자우편주소 and SNS 주소 (§2①), the four 개인식별번호 (§2②), **CI/DI and any identifier a 신용정보회사등 assigns to a customer** (§2③ — this is the legal home of 고객번호/회원번호, which no prior Korean schema labels), and 법인등록번호·사업자등록번호 (§2④).
2. **개인신용정보 is defined by linkage.** §2 1호 가목 says identifying information is credit information "only when combined with" 나~마목 (transaction, creditworthiness, capacity, other). Conversely, transaction terms, delinquency events, income/assets, credit scores and public records *are* 개인신용정보 once an identifier is present. That is exactly the long-context, multi-subject situation the benchmark targets, and it is why L-attributes carry `span_policy: mask_if_linked` rather than `must_mask`.
3. **Financial-transaction identifiers have their own statutes.** 금융실명법 §4 (거래정보등), 전자금융거래법 시행령 §7④ (거래계좌의 명칭 또는 번호, 보험증권번호, 거래 일시·금액·상대방) and 전자금융거래법 §2 10호 (접근매체: cards, certificates, 이용자번호, biometrics, passwords) ground account numbers, policy/contract numbers, card data and credentials without appeal to PIPA's general definition.

Result: the Legal tier is a *citable* list, which is the differentiator against Thunder-DeID (court-practice-driven), KDPII/Jang (survey-driven, flat) and every English benchmark (GDPR/HIPAA or no grounding).

## 3. Tier L categories and their basis

| id | 한국어 | Basis | Kind | Policy |
|---|---|---|---|---|
| person_name | 성명 | PIPA §2 1호 가; CIA §2 1호의2 가1) | identifier | must_mask |
| rrn | 주민등록번호 | PIPA §24조의2, 시행령 §19 1호; CIA 시행령 §2② 1호 | identifier | must_mask |
| foreigner_reg_no | 외국인등록번호 | PIPA 시행령 §19 4호; CIA 시행령 §2② 4호 | identifier | must_mask |
| passport_no | 여권번호 | PIPA 시행령 §19 2호; CIA 시행령 §2② 2호 | identifier | must_mask |
| driver_license_no | 운전면허번호 | PIPA 시행령 §19 3호; CIA 시행령 §2② 3호 | identifier | must_mask |
| phone_no | 전화번호 | CIA §2 1호의2 가1) | identifier | must_mask |
| address | 주소 | CIA §2 1호의2 가1) | identifier | must_mask (generalize to 시/군/구) |
| email | 전자우편주소 | CIA 시행령 §2① 1호 | identifier | must_mask |
| online_handle | SNS 주소·아이디 | CIA 시행령 §2① 2호 | identifier | must_mask |
| customer_id | 고객식별번호 (고객·회원번호, CI/DI) | CIA 시행령 §2③ 1·2호 | identifier | must_mask |
| business_reg_no | 사업자등록번호 | CIA 시행령 §2④ 2호 | identifier | must_mask |
| corp_reg_no | 법인등록번호 | CIA 시행령 §2④ 1호 | identifier | must_mask |
| bank_account_no | 계좌번호 | 금융실명법 §2 3호·§4; 전자금융거래법 시행령 §7④ 3호 | identifier | must_mask |
| securities_account_no | 증권계좌번호 | 금융실명법 §4; CIA §2 1호의3 라 | identifier | must_mask |
| card_no | 카드번호 (+CVC·유효기간) | CIA §2 1호의3 가2); 전자금융거래법 §2 10호 가 | identifier | must_mask |
| contract_no | 계약·증권·거래번호 | 전자금융거래법 시행령 §7④ 3호; CIA §2 1호의3 다 | identifier | must_mask |
| access_credential | 접근매체 (비밀번호·OTP·인증서) | 전자금융거래법 §2 10호 나·다·마 | identifier | must_mask (suppress) |
| credit_transaction | 신용거래정보 | CIA §2 1호의3 | attribute | mask_if_linked |
| transaction_record | 거래내역 | 전자금융거래법 시행령 §7④ 1·2호; 금융실명법 §4 | attribute | mask_if_linked |
| delinquency_info | 신용도판단정보 | CIA §2 1호의4 | attribute | mask_if_linked |
| financial_capacity | 신용거래능력판단정보 (직업·재산·채무·소득·납세) | CIA §2 1호의5 가 | attribute | mask_if_linked |
| credit_score | 개인신용평점 | CIA §2 1호의6 라 | attribute | mask_if_linked |
| public_record | 공공정보 (재판·조세·채무조정) | CIA §2 1호의6 가~다 | attribute | mask_if_linked |
| sensitive_info | 민감정보 (건강·범죄경력·사상 등) | PIPA §23; 시행령 §18 | attribute | must_mask |

## 4. Tier I categories

| id | 한국어 | Why it matters | Nearest prior label |
|---|---|---|---|
| dob_age | 생년월일·연령 | Classic quasi-identifier (TAB DEM/DATETIME). PIPA-personal but not in CIA's identifier list → I, argued in §6 | Thunder 연령정보; Jang DT_BIRTH/QT_AGE |
| gender | 성별 | Quasi-identifier | Jang CV_SEX |
| nationality | 국적 | Quasi-identifier; distinct from 인종·민족 (L/sensitive) | Jang LCP_COUNTRY |
| family_relation | 가족관계 | Quasi + social-engineering pretext ("your son's account") | — |
| employer_affiliation | 직장·부서·직위 | Quasi; spear-phishing personalisation level 2–3 (Francia et al. 2026) | Thunder 사업체/조직; Jang OG_* |
| education | 학력 | Quasi | Jang OGG_EDUCATION |
| life_event | 생애 사건 (퇴직·상속·이사…) | The strongest phishing hook in consultation text | — |
| investment_profile | 투자성향 | Securities-specific; collected under 자본시장법 §46 but not credit information | — |
| consultation_content | 상담·민원 내용 | 성현's core proposal; legally exportable, behaviourally dangerous | — |
| service_usage | 서비스 이용 패턴 | Time/channel habits → timing of attacks | — |
| device_network | IP·기기 | Borderline legal (IP often held to be PII); v1 keeps in I | Jang QT_IP |
| location_mention | 거주 지역·방문 지점 | Sub-address geography | Thunder 지역명; Jang LC_PLACE |

Tier I is explicitly **not a legal claim**. The paper should say so in one sentence and cite TAB (quasi-identifiers), Baroud et al. 2025 (indirect identifiers) and Staab et al. 2024 (attribute inference) as the conceptual lineage.

## 5. Span policies → task definitions

- **Span extraction** scores all 38 categories, reported as micro-F1 overall and stratified by tier and kind (L-id / L-attr / I), following REDACT's sensitivity-tier reporting. Category-level scoring; subtypes are recorded but not scored in v1.
- **De-identification** is scored on `must_mask` categories (all L-identifiers + sensitive_info) with TAB-style risk-weighted recall, plus `mask_if_linked` categories evaluated under the *linked* condition (the document contains ≥1 identifier of the same subject — always true in our corpus). Utility is information loss on non-PII tokens. **Cross-mention consistency**: the same entity (by gold coreference id) must map to the same surrogate throughout a document.
- **Identifiability probe** (small, optional): on de-identified outputs, an attacker LLM tries to infer subject attributes from I-tier spans; report inference accuracy. This is the one paragraph that carries the phishing motivation.

## 6. Open questions for review (→ ADR-0004 list)

*Removed in v1.1 for weak grounding: `crypto_wallet` (특금법 regulates VASPs, not wallet addresses as personal data) and `lifestyle_indicator` (no statutory or prior-schema lineage; overlaps financial_capacity and transaction_record). Both are recorded under `exclusions` with rationale.*

1. **dob_age: L or I?** PIPA treats DOB as personal information; CIA does not list it as an identifier; 가명정보 가이드라인 treats age as 식별가능정보 (generalise to 10-year bands). v1: I, with `generalize`. Reviewer risk: moderate.
2. **device_network (IP): L or I?** Korean case law and PIPC guidance often treat IP as personal information [?]. v1: I. Consider promoting if a citable PIPC decision is found.
3. **consultation_content boundary.** Highest annotation ambiguity. Need a written guideline + IAA on a 100-doc pilot before generation at scale.
4. **Employee names.** Agent/상담사 names are personal information but not the customer's. v1 tags them as person_name with `subject_role: staff` so analysis can split. Decide whether the de-id task must mask them (likely yes).
5. **Scoring subtypes.** v1 no. Revisit if card CVC vs PAN or deposit vs securities account shows divergent behaviour worth a table.

## 7. What differs from Thunder-DeID (for the related-work paragraph)

Thunder-DeID's 729 labels are induced from court judgments and organised by *judicial* relevance (사건관계인 vs 기타). Financial identifiers (bank accounts, cards, bills, bonds, checks) sit as leaves inside a single generic bucket 고유번호 with no format or checksum modelling; financial *institutions* and *products* are rich (18 institution types, loan/insurance/investment products, crypto exchanges) but those are public names, not customer data; and monetary amounts, transaction rows, credit scores, delinquency, income and consultation content are absent because judgments do not contain them as customer records. Our taxonomy inverts the emphasis: account/card/contract/customer identifiers get dedicated, format-validated categories; credit-information attributes are first-class; institution and product names are *excluded* as public information. Overlap is real for names, RRN, address, age, email, organisations and locations — the mapping table (`mapping_prior_work.md`) lets us reuse their label semantics there.

## 8. The variation axis — why this is a DLP benchmark and not an NER benchmark

If every 주민등록번호 appeared as `900101-1234567` and every account as `110-123-456789`, a regex with a checksum would score near 1.0 and the leaderboard would measure nothing. Real AI-DLP inputs — chat logs, STT transcripts of call-centre audio, OCR'd scans, pasted tables, and deliberate exfiltration — carry the same values in forms no pattern anticipates. So `taxonomy.yaml: variation` defines five **levels** and 26 **operations**, each with an `applies_to` selector (numeric_id / text_id / attribute / specific ids) and a `regex_catchable` flag:

| Level | Name | What changes | Regex? | Representative ops |
|---|---|---|---|---|
| T0 | canonical | nothing — standard notation with keyword anchor | yes | — (ceiling for the rule baseline) |
| T1 | formatting | separators, grouping, partial masking, affixes, honorifics, address granularity | mostly | sep_drop, regroup, partial_mask, honorific_wrap |
| T2 | lexical | Korean-numeral dictation (STT), mixed/Hanja digits, fullwidth/circled Unicode, OCR confusables, typos, name obfuscation (김O지, KMJ), romanisation, verbal amounts | no | hangul_digits, unicode_variant, ocr_confusable, name_obfuscation |
| T3 | structural | value split across turns/lines/cells, missing or wrong keyword anchor, coreference-only mentions, multi-subject interleaving, table layouts, negation/hypothetical | no | chunk_split, anchor_missing, anchor_wrong, coref_reference |
| T4 | encoded | reversed, base64/hex, arithmetic hints, homoglyph substitution (intentional evasion) | no | reversed, base64_hex, arithmetic_hint |

Each document is generated at one level (default mix T0 25 / T1 30 / T2 20 / T3 20 / T4 5 %); every gold span records its `applied_ops`, so recall can be analysed per operation. **Hard negatives** (six types: look-alike numbers, checksum-invalid values, public entities, dates shaped like RRN prefixes, placeholders, unattributed amounts) are injected at ~30 % of gold span count to make precision meaningful — a system that flags every 13-digit string should pay for it.

This gives the paper its third controlled variable alongside subject count and context length, and its most practitioner-relevant figure: rule/regex baselines vs. LLMs vs. Korean local LLMs as a function of T-level. The expected shape — rules collapse at T2, general LLMs hold through T2 and degrade at T3 (chunk_split, coref), everything struggles at T4 — is a hypothesis to test, not a result to assume. Two ops deserve a sentence each in the paper: `partial_mask` (DLP systems routinely pass "already masked" strings that still leak birth date and gender) and `hangul_digits` (call-centre STT output is the dominant unstructured PII source in Korean finance, and it is invisible to every digit regex).

Prior art for the axis: Mind the Gap (Zafar & Nowaczyk 2026) has 7 OOD shift categories for English PII; REDACT stratifies by "disclosure form"; AmBench isolates name ambiguity. None cover dictated Korean numerals, cross-turn splitting, or partial-mask leakage, and none tie variation to a legal tier.
