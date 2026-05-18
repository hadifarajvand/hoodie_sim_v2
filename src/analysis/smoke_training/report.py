from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

FEATURE_ID = "040-smoke-training"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/smoke-training")
JSON_FILENAME = "smoke-training-report.json"
MARKDOWN_FILENAME = "smoke-training-report.md"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


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


def build_smoke_training_prerequisite_tags_verified() -> list[dict[str, Any]]:
    pointer = _read_feature_pointer()
    cached_pointer_status = _git_output("diff", "--cached", "--name-only", "--", ".specify/feature.json")
    diff_main_head = _git_output("diff", "--name-only", "main...HEAD").splitlines()
    current_branch = _git_output("branch", "--show-current")
    checks = [
        ("branch", current_branch == FEATURE_ID, f"git branch --show-current == {FEATURE_ID}"),
        ("not_main", current_branch != "main", "current branch != main"),
        ("main_equals_origin_main", _git_output("rev-parse", "main") == _git_output("rev-parse", "origin/main"), "main == origin/main"),
        ("main_equals_feature_039", _git_output("rev-parse", "main") == _git_output("rev-parse", "039-paper-hoodie-network-implementation-complete^{}"), "main == 039-paper-hoodie-network-implementation-complete^{}"),
        ("prerequisite_diff_empty", _git_output("diff", "--name-only", "039-paper-hoodie-network-implementation-complete^{}", "main") == "", "diff between 039-paper-hoodie-network-implementation-complete^{} and main is empty"),
        ("feature_dir_exists", (Path("specs") / FEATURE_ID).exists(), "specs/040-smoke-training/ exists"),
        ("pointer_matches_feature", pointer == "specs/040-smoke-training", ".specify/feature.json points to specs/040-smoke-training"),
        ("pointer_not_staged", cached_pointer_status == "", ".specify/feature.json must not be staged"),
        ("pointer_not_in_main_head", ".specify/feature.json" not in diff_main_head, ".specify/feature.json must not appear in git diff --name-only main...HEAD"),
    ]
    return [{"name": name, "verified": bool(verified), "details": details} for name, verified, details in checks]


@dataclass(slots=True)
class SmokeTrainingReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    smoke_scope: dict[str, Any]
    dependency_status: str
    network_contract_verified: dict[str, Any]
    replay_contract_verified: dict[str, Any]
    delayed_reward_contract_verified: dict[str, Any]
    seed_protocol_verified: dict[str, Any]
    smoke_batch_summary: dict[str, Any]
    optimizer_step_summary: dict[str, Any]
    loss_summary: dict[str, Any]
    parameter_update_summary: dict[str, Any]
    deterministic_repeatability_verified: dict[str, Any]
    target_update_blocked_reason: str
    feature_038_training_readiness_block_respected: bool
    no_paper_reproduction_claim: bool
    no_curve_fitting: bool
    no_full_training: bool
    no_campaign_execution: bool
    no_baseline_comparison: bool
    no_target_update_execution: bool
    no_dependency_drift: bool
    no_environment_contract_drift: bool
    no_policy_drift: bool
    no_reward_timing_change: bool
    final_verdict: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "smoke_scope": dict(self.smoke_scope),
            "dependency_status": self.dependency_status,
            "network_contract_verified": dict(self.network_contract_verified),
            "replay_contract_verified": dict(self.replay_contract_verified),
            "delayed_reward_contract_verified": dict(self.delayed_reward_contract_verified),
            "seed_protocol_verified": dict(self.seed_protocol_verified),
            "smoke_batch_summary": dict(self.smoke_batch_summary),
            "optimizer_step_summary": dict(self.optimizer_step_summary),
            "loss_summary": dict(self.loss_summary),
            "parameter_update_summary": dict(self.parameter_update_summary),
            "deterministic_repeatability_verified": dict(self.deterministic_repeatability_verified),
            "target_update_blocked_reason": self.target_update_blocked_reason,
            "feature_038_training_readiness_block_respected": self.feature_038_training_readiness_block_respected,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "no_curve_fitting": self.no_curve_fitting,
            "no_full_training": self.no_full_training,
            "no_campaign_execution": self.no_campaign_execution,
            "no_baseline_comparison": self.no_baseline_comparison,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "final_verdict": self.final_verdict,
        }

    def to_markdown(self) -> str:
        payload = self.to_dict()
        lines = [
            "# Smoke Training Report",
            "",
            f"- feature_id: `{payload['feature_id']}`",
            f"- dependency_status: `{payload['dependency_status']}`",
            f"- final_verdict: `{payload['final_verdict']}`",
            f"- no_paper_reproduction_claim: `{payload['no_paper_reproduction_claim']}`",
            f"- no_curve_fitting: `{payload['no_curve_fitting']}`",
            f"- no_full_training: `{payload['no_full_training']}`",
            f"- no_campaign_execution: `{payload['no_campaign_execution']}`",
            f"- no_baseline_comparison: `{payload['no_baseline_comparison']}`",
            f"- no_target_update_execution: `{payload['no_target_update_execution']}`",
            f"- no_dependency_drift: `{payload['no_dependency_drift']}`",
            f"- no_environment_contract_drift: `{payload['no_environment_contract_drift']}`",
            f"- no_policy_drift: `{payload['no_policy_drift']}`",
            f"- no_reward_timing_change: `{payload['no_reward_timing_change']}`",
            "",
            "## Smoke Scope",
            _json_dump(payload["smoke_scope"]).strip(),
            "",
            "## Smoke Batch Summary",
            _json_dump(payload["smoke_batch_summary"]).strip(),
            "",
            "## Optimizer Step Summary",
            _json_dump(payload["optimizer_step_summary"]).strip(),
            "",
            "## Loss Summary",
            _json_dump(payload["loss_summary"]).strip(),
            "",
            "## Parameter Update Summary",
            _json_dump(payload["parameter_update_summary"]).strip(),
            "",
            "## Deterministic Repeatability",
            _json_dump(payload["deterministic_repeatability_verified"]).strip(),
            "",
            "## Prerequisite Checks",
        ]
        for check in payload["prerequisite_tags_verified"]:
            lines.append(f"- **{check['name']}**: {check['verified']} ({check['details']})")
        lines.extend(
            [
                "",
                "## Contract Checks",
                f"- **network_contract_verified**: {payload['network_contract_verified']}",
                f"- **replay_contract_verified**: {payload['replay_contract_verified']}",
                f"- **delayed_reward_contract_verified**: {payload['delayed_reward_contract_verified']}",
                f"- **seed_protocol_verified**: {payload['seed_protocol_verified']}",
                f"- **target_update_blocked_reason**: {payload['target_update_blocked_reason']}",
                "",
            ]
        )
        return "\n".join(lines)


def write_smoke_training_report(report: SmokeTrainingReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")
    return json_path, markdown_path
