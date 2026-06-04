# Documentation Upload Areas

Use this directory for project reference material that supports the CZ03 8760
analysis workflow.

## Folder structure

- `data/8760/`: documentation for the 8760 hourly input data, such as source
  notes, data dictionaries, column definitions, assumptions, QA/QC notes, and
  change history.
- `equations/power-capacity/`: backup documentation for the source data,
  derivation notes, coefficients, assumptions, and validation records for the
  power and capacity equations used by the analysis configuration.

Keep raw data files and generated analysis outputs out of this documentation
area unless they are intentionally small reference artifacts. Prefer committing
source documentation, metadata, and notes that make the analysis reproducible.
