# Mock treatment interaction table — synthetic example

All results and cohort details are invented for illustration. Gene symbols do not imply measured results. This table has a different population and model from the mock prognostic table.

## Study and model
Hypothetical cohort: 160 patients with colorectal cancer in two randomized treatment groups. Endpoint: progression-free survival. `interaction_hr` is the hazard ratio for the treatment-by-gene-expression interaction in a Cox model including treatment, high-versus-low gene expression and their interaction, with adjustment for age and stage. Values above 1 indicate a larger treatment-versus-control hazard ratio in the high-expression group compared with the low-expression group under this hypothetical coding. It is not the main-effect hazard ratio from the other table.

`interaction_p` tests that interaction. `interaction_fdr` is the hypothetical Benjamini–Hochberg adjusted p-value across all tested genes. `sample_size` is the total number of patients included for that gene. These synthetic data do not demonstrate that any candidate predicts treatment benefit. Describe both treatment groups and confidence intervals if known; missing information remains unknown.
