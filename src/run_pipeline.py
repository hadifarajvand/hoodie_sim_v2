from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from src.agents.hoodie_agent import HoodieAgent
from src.agents.torchrl_hoodie_learner import TorchRLHoodieLearner
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy
from src.analysis.analysis_runner import AnalysisRunner, AnalysisRunResult
from src.config.config_freeze import FrozenConfig
from src.config.config_loader import ConfigLoader, UnifiedConfig
from src.evaluation.validation_artifacts import ValidationArtifacts, build_validation_artifacts
from src.evaluation.validation_runner import ValidationRunner
from src.repro.output_packager import OutputPackager
from src.repro.repro_guard import ReproGuard
from src.training.training_loop import TrainingLoop

SUPPORTED_SHARED_POLICIES = {
    "FLC": FullLocalComputingPolicy,
    "HO": HorizontalOffloadingPolicy,
    "VO": VerticalOffloadingPolicy,
    "RO": RandomOffloadingPolicy,
    "MLEO": MinimumLatencyEstimateOffloadingPolicy,
    "BCO": BalancedCooperationOffloadingPolicy,
}


@dataclass(slots=True)
class PipelineResult:
    config: UnifiedConfig
    validation: ValidationArtifacts
    analysis: AnalysisRunResult
    package: dict[str, str]
    training_summaries: list[dict[str, Any]]


def _build_validation_runner(config: UnifiedConfig, policy: HoodieAgent) -> ValidationRunner:
    policies = _build_validation_policies(config, policy)
    return ValidationRunner(
        policies=policies,
        config=config.evaluation,
        topology=config.validation_topology,
    )


def _build_validation_policies(config: UnifiedConfig, hoodie: HoodieAgent) -> dict[str, object]:
    policies: dict[str, object] = {}
    for policy_name in config.validation_policies:
        if policy_name == "HOODIE":
            policies[policy_name] = hoodie
            continue
        policy_factory = SUPPORTED_SHARED_POLICIES.get(policy_name)
        if policy_factory is None:
            raise ValueError(f"Unsupported validation policy: {policy_name}")
        policies[policy_name] = _instantiate_policy(policy_name, policy_factory, config)
    return policies


def _policy_seed(config: UnifiedConfig, policy_name: str) -> int:
    base_seed = config.validation_policy_seed
    if base_seed is None:
        base_seed = config.evaluation.seed
    material = f"{base_seed}:{policy_name}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _instantiate_policy(policy_name: str, policy_factory: type[object], config: UnifiedConfig) -> object:
    seed = _policy_seed(config, policy_name)
    try:
        return policy_factory(seed=seed)  # type: ignore[call-arg]
    except TypeError:
        return policy_factory()  # type: ignore[call-arg]


def _run_validation(config: UnifiedConfig, hoodie: HoodieAgent) -> tuple[ValidationArtifacts, AnalysisRunResult]:
    validation_result = _build_validation_runner(config, hoodie).run()
    validation_artifacts = build_validation_artifacts(validation_result)
    analysis_result = AnalysisRunner(validation_artifacts).run()
    return validation_artifacts, analysis_result


def _attach_training_learner(hoodie: HoodieAgent, config: UnifiedConfig) -> None:
    learner_type = config.training.learner_type
    if learner_type is None:
        return
    if learner_type != "learner_adapter":
        return
    learner = TorchRLHoodieLearner()
    hoodie.attach_learner(learner, enabled=True)


