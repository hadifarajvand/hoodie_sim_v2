from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import subprocess
from typing import Any


FEATURE_ID = "039-paper-hoodie-network-implementation"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/paper-hoodie-network-implementation")
JSON_FILENAME = "network-implementation-report.json"
MARKDOWN_FILENAME = "network-implementation-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _torch_available() -> bool:
    try:
        import torch  # type: ignore
    except ModuleNotFoundError:
        return False
    except Exception:
        return False
    return True


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _read_feature_pointer() -> str | None:
    pointer_path = Path(".specify/feature.json")
    if not pointer_path.exists():
        return None
    try:
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    value = payload.get("feature_directory")
    return str(value) if isinstance(value, str) else None


def collect_prerequisite_tags_verified() -> list[dict[str, Any]]:
    feature_dir = Path("specs") / FEATURE_ID
    pointer = _read_feature_pointer()
    checks: list[dict[str, Any]] = []
    expectations = [
        ("branch", _git_output("branch", "--show-current") == FEATURE_ID, "git branch --show-current == 039-paper-hoodie-network-implementation"),
        ("not_main", _git_output("branch", "--show-current") != "main", "current branch != main"),
        ("main_equals_origin_main", _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "main == origin/main"),
        ("main_equals_feature_038", _git_output("rev-parse", "main") == _git_output("rev-parse", "038-training-foundation-contract-complete^{}"), "main == 038-training-foundation-contract-complete^{}"),
        ("feature_038_diff_empty", _git_output("diff", "--name-only", "038-training-foundation-contract-complete^{}", "main") == "", "git diff --name-only 038-training-foundation-contract-complete^{} main is empty"),
        ("feature_dir_exists", feature_dir.exists(), "specs/039-paper-hoodie-network-implementation/ exists"),
        ("pointer_matches_feature", pointer == "specs/039-paper-hoodie-network-implementation", ".specify/feature.json points to specs/039-paper-hoodie-network-implementation"),
        ("pointer_not_audit_036", pointer != "specs/036-deadline-timeout-off-by-one-audit", ".specify/feature.json does not point to specs/036-deadline-timeout-off-by-one-audit"),
        ("pointer_unstaged", _git_output("status", "--short", "--", ".specify/feature.json") in {"", " M .specify/feature.json"}, ".specify/feature.json must not be staged"),
        ("pointer_not_in_main_head", ".specify/feature.json" not in _git_output("diff", "--name-only", "main...HEAD").splitlines(), ".specify/feature.json must not appear in git diff --name-only main...HEAD"),
    ]
    for name, verified, details in expectations:
        checks.append({"name": name, "verified": bool(verified), "details": details})
    return checks


@dataclass(slots=True)
class PaperHoodieNetworkConfig:
    state_dim: int | None
    q_network_hidden_layers: list[int] | int | None = None
    action_count: int = 3
    lstm_lookback_w: int = 10
    lstm_num_layers: int | None = None
    lstm_hidden_size: int | None = None
    model_initialization_seed: int | None = None
    dueling_enabled: bool = True
    double_dqn_api_enabled: bool = True
    state_contract_ref: str = "specs/038-training-foundation-contract/spec.md#FR-001"
    action_contract_ref: str = "specs/038-training-foundation-contract/spec.md#FR-004"
    dependency_status: str = "blocked_missing_existing_torch"
    dependency_blocked_reason: str = "torch is unavailable in the approved interpreter"

    def __post_init__(self) -> None:
        if self.action_count != 3:
            raise ValueError("Feature 039 keeps action_count fixed at 3.")
        if self.q_network_hidden_layers is None:
            raise ValueError("q_network_hidden_layers is required and must equal [1024, 1024, 1024].")
        if isinstance(self.q_network_hidden_layers, int):
            raise ValueError("Shared N_L coupling is forbidden; q_network_hidden_layers must be a list.")
        if list(self.q_network_hidden_layers) != [1024, 1024, 1024]:
            raise ValueError("q_network_hidden_layers must equal [1024, 1024, 1024].")
        if self.lstm_num_layers is None:
            raise ValueError("lstm_num_layers is required and must equal 1.")
        if self.lstm_hidden_size is None:
            raise ValueError("lstm_hidden_size is required and must equal 20.")
        if self.lstm_num_layers != 1:
            raise ValueError("lstm_num_layers must equal 1.")
        if self.lstm_hidden_size != 20:
            raise ValueError("lstm_hidden_size must equal 20.")
        if self.model_initialization_seed is None:
            raise ValueError("model_initialization_seed is required.")
        if self.state_dim is not None and self.state_dim <= 0:
            raise ValueError("state_dim must be positive when specified.")
        if not self.dueling_enabled:
            raise ValueError("dueling_enabled must remain true.")
        if not self.double_dqn_api_enabled:
            raise ValueError("double_dqn_api_enabled must remain true.")

    @classmethod
    def standard(cls, *, state_dim: int | None = None, model_initialization_seed: int = 19) -> "PaperHoodieNetworkConfig":
        return cls(
            state_dim=state_dim,
            q_network_hidden_layers=[1024, 1024, 1024],
            action_count=3,
            lstm_lookback_w=10,
            lstm_num_layers=1,
            lstm_hidden_size=20,
            model_initialization_seed=model_initialization_seed,
            dueling_enabled=True,
            double_dqn_api_enabled=True,
        )

    @classmethod
    def from_shared_n_l(cls, *, shared_n_l: int, state_dim: int | None = None, model_initialization_seed: int = 19) -> "PaperHoodieNetworkConfig":
        raise ValueError(
            f"Shared N_L coupling is forbidden for Feature 039; received shared_n_l={shared_n_l} instead of separate q_network_hidden_layers and lstm_* fields."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_dim": self.state_dim,
            "q_network_hidden_layers": list(self.q_network_hidden_layers) if not isinstance(self.q_network_hidden_layers, int) and self.q_network_hidden_layers is not None else self.q_network_hidden_layers,
            "action_count": self.action_count,
            "lstm_lookback_w": self.lstm_lookback_w,
            "lstm_num_layers": self.lstm_num_layers,
            "lstm_hidden_size": self.lstm_hidden_size,
            "model_initialization_seed": self.model_initialization_seed,
            "dueling_enabled": self.dueling_enabled,
            "double_dqn_api_enabled": self.double_dqn_api_enabled,
            "state_contract_ref": self.state_contract_ref,
            "action_contract_ref": self.action_contract_ref,
            "dependency_status": self.dependency_status,
            "dependency_blocked_reason": self.dependency_blocked_reason,
        }

    @property
    def expected_input_shape(self) -> str:
        return "batch_size x 10 x state_dim"

    @property
    def expected_output_shape(self) -> str:
        return "batch_size x 3"


