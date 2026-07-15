from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Literal

PolicyName = Literal["FLC", "RO", "HO", "VO", "BCO", "MLEO", "HOODIE"]
PanelId = Literal[
    "figure_8a", "figure_8b", "figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e",
    "figure_10a", "figure_10b", "figure_10c", "figure_10d", "figure_10e", "figure_10f", "figure_11",
]
PanelVariant = Literal["hoodie_lstm", "hoodie_no_lstm"]

class PanelIDError(ValueError):
    pass

@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    campaign_id: str
    experiment_id: str
    policy: PolicyName
    variant: PanelVariant | None
    seed: int
    horizon: int
    warmup: int
    confidence_level: float = 0.95
    checkpoint_selection_rule: str = "best_validation"
    topology: dict[str, object] = field(default_factory=dict)
    physical: dict[str, object] = field(default_factory=dict)
    workload: dict[str, object] = field(default_factory=dict)
    training: dict[str, object] = field(default_factory=dict)
    evaluation: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.policy not in ("FLC", "RO", "HO", "VO", "BCO", "MLEO", "HOODIE"):
            raise ValueError("unknown policy")
        if self.horizon <= 0:
            raise ValueError("invalid horizon")
        if self.warmup < 0:
            raise ValueError("invalid warmup")
        if not (0.0 < self.confidence_level < 1.0):
            raise ValueError("invalid confidence level")
        if self.workload.get("task_count", 0) < 0:
            raise ValueError("negative workloads not allowed")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "campaign_id": self.campaign_id,
            "experiment_id": self.experiment_id,
            "policy": self.policy,
            "variant": self.variant,
            "seed": self.seed,
            "horizon": self.horizon,
            "warmup": self.warmup,
            "confidence_level": self.confidence_level,
            "checkpoint_selection_rule": self.checkpoint_selection_rule,
            "topology": self.topology,
            "physical": self.physical,
            "workload": self.workload,
            "training": self.training,
            "evaluation": self.evaluation,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"))

@dataclass(frozen=True, slots=True)
class PanelSpec:
    panel_id: PanelId
    independent_variable: str
    fixed_parameters: dict[str, object]
    policies: tuple[PolicyName, ...]
    variants: tuple[PanelVariant, ...] = ()
    seeds: tuple[int, ...] = ()
    training_required: bool = True
    evaluation_required: bool = True
    metric: str = "reward"
    aggregation: str = "mean"
    expected_columns: tuple[str, ...] = ()
    output_filenames: tuple[str, ...] = ()
