from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 is unsupported here.
    tomllib = None  # type: ignore[assignment]

from src.evaluation.config import EvaluationConfig
from src.environment.topology import TopologyGraph
from src.training.seed_management import SeedManagement
from src.config.training_config import TrainingConfig


class ConfigLoaderError(ValueError):
    pass


class UnifiedConfig:
    def __init__(
        self,
        *,
        training: TrainingConfig,
        evaluation: EvaluationConfig,
        runtime: dict[str, Any],
        validation_policies: tuple[str, ...],
        validation_policy_seed: int | None,
        validation_hoodie_state_path: Path | None,
        validation_topology: TopologyGraph | None,
        source_path: Path,
    ) -> None:
        self.training = training
        self.evaluation = evaluation
        self.runtime = runtime
        self.validation_policies = validation_policies
        self.validation_policy_seed = validation_policy_seed
        self.validation_hoodie_state_path = validation_hoodie_state_path
        self.validation_topology = validation_topology
        self.source_path = source_path

    def to_dict(self) -> dict[str, object]:
        return {
            "training": self.training.to_dict(),
            "evaluation": {
                "policy_name": self.evaluation.policy_name,
                "seed": self.evaluation.seed,
                "trace_id": self.evaluation.trace_id,
                "episode_count": self.evaluation.episode_count,
                "episode_length": self.evaluation.episode_length,
                "output_dir": str(self.evaluation.output_dir) if self.evaluation.output_dir is not None else None,
                "trace_mode": self.evaluation.trace_mode,
                "device": self.evaluation.device,
            },
            "runtime": self.runtime,
            "validation": {
                "policies": list(self.validation_policies),
                "policy_seed": self.validation_policy_seed,
                "hoodie_state_path": str(self.validation_hoodie_state_path) if self.validation_hoodie_state_path is not None else None,
                "topology": self._topology_to_dict(),
            },
        }

    def _topology_to_dict(self) -> dict[str, object] | None:
        if self.validation_topology is None:
            return None
        return {
            "node_ids": list(self.validation_topology.node_ids),
            "legal_adjacency": {
                source: list(destinations)
                for source, destinations in self.validation_topology.legal_adjacency.items()
            },
        }

    @property
    def snapshot(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)

    @property
    def config_hash(self) -> str:
        return sha256(self.snapshot.encode("utf-8")).hexdigest()

    def __hash__(self) -> int:
        return int(self.config_hash[:16], 16)


