from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .specification import PanelSpec

_CONTRACT_DIR = Path("resources/papers/hoodie/contracts")
_PANEL_ORDER = (
    "figure_8a",
    "figure_8b",
    "figure_9a",
    "figure_9b",
    "figure_9c",
    "figure_9d",
    "figure_9e",
    "figure_10a",
    "figure_10b",
    "figure_10c",
    "figure_10d",
    "figure_10e",
    "figure_10f",
    "figure_11",
)


@dataclass(frozen=True, slots=True)
class PanelContract:
    spec: PanelSpec
    source_contract: dict[str, Any]


def _load(name: str) -> dict[str, Any]:
    return json.loads((_CONTRACT_DIR / name).read_text(encoding="utf-8"))


def _panel_files(panel_id: str) -> tuple[str, str, str]:
    return (f"{panel_id}.svg", f"{panel_id}.pdf", f"{panel_id}.png")


def _fixed_parameters(panel: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "fixed_topology",
        "learning_rate",
        "discount_factor",
        "task_arrival_probability",
        "task_timeout_seconds",
        "training_episodes",
        "validation_episodes",
        "agent_counts",
        "action_categories",
        "traffic_scenarios",
        "rate_scenarios",
        "compared_policies",
        "series",
        "variants",
        "checkpoint_rule",
        "averaging",
        "sign_convention",
        "policy_mode",
    }
    return {key: panel[key] for key in keys if key in panel}


def _make_spec(panel: dict[str, Any]) -> PanelSpec:
    panel_id = panel["panel_id"]
    if panel_id.startswith("figure_8"):
        evaluation_required = False
        metric = "accumulated_reward"
        expected_columns = ("episode", "reward", "series")
    elif panel_id == "figure_11":
        evaluation_required = False
        metric = "average_task_delay"
        expected_columns = ("episode", "delay", "variant")
    elif panel_id.startswith("figure_9"):
        evaluation_required = True
        metric = panel.get("dependent_metric", "average_reward")
        expected_columns = ("independent_value", "metric", "series")
    else:
        evaluation_required = True
        metric = panel.get("dependent_metric", "average_delay")
        expected_columns = ("independent_value", "metric", "policy")

    return PanelSpec(
        panel_id=panel_id,
        independent_variable=panel["independent_variable"],
        fixed_parameters=_fixed_parameters(panel),
        policies=tuple(panel.get("compared_policies", ())),
        variants=tuple(panel.get("variants", ())),
        seeds=tuple(panel.get("seeds", ())),
        training_required=True,
        evaluation_required=evaluation_required,
        metric=metric,
        aggregation="mean",
        expected_columns=expected_columns,
        output_filenames=_panel_files(panel_id),
    )


FIGURE_8 = _load("figure_8.json")
FIGURE_9 = _load("figure_9.json")
FIGURE_10 = _load("figure_10.json")
FIGURE_11 = _load("figure_11.json")

PANEL_REGISTRY: dict[str, PanelContract] = {}
for payload in (*FIGURE_8["panels"], *FIGURE_9["panels"], *FIGURE_10["panels"], *FIGURE_11["panels"]):
    spec = _make_spec(payload)
    PANEL_REGISTRY[spec.panel_id] = PanelContract(spec=spec, source_contract=payload)

missing = set(_PANEL_ORDER) - set(PANEL_REGISTRY)
if missing:
    raise RuntimeError(f"missing panel registry entries: {sorted(missing)}")
