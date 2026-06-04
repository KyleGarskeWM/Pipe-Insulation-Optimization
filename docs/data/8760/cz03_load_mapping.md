# CZ03 Heating Load Mapping to Regression Variable `L`

This document records how the CZ03 heating-load field maps to the regression
predictor named `L` without changing the analysis code or the `column_map` JSON
schema.

## Source data

| Item | Value |
| --- | --- |
| Workbook | `docs/data/8760/CZ03.xlsx` |
| Sheet | `CZ03` |
| Source column | `Total Heating Load` |
| Source units | Btu/h of hourly heating load |
| Source row count | 8760 hourly records |
| Source range | 0 to 143,332.52095513802 Btu/h |

`Total Heating Load` is the hourly heating-load requirement. Values of `0` mean
there is no heating demand for that hour. The maximum observed hourly load in the
current CZ03 workbook, `143,332.52095513802` Btu/h, is the full-load reference
used to normalize the regression input.

## Regression variable `L`

The regression workbooks use `L` as a dimensionless load fraction, not as a raw
Btu/h heating-load value. Their prediction tables sample `L` from 0.25 through
1.00, where `1.00` represents full load.

Before analysis, create a derived hourly CSV column named `Normalized Heating
Load`:

```text
Normalized Heating Load = Total Heating Load / 143332.52095513802
```

Then map regression predictor `L` to that derived column.

Expected units and range for `L` in the current CZ03 data set:

- Units: dimensionless fraction of full heating load.
- Expected range: `0.0` to `1.0` after normalization.
- `L = 0.0`: no hourly heating load.
- `L = 1.0`: the CZ03 workbook peak hourly heating load of
  `143,332.52095513802` Btu/h.

Do not pass raw `Total Heating Load` Btu/h values directly into equations that
use regression predictor `L`; doing so would mix Btu/h with the regression's
fractional load variable.

## Analysis configuration mapping

`examples/cz03_analysis_config.example.json` uses two separate variables so the
regression equations and feasibility check each receive values in their expected
units:

| Config key | Value | Units after mapping | Purpose |
| --- | --- | --- | --- |
| `column_map.L` | `Normalized Heating Load` | dimensionless fraction | Regression predictor used by power/capacity equations. |
| `column_map.HeatingLoad` | `Total Heating Load` | Btu/h | Raw hourly load requirement. |
| `load.column` | `HeatingLoad` | Btu/h | Variable used for capacity feasibility checks. |
| `load.scale` | `1.0` | dimensionless multiplier | No additional scaling because `HeatingLoad` is already in Btu/h. |

With that configuration, the required-capacity calculation remains:

```text
required_capacity = HeatingLoad * 1.0 * (1 + load.capacity_margin)
```

This keeps regression predictor `L` normalized while comparing calculated
capacity against the original hourly `Total Heating Load` requirement in Btu/h.