class ConfigLoader:
    REQUIRED_TOP_LEVEL = ("training", "evaluation", "runtime", "validation")
    REQUIRED_TRAINING = (
        "learning_rate",
        "batch_size",
        "replay_buffer_capacity",
        "target_network_update_frequency",
        "episode_count",
        "episode_length",
        "seed_management",
    )
    REQUIRED_EVALUATION = (
        "policy_name",
        "seed",
        "trace_id",
        "episode_count",
        "episode_length",
    )
    REQUIRED_RUNTIME = (
        "slot_duration",
        "local_service_capacity",
        "public_service_capacity",
        "cloud_service_capacity",
        "timeout_grace_slots",
        "runtime_variant",
    )
    REQUIRED_VALIDATION = ("policies",)

    @classmethod
    def load(cls, path: str | Path) -> UnifiedConfig:
        source_path = Path(path)
        payload = cls._load_mapping(source_path)
        cls._validate_top_level(payload)
        training = cls._build_training(payload["training"])
        evaluation = cls._build_evaluation(payload["evaluation"])
        runtime = cls._build_runtime(payload["runtime"])
        validation_policies = cls._build_validation(payload["validation"])
        validation_policy_seed = cls._build_validation_policy_seed(payload["validation"])
        validation_hoodie_state_path = cls._build_validation_hoodie_state_path(payload["validation"])
        validation_topology = cls._build_validation_topology(payload["validation"])
        return UnifiedConfig(
            training=training,
            evaluation=evaluation,
            runtime=runtime,
            validation_policies=validation_policies,
            validation_policy_seed=validation_policy_seed,
            validation_hoodie_state_path=validation_hoodie_state_path,
            validation_topology=validation_topology,
            source_path=source_path,
        )

    @classmethod
    def _load_mapping(cls, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ConfigLoaderError(f"Configuration file does not exist: {path}")
        suffix = path.suffix.lower()
        raw_text = path.read_text(encoding="utf-8")
        if suffix == ".json":
            payload = json.loads(raw_text)
        elif suffix == ".toml":
            if tomllib is None:
                raise ConfigLoaderError("TOML support is unavailable")
            payload = tomllib.loads(raw_text)
        elif suffix in {".yml", ".yaml"}:
            raise ConfigLoaderError("YAML unified configs are not supported; use JSON or TOML")
        else:
            raise ConfigLoaderError(f"Unsupported configuration format: {suffix}")
        if not isinstance(payload, dict):
            raise ConfigLoaderError("Configuration root must be a mapping")
        return payload

    @classmethod
    def _validate_top_level(cls, payload: dict[str, Any]) -> None:
        missing = [name for name in cls.REQUIRED_TOP_LEVEL if name not in payload]
        if missing:
            raise ConfigLoaderError(f"Missing top-level configuration sections: {', '.join(missing)}")

    @staticmethod
    def _require_fields(section_name: str, section: dict[str, Any], required_fields: tuple[str, ...]) -> None:
        missing = [name for name in required_fields if name not in section]
        if missing:
            raise ConfigLoaderError(f"Missing required fields in {section_name}: {', '.join(missing)}")

    @classmethod
    def _build_training(cls, section: Any) -> TrainingConfig:
        if not isinstance(section, dict):
            raise ConfigLoaderError("training section must be a mapping")
        cls._require_fields("training", section, cls.REQUIRED_TRAINING)
        seed_management_raw = section["seed_management"]
        if not isinstance(seed_management_raw, dict):
            raise ConfigLoaderError("training.seed_management must be a mapping")
        cls._require_fields("training.seed_management", seed_management_raw, ("training_seed", "evaluation_seed"))
        output_dir = section.get("output_dir")
        checkpoint_manifest_path = section.get("checkpoint_manifest_path")
        checkpoint_state_path = section.get("checkpoint_state_path")
        return TrainingConfig(
            learning_rate=float(section["learning_rate"]),
            batch_size=int(section["batch_size"]),
            replay_buffer_capacity=int(section["replay_buffer_capacity"]),
            target_network_update_frequency=int(section["target_network_update_frequency"]),
            episode_count=int(section["episode_count"]),
            episode_length=int(section["episode_length"]),
            seed_management=SeedManagement(
                training_seed=int(seed_management_raw["training_seed"]),
                evaluation_seed=int(seed_management_raw["evaluation_seed"]),
            ),
            policy_name=str(section.get("policy_name", "HOODIE")),
            trace_id=str(section.get("trace_id", "training")),
            trace_mode=str(section.get("trace_mode", "deterministic_seed")),
            device=str(section.get("device", "cpu")),
            learner_type=str(section["learner_type"]) if section.get("learner_type") is not None else None,
            replay_seed=int(section["replay_seed"]) if section.get("replay_seed") is not None else None,
            torch_seed=int(section["torch_seed"]) if section.get("torch_seed") is not None else None,
            checkpoint_manifest_path=Path(checkpoint_manifest_path) if checkpoint_manifest_path is not None else None,
            checkpoint_state_path=Path(checkpoint_state_path) if checkpoint_state_path is not None else None,
            output_dir=Path(output_dir) if output_dir is not None else None,
        )

    @classmethod
    def _build_evaluation(cls, section: Any) -> EvaluationConfig:
        if not isinstance(section, dict):
            raise ConfigLoaderError("evaluation section must be a mapping")
        cls._require_fields("evaluation", section, cls.REQUIRED_EVALUATION)
        output_dir = section.get("output_dir")
        return EvaluationConfig(
            policy_name=str(section["policy_name"]),
            seed=int(section["seed"]),
            trace_id=str(section["trace_id"]),
            episode_count=int(section["episode_count"]),
            episode_length=int(section["episode_length"]),
            output_dir=Path(output_dir) if output_dir is not None else None,
            trace_mode=str(section.get("trace_mode", "deterministic_seed")),
            device=str(section.get("device", "cpu")),
        )

    @classmethod
    def _build_runtime(cls, section: Any) -> dict[str, Any]:
        if not isinstance(section, dict):
            raise ConfigLoaderError("runtime section must be a mapping")
        cls._require_fields("runtime", section, cls.REQUIRED_RUNTIME)
        return dict(section)

    @classmethod
    def _build_validation(cls, section: Any) -> tuple[str, ...]:
        if not isinstance(section, dict):
            raise ConfigLoaderError("validation section must be a mapping")
        cls._require_fields("validation", section, cls.REQUIRED_VALIDATION)
        policies = section["policies"]
        if not isinstance(policies, list) or not policies:
            raise ConfigLoaderError("validation.policies must be a non-empty list")
        normalized = tuple(str(policy) for policy in policies)
        if len(set(normalized)) != len(normalized):
            raise ConfigLoaderError("validation.policies must not contain duplicates")
        return normalized

    @staticmethod
    def _build_validation_policy_seed(section: Any) -> int | None:
        if not isinstance(section, dict):
            raise ConfigLoaderError("validation section must be a mapping")
        policy_seed = section.get("policy_seed")
        if policy_seed is None:
            return None
        return int(policy_seed)

    @staticmethod
    def _build_validation_hoodie_state_path(section: Any) -> Path | None:
        if not isinstance(section, dict):
            raise ConfigLoaderError("validation section must be a mapping")
        hoodie_state_path = section.get("hoodie_state_path")
        if hoodie_state_path is None:
            return None
        return Path(hoodie_state_path)

    @staticmethod
    def _build_validation_topology(section: Any) -> TopologyGraph | None:
        if not isinstance(section, dict):
            raise ConfigLoaderError("validation section must be a mapping")
        topology = section.get("topology")
        if topology is None:
            return None
        if not isinstance(topology, dict):
            raise ConfigLoaderError("validation.topology must be a mapping")
        node_ids = topology.get("node_ids")
        legal_adjacency = topology.get("legal_adjacency")
        if not isinstance(node_ids, list) or not node_ids:
            raise ConfigLoaderError("validation.topology.node_ids must be a non-empty list")
        if not isinstance(legal_adjacency, dict):
            raise ConfigLoaderError("validation.topology.legal_adjacency must be a mapping")
        normalized_adjacency: dict[str, tuple[str, ...]] = {}
        for source, destinations in legal_adjacency.items():
            if not isinstance(destinations, list):
                raise ConfigLoaderError("validation.topology.legal_adjacency values must be lists")
            normalized_adjacency[str(source)] = tuple(str(destination) for destination in destinations)
        return TopologyGraph(
            node_ids=tuple(str(node_id) for node_id in node_ids),
            legal_adjacency=normalized_adjacency,
        )
