# CZ03 8760 Hourly Data Dictionary

This folder documents the hourly input workbook used by the pipe insulation
optimization analysis. The canonical source file currently tracked here is
`CZ03.xlsx`, with its hourly records on the `CZ03` worksheet.

## Source workbook inventory

| File | Worksheet | Records | Notes |
| --- | --- | ---: | --- |
| `docs/data/8760/CZ03.xlsx` | `CZ03` | 8760 hourly rows plus one header row | Canonical hourly weather/load source. |
| `docs/data/8760/CZ03.xlsx` | `Read Me` | Reference notes | Includes compressor-speed lower-limit notes by ambient temperature band. |

The analysis code consumes CSV files at runtime, so `CZ03.xlsx` should be
exported to CSV without changing the canonical column names listed below. The
CSV is expected to contain exactly 8760 hourly records.

## Canonical variable mapping

Use this table when translating between the CZ03 workbook, regression workbook
variables, and analysis configuration variables.

| CZ03 workbook column name | Regression variable | Analysis config variable | Unit | Expected range / domain | Notes |
| --- | --- | --- | --- | --- | --- |
| `Environment:Site Outdoor Air Drybulb Temperature [F](Hourly)` | `DB` | `TDB` | degrees Fahrenheit (°F) | 9.365 to 98.06 observed in `CZ03.xlsx`; validate future CZ03 files as plausible CZ03 outdoor-air dry-bulb temperatures. | Hourly outdoor dry-bulb temperature. |
| `Environment:Site Outdoor Air Wetbulb Temperature [F](Hourly)` | `WB` | `TWB` | degrees Fahrenheit (°F) | 7.43354848427929 to 76.6147413785666 observed in `CZ03.xlsx`; should not exceed dry-bulb temperature for the same hour under normal psychrometric conditions. | Hourly outdoor wet-bulb temperature. |
| `Outdoor Line Length` | `O` | `OIL` | feet (ft) | Greater than or equal to 0 ft; project-specific fixed value or hourly/source value when populated. | Outdoor refrigerant or piping line length used by the regression equation. The tracked workbook header is present, but the current rows are blank, so supply this through the analysis configuration `static_values` or a populated CSV column. |
| `Indoor Line Length` | `I` | `IIL` | feet (ft) | Greater than or equal to 0 ft; project-specific fixed value or hourly/source value when populated. | Indoor refrigerant or piping line length used by the regression equation. The tracked workbook header is present, but the current rows are blank, so supply this through `static_values` or a populated CSV column. |
| `0 Capacity`, `0.25 Capacity`, `0.375 Capacity`, `0.50 Capacity`, `0.75 Capacity`, `1.00 Capacity` | `To` | `OIT` | inches (in.) of insulation thickness | One of 0, 0.25, 0.375, 0.50, 0.75, or 1.00 in. when using the workbook capacity/power result families; candidate values should remain within the regression-calibrated thickness domain. | Outdoor insulation thickness. In the regression/configuration layer this is a candidate input, not an hourly weather column. The workbook encodes thickness-specific output families in the result-column prefixes. |
| `Indoor Insulation Thickness` | `Ti` | `IIT` | inches (in.) of insulation thickness | Greater than or equal to 0 in.; project-specific fixed value or candidate values within the regression-calibrated domain. | Indoor insulation thickness. The tracked workbook header is present, but the current rows are blank, so supply this through candidate values or a populated CSV column. |
| `Total Heating Load` | `L` | `L` | load rate in the same capacity basis used by the regression, typically W for EnergyPlus-style hourly rates unless the regression workbook has been converted to IP units | 0 to 143332.52095513802 observed in `CZ03.xlsx`; must be greater than or equal to 0. | Hourly required heating load. The optimizer compares calculated capacity against `L * load.scale * (1 + load.capacity_margin)`. |

## Additional CZ03 time columns

| CZ03 workbook column name | Unit | Expected range / domain | Notes |
| --- | --- | --- | --- |
| `Month` | calendar month number | 1 to 12 | Calendar month for each hourly record. |
| `Day` | calendar day number | 1 to 31 | Calendar day within month. |
| ` Hour` | hour ending, local standard time | 1 to 24 | The source header includes a leading space. Preserve or explicitly map it when exporting to CSV. |

## Result columns and units

The workbook also contains output/result families by insulation-thickness prefix:

| CZ03 workbook column family | Unit | Expected range / domain | Notes |
| --- | --- | --- | --- |
| `<thickness> Capacity` | capacity rate in the same load basis as `Total Heating Load`, typically W unless converted by the regression workbook | Greater than or equal to 0 | Available prefixes are `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00`. These columns are source regression outputs or validation targets, not required hourly inputs to the optimizer unless used for QA. |
| `<thickness> Power` | electric power, typically W unless converted by the regression workbook | Greater than or equal to 0 | Available prefixes are `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00`. Keep this unit separate from annual energy totals. |
| `<thickness> Run Time` | runtime fraction or runtime duration as defined by the source workbook | 0 to 1 for fractions, or greater than or equal to 0 for durations | Confirm the source workbook convention before using these columns in calculations. |
| `<thickness> Energy` | energy over the hourly reporting interval, typically Wh when power is W | Greater than or equal to 0 | Derived or reported hourly energy associated with each thickness family. |
| `0 Speed` | compressor speed or normalized speed | Greater than or equal to 0 | Supporting source output; not a canonical optimizer input. |

## Analysis configuration example

A project configuration should map the canonical analysis variables to CZ03
columns or provide static/candidate values. For the tracked workbook export, the
hourly portion of `column_map` should use the canonical source columns:

```json
{
  "column_map": {
    "TDB": "Environment:Site Outdoor Air Drybulb Temperature [F](Hourly)",
    "TWB": "Environment:Site Outdoor Air Wetbulb Temperature [F](Hourly)",
    "L": "Total Heating Load",
    "OIL": "Outdoor Line Length",
    "IIL": "Indoor Line Length"
  },
  "candidates": {
    "OIT": [0, 0.25, 0.375, 0.5, 0.75, 1.0],
    "IIT": [0, 0.25, 0.375, 0.5, 0.75, 1.0]
  }
}
```

If `Outdoor Line Length`, `Indoor Line Length`, or `Indoor Insulation Thickness`
remain blank in an exported CZ03 CSV, do not map them as hourly columns. Instead,
provide the applicable values through configuration `static_values` and/or
`candidates` so every regression variable has a numeric value at evaluation time.

## QA/QC checks

Before running an optimization, confirm that the exported CZ03 CSV satisfies the
following checks:

- Exactly 8760 data rows are present after the header row.
- Temperature fields are numeric °F values and wet-bulb temperature is not above
  dry-bulb temperature for normal hourly records.
- `Total Heating Load` is numeric and non-negative.
- Line lengths are numeric and non-negative when supplied as columns.
- Insulation thickness candidates are numeric, non-negative, and within the
  regression-calibrated domain.
- Power, capacity, load, and energy units are not mixed; any conversion is
  documented in the project configuration and equation backup notes.
