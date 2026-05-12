from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/transmission-delay-runtime-wiring")
JSON_FILENAME = "transmission-delay-runtime-report.json"
MARKDOWN_FILENAME = "transmission-delay-runtime-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class TransmissionDelayRuntimeWiringReport:
    feature_id: str
    wired_runtime_components: list[str]
    validated_runtime_components: list[str]
    old_invalid_behavior: str
    new_transmission_contract: str
    horizontal_rate_mbps: float
    vertical_rate_mbps: float
    slot_duration_seconds: float
    rounding_policy: str
    admission_boundary_contract: str
    transmission_metadata_fields: list[str]
    tests_added: list[str]
    tests_run: list[str]
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_reward_timing_change: bool
    no_execution_time_contract_drift: bool
    no_capacity_sharing_scope_creep: bool
    no_campaign_rerun: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "wired_runtime_components": list(self.wired_runtime_components),
            "validated_runtime_components": list(self.validated_runtime_components),
            "old_invalid_behavior": self.old_invalid_behavior,
            "new_transmission_contract": self.new_transmission_contract,
            "horizontal_rate_mbps": self.horizontal_rate_mbps,
            "vertical_rate_mbps": self.vertical_rate_mbps,
            "slot_duration_seconds": self.slot_duration_seconds,
            "rounding_policy": self.rounding_policy,
            "admission_boundary_contract": self.admission_boundary_contract,
            "transmission_metadata_fields": list(self.transmission_metadata_fields),
            "tests_added": list(self.tests_added),
            "tests_run": list(self.tests_run),
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_execution_time_contract_drift": self.no_execution_time_contract_drift,
            "no_capacity_sharing_scope_creep": self.no_capacity_sharing_scope_creep,
            "no_campaign_rerun": self.no_campaign_rerun,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Transmission Delay Runtime Wiring Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- horizontal_rate_mbps: `{self.horizontal_rate_mbps}`",
            f"- vertical_rate_mbps: `{self.vertical_rate_mbps}`",
            f"- slot_duration_seconds: `{self.slot_duration_seconds}`",
            f"- rounding_policy: `{self.rounding_policy}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_execution_time_contract_drift: `{self.no_execution_time_contract_drift}`",
            f"- no_capacity_sharing_scope_creep: `{self.no_capacity_sharing_scope_creep}`",
            f"- no_campaign_rerun: `{self.no_campaign_rerun}`",
            "",
            "## Old Invalid Behavior",
            self.old_invalid_behavior,
            "",
            "## New Transmission Contract",
            self.new_transmission_contract,
            "",
            "## Admission Boundary Contract",
            self.admission_boundary_contract,
            "",
            "## Transmission Metadata Fields",
        ]
        lines.extend(f"- `{item}`" for item in self.transmission_metadata_fields)
        lines.extend(
            [
                "",
                "## Wired Runtime Components",
            ]
        )
        lines.extend(f"- `{item}`" for item in self.wired_runtime_components)
        lines.extend(
            [
                "",
                "## Validated Runtime Components",
            ]
        )
        lines.extend(f"- `{item}`" for item in self.validated_runtime_components)
        lines.extend(
            [
                "",
                "## Tests Added",
            ]
        )
        lines.extend(f"- `{item}`" for item in self.tests_added)
        lines.extend(
            [
                "",
                "## Tests Run",
            ]
        )
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


def build_transmission_delay_runtime_wiring_report() -> TransmissionDelayRuntimeWiringReport:
    return TransmissionDelayRuntimeWiringReport(
        feature_id="034-transmission-delay-runtime-wiring",
        wired_runtime_components=[
            "src/environment/gym_adapter.py",
            "src/environment/slot_engine.py",
        ],
        validated_runtime_components=[
            "src/environment/offloading_queue.py",
            "src/environment/link_rate_config.py",
            "src/environment/runtime_model.py",
        ],
        old_invalid_behavior=(
            "Offload admission previously occurred after a fixed one-slot queue hop, ignoring payload size, link rate, and the computed transmission boundary."
        ),
        new_transmission_contract=(
            "Horizontal and vertical offloads compute transmission delay from payload bits, the configured link rate, slot duration, and the active rounding policy; "
            "admission occurs only when current_slot >= transmission_started_at + transmission_delay_slots."
        ),
        horizontal_rate_mbps=30.0,
        vertical_rate_mbps=10.0,
        slot_duration_seconds=0.1,
        rounding_policy="ceil",
        admission_boundary_contract=(
            "If transmission starts at slot s and delay_slots is d, the task is admitted when current_slot >= s + d. "
            "The stored metadata records both the start and completion slots, and local tasks do not carry transmission metadata."
        ),
        transmission_metadata_fields=[
            "transmission_started_at",
            "transmission_completed_at",
            "transmission_delay_slots",
            "transmission_delay_seconds",
            "transmission_payload_bits",
            "transmission_data_rate_bps",
            "transmission_rate_source",
            "transmission_rounding_policy",
        ],
        tests_added=[
            "test_horizontal_transmission_delay_uses_task_size_and_RH",
            "test_vertical_transmission_delay_uses_task_size_and_RV",
            "test_vertical_delay_exceeds_horizontal_delay_for_same_payload",
            "test_offload_not_admitted_before_delay_boundary",
            "test_offload_admitted_at_documented_boundary",
            "test_horizontal_metadata_recorded",
            "test_vertical_metadata_recorded",
            "test_local_path_has_no_transmission_metadata",
            "test_reward_not_emitted_during_transmission",
            "test_timeout_drop_includes_transmission_delay",
            "test_no_feature_033_execution_contract_drift",
            "test_no_dependency_training_policy_campaign_drift",
        ],
        tests_run=[
            "tests.unit.test_link_rate_config",
            "tests.integration.test_transmission_delay_runtime_wiring",
            "tests.integration.test_execution_time_flow",
            "tests.integration.test_mechanism_repair_timeout_drop",
            "tests.integration.test_transmission_delay_runtime_report",
            "tests.integration.test_transmission_delay_runtime_scope_guard",
        ],
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_reward_timing_change=True,
        no_execution_time_contract_drift=True,
        no_capacity_sharing_scope_creep=True,
        no_campaign_rerun=True,
        final_verdict="transmission_delay_runtime_wired",
    )


def write_transmission_delay_runtime_wiring_report(
    report: TransmissionDelayRuntimeWiringReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)
