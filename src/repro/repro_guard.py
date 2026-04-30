from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec

from src.config.config_freeze import FrozenConfig
from src.config.config_loader import UnifiedConfig


class ReproGuardError(RuntimeError):
    pass


@dataclass(slots=True)
class ReproGuard:
    config: UnifiedConfig
    frozen_config: FrozenConfig | None = None

    REQUIRED_RUNTIME_KEYS = (
        "slot_duration",
        "local_service_capacity",
        "public_service_capacity",
        "cloud_service_capacity",
        "timeout_grace_slots",
        "runtime_variant",
    )
    ALLOWED_RUNTIME_VARIANTS = {"density_based", "discrete_slot_service", "constant_service"}

    def validate(self) -> None:
        if self.frozen_config is not None:
            if self.frozen_config.hash != self.config.config_hash:
                raise ReproGuardError("Configuration hash mismatch")
            self.frozen_config.ensure_unchanged()
        self._validate_seed_consistency()
        self._validate_trace_consistency()
        self._validate_learner_dependencies()
        self._validate_runtime_config()

    def _validate_seed_consistency(self) -> None:
        if self.config.evaluation.seed != self.config.training.seed_management.evaluation_seed:
            raise ReproGuardError("Evaluation seed does not match training seed management")
        if self.config.training.seed_management.training_seed is None:
            raise ReproGuardError("Training seed is required")

    def _validate_trace_consistency(self) -> None:
        if self.config.evaluation.trace_id != self.config.training.trace_id:
            raise ReproGuardError("Training and evaluation trace IDs must match")
        if self.config.evaluation.episode_count != self.config.training.episode_count:
            raise ReproGuardError("Training and evaluation episode counts must match")
        if self.config.evaluation.episode_length != self.config.training.episode_length:
            raise ReproGuardError("Training and evaluation episode lengths must match")
        if self.config.evaluation.trace_mode != self.config.training.trace_mode:
            raise ReproGuardError("Training and evaluation trace modes must match")

    def _validate_runtime_config(self) -> None:
        missing = [key for key in self.REQUIRED_RUNTIME_KEYS if key not in self.config.runtime]
        if missing:
            raise ReproGuardError(f"Missing runtime parameters: {', '.join(missing)}")
        runtime_variant = str(self.config.runtime["runtime_variant"])
        if runtime_variant not in self.ALLOWED_RUNTIME_VARIANTS:
            raise ReproGuardError(f"Unsupported runtime variant: {runtime_variant}")

    def _validate_learner_dependencies(self) -> None:
        learner_type = self.config.training.learner_type
        if learner_type is None:
            return
        if learner_type != "torchrl":
            return
        if find_spec("torch") is None or find_spec("torchrl") is None:
            raise ReproGuardError(
                "TorchRL learner requested but torch and/or torchrl are unavailable in the approved environment"
            )
