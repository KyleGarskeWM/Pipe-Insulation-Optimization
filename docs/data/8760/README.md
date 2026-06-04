# 8760 Data Documentation

Upload documentation for the 8760 hourly data here.

## CZ03 role in the regression workflow

`docs/data/8760/CZ03.xlsx` is an **application input dataset** for applying the
already-derived power and capacity regressions. It is **not** a source dataset
for training new regressions in this repository.

Use workbook `docs/data/8760/CZ03.xlsx`, sheet `CZ03`, as the 8760 hourly data
source for weather, load, and pipe-insulation context fields. The currently
committed workbook contains hourly input columns such as outdoor/indoor line
length, indoor insulation thickness, dry-bulb temperature, wet-bulb temperature,
and total heating load.

The columns in sheet `CZ03` from `0 Capacity` through `1.00 Energy` are empty
output/result placeholders for speed-bin calculations. They are **not required**
when applying the existing regressions, and they **must not be used as regression
target columns** for the current analysis workflow.

The existing regression outputs to apply are stored separately in:

- `docs/equations/power-capacity/power_regression_results.xlsx`
- `docs/equations/power-capacity/capacity_regression_results.xlsx`

Those regression-results workbooks are the traceable sources for the configured
power and capacity equations. Do not infer new power/capacity training targets
from the empty CZ03 output columns unless the project scope explicitly changes to
build new regressions and the target columns are populated with validated source
results.

If a future project scope changes from applying existing regressions to training
new regressions, first replace the empty CZ03 output placeholders with validated
observed or model-source target values. For each training row, define which
speed/bin column is the target, for example one of `0 Capacity`, `0.25 Capacity`,
`0.375 Capacity`, `0.50 Capacity`, `0.75 Capacity`, or `1.00 Capacity` for a
capacity regression, and the matching `0 Power`, `0.25 Power`, `0.375 Power`,
`0.50 Power`, `0.75 Power`, or `1.00 Power` column for a power regression.
Rows without a populated and explicitly selected target speed/bin must be
excluded from any future training dataset.

## Recommended supporting materials

Recommended materials include:

- Data source and version/date received.
- Data dictionary or column definitions for the hourly file.
- Units for each hourly field used by the analysis.
- Notes on any preprocessing, normalization, or filtering applied before use.
- QA/QC checks confirming the file contains exactly 8760 hourly records.
- Known limitations, assumptions, or gaps in the data.
- Change log for revised 8760 documentation.

The analysis expects the actual 8760 CSV path to be supplied at runtime; this
folder is intended for supporting documentation rather than generated outputs.
