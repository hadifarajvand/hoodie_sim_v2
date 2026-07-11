from __future__ import annotations

from importlib import import_module
from typing import Any

from .config import (
    CampaignConfig,
    CampaignSeedBundle,
    CampaignStage,
    PilotBudget,
    TargetUpdateContract,
)
from .readiness import CampaignReadinessProbe, ReadinessProbeResult, run_campaign_readiness_probe
from .replay import (
    ACTION_INDEX_TO_SEMANTICS,
    ACTION_INDEX_TO_SEMANTICS_PAPER,
    PAPER_ACTION_COUNT,
    PAPER_LOOKBACK_W,
    PAPER_STATE_DIM,
    ReplayBuffer,
    ReplayBatch,
    ReplayTransition,
    build_state_window,
    build_state_window_tensor,
    build_state_vector,
    legal_action_mask_to_tuple,
)
from .report import (
    CampaignReport,
    build_campaign_prerequisite_tags_verified,
    collect_prior_feature_gates_verified,
    write_campaign_report,
)

_LAZY_IMPORTS = {
    "CampaignExecutionResult": (".runner", "CampaignExecutionResult"),
    "generate_campaign_artifacts": (".runner", "generate_campaign_artifacts"),
    "main": (".runner", "main"),
    "run_campaign": (".runner", "run_campaign"),
    "DDQNTrainer": (".trainer", "DDQNTrainer"),
    "EvaluationSummary": (".trainer", "EvaluationSummary"),
    "PilotTrainingResult": (".trainer", "PilotTrainingResult"),
    "CampaignCheckpointMetadata": (".trainer", "CampaignCheckpointMetadata"),
    "run_campaign_evaluation": (".trainer", "run_campaign_evaluation"),
    "run_pilot_training": (".trainer", "run_pilot_training"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_IMPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


__all__ = [
    "ACTION_INDEX_TO_SEMANTICS",
    "ACTION_INDEX_TO_SEMANTICS_PAPER",
    "CampaignCheckpointMetadata",
    "CampaignConfig",
    "CampaignExecutionResult",
    "CampaignReadinessProbe",
    "CampaignReport",
    "CampaignSeedBundle",
    "CampaignStage",
    "DDQNTrainer",
    "EvaluationSummary",
    "PilotBudget",
    "PilotTrainingResult",
    "ReadinessProbeResult",
    "ReplayBatch",
    "ReplayBuffer",
    "ReplayTransition",
    "TargetUpdateContract",
    "build_campaign_prerequisite_tags_verified",
    "build_state_vector",
    "build_state_window",
    "build_state_window_tensor",
    "collect_prior_feature_gates_verified",
    "generate_campaign_artifacts",
    "legal_action_mask_to_tuple",
    "main",
    "run_campaign",
    "run_campaign_evaluation",
    "run_campaign_readiness_probe",
    "run_pilot_training",
    "write_campaign_report",
]
