from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/deadline-timeout-off-by-one-audit")
JSON_FILENAME = "deadline-timeout-off-by-one-report.json"
MARKDOWN_FILENAME = "deadline-timeout-off-by-one-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class DeadlineTimeoutOffByOneAuditReport:
    feature_id: str
    timeout_slots: int
    slot_duration_seconds: float
    timeout_seconds: float
    deadline_contract: str
    old_runtime_behavior: str
    contradiction_detected: bool
    repaired_runtime_components: list[str]
    validated_runtime_components: list[str]
    boundary_cases_validated: list[str]
    tests_added: list[str]
    tests_run: list[str]
    no_paper_recovery_claims: bool
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_reward_timing_change: bool
    no_execution_time_contract_drift: bool
    no_transmission_delay_contract_drift: bool
    no_capacity_sharing_contract_drift: bool
    no_campaign_rerun: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "timeout_slots": self.timeout_slots,
            "slot_duration_seconds": self.slot_duration_seconds,
            "timeout_seconds": self.timeout_seconds,
            "deadline_contract": self.deadline_contract,
            "old_runtime_behavior": self.old_runtime_behavior,
            "contradiction_detected": self.contradiction_detected,
            "repaired_runtime_components": list(self.repaired_runtime_components),
            "validated_runtime_components": list(self.validated_runtime_components),
            "boundary_cases_validated": list(self.boundary_cases_validated),
            "tests_added": list(self.tests_added),
            "tests_run": list(self.tests_run),
            "no_paper_recovery_claims": self.no_paper_recovery_claims,
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_execution_time_contract_drift": self.no_execution_time_contract_drift,
            "no_transmission_delay_contract_drift": self.no_transmission_delay_contract_drift,
            "no_capacity_sharing_contract_drift": self.no_capacity_sharing_contract_drift,
            "no_campaign_rerun": self.no_campaign_rerun,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Deadline/Timeout Off-by-One Audit Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- timeout_slots: `{self.timeout_slots}`",
            f"- slot_duration_seconds: `{self.slot_duration_seconds}`",
            f"- timeout_seconds: `{self.timeout_seconds}`",
            f"- contradiction_detected: `{self.contradiction_detected}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_paper_recovery_claims: `{self.no_paper_recovery_claims}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_execution_time_contract_drift: `{self.no_execution_time_contract_drift}`",
            f"- no_transmission_delay_contract_drift: `{self.no_transmission_delay_contract_drift}`",
            f"- no_capacity_sharing_contract_drift: `{self.no_capacity_sharing_contract_drift}`",
            f"- no_campaign_rerun: `{self.no_campaign_rerun}`",
            "",
            "## Deadline Contract",
            self.deadline_contract,
            "",
            "## Old Runtime Behavior",
            self.old_runtime_behavior,
            "",
            "## Repaired Runtime Components",
        ]
        lines.extend(f"- `{item}`" for item in self.repaired_runtime_components)
        lines.extend(["", "## Validated Runtime Components"])
        lines.extend(f"- `{item}`" for item in self.validated_runtime_components)
        lines.extend(["", "## Boundary Cases Validated"])
        lines.extend(f"- `{item}`" for item in self.boundary_cases_validated)
        lines.extend(["", "## Tests Added"])
        lines.extend(f"- `{item}`" for item in self.tests_added)
        lines.extend(["", "## Tests Run"])
        lines.extend(f"- `{item}`" for item in self.tests_run)
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        md_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        md_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, md_path


def build_deadline_timeout_off_by_one_audit_report() -> DeadlineTimeoutOffByOneAuditReport:
    return DeadlineTimeoutOffByOneAuditReport(
        feature_id="036-deadline-timeout-off-by-one-audit",
        timeout_slots=20,
        slot_duration_seconds=0.1,
        timeout_seconds=2.0,
        deadline_contract=(
            "absolute_deadline_slot = arrival_slot + timeout_slots; completion_slot <= absolute_deadline_slot is completed; completion_slot > absolute_deadline_slot is dropped; exact-boundary completion is accepted."
        ),
        old_runtime_behavior=(
            "deadline_rules.has_expired previously returned True for current_slot >= absolute_deadline_slot, which incorrectly treated exact-boundary current_slot == absolute_deadline_slot as expired."
        ),
        contradiction_detected=True,
        repaired_runtime_components=[
            "src/environment/deadline_rules.py",
        ],
        validated_runtime_components=[
            "src/environment/runtime_model.py",
            "src/environment/environment.py",
            "src/environment/gym_adapter.py",
            "src/environment/traffic_config.py",
        ],
        boundary_cases_validated=[
            "current_slot < absolute_deadline_slot -> not expired",
            "current_slot == absolute_deadline_slot -> not expired",
            "current_slot > absolute_deadline_slot -> expired",
            "completion_slot == absolute_deadline_slot -> completed",
            "completion_slot == absolute_deadline_slot + 1 -> dropped",
            "arrival_slot = 5, timeout_slots = 20, absolute_deadline_slot = 25, completion_slot = 25 -> completed",
        ],
        tests_added=[
            "test_task_not_expired_before_deadline",
            "test_task_not_expired_at_deadline",
            "test_task_expires_after_deadline",
            "test_completion_at_deadline_is_completed",
            "test_completion_after_deadline_is_dropped",
            "test_nonzero_arrival_exact_deadline_boundary",
            "test_environment_exact_deadline_completion_not_dropped",
            "test_reward_emitted_only_after_terminal_completion_drop",
            "test_drop_penalty_only_after_deadline_drop",
            "test_feature_033_execution_contract_not_changed",
            "test_feature_034_transmission_delay_contract_not_changed",
            "test_feature_035_capacity_sharing_contract_not_changed",
            "test_scope_guard_no_training_policy_dependency_campaign_drift",
        ],
        tests_run=[
            "tests.unit.test_deadline_rules",
            "tests.unit.test_timeout_boundary_contract",
            "tests.integration.test_deadline_timeout_off_by_one_audit",
            "tests.integration.test_deadline_timeout_off_by_one_report",
            "tests.integration.test_deadline_timeout_off_by_one_scope_guard",
            "tests.integration.test_execution_time_flow",
            "tests.integration.test_transmission_delay_runtime_wiring",
            "tests.integration.test_public_cloud_capacity_sharing_flow",
            "tests.integration.test_mechanism_repair_timeout_drop",
        ],
        no_paper_recovery_claims=True,
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_reward_timing_change=True,
        no_execution_time_contract_drift=True,
        no_transmission_delay_contract_drift=True,
        no_capacity_sharing_contract_drift=True,
        no_campaign_rerun=True,
        final_verdict="deadline_timeout_boundary_repaired",
    )


def write_deadline_timeout_off_by_one_audit_report(
    report: DeadlineTimeoutOffByOneAuditReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)

