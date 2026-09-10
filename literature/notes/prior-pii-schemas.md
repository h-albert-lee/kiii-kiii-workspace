# Prior PII label schemas — full extraction

- Extracted 2026-09-10 from primary PDFs / dataset cards / source code. Basis for `taxonomy/mapping_prior_work.md`.
- [?] = could not retrieve or verify.

---

## 1. Thunder-DeID (Hahm et al., Findings of EMNLP 2025)

- Source: ACL PDF Appendix D. **Use the Findings numbers**: 2 top tiers / 16 subcategories / 80 granular categories / 729 labels; 48,306 entities from 6,700 judgments (3,000 civil / 3,000 criminal / 700 administrative), 80/10/10 split by case type. Earlier arXiv version: 17 / 67 / 595, 27,402 entities, 4,500 judgments.
- Tier 1: **Direct = 사건관계인 특정 정보**; **Quasi = 기타 (사건관계인이나 제3자를 특정할 수 있는) 정보**.
- Marker format `≪카테고리≫entity≪/카테고리≫`; custom tokenizer with start/end marker tokens per label. Replacement lists curated for 691 of 729 labels.
- Legal basis cited: Judicial Rule No. 1778, Supreme Court Regulation No. 2809; 민사소송법 §163조의2, 형사소송법 §59조의3.
- Metrics: "binary token-level" (mask / no-mask, type-agnostic) and "token-level" (type-aware micro F1). 1.5B binary F1 0.9808; 800M token-level F1 0.9105. Per-Epoch Entity Replacement > Single.
- Annotation rules retrievable: lower-level address components and incident-related place names de-identified; dates and incident numbers are quasi; government institution names excluded unless crime location. IAA not reported [?].
- HF model `thunder-research-group/SNU_Thunder-DeID-1.5B` returns 401 (gated) [?]; GitHub `mcrl/SNU_Thunder-DeID` 404 [?].

### Taxonomy (Appendix D)

| Tier 1 | Subcategory (16) | 한국어 | Granular (80) → leaf examples |
|---|---|---|---|
| Direct | Names | 인명 | 내국인이름; 외국인이름 (Mongolian, Vietnamese, English, Japanese, Chinese … names); 아이디·닉네임 |
| Direct | Age and DOB | 연령정보 | age, year of birth, date of birth |
| Direct | Email | 이메일주소 | |
| Direct | RRN | 주민등록번호 | |
| Quasi | Work and Criminal Backgrounds | 사건관계인이력 | 범죄경력 |
| Quasi | Incident-related Numerical Info | 사건 관련 숫자 정보 | **고유번호**: bank accounts, management numbers, case numbers, **bitcoin wallets, checks, cards, bills, guarantees, receipts, bonds**, phone numbers, licenses, passwords, registrations, corporate registrations, vehicle registrations …; 장소 관련 번호 (room, unit, floor, flight, route …); 기타 숫자 |
| Quasi | Incident-related Sites | 사건 관련 장소 | interior spaces, transport infra, construction, forest/water, maritime |
| Quasi | Geographic Info | 지리정보 | 주소 (province → parcel), 지역명, 도로명, 구간 |
| Quasi | Organizations | 조직 | community, social/religious, associations (mutual aid, **labor unions**, cooperatives…), military/police units, departments, ranks/duties, illegal orgs |
| Quasi | Institutions and Facilities | 기관 및 시설 | 19 granular incl. 정부기관 (tax offices), 의료기관, 교육기관, **금융관련공공기관 (financial services agencies, banks, savings banks)** |
| Quasi | Corporate Entities | 사업체 | 19 granular incl. **금융·세무: financial companies, loan businesses, insurance companies, trust companies, pawnshops, securities companies, credit card companies, investment firms, foreign banks, tax/accounting/appraisal corporations …** |
| Quasi | Consumer Products | 상품 일반 | food/drugs, industrial, publications, ICT products |
| Quasi | Media and Telecom | 방송통신서비스 | broadcasting, platforms (incl. voice-phishing apps), e-commerce, social media, games |
| Quasi | **Financial Products and Services** | **금융서비스** | 투자·보험·대출 서비스 (loan products, insurance plans, financial investment products); 가상자산 (cryptocurrencies, exchanges) |
| Quasi | Culture and Society | 사회·문화 | heritage, arts, education/academia, events, sports, projects/contracts |
| Quasi | URL | URL | |

**Financial takeaway**: no dedicated account/card label — they are leaves inside 고유번호 (quasi). Institutions and products are labelled (public names). Monetary amounts are not PII.

---

## 2. KDPII (Fei, Kang, Park, Jang, Lee, Kim — IEEE Access 12, 2024, DOI 10.1109/ACCESS.2024.3461804)

