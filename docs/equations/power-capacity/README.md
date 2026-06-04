# Power and Capacity Equation Data Dictionary

This folder documents how the power and capacity regression variables map to the
CZ03 hourly workbook and to the analysis configuration used by the optimizer.
Store equation derivations, coefficient tables, source result files, and
validation records here whenever equations are updated.

## Canonical regression-to-configuration mapping

The regression workbook uses concise variable names. The analysis configuration
uses more descriptive identifiers. These mappings are canonical for power and
capacity equations:

| Regression variable | Analysis config variable | Source CZ03 workbook column / source | Unit | Expected range / domain | Equation role |
| --- | --- | --- | --- | --- | --- |
| `DB` | `TDB` | `Environment:Site Outdoor Air Drybulb Temperature [F](Hourly)` | degrees Fahrenheit (°F) | 9.365 to 98.06 observed in `docs/data/8760/CZ03.xlsx`; use the regression-calibrated outdoor-air range for other climate files. | Independent variable for outdoor dry-bulb temperature. |
| `WB` | `TWB` | `Environment:Site Outdoor Air Wetbulb Temperature [F](Hourly)` | degrees Fahrenheit (°F) | 7.43354848427929 to 76.6147413785666 observed in `docs/data/8760/CZ03.xlsx`; normally less than or equal to `DB` for the same hour. | Independent variable for outdoor wet-bulb temperature. |
| `O` | `OIL` | `Outdoor Line Length` or configuration `static_values.OIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Outdoor line-length term. |
| `I` | `IIL` | `Indoor Line Length` or configuration `static_values.IIL` | feet (ft) | Greater than or equal to 0 ft; project-specific design value. | Indoor line-length term. |
| `To` | `OIT` | Outdoor insulation-thickness candidate; workbook result-column prefixes `0`, `0.25`, `0.375`, `0.50`, `0.75`, and `1.00` document the calibrated source cases | inches (in.) | Candidate value within the calibrated domain, commonly 0 to 1.00 in. for the tracked workbook families. | Outdoor insulation-thickness term. |
| `Ti` | `IIT` | `Indoor Insulation Thickness`, candidate list, or configuration `static_values.IIT` | inches (in.) | Candidate or fixed value greater than or equal to 0 in. and within the calibrated domain. | Indoor insulation-thickness term. |
| `L` | `L` | `Total Heating Load` | load rate in the same basis as capacity, typically W unless the regression workbook has been converted to IP units | 0 to 143332.52095513802 observed in `docs/data/8760/CZ03.xlsx`; non-negative. | Hourly load requirement used for feasibility checks and any load-dependent regression terms. |

## Units used by equation inputs and outputs

| Quantity | Canonical unit | Notes |
| --- | --- | --- |
| Temperature (`DB`, `WB`, `TDB`, `TWB`) | degrees Fahrenheit (°F) | Keep equation coefficients aligned to °F inputs. Convert source data before evaluation if coefficients are ever refit in °C. |
| Line length (`O`, `I`, `OIL`, `IIL`) | feet (ft) | Outdoor and indoor line lengths must use the same length unit assumed during regression fitting. |
| Insulation thickness (`To`, `Ti`, `OIT`, `IIT`) | inches (in.) | Candidate values should stay inside the fitted thickness domain unless the equation owner explicitly approves extrapolation. |
| Load (`L`) | same rate basis as capacity, typically W | `load.scale` may convert this value before feasibility checks. Document any conversion from W, Btu/h, tons, or percent load in the project configuration. |
| Power (`P`, calculated power, `<thickness> Power`) | electric power, typically W | Annual objectives sum hourly power values as configured by the analysis; convert to energy units explicitly when reporting energy. |
| Capacity (`C`, calculated capacity, `<thickness> Capacity`) | same rate basis as load, typically W | Feasibility requires calculated capacity to meet or exceed scaled required load for every hourly record. |

## Equation implementation guidance

- Regression equations in analysis configuration must use the analysis config
  variable names (`TDB`, `TWB`, `OIT`, `IIT`, `OIL`, `IIL`, and `L`), not the
  concise regression workbook names.
- When copying an equation from a regression workbook, translate variables with
  the canonical mapping table above before adding it to configuration.
- Keep power and capacity equations dimensionally consistent with the listed
  units. Do not mix W, Btu/h, tons, or percent load without documenting the
  conversion in `load.scale`, `static_values`, or the equation notes.
- If a CZ03 export leaves line length or thickness columns blank, supply those
  values as candidates or static configuration values so every equation variable
  is numeric at evaluation time.
- Treat candidate values outside the calibrated source-domain as extrapolation;
  record the rationale and validation evidence in this folder.

## Validation checklist

For each equation or coefficient update, store backup materials in this folder
that demonstrate:

- The source workbook, worksheet, coefficient table, and date/version used.
- The translated equation using analysis config variable names.
- Units for every input and output term.
- Minimum and maximum values used during fitting or validation.
- A comparison of configured equation results against source workbook power and
  capacity outputs for representative hours and insulation thickness cases.
- Any scaling applied to load, power, capacity, or energy before optimization.
