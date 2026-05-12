from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/public-cloud-queue-capacity-sharing")
JSON_FILENAME = "public-cloud-capacity-sharing-report.json"
MARKDOWN_FILENAME = "public-cloud-capacity-sharing-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class PublicCloudQueueCapacitySharingReport:
    feature_id: str
    old_invalid_behavior: str
    new_capacity_sharing_contract: str
    sharing_rule: str
    redistribution_policy: str
    wired_runtime_components: list[str]
    validated_runtime_components: list[str]
    destination_kinds_validated: list[str]
    tests_added: list[str]
    tests_run: list[str]
    no_paper_recovery_claims: bool
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_reward_timing_change: bool
    no_execution_time_contract_drift: bool
    no_transmission_delay_contract_drift: bool
    no_campaign_rerun: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "old_invalid_behavior": self.old_invalid_behavior,
            "new_capacity_sharing_contract": self.new_capacity_sharing_contract,
            "sharing_rule": self.sharing_rule,
            "redistribution_policy": self.redistribution_policy,
            "wired_runtime_components": list(self.wired_runtime_components),
            "validated_runtime_components": list(self.validated_runtime_components),
            "destination_kinds_validated": list(self.destination_kinds_validated),
            "tests_added": list(self.tests_added),
            "tests_run": list(self.tests_run),
            "no_paper_recovery_claims": self.no_paper_recovery_claims,
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_execution_time_contract_drift": self.no_execution_time_contract_drift,
            "no_transmission_delay_contract_drift": self.no_transmission_delay_contract_drift,
            "no_campaign_rerun": self.no_campaign_rerun,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Public/Cloud Queue Capacity Sharing Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- sharing_rule: `{self.sharing_rule}`",
            f"- redistribution_policy: `{self.redistribution_policy}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_paper_recovery_claims: `{self.no_paper_recovery_claims}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_execution_time_contract_drift: `{self.no_execution_time_contract_drift}`",
            f"- no_transmission_delay_contract_drift: `{self.no_transmission_delay_contract_drift}`",
            f"- no_campaign_rerun: `{self.no_campaign_rerun}`",
            "",
            "## Old Invalid Behavior",
            self.old_invalid_behavior,
            "",
            "## New Capacity Sharing Contract",
            self.new_capacity_sharing_contract,
            "",
            "## Wired Runtime Components",
        ]
        lines.extend(f"- `{item}`" for item in self.wired_runtime_components)
        lines.extend(["", "## Validated Runtime Components"])
        lines.extend(f"- `{item}`" for item in self.validated_runtime_components)
        lines.extend(["", "## Destination Kinds Validated"])
        lines.extend(f"- `{item}`" for item in self.destination_kinds_validated)
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


def build_public_cloud_queue_capacity_sharing_report() -> PublicCloudQueueCapacitySharingReport:
    return PublicCloudQueueCapacitySharingReport(
        feature_id="035-public-cloud-queue-capacity-sharing-contract",
        old_invalid_behavior=(
            "Each public/cloud queue previously received the full host capacity independently, so multiple active heads could silently multiply the configured per-slot CPU budget."
        ),
        new_capacity_sharing_contract=(
            "Public EA heads are grouped by destination host_node_id and cloud heads are grouped under host_node_id == \"cloud\"; each host pool splits its fixed per-slot CPU capacity equally across the active heads present at slot start."
        ),
        sharing_rule="deterministic_equal_share_at_slot_start",
        redistribution_policy="no_same_slot_redistribution",
        wired_runtime_components=[
            "src/environment/gym_adapter.py",
        ],
        validated_runtime_components=[
            "src/environment/public_queue.py",
            "src/environment/offloading_queue.py",
            "src/environment/compute_config.py",
            "src/environment/execution_helper.py",
            "src/environment/link_rate_config.py",
        ],
        destination_kinds_validated=["public", "cloud", "local"],
        tests_added=[
            "test_single_public_queue_gets_full_edge_capacity",
            "test_two_public_queues_same_host_share_edge_capacity_equally",
            "test_two_public_queues_different_hosts_do_not_share_capacity",
            "test_two_cloud_queues_share_global_cloud_capacity_equally",
            "test_total_public_host_consumption_does_not_exceed_edge_capacity",
            "test_total_cloud_consumption_does_not_exceed_cloud_capacity",
            "test_capacity_sharing_order_is_deterministic",
            "test_local_private_execution_not_changed",
            "test_feature_033_execution_contract_not_changed",
            "test_feature_034_transmission_delay_contract_not_changed",
            "test_reward_timing_not_changed",
            "test_scope_guard_no_training_policy_dependency_campaign_drift",
        ],
        tests_run=[
            "tests.integration.test_public_cloud_capacity_sharing_flow",
            "tests.integration.test_public_cloud_capacity_sharing_report",
            "tests.integration.test_public_cloud_capacity_sharing_scope_guard",
            "tests.integration.test_execution_time_flow",
            "tests.integration.test_transmission_delay_runtime_wiring",
        ],
        no_paper_recovery_claims=True,
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_reward_timing_change=True,
        no_execution_time_contract_drift=True,
        no_transmission_delay_contract_drift=True,
        no_campaign_rerun=True,
        final_verdict="public_cloud_capacity_sharing_wired",
    )


def write_public_cloud_queue_capacity_sharing_report(
    report: PublicCloudQueueCapacitySharingReport,
    output_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    return report.write(output_dir)

