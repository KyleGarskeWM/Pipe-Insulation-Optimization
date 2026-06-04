import csv
import json

from pipe_insulation_optimization.analysis import AnalysisConfig, evaluate_equation, run_analysis


def test_evaluate_equation_supports_math_functions():
    values = {"TDB": 4.0, "OIT": 2.0}

    result = evaluate_equation("sqrt(TDB) + OIT", values)

    assert result == 4.0


def test_run_analysis_selects_lowest_power_feasible_candidate(tmp_path):
    cz03_path = tmp_path / "cz03.csv"
    with cz03_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "DB Temperature",
                "WB Temperature",
                "load %",
                "Outdoor Insulation Length",
                "Indoor Insulation Length",
            ],
        )
        writer.writeheader()
        for _ in range(8760):
            writer.writerow(
                {
                    "DB Temperature": 80.0,
                    "WB Temperature": 65.0,
                    "load %": 50.0,
                    "Outdoor Insulation Length": 10.0,
                    "Indoor Insulation Length": 5.0,
                }
            )

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "column_map": {
                    "TDB": "DB Temperature",
                    "TWB": "WB Temperature",
                    "L": "load %",
                    "OIL": "Outdoor Insulation Length",
                    "IIL": "Indoor Insulation Length",
                },
                "candidates": {"OIT": [0.5, 1.0], "IIT": [0.5, 1.0]},
                "load": {"column": "L", "scale": 1.0},
                "equations": {
                    "power": "100 - 10*OIT - 2*IIT + 0*TDB",
                    "capacity": "40 + 20*OIT + 10*IIT + 0*TWB",
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_analysis(cz03_path, AnalysisConfig.from_path(config_path))

    assert result.best_candidate is not None
    assert result.best_candidate["OIT"] == 1.0
    assert result.best_candidate["IIT"] == 1.0
    assert result.best_candidate["unmet_load_hours"] == 0
    assert len(result.hourly_results) == 8760
