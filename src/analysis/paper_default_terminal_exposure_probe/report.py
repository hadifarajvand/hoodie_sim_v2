from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

FEATURE_ID = "042-paper-default-terminal-exposure-probe"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/paper-default-terminal-exposure-probe")
JSON_FILENAME = "terminal-exposure-report.json"
MARKDOWN_FILENAME = "terminal-exposure-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _git_status_short(*args: str) -> str:
    result = subprocess.run(["git", "status", "--short", *args], check=True, capture_output=True, text=True)
    return result.stdout


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


def build_prerequisite_tags_verified() -> list[dict[str, Any]]:
    pointer = _read_feature_pointer()
    diff_main_head = _git_output("diff", "--name-only", "main...HEAD").splitlines()
    checks = [
        ("branch", _git_output("branch", "--show-current") == FEATURE_ID, "git branch --show-current == 042-paper-default-terminal-exposure-probe"),
        ("not_main", _git_output("branch", "--show-current") != "main", "current branch != main"),
        ("main_equals_origin_main", _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "main == origin/main"),
        ("main_equals_feature_041", _git_output("rev-parse", "main") == _git_output("rev-parse", "041-full-training-reproduction-campaign-complete^{}"), "main == 041-full-training-reproduction-campaign-complete^{}"),
        ("prerequisite_diff_empty", _git_output("diff", "--name-only", "041-full-training-reproduction-campaign-complete^{}", "main") == "", "diff between 041-full-training-reproduction-campaign-complete^{} and main is empty"),
        ("pointer_matches_feature", pointer == "specs/042-paper-default-terminal-exposure-probe", ".specify/feature.json points to specs/042-paper-default-terminal-exposure-probe"),
        ("pointer_not_staged", ".specify/feature.json" not in _git_status_short("--", ".specify/feature.json"), ".specify/feature.json must not be staged"),
        ("pointer_not_in_main_head", ".specify/feature.json" not in diff_main_head, ".specify/feature.json must not appear in git diff --name-only main...HEAD"),
    ]
    return [{"name": name, "verified": bool(verified), "details": details} for name, verified, details in checks]


def collect_prior_feature_gates_verified() -> list[dict[str, Any]]:
    features = [
        ("037", "baseline revalidation", "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json"),
        ("038", "training foundation", "artifacts/analysis/training-foundation-contract/training-foundation-report.json"),
        ("039", "paper HOODIE network", "artifacts/analysis/paper-hoodie-network-implementation/network-implementation-report.json"),
        ("040", "smoke training", "artifacts/analysis/smoke-training/smoke-training-report.json"),
        ("041", "full-training campaign gate", "artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json"),
    ]
    return [
        {"feature": feature, "name": name, "verified": Path(path).exists(), "details": f"{path} exists"}
        for feature, name, path in features
    ]


@dataclass(slots=True)
class TerminalExposureReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    probe_config: dict[str, Any]
    probe_strategies: list[str]
    per_strategy_results: list[dict[str, Any]]
    aggregate_terminal_exposure_summary: dict[str, Any]
    reward_timing_contract_verified: bool
    pending_at_horizon_contract_verified: bool
    legal_action_mask_verified: bool
    runtime_contracts_verified: dict[str, Any]
    diagnosis: str
    recommended_next_feature: str | None
    no_training_started: bool
    no_optimizer_step: bool
    no_replay_training: bool
    no_target_update_execution: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool
    no_curve_fitting: bool
    no_simulator_output_tuning: bool
    no_paper_reproduction_claim: bool
    final_verdict: str
    no_unrelated_dirty_files: bool | None = None

    def __post_init__(self) -> None:
        required_flags = {
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
        }
        for name, value in required_flags.items():
            if value is not True:
                raise ValueError(f"TerminalExposureReport.{name} must be true.")
        if self.final_verdict not in {
            "terminal_exposure_present",
            "terminal_exposure_absent_under_paper_default",
            "probe_failed_runtime_error",
            "prerequisite_blocked",
        }:
            raise ValueError("TerminalExposureReport.final_verdict has an invalid value.")
        if not self.diagnosis:
            raise ValueError("TerminalExposureReport.diagnosis is required.")
        if self.final_verdict == "terminal_exposure_absent_under_paper_default" and not self.recommended_next_feature:
            raise ValueError("TerminalExposureReport.recommended_next_feature is required when terminal exposure is absent.")

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "probe_config": dict(self.probe_config),
            "probe_strategies": list(self.probe_strategies),
            "per_strategy_results": list(self.per_strategy_results),
            "aggregate_terminal_exposure_summary": dict(self.aggregate_terminal_exposure_summary),
            "reward_timing_contract_verified": self.reward_timing_contract_verified,
            "pending_at_horizon_contract_verified": self.pending_at_horizon_contract_verified,
            "legal_action_mask_verified": self.legal_action_mask_verified,
            "runtime_contracts_verified": dict(self.runtime_contracts_verified),
            "diagnosis": self.diagnosis,
            "recommended_next_feature": self.recommended_next_feature,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }
        if self.no_unrelated_dirty_files is not None:
            payload["no_unrelated_dirty_files"] = self.no_unrelated_dirty_files
        return payload

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Terminal Exposure Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- diagnosis: `{payload['diagnosis']}`",
            f"- recommended_next_feature: `{payload['recommended_next_feature']}`",
            "",
            "## Audit Flags",
        ]
        for key in (
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            lines.append(f"- **{key}**: `{payload[key]}`")
        lines.extend([
            "",
            "## Aggregate Summary",
            _json_dump(payload["aggregate_terminal_exposure_summary"]).strip(),
            "",
            "## Per-Strategy Results",
            _json_dump(payload["per_strategy_results"]).strip(),
            "",
            "## Prerequisite Checks",
        ])
        for check in payload["prerequisite_tags_verified"]:
            lines.append(f"- **{check['name']}**: {check['verified']} ({check['details']})")
        return "\n".join(lines)


def write_terminal_exposure_report(report: TerminalExposureReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path
