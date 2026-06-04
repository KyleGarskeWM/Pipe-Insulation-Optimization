# Regression Input Definitions

## Insulation thickness predictors

The regression result workbooks in this directory use predictor names `To` and
`Ti` on the `Predictions` sheets.

- `To` means **outdoor insulation thickness**.
- `Ti` means **indoor insulation thickness**.

Both predictors use inches. The candidate values present in the regression
result workbooks are `0`, `0.25`, `0.375`, `0.5`, `0.75`, and `1.0`, so the
analysis configuration records a valid range of `0.0` to `1.0` inches for each
thickness predictor.

## CZ03 hourly data fields

The CZ03 workbook at `docs/data/8760/CZ03.xlsx`, sheet `CZ03`, includes an
`Indoor Insulation Thickness` column header, but that field is not populated as
an hourly measurement in the committed data. The needed `Outdoor Insulation
Thickness` field is not present in the CZ03 sheet.

Because these thickness values are not hourly measurements, `To` and `Ti` are
kept as candidate grid variables in `examples/cz03_analysis_config.example.json`
instead of being added to `column_map` as CZ03 columns.
