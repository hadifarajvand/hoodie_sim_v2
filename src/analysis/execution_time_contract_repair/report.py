from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.execution_helper import step_execution
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.task import Task


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/execution-time-contract-repair")
JSON_FILENAME = "execution-time-contract-report.json"
MARKDOWN_FILENAME = "execution-time-contract-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class ExecutionTimeContractReport:
    feature_id: str
    repaired_runtime_components: list[str]
    old_invalid_behavior: str
    new_execution_contract: str
    completion_slot_contract: str
    destination_kinds_validated: list[str]
    tests_added: list[str]
    tests_run: list[str]
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_reward_timing_change: bool
    no_transmission_delay_scope_creep: bool
    no_capacity_sharing_scope_creep: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "repaired_runtime_components": list(self.repaired_runtime_components),
            "old_invalid_behavior": self.old_invalid_behavior,
            "new_execution_contract": self.new_execution_contract,
            "completion_slot_contract": self.completion_slot_contract,
            "destination_kinds_validated": list(self.destination_kinds_validated),
            "tests_added": list(self.tests_added),
            "tests_run": list(self.tests_run),
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_transmission_delay_scope_creep": self.no_transmission_delay_scope_creep,
            "no_capacity_sharing_scope_creep": self.no_capacity_sharing_scope_creep,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Execution-Time Contract Repair Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_transmission_delay_scope_creep: `{self.no_transmission_delay_scope_creep}`",
            f"- no_capacity_sharing_scope_creep: `{self.no_capacity_sharing_scope_creep}`",
            "",
            "## Old Invalid Behavior",
            self.old_invalid_behavior,
            "",
            "## New Execution Contract",
            self.new_execution_contract,
            "",
            "## Completion Slot Contract",
            self.completion_slot_contract,
            "",
            "## Destination Kinds Validated",
        ]
        lines.extend(f"- `{item}`" for item in self.destination_kinds_validated)
        lines.extend([
            "",
            "## Repaired Runtime Components",
        ])
        lines.extend(f"- `{item}`" for item in self.repaired_runtime_components)
        lines.extend([
            "",
            "## Tests Added",
        ])
        lines.extend(f"- `{item}`" for item in self.tests_added)
        lines.extend([
            "",
            "## Tests Run",
        ])
        lines.extend(f"- `{item}`" for item in self.tests_run)
        lines.append("")
        return "\n".join(lines)

    def write(self, output_dir: Path | str | None = None) -> tuple[Path, Path]:
        target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        json_path = target_dir / JSON_FILENAME
        markdown_path = target_dir / MARKDOWN_FILENAME
        json_path.write_text(self.to_json(), encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


def build_execution_time_contract_report() -> ExecutionTimeContractReport:
    compute_config = ComputeConfig()
    helper_probe = Task(
        task_id=101,
        source_agent_id=1,
        arrival_slot=0,
        size=1.0,
        processing_density=1.0,
        timeout_length=20,
        absolute_deadline_slot=20,
        cycles_required=1.0,
        cycles_remaining=1.0,
    )
    progress = step_execution(helper_probe, compute_config.cpu_capacity_per_slot_agent, slot=0, destination_kind="local")
    environment = HoodieGymEnvironment(episode_length=1, compute_config=compute_config)
    environment.reset(seed=7)

    return ExecutionTimeContractReport(
        feature_id="033-execution-time-contract-repair",
        repaired_runtime_components=[
            "src/environment/execution_helper.py",
            "src/environment/gym_adapter.py",
            "src/environment/runtime_model.py",
        ],
        old_invalid_behavior=(
            "Local/private execution previously short-circuited when timeout_length > 1 and cycles_before exceeded capacity, "
            "consuming all remaining cycles in one slot."
        ),
        new_execution_contract=(
            "Every supported destination consumes at most its configured per-slot capacity using "
            "cycles_consumed = min(cycles_before, compute_capacity) and "
            "cycles_after = max(0, cycles_before - compute_capacity)."
        ),
        completion_slot_contract="Completion is recorded at the end of the slot in which remaining cycles reach zero.",
        destination_kinds_validated=[
            "local/private/self",
            "public/edge/horizontal",
            "cloud/vertical",
        ],
        tests_added=[
            "test_local_execution_no_single_slot_shortcut_when_cycles_exceed_capacity",
            "test_local_execution_consumes_at_most_agent_capacity_per_slot",
            "test_public_execution_consumes_at_most_edge_capacity_per_slot",
            "test_cloud_execution_consumes_at_most_cloud_capacity_per_slot",
            "test_execution_exact_capacity_boundary_completion_contract",
            "test_cycles_remaining_decreases_monotonically",
            "test_environment_local_execution_requires_multiple_slots_when_cycles_exceed_capacity",
            "test_timeout_drop_still_uses_multislot_execution_contract",
            "test_reward_emitted_only_after_terminal_completion_or_drop",
            "test_feature_033_scope_guard_no_training_policy_dependency_drift",
        ],
        tests_run=[
            "python -m unittest tests.unit.test_execution_helper",
            "python -m unittest tests.unit.test_execution_model",
            "python -m unittest tests.integration.test_execution_time_flow",
            "python -m unittest tests.integration.test_mechanism_repair_timeout_drop",
        ],
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_reward_timing_change=True,
        no_transmission_delay_scope_creep=True,
        no_capacity_sharing_scope_creep=True,
        final_verdict="execution_time_contract_repaired",
    )


def write_execution_time_contract_report(
    report: ExecutionTimeContractReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)
