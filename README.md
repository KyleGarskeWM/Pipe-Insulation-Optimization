# Pipe Insulation Optimization

This repository contains a Python workflow for evaluating pipe insulation
thickness options against CZ03 8760 hourly data.  The analysis computes hourly
power and capacity for each candidate insulation option, filters candidates that
fail to meet the load requirement, and selects the feasible option with the
lowest power objective.

## Required input files

1. **CZ03 hourly CSV** with exactly 8760 rows.
2. **Analysis configuration JSON** containing:
   - `column_map`: maps equation variable names to CZ03 CSV column names.
   - `equations.power`: power equation from the results file.
   - `equations.capacity`: capacity equation from the results file.
   - `candidates`: insulation thickness values to test, typically `OIT` and
     `IIT`.
   - `static_values`: constants that are not hourly CZ03 columns.
   - `load`: load variable, scaling, and optional capacity safety margin.

An editable starter configuration is available at
`examples/cz03_analysis_config.example.json`. Replace the example equations with
the equations from the results files before making engineering decisions.

Supporting documentation can be uploaded under `docs/`: use
`docs/data/8760/` for 8760 hourly data documentation and
`docs/equations/power-capacity/` for backup documentation related to the data,
derivations, assumptions, and validation records for the power and capacity
equations.

## Equation variables

The configuration is designed around these variables:

- `P`: calculated power output; represented by `equations.power`.
- `TDB`: dry-bulb temperature from CZ03.
- `TWB`: wet-bulb temperature from CZ03.
- `OIT`: outdoor insulation thickness candidate.
- `IIT`: indoor insulation thickness candidate.
- `OIL`: outdoor insulation length from CZ03 or `static_values`.
- `IIL`: indoor insulation length from CZ03 or `static_values`.
- `L`: load percentage or load requirement from CZ03.

Equations may use arithmetic operators and these functions: `abs`, `acos`,
`asin`, `atan`, `ceil`, `cos`, `exp`, `floor`, `log`, `log10`, `max`,
`maximum`, `min`, `minimum`, `round`, `sin`, `sqrt`, and `tan`.

## Running the analysis

Install dependencies and run:

```bash
python scripts/analyze_cz03.py \
  --cz03 path/to/CZ03_8760.csv \
  --config examples/cz03_analysis_config.example.json \
  --output-dir analysis_outputs
```

The command writes:

- `analysis_outputs/cz03_insulation_analysis_candidate_summary.csv`: one row per
  candidate thickness combination.
- `analysis_outputs/cz03_insulation_analysis_best_hourly.csv`: hourly power,
  capacity, and unmet-load values for the selected feasible candidate.

## Optimization method

The script performs a grid search over the configured insulation candidates. A
candidate is feasible only when calculated capacity is greater than or equal to
`L * load.scale * (1 + load.capacity_margin)` for all 8760 hours. Among feasible
candidates, the selected option minimizes `objective`, which can be
`annual_power`, `average_power`, or `peak_power`.