- Abstract: built "a comprehensive and organized framework for classifying Korean PII" examining existing benchmarks (TAB cited); evaluated LMs — "most of them were significantly better at recognizing universal PII than language-specific PII". Full text not retrieved (IEEE 403) [?].
- Zenodo v1 10968609 (2024-04, CC-BY-4.0): train.json 49.8 MB / valid 6.3 / test 6.1. Zenodo v2 16759166 ("REVISED", 2024-12, mod. 2025-08): `PII_dataset_V3.json` 33.3 MB.
- **Label set = Jang et al. 2024 PNE tags** (same Yonsei lab), confirmed via ko-pii's KDPII adapter. Format: `{"query": "<dialogue>", "answer": [{"label": "PS_NAME", "form": "김민지"}, …]}` — label/form pairs, no offsets.
- Stats (ko-pii docs): 53,778 dialogue documents; test split 4,891; 42% of PERSON gold are 2-char given names.
- ko-pii on KDPII test: ACCOUNT F1 0.843, CARD F1 0.130 — **88% of KDPII gold card numbers fail Luhn** (synthetic, non-valid). Do not reuse KDPII card numbers as format ground truth.

---

## 3. Jang, Cho, Seong, Kim, Woo — Applied Sciences 14(13):5682, 2024 — 33 PNE tags

Table 6 (TTA general tag → PNE tag). 4,581 dialogs; train 4,022 (19,650 tags) / test 559 (2,659 tags); BIO; best KPF-BERT F1 0.943.

| # | Item | PNE tag | # | Item | PNE tag |
|---|---|---|---|---|---|
| 1 | Name | PS_NAME | 18 | Mobile | QT_MOBILE |
| 2 | Nickname | PS_NICKNAME | 19 | Phone/FAX | QT_PHONE |
| 3 | DOB | DT_BIRTH | 20 | **Card no.** | **QT_CARD_NUMBER** |
| 4 | Age | QT_AGE | 21 | **Account no.** | **QT_ACCOUNT_NUMBER** |
| 5 | Gender | CV_SEX | 22 | Email | TMI_EMAIL |
| 6 | Height | QT_LENGTH | 23 | Plate no. | QT_PLATE_NUMBER |
| 7 | Weight | QT_WEIGHT | 24 | Workplace | OG_WORKPLACE |
| 8 | Blood type | TM_BLOOD_TYPE | 25 | Department | OG_DEPARTMENT |
| 9 | Religion | OGG_RELIGION | 26 | Position | CV_POSITION |
| 10 | Nationality | LCP_COUNTRY | 27 | School | OGG_EDUCATION |
| 11 | Club | OGG_CLUB | 28 | Grade | QT_GRADE |
| 12 | Address | LC_ADDRESS | 29 | Major | FD_MAJOR |
| 13 | Place | LC_PLACE | 30 | ID | PS_ID |
| 14 | RRN | QT_RESIDENT_NUMBER | 31 | URL | TMI_SITE |
| 15 | Alien reg. no. | QT_ALIEN_NUMBER | 32 | IP | QT_IP |
| 16 | Passport | QT_PASSPORT_NUMBER | 33 | Military unit | CV_MILITARY_CAMP |
| 17 | Driver's license | QT_DRIVER_NUMBER | | | |

Dropped candidates (Table 5): anniversaries, medical insurance number, medical history, building name, hometown, house type.

---

## 4. ko-pii (Marker-Inc-Korea, v1.16.0, MIT)

33 rule categories: RRN, FRN, BUSINESS_REG, CORP_REG, DRIVER_LICENSE, PASSPORT, CARD, PNU, MEDICAL_INSURANCE, PRESCRIPTION_ID, EDI_DRUG, FAX, ACCOUNT, EMPLOYEE_ID, PETITION_ID, COURT_CASE, PHONE, EMAIL, IP, URL, POSTAL_CODE, VEHICLE, DOC_ID, PERSON, ADDRESS, NATIONALITY, EDUCATION, MAJOR, POSITION, DT_BIRTH, AGE, HEIGHT, WEIGHT.

Validation logic worth reusing (MIT):
- RRN: weights (2,3,4,5,6,7,8,9,2,3,4,5), c=(11−sum mod 11) mod 10; post-2020-10-05 randomised → checksum failure only lowers confidence.
- BUSINESS_REG: weights (1,3,7,1,3,7,1,3,5) + (d9×5)//10; c=(10−sum mod 10) mod 10.
- CORP_REG: alternating weights (1,2); c=(10−sum mod 10) mod 10.
- CARD: 13–19 digits, Luhn, first digit ∈ {2,3,4,5,6,9} (9 = Korean domestic e.g. BC).
- ACCOUNT: **no checksum**; "3-way anchor" — 계좌/계좌번호 keyword before 10–20 digits, or Korean bank name (60+ list) before/after.
- DRIVER_LICENSE: region code 11–28 whitelist. PASSPORT: prefix M/S/PP/PD + 8 digits.
- Grouping `CATEGORY_BY_LABEL`: 고유식별정보 / 법인·사업자 / **금융정보 (CARD, ACCOUNT)** / 민감정보(건강) / 일반 / 참조 / 준식별자.
- Benchmarks: own synthetic 540 docs F1 0.790; KDPII 4,891 docs 0.660; KLUE-NER 5,000 docs 0.419.

