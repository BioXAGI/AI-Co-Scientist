# MOCK RESEARCH CONTEXT — ALL NUMBERS ARE SYNTHETIC

This example demonstrates input structure only. Gene symbols are real, but the cohort, models, effect estimates and findings in the accompanying CSV are fabricated and must never be interpreted as published or observed results.

## Research question
Prioritize candidate prognostic biomarkers and explore potential intervention targets for colorectal cancer. Generate testable hypotheses, distinguish target hypotheses from prognostic associations, and describe evidence required for each.

## Mock study cohort
Hypothetical discovery cohort: 300 patients with primary colorectal cancer and bulk tumor RNA sequencing. Hypothetical endpoint: overall survival from diagnosis. No external validation cohort has yet been specified. This mock cohort is not the single-cell dataset analyzed elsewhere in this conversation.

## Mock statistical model definitions
Each row is one gene. All hazard ratios compare high versus low tumor expression using an illustrative pre-specified threshold; values above 1 indicate greater hazard in the high-expression group for this hypothetical endpoint. `cox_univ_*` columns describe a univariable Cox proportional-hazards model. `cox_adjusted_*` columns describe a multivariable model adjusted for age, stage and sex. Columns ending in `_ci_lower` and `_ci_upper` are 95% confidence interval bounds. `cox_adjusted_fdr` is the Benjamini–Hochberg adjusted p-value over the full hypothetical tested gene set. Example values are synthetic, not recomputed from patient data.

## Prioritization and limitations
Report each model separately and do not select target candidates solely from hazard ratio or p-value. Consider expression in normal tissue, tumor cell location, protein evidence, surface accessibility, biological mechanism, assay and model assumptions, confounding, sample size, missingness, multiple-testing and independent cohort validation. No gene is assumed to be causal or treatment-predictive. Missing or ambiguous metadata must be highlighted rather than invented.

## Requested output
For each candidate, report gene symbol, source CSV row, relevant hazard ratio, confidence interval and p-value with model and comparator; distinguish observed mock data, background evidence, and speculative hypotheses. Separate proposed prognostic biomarkers from treatment-response biomarkers and intervention targets. State what experiments and independent evidence are required. Verify any literature citations externally.
