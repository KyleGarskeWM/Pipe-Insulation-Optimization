# Power and Capacity Equation Backup Documentation

Upload backup documentation for the data supporting the power and capacity
equations here.

Recommended materials include:

- Original results files or references used to define the power equation.
- Original results files or references used to define the capacity equation.
- Equation derivation notes, coefficient tables, and variable definitions.
- Units and valid ranges for each equation input.
- Assumptions used when translating source equations into the analysis
  configuration.
- Validation records comparing configured equations against source results.
- Change log for equation or coefficient updates.

## Relationship to CZ03 application data

The workbooks `power_regression_results.xlsx` and
`capacity_regression_results.xlsx` are the existing regression-output references
for power and capacity. They are separate from `docs/data/8760/CZ03.xlsx`, which
is used as the 8760 input dataset for applying those regressions.

Do not use empty output placeholders in `docs/data/8760/CZ03.xlsx`, sheet
`CZ03`, from `0 Capacity` through `1.00 Energy` as training targets for the
current workflow. Those CZ03 columns are not needed when applying the existing
regressions documented here.

When equations are updated in `examples/cz03_analysis_config.example.json` or a
project-specific configuration, store the supporting backup documentation here
so the source and rationale remain traceable.