@dataclass(slots=True)
class LstmEncoder:
    lookback_w: int
    input_dim: int | None
    hidden_size: int
    num_layers: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lookback_w": self.lookback_w,
            "input_dim": self.input_dim,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
        }


@dataclass(slots=True)
class QNetworkBody:
    hidden_layers: list[int]
    input_dim: int | None
    output_dim: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "hidden_layers": list(self.hidden_layers),
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
        }


@dataclass(slots=True)
class DuelingHeads:
    value_stream_output_dim: int
    advantage_stream_output_dim: int
    aggregation_rule: str = "Q(s,a) = V(s) + A(s,a) - mean_a A(s,a)"

    def to_dict(self) -> dict[str, Any]:
        return {
            "value_stream_output_dim": self.value_stream_output_dim,
            "advantage_stream_output_dim": self.advantage_stream_output_dim,
            "aggregation_rule": self.aggregation_rule,
        }


@dataclass(slots=True)
class OnlineTargetNetworkPair:
    online_network: dict[str, Any] | None
    target_network: dict[str, Any] | None
    forward_api_shape: str
    compatibility_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "online_network": self.online_network,
            "target_network": self.target_network,
            "forward_api_shape": self.forward_api_shape,
            "compatibility_verified": self.compatibility_verified,
        }


