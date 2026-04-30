from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.evaluation.config import EvaluationConfig
from src.training.seed_management import SeedManagement


@dataclass(slots=True)
class TrainingConfig:
    learning_rate: float
    batch_size: int
    replay_buffer_capacity: int
    target_network_update_frequency: int
    episode_count: int
    episode_length: int
    seed_management: SeedManagement = field(default_factory=SeedManagement)
    policy_name: str = "HOODIE"
    trace_id: str = "training"
    trace_mode: str = "deterministic_seed"
    device: str = "cpu"
    learner_type: str | None = None
    replay_seed: int | None = None
    torch_seed: int | None = None
    checkpoint_manifest_path: Path | None = None
    checkpoint_state_path: Path | None = None
    output_dir: Path | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["output_dir"] = str(self.output_dir) if self.output_dir is not None else None
        if self.learner_type is None:
            payload.pop("learner_type", None)
        if self.replay_seed is None:
            payload.pop("replay_seed", None)
        if self.torch_seed is None:
            payload.pop("torch_seed", None)
        if self.checkpoint_manifest_path is None:
            payload.pop("checkpoint_manifest_path", None)
        else:
            payload["checkpoint_manifest_path"] = str(self.checkpoint_manifest_path)
        if self.checkpoint_state_path is None:
            payload.pop("checkpoint_state_path", None)
        else:
            payload["checkpoint_state_path"] = str(self.checkpoint_state_path)
        return payload

    def to_evaluation_config(self) -> EvaluationConfig:
        return EvaluationConfig(
            policy_name=self.policy_name,
            seed=self.seed_management.evaluation_seed,
            trace_id=self.trace_id,
            episode_count=self.episode_count,
            episode_length=self.episode_length,
            output_dir=self.output_dir,
            trace_mode=self.trace_mode,
            device=self.device,
        )
