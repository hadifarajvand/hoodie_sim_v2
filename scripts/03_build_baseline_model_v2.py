"""Build a simple baseline PLAXIS 2D slope model.

This script intentionally builds only the baseline slope. It does not add piles
and it does not run the full parametric batch.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sheykhzadeh.config_loader import load_and_validate_configs
from sheykhzadeh.geometry import slope_polygon_points
from sheykhzadeh.materials import create_soil_materials
from sheykhzadeh.plaxis_client import connect_input


def _try_call(label: str, func, *args):
    try:
        result = func(*args)
        print(f"OK: {label}")
        return result
    except Exception as exc:
        print(f"WARN: {label} failed: {exc}")
        return None


def _new_project(g_i) -> None:
    _try_call("new project", g_i.new)
    _try_call("go to structures", getattr(g_i, "gotostructures", lambda: None))


def _create_soil_polygon(g_i, geometry_cfg):
    points = slope_polygon_points(geometry_cfg)
    print("Creating slope polygon with points:")
    for point in points:
        print(f"  {point}")
    polygon = g_i.polygon(*points)
    print("OK: slope polygon created")
    return polygon


def _assign_material(g_i, soil_object, material) -> None:
    # PLAXIS object return shapes vary between versions. Try the common options.
    candidates = []
    if soil_object is not None:
        candidates.append(soil_object)
        if isinstance(soil_object, (list, tuple)):
            candidates.extend(soil_object)
    for candidate in candidates:
        try:
            g_i.setmaterial(candidate, material)
            print("OK: material assigned")
            return
        except Exception:
            pass
    print("WARN: material assignment was not confirmed. Assign manually if needed.")


def _mesh(g_i) -> None:
    if hasattr(g_i, "gotomesh"):
        _try_call("go to mesh", g_i.gotomesh)
    if hasattr(g_i, "mesh"):
        _try_call("generate mesh", g_i.mesh, 0.06)
    elif hasattr(g_i, "generatemesh"):
        _try_call("generate mesh", g_i.generatemesh)
    else:
        print("WARN: mesh command not found for this PLAXIS version.")


def main() -> int:
    configs = load_and_validate_configs(ROOT)
    _, g_i = connect_input()
    _new_project(g_i)
    materials = create_soil_materials(g_i, configs["materials"])
    soil = _create_soil_polygon(g_i, configs["geometry"])
    _assign_material(g_i, soil, materials["weak_soil"])
    _mesh(g_i)
    print("Baseline model build attempt finished.")
    print("Check PLAXIS Input visually before moving to pile scenarios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
