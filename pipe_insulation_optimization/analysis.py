"""Analyze pipe insulation options against 8760 hourly CZ03 weather/load data.

The equations exported from external result files vary by project, so this module
keeps equations in a JSON configuration file. Equations are evaluated for every
hour against the CZ03 columns plus candidate insulation thickness values and
fixed/static values.
"""

from __future__ import annotations

import argparse
import ast
import csv
import itertools
import json
import math
import operator
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping

_ALLOWED_BINARY_OPERATORS: Mapping[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY_OPERATORS: Mapping[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_ALLOWED_FUNCTIONS: Mapping[str, Any] = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "ceil": math.ceil,
    "cos": math.cos,
    "exp": math.exp,
    "floor": math.floor,
    "log": math.log,
    "log10": math.log10,
    "max": max,
    "maximum": max,
    "min": min,
    "minimum": min,
    "round": round,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}
_ALLOWED_CONSTANTS: Mapping[str, float] = {"e": math.e, "pi": math.pi}


@dataclass(frozen=True)
class AnalysisConfig:
    """Configuration required to evaluate equations and search candidates."""

    column_map: Mapping[str, str]
    power_equation: str
    capacity_equation: str
    candidate_values: Mapping[str, list[float]]
    static_values: Mapping[str, float]
    static_value_units: Mapping[str, str]
    load_column: str
    load_scale: float
    capacity_margin: float
    objective: str
    output_prefix: str

    @classmethod
    def from_path(cls, path: str | Path) -> "AnalysisConfig":
        """Load an analysis configuration from JSON."""

        with Path(path).open(encoding="utf-8") as file:
            raw = json.load(file)

        required = ["column_map", "equations", "candidates", "load"]
        missing = [key for key in required if key not in raw]
        if missing:
            raise ValueError(f"Configuration is missing required keys: {missing}")

        equations = raw["equations"]
        if "power" not in equations or "capacity" not in equations:
            raise ValueError("Configuration 'equations' must include 'power' and 'capacity'.")

        load = raw["load"]
        return cls(
            column_map=raw["column_map"],
            power_equation=equations["power"],
            capacity_equation=equations["capacity"],
            candidate_values=raw["candidates"],
            static_values=raw.get("static_values", {}),
            static_value_units=raw.get("static_value_units", {}),
            load_column=load.get("column", "L"),
            load_scale=float(load.get("scale", 1.0)),
            capacity_margin=float(load.get("capacity_margin", 0.0)),
            objective=raw.get("objective", "annual_power"),
            output_prefix=raw.get("output_prefix", "cz03_insulation_analysis"),
        )


@dataclass(frozen=True)
class OptimizationResult:
    """Best candidate and detailed search outputs."""

    best_candidate: dict[str, Any] | None
    candidate_summary: list[dict[str, Any]]
    hourly_results: list[dict[str, Any]]


def _evaluate_node(node: ast.AST, variables: Mapping[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body, variables)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant in equation: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in variables:
            return float(variables[node.id])
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]
        raise ValueError(f"Unknown equation variable: {node.id}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY_OPERATORS:
        return _ALLOWED_BINARY_OPERATORS[type(node.op)](
            _evaluate_node(node.left, variables), _evaluate_node(node.right, variables)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPERATORS:
        return _ALLOWED_UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand, variables))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function_name = node.func.id
        if function_name not in _ALLOWED_FUNCTIONS:
            raise ValueError(f"Unsupported equation function: {function_name}")
        args = [_evaluate_node(arg, variables) for arg in node.args]
        kwargs = {kw.arg: _evaluate_node(kw.value, variables) for kw in node.keywords}
        return float(_ALLOWED_FUNCTIONS[function_name](*args, **kwargs))
    raise ValueError(f"Unsupported equation syntax: {ast.dump(node)}")


def compile_equation(equation: str) -> ast.Expression:
    """Parse an equation once so it can be evaluated efficiently per hour."""

    return ast.parse(equation, mode="eval")


def evaluate_equation(equation: str, variables: Mapping[str, float]) -> float:
    """Safely evaluate an algebraic equation against scalar variables."""

    return _evaluate_node(compile_equation(equation), variables)


def _read_hourly_data(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CZ03 hourly data file not found: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 8760:
        raise ValueError(f"Expected 8760 hourly records, found {len(rows)} in {csv_path}.")
    return rows


def _build_hour_variables(row: Mapping[str, str], config: AnalysisConfig) -> dict[str, float]:
    variables: dict[str, float] = {}
    for equation_name, source_column in config.column_map.items():
        if source_column not in row:
            raise ValueError(
                f"Column map for '{equation_name}' references missing CZ03 column '{source_column}'."
            )
        variables[equation_name] = float(row[source_column])
    variables.update({name: float(value) for name, value in config.static_values.items()})
    return variables


def _candidate_grid(candidate_values: Mapping[str, list[float]]) -> Iterable[dict[str, float]]:
    names = list(candidate_values)
    if not names:
        yield {}
        return
    for values in itertools.product(*(candidate_values[name] for name in names)):
        yield dict(zip(names, (float(value) for value in values), strict=True))


def _objective_value(power: list[float], objective: str) -> float:
    if objective == "annual_power":
        return float(sum(power))
    if objective == "average_power":
        return float(fmean(power))
    if objective == "peak_power":
        return float(max(power))
    raise ValueError("Objective must be one of: annual_power, average_power, peak_power.")


def run_analysis(cz03_path: str | Path, config: AnalysisConfig) -> OptimizationResult:
    """Run a grid-search insulation optimization over CZ03 hourly data."""

    hourly_data = _read_hourly_data(cz03_path)
    power_tree = compile_equation(config.power_equation)
    capacity_tree = compile_equation(config.capacity_equation)
    summary_records: list[dict[str, Any]] = []
    best_hourly: list[dict[str, Any]] = []
    best_objective = math.inf

    for candidate in _candidate_grid(config.candidate_values):
        power_values: list[float] = []
        capacity_values: list[float] = []
        required_capacity_values: list[float] = []
        unmet_load_values: list[float] = []

        for row in hourly_data:
            variables = _build_hour_variables(row, config)
            variables.update(candidate)
            if config.load_column not in variables:
                raise ValueError(
                    f"Load variable '{config.load_column}' is not available. "
                    "Add it to column_map or static_values."
                )
            power = float(_evaluate_node(power_tree, variables))
            capacity = float(_evaluate_node(capacity_tree, variables))
            required_capacity = variables[config.load_column] * config.load_scale * (1.0 + config.capacity_margin)
            unmet_load = max(required_capacity - capacity, 0.0)
            power_values.append(power)
            capacity_values.append(capacity)
            required_capacity_values.append(required_capacity)
            unmet_load_values.append(unmet_load)

        feasible = all(unmet_load <= 1e-9 for unmet_load in unmet_load_values)
        objective_value = _objective_value(power_values, config.objective)
        record = {
            **candidate,
            "feasible": feasible,
            "objective": objective_value,
            "annual_power": float(sum(power_values)),
            "average_power": float(fmean(power_values)),
            "peak_power": float(max(power_values)),
            "minimum_capacity": float(min(capacity_values)),
            "peak_capacity": float(max(capacity_values)),
            "peak_required_capacity": float(max(required_capacity_values)),
            "unmet_load_hours": sum(unmet_load > 1e-9 for unmet_load in unmet_load_values),
            "maximum_unmet_load": float(max(unmet_load_values)),
        }
        summary_records.append(record)

        if feasible and objective_value < best_objective:
            best_objective = objective_value
            best_hourly = []
            for index, row in enumerate(hourly_data):
                best_hourly.append(
                    {
                        **row,
                        **candidate,
                        "required_capacity": required_capacity_values[index],
                        "calculated_power": power_values[index],
                        "calculated_capacity": capacity_values[index],
                        "unmet_load": unmet_load_values[index],
                    }
                )

    summary_records.sort(key=lambda record: (not record["feasible"], record["objective"]))
    best_candidate = summary_records[0] if summary_records and summary_records[0]["feasible"] else None
    return OptimizationResult(
        best_candidate=best_candidate,
        candidate_summary=summary_records,
        hourly_results=best_hourly,
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(result: OptimizationResult, output_dir: str | Path, output_prefix: str) -> None:
    """Write summary and best-hour hourly CSV files."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _write_csv(directory / f"{output_prefix}_candidate_summary.csv", result.candidate_summary)
    _write_csv(directory / f"{output_prefix}_best_hourly.csv", result.hourly_results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optimize pipe insulation using CZ03 8760 hourly data.")
    parser.add_argument("--cz03", required=True, help="Path to the CZ03 8760 hourly CSV file.")
    parser.add_argument("--config", required=True, help="Path to the JSON equation/configuration file.")
    parser.add_argument("--output-dir", default="analysis_outputs", help="Directory for output CSV files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AnalysisConfig.from_path(args.config)
    result = run_analysis(args.cz03, config)
    write_outputs(result, args.output_dir, config.output_prefix)

    if result.best_candidate is None:
        print("No feasible insulation candidate met the required load for all 8760 hours.")
        return 2

    print("Best feasible insulation candidate:")
    for key, value in result.best_candidate.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
