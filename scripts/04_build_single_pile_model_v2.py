"""Build one PLAXIS 2D pile-stabilized slope scenario.

Default scenario is S05: D = 1.0 m and A2_double_aligned.
This is intentionally a single-scenario builder, not a batch runner.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sheykhzadeh.config_loader import load_and_validate_configs
from sheykhzadeh.geometry import slope_polygon_points
from sheykhzadeh.materials import create_soil_materials
from sheykhzadeh.plaxis_client import connect_input
from sheykhzadeh.scenario_generator import generate_scenarios


def _try(label: str, func, *args):
    try:
        value = func(*args)
        print(f"OK: {label}")
        return value
    except Exception as exc:
        print(f"WARN: {label} failed: {exc}")
        return None


def _surface_y_at_x(x: float, geometry_cfg: dict) -> float:
    slope = geometry_cfg["slope"]
    toe_x = float(slope["toe_x_m"])
    crest_x = float(slope["crest_x_m"])
    h = float(slope["height_m"])
    if x <= toe_x:
        return 0.0
    if x >= crest_x:
        return h
    return (x - toe_x) / (crest_x - toe_x) * h


def _new_model(g_i) -> None:
    _try("new model", g_i.new)
    if hasattr(g_i, "gotostructures"):
        _try("go to structures", g_i.gotostructures)


def _create_soil(g_i, geometry_cfg, material):
    points = slope_polygon_points(geometry_cfg)
    print("Creating slope polygon:")
    for point in points:
        print(f"  {point}")
    soil = g_i.polygon(*points)
    _assign_material(g_i, soil, material)
    return soil


def _assign_material(g_i, target, material) -> None:
    candidates = [target]
    if isinstance(target, (list, tuple)):
        candidates.extend(target)
    for item in candidates:
        try:
            g_i.setmaterial(item, material)
            print("OK: material assigned")
            return
        except Exception:
            pass
    print("WARN: material assignment was not confirmed")


def _create_embedded_beam_material(g_i, scenario: dict, pile_cfg: dict):
    diameter = float(scenario["diameter_m"])
    spacing = float(scenario["spacing_y_m"])
    e_kpa = float(pile_cfg["E_kPa"])
    gamma = float(pile_cfg["gamma_kN_m3"])
    name = f"pile_D{diameter:.2f}_S{spacing:.2f}"

    attempts = [
        (
            "embeddedbeammat full",
            (
                "Identification", name,
                "MaterialType", "Elastic",
                "E", e_kpa,
                "gamma", gamma,
                "Diameter", diameter,
                "LSpacing", spacing,
            ),
        ),
        (
            "embeddedbeammat basic",
            (
                "Identification", name,
                "E", e_kpa,
                "gamma", gamma,
                "Diameter", diameter,
            ),
        ),
    ]

    if not hasattr(g_i, "embeddedbeammat"):
        print("WARN: embeddedbeammat command not available in this PLAXIS object")
        return None

    for label, props in attempts:
        try:
            mat = g_i.embeddedbeammat(*props)
            print(f"OK: {label}")
            return mat
        except Exception as exc:
            print(f"WARN: {label} failed: {exc}")

    try:
        mat = g_i.embeddedbeammat()
        mat.Identification = name
        print("OK: empty embedded beam material created; set remaining properties manually if needed")
        return mat
    except Exception as exc:
        print(f"WARN: could not create embedded beam material: {exc}")
        return None


def _row_x_positions(scenario: dict, geometry_cfg: dict) -> list[float]:
    slope = geometry_cfg["slope"]
    toe_x = float(slope["toe_x_m"])
    crest_x = float(slope["crest_x_m"])
    center_x = (toe_x + crest_x) / 2.0
    rows = int(scenario["rows"])
    row_spacing = float(scenario["row_spacing_x_m"])
    if rows == 1:
        return [center_x]
    start = center_x - row_spacing * (rows - 1) / 2.0
    return [start + i * row_spacing for i in range(rows)]


def _create_pile_rows(g_i, scenario: dict, geometry_cfg: dict, pile_mat) -> list:
    slip_depth = float(geometry_cfg["slip_surface"]["estimated_depth_at_pile_m"])
    socket = float(scenario["socket_length_m"])
    pile_length = slip_depth + socket
    created = []

    for idx, x in enumerate(_row_x_positions(scenario, geometry_cfg), start=1):
        y_top = _surface_y_at_x(x, geometry_cfg)
        y_bottom = y_top - pile_length
        print(f"Creating pile row {idx}: x={x:.3f}, y_top={y_top:.3f}, y_bottom={y_bottom:.3f}")
        line = _try(f"pile row {idx} line", g_i.line, (x, y_top), (x, y_bottom))
        beam = None
        if line is not None and hasattr(g_i, "embeddedbeamrow"):
            beam = _try(f"pile row {idx} embeddedbeamrow", g_i.embeddedbeamrow, line)
        if beam is None and line is not None and hasattr(g_i, "embeddedbeam"):
            beam = _try(f"pile row {idx} embeddedbeam", g_i.embeddedbeam, line)
        target = beam or line
        if pile_mat is not None and target is not None:
            _assign_material(g_i, target, pile_mat)
        created.append(target)
    return created


def _mesh(g_i) -> None:
    if hasattr(g_i, "gotomesh"):
        _try("go to mesh", g_i.gotomesh)
    if hasattr(g_i, "mesh"):
        _try("generate mesh", g_i.mesh, 0.06)
    elif hasattr(g_i, "generatemesh"):
        _try("generate mesh", g_i.generatemesh)
    else:
        print("WARN: mesh command not found")


def _load_or_generate_scenarios(configs: dict) -> pd.DataFrame:
    scenario_csv = ROOT / "results" / "tables" / "scenario_matrix.csv"
    if scenario_csv.exists():
        return pd.read_csv(scenario_csv)
    return pd.DataFrame(generate_scenarios(configs))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="S05", help="Scenario ID, default S05")
    args = parser.parse_args()

    configs = load_and_validate_configs(ROOT)
    scenarios = _load_or_generate_scenarios(configs)
    selected = scenarios.loc[scenarios["scenario_id"] == args.scenario]
    if selected.empty:
        raise SystemExit(f"Scenario {args.scenario} was not found")
    scenario = selected.iloc[0].to_dict()

    print(f"Building scenario {scenario['scenario_id']}: D={scenario['diameter_m']} m, {scenario['arrangement_id']}")
    _, g_i = connect_input()
    _new_model(g_i)
    soil_mats = create_soil_materials(g_i, configs["materials"])
    _create_soil(g_i, configs["geometry"], soil_mats["weak_soil"])
    pile_mat = _create_embedded_beam_material(g_i, scenario, configs["piles"]["pile"])
    _create_pile_rows(g_i, scenario, configs["geometry"], pile_mat)
    _mesh(g_i)
    print("Single pile scenario build attempt finished. Check PLAXIS Input visually.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