def _load_hoodie_state(state_path: str | Path) -> dict[str, Any]:
    path = Path(state_path)
    if not path.exists():
        raise FileNotFoundError(f"HOODIE state checkpoint does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("HOODIE state checkpoint must be a JSON object")
    return payload


def run_pipeline(
    config_path: str | Path,
    output_dir: str | Path,
    *,
    run_training: bool = False,
    deterministic: bool = False,
    timestamp: str | None = None,
) -> PipelineResult:
    config = ConfigLoader.load(config_path)
    frozen = FrozenConfig(config)
    ReproGuard(config=config, frozen_config=frozen).validate()

    hoodie = HoodieAgent()
    _attach_training_learner(hoodie, config)
    training_summaries: list[dict[str, Any]] = []
    hoodie_state: dict[str, Any] | None = None
    if run_training:
        training_loop = TrainingLoop(policy=hoodie, config=config.training, topology=config.validation_topology)
        training_summaries = [asdict(summary) for summary in training_loop.run()]
        hoodie_state = hoodie.export_state()
    elif config.validation_hoodie_state_path is not None:
        hoodie = HoodieAgent.from_state(_load_hoodie_state(config.validation_hoodie_state_path))
        hoodie_state = hoodie.export_state()

    validation_artifacts, analysis_result = _run_validation(config, hoodie)
    package = OutputPackager(Path(output_dir), deterministic=deterministic, timestamp=timestamp).package(
        config=config,
        validation_artifacts=validation_artifacts,
        analysis_result=analysis_result,
        training_summaries=training_summaries or None,
        hoodie_state=hoodie_state,
        hoodie_validation_mode="trained" if hoodie_state is not None else "fresh",
    )
    return PipelineResult(
        config=config,
        validation=validation_artifacts,
        analysis=analysis_result,
        package=package,
        training_summaries=training_summaries,
    )


def run_validation_only(
    config_path: str | Path,
    output_dir: str | Path,
    *,
    deterministic: bool = False,
    timestamp: str | None = None,
) -> dict[str, str]:
    config = ConfigLoader.load(config_path)
    frozen = FrozenConfig(config)
    ReproGuard(config=config, frozen_config=frozen).validate()

    hoodie = HoodieAgent()
    hoodie_state: dict[str, Any] | None = None
    hoodie_validation_mode = "fresh"
    if config.validation_hoodie_state_path is not None:
        hoodie = HoodieAgent.from_state(_load_hoodie_state(config.validation_hoodie_state_path))
        hoodie_state = hoodie.export_state()
        hoodie_validation_mode = "trained"
    validation_artifacts, _analysis_result = _run_validation(config, hoodie)
    return OutputPackager(Path(output_dir), deterministic=deterministic, timestamp=timestamp).package(
        config=config,
        validation_artifacts=validation_artifacts,
        analysis_result=None,
        hoodie_state=hoodie_state,
        hoodie_validation_mode=hoodie_validation_mode,
    )


def run_analysis_only(
    config_path: str | Path,
    output_dir: str | Path,
    *,
    deterministic: bool = False,
    timestamp: str | None = None,
) -> dict[str, str]:
    config = ConfigLoader.load(config_path)
    frozen = FrozenConfig(config)
    ReproGuard(config=config, frozen_config=frozen).validate()

    run_dir = Path(output_dir) / "outputs"
    if not run_dir.exists():
        raise FileNotFoundError(f"No outputs directory found at {run_dir}")
    candidates = sorted(run_dir.iterdir())
    if not candidates:
        raise FileNotFoundError(f"No packaged runs found under {run_dir}")
    latest_run = candidates[-1]
    validation_path = latest_run / "validation_artifacts.json"
    if not validation_path.exists():
        raise FileNotFoundError(f"Missing validation artifacts at {validation_path}")
    validation_payload = OutputPackager.load_validation_artifacts(validation_path)
    analysis_result = AnalysisRunner(validation_payload).run()
    package = OutputPackager(Path(output_dir), deterministic=deterministic, timestamp=timestamp).package(
        config=config,
        validation_artifacts=build_validation_artifacts_from_dict(validation_payload),
        analysis_result=analysis_result,
    )
    return package


def build_validation_artifacts_from_dict(payload: dict[str, Any]) -> ValidationArtifacts:
    from src.evaluation.validation_runner import ValidationPolicyResult, ValidationRunResult

    policy_results: list[ValidationPolicyResult] = []
    baseline = payload["policy_results"]["baseline"]
    if baseline is not None:
        policy_results.append(
            ValidationPolicyResult(policy_name=baseline["policy_name"], trace_results=baseline["trace_results"])
        )
    for policy in payload["policy_results"]["compared_policies"]:
        policy_results.append(
            ValidationPolicyResult(policy_name=policy["policy_name"], trace_results=policy["trace_results"])
        )
    run_result = ValidationRunResult(
        config_snapshot=payload.get("evaluation_config_snapshot", payload.get("config_snapshot")),
        config_hash=payload.get("evaluation_config_hash", payload.get("config_hash")),
        baseline_policy_name=payload["baseline_policy_name"],
        policy_order=tuple(payload["policy_order"]),
        policy_results=policy_results,
    )
    return ValidationArtifacts(validation=run_result, comparison=payload["comparison"])