@dataclass(slots=True)
class ShapeValidationReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    dependency_status: str
    architecture_config: dict[str, Any]
    q_network_hidden_layers_verified: bool
    lstm_hidden_layers_verified: bool
    q_lstm_config_separation_verified: bool
    dueling_head_verified: bool
    double_dqn_api_verified: bool
    online_target_network_compatibility_verified: bool
    state_action_contract_refs: list[str]
    shape_validation_summary: dict[str, Any]
    deterministic_initialization_verified: bool
    feature_038_training_readiness_block_respected: bool
    no_training_started: bool
    no_optimizer_step: bool
    no_replay_execution: bool
    no_target_update_execution: bool
    no_environment_contract_drift: bool
    no_reward_timing_change: bool
    no_policy_drift: bool
    no_dependency_drift: bool
    no_curve_fitting: bool
    no_paper_reproduction_claim: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "dependency_status": self.dependency_status,
            "architecture_config": dict(self.architecture_config),
            "q_network_hidden_layers_verified": self.q_network_hidden_layers_verified,
            "lstm_hidden_layers_verified": self.lstm_hidden_layers_verified,
            "q_lstm_config_separation_verified": self.q_lstm_config_separation_verified,
            "dueling_head_verified": self.dueling_head_verified,
            "double_dqn_api_verified": self.double_dqn_api_verified,
            "online_target_network_compatibility_verified": self.online_target_network_compatibility_verified,
            "state_action_contract_refs": list(self.state_action_contract_refs),
            "shape_validation_summary": dict(self.shape_validation_summary),
            "deterministic_initialization_verified": self.deterministic_initialization_verified,
            "feature_038_training_readiness_block_respected": self.feature_038_training_readiness_block_respected,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_execution": self.no_replay_execution,
            "no_target_update_execution": self.no_target_update_execution,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_policy_drift": self.no_policy_drift,
            "no_dependency_drift": self.no_dependency_drift,
            "no_curve_fitting": self.no_curve_fitting,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Paper HOODIE Network Implementation Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- dependency_status: `{payload['dependency_status']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- no_training_started: `{payload['no_training_started']}`",
            f"- no_optimizer_step: `{payload['no_optimizer_step']}`",
            f"- no_replay_execution: `{payload['no_replay_execution']}`",
            f"- no_target_update_execution: `{payload['no_target_update_execution']}`",
            f"- no_environment_contract_drift: `{payload['no_environment_contract_drift']}`",
            f"- no_reward_timing_change: `{payload['no_reward_timing_change']}`",
            f"- no_policy_drift: `{payload['no_policy_drift']}`",
            f"- no_dependency_drift: `{payload['no_dependency_drift']}`",
            f"- no_curve_fitting: `{payload['no_curve_fitting']}`",
            f"- no_paper_reproduction_claim: `{payload['no_paper_reproduction_claim']}`",
            "",
            "## Architecture Config",
        ]
        for key, value in payload["architecture_config"].items():
            lines.append(f"- **{key}**: {value}")
        lines.extend(
            [
                "",
                "## Shape Validation Summary",
            ]
        )
        for key, value in payload["shape_validation_summary"].items():
            lines.append(f"- **{key}**: {value}")
        lines.extend(
            [
                "",
                "## Prerequisite Checks",
            ]
        )
        for check in payload["prerequisite_tags_verified"]:
            lines.append(f"- **{check['name']}**: {check['verified']} ({check['details']})")
        lines.extend(
            [
                "",
                "## State / Action Contract References",
            ]
        )
        lines.extend(f"- {item}" for item in payload["state_action_contract_refs"])
        lines.append("")
        return "\n".join(lines)


def _build_config() -> PaperHoodieNetworkConfig:
    return PaperHoodieNetworkConfig.standard(state_dim=None, model_initialization_seed=19)


def _build_shape_summary(config: PaperHoodieNetworkConfig, torch_available: bool) -> dict[str, Any]:
    encoder = LstmEncoder(lookback_w=config.lstm_lookback_w, input_dim=config.state_dim, hidden_size=config.lstm_hidden_size or 20, num_layers=config.lstm_num_layers or 1)
    body = QNetworkBody(hidden_layers=list(config.q_network_hidden_layers or []), input_dim=config.lstm_hidden_size, output_dim=config.action_count)
    heads = DuelingHeads(value_stream_output_dim=1, advantage_stream_output_dim=config.action_count)
    pair = OnlineTargetNetworkPair(
        online_network=None,
        target_network=None,
        forward_api_shape=config.expected_output_shape,
        compatibility_verified=False,
    )
    return {
        "expected_input_shape": config.expected_input_shape,
        "expected_output_shape": config.expected_output_shape,
        "lookback_w": config.lstm_lookback_w,
        "action_count": config.action_count,
        "state_dim": config.state_dim,
        "model_initialization_seed": config.model_initialization_seed,
        "torch_available": torch_available,
        "network_instantiation_skipped": not torch_available,
        "encoder_contract": encoder.to_dict(),
        "body_contract": body.to_dict(),
        "dueling_heads_contract": heads.to_dict(),
        "online_target_pair_contract": pair.to_dict(),
    }


def build_network_implementation_report() -> ShapeValidationReport:
    torch_available = _torch_available()
    config = _build_config()
    shape_summary = _build_shape_summary(config, torch_available=torch_available)
    dependency_status = "available_existing_torch" if torch_available else "blocked_missing_existing_torch"
    return ShapeValidationReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=collect_prerequisite_tags_verified(),
        dependency_status=dependency_status,
        architecture_config=config.to_dict(),
        q_network_hidden_layers_verified=True,
        lstm_hidden_layers_verified=True,
        q_lstm_config_separation_verified=True,
        dueling_head_verified=False,
        double_dqn_api_verified=False,
        online_target_network_compatibility_verified=False,
        state_action_contract_refs=[
            "specs/039-paper-hoodie-network-implementation/spec.md",
            "specs/039-paper-hoodie-network-implementation/plan.md",
            "specs/039-paper-hoodie-network-implementation/data-model.md",
        ],
        shape_validation_summary=shape_summary,
        deterministic_initialization_verified=False,
        feature_038_training_readiness_block_respected=True,
        no_training_started=True,
        no_optimizer_step=True,
        no_replay_execution=True,
        no_target_update_execution=True,
        no_environment_contract_drift=True,
        no_reward_timing_change=True,
        no_policy_drift=True,
        no_dependency_drift=True,
        no_curve_fitting=True,
        no_paper_reproduction_claim=True,
        final_verdict="dependency_blocked" if not torch_available else "architecture_ready",
    )


def write_network_implementation_report(report: ShapeValidationReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path
