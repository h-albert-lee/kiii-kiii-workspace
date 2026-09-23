# ADR-0028: Record practitioner appropriateness review separately from annotation validation

- Date: 2026-09-23
- Status: accepted; based on the user's report in this conversation

Five people with financial-sector employment experience each inspected a different 10% sample of the dataset. They judged the documents broadly similar to financial-sector documents and suitable as a dataset. The review concerned appropriateness only.

Report this as a qualitative practitioner assessment of document resemblance and suitability. Do not describe it as span/category validation, adjudication, inter-annotator agreement, a numerical acceptance rate, or proof that the entire corpus represents production traffic. The user clarified that reviewers saw different samples. Random selection, statistical independence and exact overlap have not been established. Sample IDs and selection method have not been supplied, so do not quantify unique review coverage as 50% without a deduplication record.

The paper may now describe this review, superseding the previous absence of a completed practitioner review. Keep the existing public dataset card unchanged in this update, consistent with the earlier request about its content. No data, annotations, release revision or evaluation split changes. Continue with the single evaluation set and no benchmark-trained baselines (ADR-0026).

Cite TWICE and NMIXX as relevant published work in third person, alongside Korean financial evaluation research. Do not claim their embedding/semantic evaluation tasks directly evaluate PII detection.
