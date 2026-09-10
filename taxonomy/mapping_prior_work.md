# Mapping to prior PII schemas

*Generated from `taxonomy.yaml` fields `thunder_deid` / `jang2024` plus ko-pii, Gretel, ai4privacy, TAB. Sources and label extraction: `literature/notes/prior-pii-schemas.md`. "—" = no counterpart.*

## Coverage summary

| Concept group | Ours | Thunder-DeID (729 labels) | KDPII / Jang 2024 (33 PNE tags) | ko-pii (33 rules) | Gretel finance (29 types) | ai4privacy 300k (27 + FinPII) | TAB |
|---|---|---|---|---|---|---|---|
| Direct/quasi split | L/I tiers + identifier/attribute kinds | 2 top tiers (사건관계인 / 기타) | flat | implicit 준식별자 group | flat | flat | direct/quasi + confidential flag + mask decision |
| Statute citation per category | **yes** | judicial rules only | none | partial (mapping.py) | none | none | GDPR special categories only |
| Account number | bank_account_no, securities_account_no (separate) | leaf in 고유번호 | QT_ACCOUNT_NUMBER | ACCOUNT (anchor, no checksum) | bban, iban, bank_routing_number | ACCOUNT, BANKNUM, IBAN | CODE |
| Card | card_no (+cvc, expiry subtypes; Luhn) | leaf in 고유번호 | QT_CARD_NUMBER (88% Luhn-invalid gold) | CARD (Luhn + BIN) | credit_card_number, security_code | CREDITCARD, CVV, CARDEXPIRY, PIN | CODE |
| Customer / member ID, CI/DI | customer_id | management numbers | — | EMPLOYEE_ID only | customer_id, employee_id | USERNAME, DOCNUM | CODE |
| Contract / policy / approval no. | contract_no | receipts, guarantees, complaints, case numbers | — | PETITION_ID, COURT_CASE | — | DOCNUM | CODE |
| Access credential | access_credential | passwords | — | — | account_pin, password, api_key | PIN, OTP, PASS | — |
| Business / corporate reg. no. | business_reg_no, corp_reg_no (checksums) | corporate registrations | — | BUSINESS_REG, CORP_REG (checksums) | — | TAXNUM | CODE |
| Transaction terms / rows | credit_transaction, transaction_record | **—** (amounts not PII) | — | — | — | AMOUNT, BALANCE, SALARY, CUR | QUANTITY |
| Delinquency / public record | delinquency_info, public_record | 사건관계인이력 (partial) | — | — | — | — | MISC |
| Income / assets / occupation | financial_capacity | — | — | — | — | SALARY | DEM |
| Credit score | credit_score | — | — | — | — | CREDRATING | — |
| Sensitive (health etc.) | sensitive_info | 범죄경력 | OGG_RELIGION | MEDICAL_INSURANCE, PRESCRIPTION_ID (IDs, not content) | — | — | confidential flag |
| Financial institution / product names | **excluded** (public) | 금융·세무 (18 types), 금융서비스, 가상자산 | — | bank names as anchors | company | BANK, CARDISSUER | ORG |
| Investment profile | investment_profile | — | — | — | — | — | — |
| Consultation content / usage / life event | consultation_content, service_usage, life_event | — | — | — | — | — | MISC |
| Crypto | crypto_wallet | bitcoin wallets; 가상자산 | — | — | — | CRYPTOADDRESS | CODE |
| Korean coverage | yes | yes (legal) | yes (dialogue) | yes (rules) | **no** | **no** (APAC 3M commercial only) | no |

## Category-level mapping (ours → prior)

