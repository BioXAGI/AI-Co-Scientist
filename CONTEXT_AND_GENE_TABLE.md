# Research context and gene statistics

This local working copy is based on `BioXAGI/AI-Co-Scientist` at commit `f0cc32a0d8618fceca8394ac2d5b8fa6a70b5362`. It is inspired by Google's research paper and is not Google's official implementation. No changes are published.

The project accepts an optional common Markdown context and multiple gene statistics CSVs, each with its own table-specific Markdown context, via the Streamlit interface, the command line, or the Python API. Each CSV and description is kept together as a named dataset in the inputs passed to generation, ranking, refinement and reporting. The unchanged agents are language-model based and have placeholder parsing and literature-search components; generated citations, gene-row references, rankings, statistical interpretations and target claims must be checked manually. A hazard ratio alone does not establish a treatment-predictive marker or a causal, druggable target.

The context should describe cancer, cohort, sample size, assay, endpoints, analysis model, covariates, expression comparison, confidence intervals, multiple-testing adjustment, and validation needs. See `examples/research_context.md`. `examples/example_genes.csv` uses real gene symbols but entirely fictional statistical values for demonstration only.

For the simplest starting point, provide a gene list directly in Markdown: see `examples/simple_gene_context.md`. Its MMP9/GPC1 unfavorable and IL2/TNF favorable groups are illustrative user-provided assumptions, not validated findings. No CSV is required. Supply the outcome, cohort, comparison and evidence when available; the agents should flag these as missing rather than inventing them.

```
python -m src.main --context-md examples/simple_gene_context.md --validate-inputs
python -m src.main --goal "To evaluate candidate colorectal cancer biomarkers and targets" --context-md examples/simple_gene_context.md --output results
```

The second command invokes the model and requires installed project dependencies and configured model access.

CSV accepts UTF-8 with a header; the first column is the gene identifier by default, regardless of its header. Pass `--gene-column` to override it. Other columns are flexible and may describe different models and outcomes: for example, `cox_univ_hr`, `cox_univ_p_value`, `cox_adjusted_hr`, `cox_adjusted_p_value`, `cox_adjusted_fdr`, and confidence interval columns. Define each column, outcome, comparator, covariates, and adjustment in your Markdown context. All columns, data rows, and duplicate genes are preserved in their input order; each gets its source row number. Many common hazard-ratio and probability column patterns are checked for basic numeric plausibility; unfamiliar names are preserved but may not be automatically validated. Warnings do not repair or discard entries. The tool does not resolve gene aliases or reinterpret statistical models. Input files are limited to 1 MB each and 180,000 combined serialized prompt characters; exceeding a limit produces an explicit error rather than silently truncating rows. Consider data sensitivity and model token/cost limits before sending.

For multiple tables, specify `--table-csv` and `--table-context-md` once per pair, in matching order. Each table must have its own description, even if it shares a general project context. `--context-md` supplies optional common context. The first column of each table defaults to its gene identifier. For overrides, repeat `--table-gene-column` once per table, using `-` where the first column should be used. `source_row` is reserved for provenance; rename an input column with that exact name. Dataset identifiers (`table_1`, `table_2`, ...) and both filenames and hashes are recorded. Duplicate filenames remain distinct through their dataset IDs. Input content is serialized into the agent prompt; this does not guarantee that an LLM will obey the source boundaries or correctly interpret every table.

Example: two mock datasets, with distinct prognostic and treatment-interaction contexts:

```
python -m src.main --table-csv examples/example_genes.csv --table-context-md examples/research_context.md --table-csv examples/mock_treatment_results.csv --table-context-md examples/mock_treatment_context.md --validate-inputs
```

Remove `--validate-inputs` and add `--goal "To evaluate cancer biomarkers and treatment interactions" --output results` to run the agents with configured model access. A table/description count mismatch fails before the workflow starts. The existing single-table command below remains available.

Validate files locally, without sending them to a model:

```
python -m src.main --context-md examples/research_context.md --genes-csv examples/example_genes.csv --validate-inputs
```

Generate hypotheses (requires dependencies, model access, and an API key; this sends the complete input files to the configured model):

```
python -m src.main --goal "To evaluate candidate colorectal cancer prognostic biomarkers and potential targets" --context-md path/to/context.md --genes-csv path/to/genes.csv --gene-column gene --output results
```

Python API:

```
from src import AICoScientist
from src.research_inputs import load_paths
data = load_paths('context.md', 'genes.csv', gene_column='gene')
result = AICoScientist().run_full_workflow('To evaluate candidate cancer biomarkers', research_inputs=data)
```

Alternatively, run the original `run_ui.py` Streamlit interface and upload the files. Saved JSON reports record input file names, SHA-256 hashes, column mapping, row count and validation warnings; files themselves are not copied into the report. Agent logging may contain input material. Do not include identifiable patient-level information without appropriate handling. LLM responses are not guaranteed to cite or interpret data correctly, and the prior search tool is a placeholder rather than evidence retrieval.

Tests: `python -m unittest discover -s tests -v`. No external API is required for these tests. Install project dependencies from requirements.txt to run the actual agent workflow or UI. The default model in the original project may be obsolete or unavailable to your account; configure an available one.
