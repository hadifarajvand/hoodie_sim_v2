from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.analysis.user_approved_assumption_patch_registry.registry import build_user_approved_assumption_registry

from .runner import load_runtime_adoption_contracts


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/runtime-adoption-approved-assumption-registry")
JSON_FILENAME = "runtime-adoption-report.json"
MARKDOWN_FILENAME = "runtime-adoption-report.md"


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class RuntimeAdoptionReport:
    feature_id: str
    consumed_assumption_ids: list[str]
    runtime_components_changed: list[str]
    runtime_components_validated: list[str]
    tests_added: list[str]
    tests_run: list[str]
    old_stale_values_detected_or_replaced: list[str]
    no_paper_recovery_claims: bool
    no_dependency_drift: bool
    no_training_or_policy_drift: bool
    no_reward_timing_change: bool
    no_campaign_rerun: bool
    final_verdict: str

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "consumed_assumption_ids": list(self.consumed_assumption_ids),
            "runtime_components_changed": list(self.runtime_components_changed),
            "runtime_components_validated": list(self.runtime_components_validated),
            "tests_added": list(self.tests_added),
            "tests_run": list(self.tests_run),
            "old_stale_values_detected_or_replaced": list(self.old_stale_values_detected_or_replaced),
            "no_paper_recovery_claims": self.no_paper_recovery_claims,
            "no_dependency_drift": self.no_dependency_drift,
            "no_training_or_policy_drift": self.no_training_or_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_campaign_rerun": self.no_campaign_rerun,
            "final_verdict": self.final_verdict,
        }

    def to_json(self) -> str:
        return _json_dump(self.to_dict())

    def to_markdown(self) -> str:
        lines = [
            "# Runtime Adoption Report",
            "",
            f"- feature_id: `{self.feature_id}`",
            f"- final_verdict: `{self.final_verdict}`",
            f"- no_paper_recovery_claims: `{self.no_paper_recovery_claims}`",
            f"- no_dependency_drift: `{self.no_dependency_drift}`",
            f"- no_training_or_policy_drift: `{self.no_training_or_policy_drift}`",
            f"- no_reward_timing_change: `{self.no_reward_timing_change}`",
            f"- no_campaign_rerun: `{self.no_campaign_rerun}`",
            "",
            "## Consumed Assumptions",
        ]
        lines.extend(f"- `{item}`" for item in self.consumed_assumption_ids)
        lines.extend([
            "",
            "## Runtime Components Changed",
        ])
        lines.extend(f"- `{item}`" for item in self.runtime_components_changed)
        lines.extend([
            "",
            "## Runtime Components Validated",
        ])
        lines.extend(f"- `{item}`" for item in self.runtime_components_validated)
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
        lines.extend([
            "",
            "## Old Stale Values Replaced",
        ])
        lines.extend(f"- `{item}`" for item in self.old_stale_values_detected_or_replaced)
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


def build_runtime_adoption_report() -> RuntimeAdoptionReport:
    registry = build_user_approved_assumption_registry()
    contracts = load_runtime_adoption_contracts()
    consumed_ids = [entry["item_id"] for entry in registry["entries"]]
    _ = contracts.compute_config.cpu_capacity_per_slot_cloud
    return RuntimeAdoptionReport(
        feature_id="032-runtime-adoption-approved-assumption-registry",
        consumed_assumption_ids=consumed_ids,
        runtime_components_changed=[
            "src/environment/compute_config.py",
            "src/environment/topology.py",
            "src/environment/gym_adapter.py",
            "src/environment/link_rate_config.py",
            "src/environment/traffic_config.py",
            "src/evaluation/aggregate_metrics.py",
            "src/evaluation/runner.py",
        ],
        runtime_components_validated=[
            "Figure_7_adjacency",
            "legal_horizontal_destinations",
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "timeout_value",
            "multi_agent_aggregation_reduction_order",
        ],
        tests_added=[
            "test_compute_config_uses_approved_assumption_capacities",
            "test_topology_figure7_adjacency_invariants",
            "test_horizontal_legality_neighbor_only_no_self_no_non_neighbor",
            "test_action_mask_rejects_non_neighbor_horizontal_destinations",
            "test_vertical_cloud_action_not_constrained_by_horizontal_adjacency",
            "test_cloud_vertical_rate_uses_RV_10mbps_no_fake_cloud_rate",
            "test_timeout_contract_20_slots_2_seconds",
            "test_timeout_drop_behavior_consumes_runtime_contract",
            "test_aggregation_per_agent_episode_sum_then_mean",
            "test_aggregation_excludes_nan_no_task_omitted_slots",
            "test_feature_032_scope_guard_no_training_policy_dependency_drift",
        ],
        tests_run=[
            "python -m unittest tests.unit.test_compute_config",
            "python -m unittest tests.unit.test_runtime_adoption_approved_assumption_registry",
            "python -m unittest tests.integration.test_runtime_adoption_report",
        ],
        old_stale_values_detected_or_replaced=[
            "ComputeConfig defaults 32.0/64.0/128.0 replaced with 0.5/0.5/3.0",
            "EvaluationRunner compute defaults 128.0/256.0/512.0 replaced with 0.5/0.5/3.0",
        ],
        no_paper_recovery_claims=True,
        no_dependency_drift=True,
        no_training_or_policy_drift=True,
        no_reward_timing_change=True,
        no_campaign_rerun=True,
        final_verdict="runtime_adoption_completed_with_user_approved_assumptions",
    )


def write_runtime_adoption_report(report: RuntimeAdoptionReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    return report.write(output_dir)