| ours | Thunder-DeID | Jang 2024 / KDPII | ko-pii |
|---|---|---|---|
| person_name | 인명 > 내국인이름 / 외국인이름 | PS_NAME | PERSON |
| rrn | 주민등록번호 | QT_RESIDENT_NUMBER | RRN |
| foreigner_reg_no | — | QT_ALIEN_NUMBER | FRN |
| passport_no | 고유번호 leaf | QT_PASSPORT_NUMBER | PASSPORT |
| driver_license_no | 고유번호 > licenses | QT_DRIVER_NUMBER | DRIVER_LICENSE |
| phone_no | 고유번호 > phone numbers | QT_MOBILE / QT_PHONE | PHONE, FAX |
| address | 지리정보 > 주소 | LC_ADDRESS | ADDRESS, POSTAL_CODE |
| email | 이메일주소 | TMI_EMAIL | EMAIL |
| online_handle | 인명 > 아이디·닉네임; URL | PS_ID / PS_NICKNAME / TMI_SITE | URL |
| customer_id | 고유번호 > management numbers | — | EMPLOYEE_ID (partial) |
| business_reg_no | 고유번호 > corporate registrations | — | BUSINESS_REG |
| corp_reg_no | 고유번호 > corporate registrations | — | CORP_REG |
| bank_account_no | 고유번호 > bank accounts | QT_ACCOUNT_NUMBER | ACCOUNT |
| securities_account_no | 고유번호 leaf | — | — |
| card_no | 고유번호 > cards | QT_CARD_NUMBER | CARD |
| contract_no | 고유번호 > receipts/guarantees/complaints/case numbers | — | PETITION_ID, COURT_CASE, DOC_ID |
| access_credential | 고유번호 > passwords | — | — |
| crypto_wallet | 고유번호 > bitcoin wallets | — | — |
| credit_transaction | — | — | — |
| transaction_record | — | — | — |
| delinquency_info | — | — | — |
| financial_capacity | — | (CV_POSITION ≠ occupation) | — |
| credit_score | — | — | — |
| public_record | 사건관계인이력 (partial) | — | — |
| sensitive_info | 사건관계인이력 > 범죄경력 | OGG_RELIGION | — |
| dob_age | 연령정보 | DT_BIRTH / QT_AGE | DT_BIRTH, AGE |
| gender | — | CV_SEX | — |
| nationality | — | LCP_COUNTRY | NATIONALITY |
| family_relation | — | — | — |
| employer_affiliation | 사업체; 조직 > 세부부서 / 업무·권한 | OG_WORKPLACE / OG_DEPARTMENT / CV_POSITION | POSITION |
| education | 기관 및 시설 > 교육기관 | OGG_EDUCATION / FD_MAJOR / QT_GRADE | EDUCATION, MAJOR |
| life_event | — | — | — |
| investment_profile | — | — | — |
| consultation_content | — | — | — |
| service_usage | — | — | — |
| device_network | — | QT_IP | IP |
| location_mention | 지리정보 > 지역명; 사건 관련 장소 | LC_PLACE | — |
| lifestyle_indicator | 상품 일반 (partial) | — | — |

Prior labels with **no** counterpart in ours (deliberate): Thunder-DeID 기관·시설/사업체/상품/방송통신/사회·문화 (public entities → excluded), Jang QT_LENGTH/QT_WEIGHT/TM_BLOOD_TYPE (not financial; would fall under sensitive_info.health only if medical), CV_MILITARY_CAMP, QT_PLATE_NUMBER (could be added as a subtype of lifestyle_indicator if vehicle finance documents are generated), ko-pii PNU/EDI_DRUG.

## Reuse decisions

- **Label semantics** for names, RRN, address, age, email, education, locations follow Thunder-DeID's leaf definitions where they exist, so cross-dataset transfer tests are meaningful.
- **Checksums** for RRN, 사업자·법인등록번호, card (Luhn) follow ko-pii's implementations (MIT) — cite and reuse rather than rewrite.
- **Document-type inventory** borrows from Gretel's 60 financial document types, filtered to the 10 Korean-relevant ones in `taxonomy.yaml: document_types`.
- **KDPII test split (4,891 dialogues)** is a candidate out-of-domain transfer set for the L-identifier subset that both schemas share (12 categories).