---

## 5. Gretel `synthetic_pii_finance_multilingual`

- 55,940 records (50,776 / 5,164); 7 languages (EN 28,910; ES, SV, DE, IT, NL, FR ≈4.4–4.6k each) — **no Korean**. Avg doc 1,357 chars. Fields: document_type, expanded_type, language, generated_text, pii_spans (start, end, type), quality scores.
- 29 PII types: account_pin, api_key, bank_routing_number, bban, company, credit_card_number, credit_card_security_code, customer_id, date, date_of_birth, date_time, driver_license_number, email, employee_id, first_name, iban, ipv4, ipv6, last_name, local_latlng, name, passport_number, password, phone_number, ssn, street_address, swift_bic_code, time, user_name.
- 60 document types observed (of "100 types × 20 subtypes" claimed), e.g. Bank Statement, Credit Card Statement/Application, Loan Application/Agreement, Mortgage Contract, Insurance Policy, Insurance/Health Insurance Claim Form, Customer support conversational log, Email, Transaction/Payment/Trade Confirmation, Tax Return, KYC-like Customer Agreement, Financial Statement, Audit Report, Securities/Investment Prospectus, Cryptocurrency Transaction Report, plus machine formats (SWIFT/MT940, FIX, FpML, XBRL, BAI, EDI, CSV).

---

## 6. ai4privacy `pii-masking-300k`

- OpenPII-220k: "27 PII classes" (list not enumerated in README [?]); FinPII-80k "~20 additional types tailored to insurance and finance" (commercial, not in public files). 6 languages (EN/FR/DE/IT/NL/ES), 177,677 train rows, 30.4M tokens.
- Label universe from repo QA file (mixes public + FinPII): BUILDING, BANK, SALARY, TIME, CREDITCARD, CARDISSUER, PIN, CVV, CARDEXPIRY, TAXNUM, BALANCE, STATE, SEX, IDCARD, DRIVERLICENSE, OTP, GIVENNAME1/2, DATE, USERNAME, PASSPORT, TEL, ACCOUNT, BIC, IP, CUR, CRYPTOADDRESS, POSTCODE, DOB, TITLE, CITY, COUNTRY, STREET, PASS, SECADDRESS, BANKCOUNTRY/STREET/MUNICIP/POSTCODE/STATE, BANKNUM, AMOUNT, IBAN, DOCNUM, SOCIALNUMBER, EMAIL, CREDRATING, GEOCOORD, LASTNAME1/2/3.
- APAC 3M release lists Korean among 30 languages; Korean share/quality unverified; financial pack commercial [?].

---

## 7. TAB (Pilán et al., Computational Linguistics 2022; arXiv 2202.00443)

- 1,268 ECHR cases; 155,006 mentions; 108,151 entities; κ = 0.74 (type, partial span), α = 0.95.
- Semantic categories (verbatim): PERSON "Names of people, including nicknames/aliases, usernames and initials." · CODE "Numbers and identification codes, such as social security numbers, phone numbers, passport numbers or license plates" · LOC · ORG · DEM "Demographic attributes … job titles, ranks, education, physical descriptions, diagnosis, birthmarks, ages" · DATETIME · QUANTITY "percentages or monetary values" · MISC.
- Identifier type: **Direct** = "values that are unique to a given individual … full name, cellphone number, address of residence, email address, social security number, bank account, medical record number." **Quasi** = "publicly known information … that does not enable re-identification when considered in isolation, but may do so when combined with other quasi-identifiers."
- Masking decision per mention ("whether the entity mention ought to be masked"); confidential attribute flag BELIEF / POLITICS / SEX / ETHNIC / HEALTH / NOT_CONFIDENTIAL (GDPR special categories); coreference links annotated.

---

Sources: [Thunder-DeID PDF](https://aclanthology.org/2025.findings-emnlp.682.pdf) · [arXiv 2506.15266](https://arxiv.org/abs/2506.15266) · [KDPII Zenodo v2](https://zenodo.org/records/16759166) · [KDPII Zenodo v1](https://zenodo.org/records/10968609) · [DOAJ](https://doaj.org/article/1e0ddb4fbc2e4451865a637cb8fccf51) · [Jang et al.](https://www.mdpi.com/2076-3417/14/13/5682) · [ko-pii](https://github.com/Marker-Inc-Korea/ko-pii) · [Gretel](https://huggingface.co/datasets/gretelai/synthetic_pii_finance_multilingual) · [ai4privacy](https://huggingface.co/datasets/ai4privacy/pii-masking-300k) · [TAB](https://arxiv.org/abs/2202.00443)
