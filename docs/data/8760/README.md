# 8760 Data Documentation

Upload documentation for the 8760 hourly data here.

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

## CZ03 workbook inventory

The canonical source workbook currently tracked in this folder is
`docs/data/8760/CZ03.xlsx`. Its hourly source data is on the `CZ03` worksheet,
which contains one header row and 8760 hourly data rows. The workbook also has a
`Read Me` worksheet with compressor-speed lower-limit notes by ambient
temperature band.

When using this workbook with the analysis code, export the `CZ03` worksheet to
CSV and preserve the canonical source column names below unless the analysis
configuration explicitly maps renamed columns.

## Canonical CZ03 data dictionary

Use this table as the canonical mapping between CZ03 source columns, regression
workbook variables, and analysis configuration variables.

| CZ03 source column / source | Regression variable | Analysis config variable | Unit | Expected range / domain | Notes |
| --- | --- | --- | --- | --- | --- |
| `Environment:Site Outdoor Air Drybulb Temperature [F](Hourly)` | `DB` | `TDB` | degrees Fahrenheit (°F) | 9.365 to 98.06 observed in `CZ03.xlsx`; future files should remain within plausible CZ03 outdoor dry-bulb conditions. | Hourly outdoor dry-bulb temperature. |
| `Environment:Site Outdoor Air Wetbulb Temperature [F](Hourly)` | `WB` | `TWB` | degrees Fahrenheit (°F) | 7.43354848427929 to 76.6147413785666 observed in `CZ03.xlsx`; normally less than or equal to dry-bulb temperature for the same hour. | Hourly outdoor wet-bulb temperature. |
| `Outdoor Line Length` or configuration `static_values.OIL` | `O` | `OIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Outdoor line length. The tracked workbook has the header, but current hourly cells are blank, so provide a populated CSV column or a static config value. |
| `Indoor Line Length` or configuration `static_values.IIL` | `I` | `IIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Indoor line length. The tracked workbook has the header, but current hourly cells are blank, so provide a populated CSV column or a static config value. |
| Outdoor insulation-thickness candidate; source workbook result prefixes `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00` | `To` | `OIT` | inches (in.) | Candidate value within the regression-calibrated domain; the tracked workbook result families cover 0 to 1.00 in. | Outdoor insulation thickness is a candidate/configuration input, not an hourly weather column. |
| `Indoor Insulation Thickness`, candidate list, or configuration `static_values.IIT` | `Ti` | `IIT` | inches (in.) | Greater than or equal to 0 in. and within the regression-calibrated domain. | Indoor insulation thickness. The tracked workbook has the header, but current hourly cells are blank, so provide candidate/static values or a populated CSV column. |
| `Total Heating Load` | `L` | `L` | Load rate in the same capacity basis used by the regression, typically W for EnergyPlus-style hourly rates unless converted elsewhere. | 0 to 143332.52095513802 observed in `CZ03.xlsx`; must be non-negative. | Hourly required heating load. The optimizer compares calculated capacity against `L * load.scale * (1 + load.capacity_margin)`. |

## Additional CZ03 columns and units

| CZ03 source column or family | Unit | Expected range / domain | Notes |
| --- | --- | --- | --- |
| `Month` | Calendar month number | 1 to 12 | Calendar month for each hourly record. |
| `Day` | Calendar day number | 1 to 31 | Calendar day within month. |
| ` Hour` | Hour ending, local standard time | 1 to 24 | The source header includes a leading space. Preserve it or map it explicitly if used. |
| `<thickness> Capacity` | Capacity rate in the same basis as `Total Heating Load`, typically W unless converted elsewhere. | Greater than or equal to 0 | Workbook result/validation family for prefixes `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00`; not required as an optimizer input. |
| `<thickness> Power` | Electric power, typically W unless converted elsewhere. | Greater than or equal to 0 | Workbook result/validation family for prefixes `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00`; keep separate from hourly energy. |
| `<thickness> Run Time` | Runtime fraction or duration as defined by the source workbook. | 0 to 1 for fractions, or greater than or equal to 0 for durations. | Confirm the source convention before calculation use. |
| `<thickness> Energy` | Energy over the hourly reporting interval, typically Wh when power is W. | Greater than or equal to 0 | Derived or reported hourly energy associated with each thickness family. |
| `0 Speed` | Compressor speed or normalized speed | Greater than or equal to 0 | Supporting source output; not a canonical optimizer input. |

## Analysis configuration notes

A project configuration should map hourly analysis variables to CZ03 columns and
provide non-hourly variables through `candidates` or `static_values`. For an
export of the tracked workbook, the hourly `column_map` should use:

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
remain blank in the exported CSV, do not map those blank columns as hourly
inputs. Provide the applicable numeric values through `static_values` and/or
`candidates` instead.

## QA/QC checks

Before running an optimization, confirm that:

- The exported CSV contains exactly 8760 data rows after the header row.
- Temperature fields are numeric °F values, and wet-bulb temperature is not above
  dry-bulb temperature for normal hourly records.
- `Total Heating Load` is numeric and non-negative.
- Line lengths are numeric and non-negative when supplied as columns or static
  values.
- Insulation thickness candidates are numeric, non-negative, and within the
  regression-calibrated domain.
- Power, capacity, load, and energy units are not mixed; document any conversion
  in the project configuration and equation backup notes.
