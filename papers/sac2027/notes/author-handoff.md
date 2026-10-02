# Author and submission handoff — 2026-10-02

Use [docs/authors.yaml](../../../docs/authors.yaml) as the shared administrative source of truth. This document is for submission operators, not the anonymous PDF or source archive. The operator supplied the order, affiliations and roles, then personally selected all six OpenReview profiles and reordered them in the workshop form. No email address or ORCID has been supplied for this roster: collect the actual addresses needed by EasyChair rather than guessing from masked profile emails.

| Order | Manuscript/submission name | Operator-specified affiliation | Role | Operator-confirmed OpenReview profile |
|---|---|---|---|---|
| 1 | Eunbin Shin | LG AI Research | Equal first author | [~Eunbin_Shin2](https://openreview.net/profile?id=~Eunbin_Shin2) |
| 2 | Sara Yu | KT | Equal first author | [~Sara_Yu1](https://openreview.net/profile?id=~Sara_Yu1) |
| 3 | Seonghyun Kim | Toss Securities | Author | [~Seonghyun_Kim2](https://openreview.net/profile?id=~Seonghyun_Kim2) |
| 4 | MinKyeong Shin | Shinhan Securities | Author | [~MinKyeong_Shin1](https://openreview.net/profile?id=~MinKyeong_Shin1) |
| 5 | Yewon Hwang | kakao mobility | Author | [~Yewon_hwang3](https://openreview.net/profile?id=~Yewon_hwang3) |
| 6 | Hanwool Lee | Seoul National University **and** AIM Intelligence | Corresponding author | [~Hanwool_Lee1](https://openreview.net/profile?id=~Hanwool_Lee1) |

## Names and affiliations: avoid carrying over profile artifacts

- MinKyeong Shin is the spelling on the profile selected by the operator; the earlier `Minkyung Shin` was explicitly provisional. Use `MinKyeong Shin` for consistency with the actual workshop submission; ask the author only if a later preferred publication spelling differs.
- The Yewon profile displays `Yewon hwang`; the operator specified `Yewon Hwang`. Keep the supplied capitalization in manuscript/EasyChair fields where editable, while retaining profile ID `~Yewon_hwang3`.
- Use **Seonghyun Kim**, not the older template's `Sunghyun Kim`; use **Hanwool Lee**, not `Hanwool Albert Lee`.
- Profile institutional histories do not override supplied current affiliations. The workshop record displays LG Corporation and Shinhan Financial Group, and no active institution for Sara, Seonghyun or Yewon. Those are OpenReview metadata limitations, not claims that they lack affiliations. For SAC, enter the affiliations in the table above.
- Hanwool has two affiliations. Do not collapse them into one organization or replace SNU with AIM alone. Obtain requested city/address/email/ORCID fields from the author rather than inventing them.

## Roles and anonymous handling

Equal-contribution wording: **“Eunbin Shin and Sara Yu contributed equally to this work.”** Keep Eunbin first and Sara second; equal contribution does not authorize alphabetic reordering. Mark Hanwool as corresponding author using the venue's actual author/contact field and an author-supplied email.

The observed workshop form had no dedicated equal-first or corresponding-author role fields. The order and profile list were entered; these role annotations are retained here for camera-ready and SAC metadata. They were not inserted into the double-blind PDF. The old two-author LaTeX template is not the author roster. Do not expose this handoff or author YAML inside an anonymous source bundle.

## Workshop receipt and SAC distinction

- Workshop: **submitted #11**, [OpenReview record](https://openreview.net/forum?noteId=klGll15Rn5), October 2, 2026. [Machine-readable receipt](../../../docs/submissions/icaif2026.json) records the PDF hash and source commit; use its latest revision when comparing manuscripts.
- Initial upload was the October 1 workshop snapshot `8d73e63`, six PDF pages with four main-text pages. Full abstract and downloaded PDF hash matched. Subsequent gloss-only updates are recorded in the receipt/history.
- Paper license is **CC BY 4.0**, explicitly approved by the operator. Dataset license remains **CC BY-NC 4.0**. Neither changes the other.
- The operator explicitly approved sharing author emails with Program Chairs and public release of the accepted submission and author names. This was required by the actual OpenReview form, despite the workshop homepage saying papers would not be made public. Do not assert nonpublication is guaranteed.
- The operator confirmed on October 2 that an **existing EasyChair account used for the NMIXX submission is available**. Reuse that account for SAC; no new account is needed. Login email and credentials are not recorded here, and a currently authenticated session has not been verified by this handoff.
- SAC is **not submitted**. Create a distinct Kiii² AIFT submission, never reuse NMIXX #185 or workshop #11 as a SAC identifier. The operator reports Prof. Yongjae Lee allowed workshop/SAC parallel submission (ADR-0039); disclose the actual workshop status accurately if asked.
- This handoff is not evidence that every coauthor has separately approved final SAC wording, attendance, conflicts, or any new license/fee terms. Complete the actual form with operator-provided facts.

## Selective wording port

The workshop revision adds English glosses for Korean numeral examples in the introduction and construction section, translates the statutory name/address/phone phrase, and explains the Korean labels/digit words in Figure 1's caption. It changes no results, taxonomy, data, or protocol. The verified outbound workshop commit is `2d7f6cff46c5891586ff7546ceeb88935a9451d9` (OpenReview #11 PDF updated and downloaded hash verified). Inspect that commit/diff and the receipt; port these small wording changes selectively into SAC's corresponding prose/figure caption. SAC's independent figure design and eight-page limit remain in force. Do not replace Sara's live workshop sources or copy workshop files wholesale into SAC.
