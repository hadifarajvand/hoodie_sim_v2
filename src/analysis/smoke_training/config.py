from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig

FEATURE_ID = "040-smoke-training"
SMOKE_STATE_DIM = 3
SMOKE_ACTION_COUNT = 3
SMOKE_LOOKBACK_W = 10
SMOKE_BATCH_SIZE = 2
SMOKE_OPTIMIZER_STEPS = 1
SMOKE_MODEL_INITIALIZATION_SEED = 19
SMOKE_SEED = 40
SMOKE_LEARNING_RATE = 7e-7
SMOKE_DATA_SOURCE = "smoke_fixture"


@dataclass(slots=True)
class SmokeSeedBundle:
    smoke_seed: int = SMOKE_SEED
    python_seed: int = SMOKE_SEED
    torch_seed: int = SMOKE_SEED
    model_initialization_seed: int = SMOKE_MODEL_INITIALIZATION_SEED

    def __post_init__(self) -> None:
        for field_name in ("smoke_seed", "python_seed", "torch_seed", "model_initialization_seed"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise ValueError(f"{field_name} must be an integer.")

    @property
    def signature(self) -> str:
        return (
            f"smoke={self.smoke_seed}|python={self.python_seed}|"
            f"torch={self.torch_seed}|model={self.model_initialization_seed}"
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "smoke_seed": self.smoke_seed,
            "python_seed": self.python_seed,
            "torch_seed": self.torch_seed,
            "model_initialization_seed": self.model_initialization_seed,
        }


@dataclass(slots=True)
class SmokeTrainingConfig:
    feature_id: str = FEATURE_ID
    state_dim: int = SMOKE_STATE_DIM
    action_count: int = SMOKE_ACTION_COUNT
    lookback_w: int = SMOKE_LOOKBACK_W
    batch_size: int = SMOKE_BATCH_SIZE
    optimizer_steps: int = SMOKE_OPTIMIZER_STEPS
    model_initialization_seed: int = SMOKE_MODEL_INITIALIZATION_SEED
    smoke_seed: int = SMOKE_SEED
    learning_rate: float = SMOKE_LEARNING_RATE
    use_fixture_transitions: bool = True
    enable_environment_rollout: bool = False
    target_update_enabled: bool = False
    data_source: str = SMOKE_DATA_SOURCE
    seed_bundle: SmokeSeedBundle | None = None

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("SmokeTrainingConfig.feature_id must be 040-smoke-training.")
        if self.state_dim != SMOKE_STATE_DIM:
            raise ValueError("SmokeTrainingConfig.state_dim must be 3.")
        if self.action_count != SMOKE_ACTION_COUNT:
            raise ValueError("SmokeTrainingConfig.action_count must be 3.")
        if self.lookback_w != SMOKE_LOOKBACK_W:
            raise ValueError("SmokeTrainingConfig.lookback_w must be 10.")
        if self.batch_size != SMOKE_BATCH_SIZE:
            raise ValueError("SmokeTrainingConfig.batch_size must be 2.")
        if self.optimizer_steps != SMOKE_OPTIMIZER_STEPS:
            raise ValueError("SmokeTrainingConfig.optimizer_steps must be 1.")
        if self.model_initialization_seed != SMOKE_MODEL_INITIALIZATION_SEED:
            raise ValueError("SmokeTrainingConfig.model_initialization_seed must be 19.")
        if self.smoke_seed != SMOKE_SEED:
            raise ValueError("SmokeTrainingConfig.smoke_seed must be fixed at 40.")
        if self.learning_rate <= 0:
            raise ValueError("SmokeTrainingConfig.learning_rate must be positive.")
        if not self.use_fixture_transitions:
            raise ValueError("SmokeTrainingConfig.use_fixture_transitions must remain true.")
        if self.target_update_enabled:
            raise ValueError("SmokeTrainingConfig.target_update_enabled must remain false.")
        if self.data_source != SMOKE_DATA_SOURCE:
            raise ValueError("SmokeTrainingConfig.data_source must be smoke_fixture.")
        if self.seed_bundle is None:
            self.seed_bundle = SmokeSeedBundle(
                smoke_seed=self.smoke_seed,
                python_seed=self.smoke_seed,
                torch_seed=self.smoke_seed,
                model_initialization_seed=self.model_initialization_seed,
            )
        elif not isinstance(self.seed_bundle, SmokeSeedBundle):
            raise ValueError("seed_bundle must be a SmokeSeedBundle.")
        elif self.seed_bundle.model_initialization_seed != self.model_initialization_seed:
            raise ValueError("seed_bundle.model_initialization_seed must match the config model seed.")

    def build_network_config(self) -> PaperHoodieNetworkConfig:
        return PaperHoodieNetworkConfig.standard(
            state_dim=self.state_dim,
            model_initialization_seed=self.model_initialization_seed,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "state_dim": self.state_dim,
            "action_count": self.action_count,
            "lookback_w": self.lookback_w,
            "batch_size": self.batch_size,
            "optimizer_steps": self.optimizer_steps,
            "model_initialization_seed": self.model_initialization_seed,
            "smoke_seed": self.smoke_seed,
            "learning_rate": self.learning_rate,
            "use_fixture_transitions": self.use_fixture_transitions,
            "enable_environment_rollout": self.enable_environment_rollout,
            "target_update_enabled": self.target_update_enabled,
            "data_source": self.data_source,
            "seed_bundle": self.seed_bundle.to_dict() if self.seed_bundle else None,
        }
