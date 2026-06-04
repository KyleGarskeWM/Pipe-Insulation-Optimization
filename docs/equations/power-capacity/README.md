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

When equations are updated in `examples/cz03_analysis_config.example.json` or a
project-specific configuration, store the supporting backup documentation here
so the source and rationale remain traceable.

## Canonical power/capacity variable mapping

The regression workbook uses concise variable names, while the analysis
configuration uses descriptive identifiers. Use this table as the canonical
translation when copying equations into configuration.

| Regression variable | Analysis config variable | CZ03 source column / source | Unit | Expected range / domain | Equation role |
| --- | --- | --- | --- | --- | --- |
| `DB` | `TDB` | `Environment:Site Outdoor Air Drybulb Temperature [F](Hourly)` | degrees Fahrenheit (°F) | 9.365 to 98.06 observed in `docs/data/8760/CZ03.xlsx`; use the regression-calibrated range for other files. | Outdoor dry-bulb temperature term. |
| `WB` | `TWB` | `Environment:Site Outdoor Air Wetbulb Temperature [F](Hourly)` | degrees Fahrenheit (°F) | 7.43354848427929 to 76.6147413785666 observed in `docs/data/8760/CZ03.xlsx`; normally less than or equal to `DB` for the same hour. | Outdoor wet-bulb temperature term. |
| `O` | `OIL` | `Outdoor Line Length` or configuration `static_values.OIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Outdoor line-length term. |
| `I` | `IIL` | `Indoor Line Length` or configuration `static_values.IIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Indoor line-length term. |
| `To` | `OIT` | Outdoor insulation-thickness candidate; source workbook result prefixes `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00` | inches (in.) | Candidate value within the calibrated domain; the tracked workbook result families cover 0 to 1.00 in. | Outdoor insulation-thickness term. |
| `Ti` | `IIT` | `Indoor Insulation Thickness`, candidate list, or configuration `static_values.IIT` | inches (in.) | Greater than or equal to 0 in. and within the calibrated domain. | Indoor insulation-thickness term. |
| `L` | `L` | `Total Heating Load` | Load rate in the same basis as capacity, typically W unless converted elsewhere. | 0 to 143332.52095513802 observed in `docs/data/8760/CZ03.xlsx`; non-negative. | Hourly load requirement and any load-dependent regression term. |

## Units for equation inputs and outputs

| Quantity | Canonical unit | Notes |
| --- | --- | --- |
| Temperature (`DB`, `WB`, `TDB`, `TWB`) | degrees Fahrenheit (°F) | Keep coefficients aligned with °F inputs unless equations are refit for °C. |
| Line length (`O`, `I`, `OIL`, `IIL`) | feet (ft) | Outdoor and indoor line lengths must use the units assumed during regression fitting. |
| Insulation thickness (`To`, `Ti`, `OIT`, `IIT`) | inches (in.) | Candidate values outside the fitted domain are extrapolations and need documented approval/validation. |
| Load (`L`) | Same rate basis as capacity, typically W | Use `load.scale` only when a documented conversion is required before feasibility checks. |
| Power (`P`, calculated power, `<thickness> Power`) | Electric power, typically W | Convert explicitly before reporting energy or annual totals in kWh. |
| Capacity (`C`, calculated capacity, `<thickness> Capacity`) | Same rate basis as load, typically W | Feasibility requires calculated capacity to meet or exceed scaled required load for every hour. |

## Equation implementation guidance

- Regression equations in analysis configuration must use analysis config
  variable names (`TDB`, `TWB`, `OIT`, `IIT`, `OIL`, `IIL`, and `L`), not the
  concise regression workbook names.
- Keep power and capacity equations dimensionally consistent with the documented
  units. Do not mix W, Btu/h, tons, or percent load without documenting the
  conversion in `load.scale`, `static_values`, or equation notes.
- If a CZ03 export leaves line length or thickness columns blank, supply those
  values as candidates or static configuration values so every equation variable
  is numeric at evaluation time.
- Store validation evidence for any equation update, including source workbook
  version, translated equation, coefficient table, fitted/validated min-max
  ranges, and comparisons against source power/capacity outputs.
