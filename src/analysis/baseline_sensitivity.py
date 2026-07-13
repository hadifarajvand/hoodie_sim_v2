from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import csv
import json
from itertools import combinations
from typing import Any


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _sorted_items(mapping: dict[Any, Any]) -> list[dict[str, Any]]:
    return [{"key": key, "value": mapping[key]} for key in sorted(mapping)]


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_relpath(base: Path, path: Path) -> str:
    return path.relative_to(base).as_posix()


@dataclass(slots=True)
class MissingArtifact:
    path: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "reason": self.reason}


@dataclass(slots=True)
class SensitivityFinding:
    category: str
    severity: str
    description: str
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "evidence": list(self.evidence),
        }


@dataclass(slots=True)
class TraceComparison:
    seed: int
    left_scenario: str
    right_scenario: str
    comparison: str
    task_count_left: int
    task_count_right: int
    task_count_difference: int
    arrival_slot_differences: list[dict[str, int]]
    task_size_differences: list[dict[str, float]]
    processing_density_differences: list[dict[str, float]]

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "left_scenario": self.left_scenario,
            "right_scenario": self.right_scenario,
            "comparison": self.comparison,
            "task_count_left": self.task_count_left,
            "task_count_right": self.task_count_right,
            "task_count_difference": self.task_count_difference,
            "arrival_slot_differences": list(self.arrival_slot_differences),
            "task_size_differences": list(self.task_size_differences),
            "processing_density_differences": list(self.processing_density_differences),
        }


@dataclass(slots=True)
class PolicyComparison:
    policy_name: str
    action_distribution: list[dict[str, int]]
    terminal_outcome_distribution: list[dict[str, int]]
    completed_tasks: int
    dropped_tasks: int
    average_delay: float
    action_signature: str
    outcome_signature: str

    def to_dict(self) -> dict[str, object]:
        return {
            "policy_name": self.policy_name,
            "action_distribution": list(self.action_distribution),
            "terminal_outcome_distribution": list(self.terminal_outcome_distribution),
            "completed_tasks": self.completed_tasks,
            "dropped_tasks": self.dropped_tasks,
            "average_delay": self.average_delay,
            "action_signature": self.action_signature,
            "outcome_signature": self.outcome_signature,
        }


@dataclass(slots=True)
class ScenarioComparison:
    scenario_name: str
    throughput: int
    drop_ratio: float
    average_delay: float
    completed_tasks: int
    dropped_tasks: int
    distinguishable: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "scenario_name": self.scenario_name,
            "throughput": self.throughput,
            "drop_ratio": self.drop_ratio,
            "average_delay": self.average_delay,
            "completed_tasks": self.completed_tasks,
            "dropped_tasks": self.dropped_tasks,
            "distinguishable": self.distinguishable,
        }


@dataclass(slots=True)
class SensitivityReport:
    campaign_root: str
    analysis_output_dir: str
    audit_report_present: bool
    missing_artifacts: list[dict[str, object]]
    findings: list[dict[str, object]]
    trace_comparisons: list[dict[str, object]]
    policy_comparisons: list[dict[str, object]]
    scenario_comparisons: list[dict[str, object]]
    saturation_diagnosis: dict[str, object]
    classifications: list[str]
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "campaign_root": self.campaign_root,
            "analysis_output_dir": self.analysis_output_dir,
            "audit_report_present": self.audit_report_present,
            "missing_artifacts": list(self.missing_artifacts),
            "findings": list(self.findings),
            "trace_comparisons": list(self.trace_comparisons),
            "policy_comparisons": list(self.policy_comparisons),
            "scenario_comparisons": list(self.scenario_comparisons),
            "saturation_diagnosis": dict(self.saturation_diagnosis),
            "classifications": list(self.classifications),
            "passed": self.passed,
        }


class BaselineSensitivityAnalyzer:
    def __init__(self, campaign_root: Path, analysis_output_dir: Path):
        self.campaign_root = Path(campaign_root)
        self.analysis_output_dir = Path(analysis_output_dir)
        self.campaign_dir = self.campaign_root / "campaign"
        self.matrix_dir = self.campaign_root / "matrix"
        self.trace_dir = self.matrix_dir / "traces"
        self.bundle_dir = self.campaign_root / "bundle"
        self.audit_dir = self.campaign_root / "audit"

    def _exists(self, relative_path: str) -> bool:
        return (self.campaign_root / relative_path).exists()

    def _required_files(self) -> list[str]:
        return [
            "campaign/campaign-summary.json",
            "campaign/policy-summary.json",
            "campaign/scenario-summary.json",
            "campaign/determinism-check.json",
            "matrix/matrix-summary.csv",
            "bundle/manifest.json",
            "bundle/validation-summary.json",
        ]

    def _load_json(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_optional_json(self, path: Path, default: Any) -> Any:
        return self._load_json(path) if path.exists() else default

    def _missing_artifacts(self) -> list[MissingArtifact]:
        missing = []
        for relative_path in self._required_files():
            if not self._exists(relative_path):
                missing.append(MissingArtifact(path=relative_path, reason="missing_required_file"))
        if not self.trace_dir.exists():
            missing.append(MissingArtifact(path="matrix/traces", reason="missing_trace_directory"))
        return missing

    def _campaign_summary(self) -> dict[str, Any]:
        return self._load_optional_json(self.campaign_dir / "campaign-summary.json", {})

    def _policy_summary(self) -> list[dict[str, Any]]:
        payload = self._load_optional_json(self.campaign_dir / "policy-summary.json", [])
        return list(payload)

    def _scenario_summary(self) -> list[dict[str, Any]]:
        payload = self._load_optional_json(self.campaign_dir / "scenario-summary.json", [])
        return list(payload)

    def _audit_report(self) -> dict[str, Any]:
        path = self.campaign_root / "audit" / "audit-report.json"
        return self._load_optional_json(path, {})

    def _matrix_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        path = self.matrix_dir / "matrix-summary.csv"
        if not path.exists():
            return records
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                records.append(dict(row))
        return records

    def _matrix_result_files(self) -> list[Path]:
        if not self.matrix_dir.exists():
            return []
        return sorted(
            path for path in self.matrix_dir.glob("*.json")
            if path.is_file() and not path.name.startswith("result-")
        )

    def _matrix_results(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for path in self._matrix_result_files():
            results.append(self._load_json(path))
        return results

    def _trace_files(self) -> list[Path]:
        if not self.trace_dir.exists():
            return []
        return sorted(path for path in self.trace_dir.glob("*.json") if path.is_file())

    def _trace_payloads(self) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for path in self._trace_files():
            payload = self._load_json(path)
            payload["_path"] = _stable_relpath(self.campaign_root, path)
            payloads.append(payload)
        return payloads

    def _value_distribution(self, values: list[Any]) -> list[dict[str, object]]:
        counts: dict[str, int] = {}
        for value in values:
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
        return [{"key": key, "count": counts[key]} for key in sorted(counts)]

    def _trace_signature(self, payload: dict[str, Any]) -> dict[str, Any]:
        tasks = list(payload.get("tasks", []))
        arrival_slots: list[int] = [int(task.get("arrival_slot", 0)) for task in tasks]
        task_sizes = [task.get("size") for task in tasks if task.get("size") is not None]
        processing_density = [task.get("processing_density") for task in tasks if task.get("processing_density") is not None]
        return {
            "trace_id": str(payload.get("trace_id", "")),
            "seed": int(payload.get("seed", 0)),
            "scenario_name": str(payload.get("metadata", {}).get("scenario_name", "")),
            "task_count": len(tasks),
            "arrival_slot_distribution": self._value_distribution(arrival_slots),
            "task_size_distribution": self._value_distribution(task_sizes),
            "processing_density_distribution": self._value_distribution(processing_density),
        }

    def _trace_grouped(self) -> dict[str, dict[int, dict[str, Any]]]:
        grouped: dict[str, dict[int, dict[str, Any]]] = {}
        for payload in self._trace_payloads():
            signature = self._trace_signature(payload)
            scenario_name = signature["scenario_name"]
            seed = int(signature["seed"])
            grouped.setdefault(scenario_name, {})[seed] = signature
        return grouped

    def _compare_distributions(self, left: list[dict[str, object]], right: list[dict[str, object]]) -> dict[str, object]:
        left_map = {item["key"]: item["count"] for item in left}
        right_map = {item["key"]: item["count"] for item in right}
        keys = sorted(set(left_map) | set(right_map))
        differences = []
        for key in keys:
            left_count = int(left_map.get(key, 0))
            right_count = int(right_map.get(key, 0))
            if left_count != right_count:
                differences.append({"key": key, "left": left_count, "right": right_count})
        return {
            "identical": not differences,
            "differences": differences,
        }

    def _trace_comparisons(self) -> list[TraceComparison]:
        grouped = self._trace_grouped()
        if not grouped:
            return []
        comparisons: list[TraceComparison] = []
        for left_scenario, right_scenario in combinations(sorted(grouped), 2):
            shared_seeds = sorted(set(grouped[left_scenario]) & set(grouped[right_scenario]))
            for seed in shared_seeds:
                left = grouped[left_scenario][seed]
                right = grouped[right_scenario][seed]
                arrival_cmp = self._compare_distributions(left["arrival_slot_distribution"], right["arrival_slot_distribution"])
                size_cmp = self._compare_distributions(left["task_size_distribution"], right["task_size_distribution"])
                density_cmp = self._compare_distributions(left["processing_density_distribution"], right["processing_density_distribution"])
                identical = (
                    left["task_count"] == right["task_count"]
                    and arrival_cmp["identical"]
                    and size_cmp["identical"]
                    and density_cmp["identical"]
                )
                same_count = left["task_count"] == right["task_count"]
                if identical:
                    comparison = "identical"
                elif same_count:
                    comparison = "same_count_but_different_slots"
                else:
                    comparison = "different_count"
                comparisons.append(
                    TraceComparison(
                        seed=seed,
                        left_scenario=left_scenario,
                        right_scenario=right_scenario,
                        comparison=comparison,
                        task_count_left=left["task_count"],
                        task_count_right=right["task_count"],
                        task_count_difference=abs(left["task_count"] - right["task_count"]),
                        arrival_slot_differences=arrival_cmp["differences"],
                        task_size_differences=size_cmp["differences"],
                        processing_density_differences=density_cmp["differences"],
                    )
                )
        return comparisons

    def _policy_grouped(self) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for result in self._matrix_results():
            policy_name = str(result.get("policy_name", ""))
            final_metrics = dict(result.get("final_metrics", {}))
            raw_records = list(final_metrics.get("raw_records", []))
            action_counts: dict[str, int] = {}
            outcome_counts: dict[str, int] = {}
            for record in raw_records:
                action = str(record.get("selected_action", "unknown"))
                outcome = str(record.get("terminal_outcome", "unknown"))
                action_counts[action] = action_counts.get(action, 0) + 1
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
            grouped.setdefault(policy_name, []).append(
                {
                    "scenario_name": str(result.get("scenario_name", "")),
                    "seed": int(result.get("seed", 0)),
                    "action_distribution": action_counts,
                    "terminal_outcome_distribution": outcome_counts,
                    "completed_tasks": int(final_metrics.get("completed_tasks", 0)),
                    "dropped_tasks": int(final_metrics.get("dropped_tasks", 0)),
                    "average_delay": float(final_metrics.get("average_delay", 0.0)),
                }
            )
        return grouped

    def _policy_comparisons(self) -> list[PolicyComparison]:
        comparisons: list[PolicyComparison] = []
        grouped = self._policy_grouped()
        for policy_name in sorted(grouped):
            entries = grouped[policy_name]
            action_counts: dict[str, int] = {}
            outcome_counts: dict[str, int] = {}
            completed_tasks = 0
            dropped_tasks = 0
            average_delays: list[float] = []
            for entry in entries:
                for action, count in entry["action_distribution"].items():
                    action_counts[action] = action_counts.get(action, 0) + int(count)
                for outcome, count in entry["terminal_outcome_distribution"].items():
                    outcome_counts[outcome] = outcome_counts.get(outcome, 0) + int(count)
                completed_tasks += int(entry["completed_tasks"])
                dropped_tasks += int(entry["dropped_tasks"])
                average_delays.append(float(entry["average_delay"]))
            action_signature_payload = {"action_distribution": sorted(action_counts.items())}
            outcome_signature_payload = {"terminal_outcome_distribution": sorted(outcome_counts.items())}
            comparisons.append(
                PolicyComparison(
                    policy_name=policy_name,
                    action_distribution=[{"key": key, "count": value} for key, value in sorted(action_counts.items())],
                    terminal_outcome_distribution=[{"key": key, "count": value} for key, value in sorted(outcome_counts.items())],
                    completed_tasks=completed_tasks,
                    dropped_tasks=dropped_tasks,
                    average_delay=sum(average_delays) / len(average_delays) if average_delays else 0.0,
                    action_signature=sha256(_json_dump(action_signature_payload).encode("utf-8")).hexdigest(),
                    outcome_signature=sha256(_json_dump(outcome_signature_payload).encode("utf-8")).hexdigest(),
                )
            )
        return comparisons

    def _scenario_comparisons(self) -> list[ScenarioComparison]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for record in self._matrix_records():
            scenario_name = str(record.get("scenario_name", ""))
            grouped.setdefault(scenario_name, []).append(record)
        comparisons: list[ScenarioComparison] = []
        for scenario_name in sorted(grouped):
            rows = grouped[scenario_name]
            throughput = sum(int(row.get("throughput", 0)) for row in rows)
            completed = sum(int(row.get("completed_tasks", 0)) for row in rows)
            dropped = sum(int(row.get("dropped_tasks", 0)) for row in rows)
            total = sum(int(row.get("total_tasks", 0)) for row in rows)
            average_delay_values = [float(row.get("average_delay", 0.0)) for row in rows]
            drop_ratio_values = [float(row.get("drop_ratio", 0.0)) for row in rows]
            comparisons.append(
                ScenarioComparison(
                    scenario_name=scenario_name,
                    throughput=throughput,
                    drop_ratio=sum(drop_ratio_values) / len(drop_ratio_values) if drop_ratio_values else 0.0,
                    average_delay=sum(average_delay_values) / len(average_delay_values) if average_delay_values else 0.0,
                    completed_tasks=completed,
                    dropped_tasks=dropped,
                    distinguishable=True,
                )
            )
        if len(comparisons) >= 2:
            baseline = {item.scenario_name: item for item in comparisons}
            reference = baseline.get("paper_default")
            if reference is not None:
                for item in comparisons:
                    if item.scenario_name == "paper_default":
                        continue
                    item.distinguishable = (
                        item.throughput != reference.throughput
                        or abs(item.drop_ratio - reference.drop_ratio) > 1e-9
                        or abs(item.average_delay - reference.average_delay) > 1e-9
                        or item.completed_tasks != reference.completed_tasks
                        or item.dropped_tasks != reference.dropped_tasks
                    )
        return comparisons

    def _scenario_trace_identity(self, trace_comparisons: list[TraceComparison]) -> dict[str, Any]:
        moderate_pair = [
            item for item in trace_comparisons
            if {item.left_scenario, item.right_scenario} == {"paper_default", "moderate"}
        ]
        if not moderate_pair:
            return {"paper_default_vs_moderate": "insufficient_evidence"}
        comparisons = [item.comparison for item in moderate_pair]
        if all(item == "identical" for item in comparisons):
            status = "trace_input_collapsed"
        elif any(item in {"same_count_but_different_slots", "different_count"} for item in comparisons):
            status = "trace_input_distinguishable"
        else:
            status = "insufficient_evidence"
        return {"paper_default_vs_moderate": status, "comparisons": [item.to_dict() for item in moderate_pair]}

    def _policy_behavior_classification(self, policy_comparisons: list[PolicyComparison]) -> dict[str, Any]:
        if not policy_comparisons:
            return {"status": "insufficient_evidence", "identical_policy_groups": [], "near_identical_outcome_groups": []}
        action_groups: dict[str, list[str]] = {}
        outcome_groups: dict[str, list[str]] = {}
        for item in policy_comparisons:
            action_groups.setdefault(item.action_signature, []).append(item.policy_name)
            outcome_groups.setdefault(item.outcome_signature, []).append(item.policy_name)
        identical_policy_groups = [sorted(names) for names in action_groups.values() if len(names) > 1]
        near_identical_outcome_groups = []
        for signature, names in outcome_groups.items():
            if len(names) > 1:
                action_signatures = {item.action_signature for item in policy_comparisons if item.policy_name in names}
                if len(action_signatures) > 1:
                    near_identical_outcome_groups.append(sorted(names))
        if identical_policy_groups:
            return {
                "status": "policy_behavior_collapsed",
                "identical_policy_groups": sorted(identical_policy_groups),
                "near_identical_outcome_groups": sorted(near_identical_outcome_groups),
            }
        if near_identical_outcome_groups:
            return {
                "status": "near_identical_outcome_behavior",
                "identical_policy_groups": [],
                "near_identical_outcome_groups": sorted(near_identical_outcome_groups),
            }
        return {"status": "insufficient_evidence", "identical_policy_groups": [], "near_identical_outcome_groups": []}

    def _scenario_output_classification(self, scenario_comparisons: list[ScenarioComparison]) -> dict[str, Any]:
        if not scenario_comparisons:
            return {"status": "insufficient_evidence"}
        reference = next((item for item in scenario_comparisons if item.scenario_name == "paper_default"), None)
        if reference is None:
            return {"status": "insufficient_evidence"}
        moderate = next((item for item in scenario_comparisons if item.scenario_name == "moderate"), None)
        if moderate is None:
            return {"status": "insufficient_evidence"}
        if (
            abs(moderate.throughput - reference.throughput) < 1e-9
            and abs(moderate.drop_ratio - reference.drop_ratio) < 1e-9
            and abs(moderate.average_delay - reference.average_delay) < 1e-9
            and moderate.completed_tasks == reference.completed_tasks
            and moderate.dropped_tasks == reference.dropped_tasks
        ):
            status = "scenario_output_collapsed"
        else:
            status = "scenario_output_distinguishable"
        return {
            "status": status,
            "paper_default": reference.to_dict(),
            "moderate": moderate.to_dict(),
        }

    def _saturation_diagnosis(self, campaign_summary: dict[str, Any], scenario_comparisons: list[ScenarioComparison]) -> dict[str, Any]:
        drop_ratio = float(campaign_summary.get("mean_drop_ratio", 0.0))
        total_delay = float(campaign_summary.get("mean_average_delay", 0.0))
        total_completed = int(campaign_summary.get("total_completed_tasks", 0))
        total_dropped = int(campaign_summary.get("total_dropped_tasks", 0))
        total_tasks = int(campaign_summary.get("total_tasks", 0))
        pressure = {
            "high_drop_ratio": drop_ratio >= 0.5,
            "delay_pressure": total_delay >= 5.0,
            "drop_pressure": total_dropped > total_completed,
            "load_pressure": total_tasks > 0 and total_dropped / max(total_tasks, 1) >= 0.5,
        }
        dominant = sum(1 for flag in pressure.values() if flag)
        status = "saturation_dominant" if dominant >= 2 else "insufficient_evidence"
        return {
            "status": status,
            "pressure_signals": pressure,
            "scenario_count": len(scenario_comparisons),
            "completed_tasks": total_completed,
            "dropped_tasks": total_dropped,
            "total_tasks": total_tasks,
            "mean_average_delay": total_delay,
            "mean_drop_ratio": drop_ratio,
        }

    def _accounting_clean(self) -> dict[str, Any]:
        campaign_summary = self._campaign_summary()
        matrix_results = self._matrix_results()
        expected_runs = len(matrix_results)
        discovered_runs = int(campaign_summary.get("result_count", expected_runs))
        expected_total_tasks = sum(int(result.get("final_metrics", {}).get("total_tasks", 0)) for result in matrix_results)
        discovered_total_tasks = int(campaign_summary.get("total_tasks", expected_total_tasks))
        passed = expected_runs == discovered_runs and expected_total_tasks == discovered_total_tasks
        return {
            "status": "accounting_clean" if passed else "accounting_inconsistent",
            "expected_runs": expected_runs,
            "discovered_runs": discovered_runs,
            "expected_total_tasks": expected_total_tasks,
            "discovered_total_tasks": discovered_total_tasks,
            "passed": passed,
        }

    def analyze(self) -> SensitivityReport:
        missing = self._missing_artifacts()
        campaign_summary = self._campaign_summary()
        audit_report = self._audit_report()
        trace_comparisons = self._trace_comparisons()
        policy_comparisons = self._policy_comparisons()
        scenario_comparisons = self._scenario_comparisons()
        findings: list[SensitivityFinding] = []

        if missing:
            findings.append(
                SensitivityFinding(
                    category="missing_artifacts",
                    severity="critical",
                    description="One or more required campaign artifacts are missing.",
                    evidence=[item.path for item in missing],
                )
            )

        trace_classification = self._scenario_trace_identity(trace_comparisons)
        if trace_classification["paper_default_vs_moderate"] == "trace_input_collapsed":
            findings.append(
                SensitivityFinding(
                    category="trace_input_collapsed",
                    severity="warning",
                    description="paper_default and moderate traces are identical for all shared seeds.",
                    evidence=[json.dumps(item.to_dict(), sort_keys=True) for item in trace_comparisons],
                )
            )

        policy_classification = self._policy_behavior_classification(policy_comparisons)
        if policy_classification["status"] == "policy_behavior_collapsed":
            findings.append(
                SensitivityFinding(
                    category="policy_behavior_collapsed",
                    severity="warning",
                    description="One or more policy groups share identical signatures.",
                    evidence=[json.dumps(group, sort_keys=True) for group in policy_classification["identical_policy_groups"]],
                )
            )
        if policy_classification["near_identical_outcome_groups"]:
            findings.append(
                SensitivityFinding(
                    category="near_identical_outcome_behavior",
                    severity="informational",
                    description="Policies share outcome distributions even though their action signatures differ.",
                    evidence=[json.dumps(group, sort_keys=True) for group in policy_classification["near_identical_outcome_groups"]],
                )
            )

        scenario_classification = self._scenario_output_classification(scenario_comparisons)
        if scenario_classification["status"] == "scenario_output_collapsed":
            findings.append(
                SensitivityFinding(
                    category="scenario_output_collapsed",
                    severity="warning",
                    description="Scenario-level outputs are collapsed between paper_default and moderate.",
                    evidence=[json.dumps(scenario_classification, sort_keys=True)],
                )
            )

        saturation = self._saturation_diagnosis(campaign_summary, scenario_comparisons)
        if saturation["status"] == "saturation_dominant":
            findings.append(
                SensitivityFinding(
                    category="saturation_dominant",
                    severity="informational",
                    description="High drop ratio and delay patterns are consistent with saturation pressure.",
                    evidence=[json.dumps(saturation, sort_keys=True)],
                )
            )

        accounting = self._accounting_clean()
        if not accounting["passed"]:
            findings.append(
                SensitivityFinding(
                    category="accounting_inconsistent",
                    severity="critical",
                    description="Campaign accounting does not reconcile cleanly.",
                    evidence=[json.dumps(accounting, sort_keys=True)],
                )
            )

        classifications = {
            "trace_input_collapsed" if trace_classification["paper_default_vs_moderate"] == "trace_input_collapsed" else "insufficient_evidence",
            "policy_behavior_collapsed"
            if policy_classification["status"] == "policy_behavior_collapsed"
            else "near_identical_outcome_behavior"
            if policy_classification["status"] == "near_identical_outcome_behavior"
            else "insufficient_evidence",
            "scenario_output_collapsed" if scenario_classification["status"] == "scenario_output_collapsed" else "scenario_output_distinguishable" if scenario_classification["status"] == "scenario_output_distinguishable" else "insufficient_evidence",
            "saturation_dominant" if saturation["status"] == "saturation_dominant" else "insufficient_evidence",
            "accounting_clean" if accounting["status"] == "accounting_clean" else "accounting_inconsistent",
        }
        classifications = sorted(classifications)
        passed = not any(finding.severity == "critical" for finding in findings)
        return SensitivityReport(
            campaign_root=self.campaign_root.as_posix(),
            analysis_output_dir=self.analysis_output_dir.as_posix(),
            audit_report_present=bool(audit_report),
            missing_artifacts=[item.to_dict() for item in missing],
            findings=[finding.to_dict() for finding in sorted(findings, key=lambda item: (item.severity, item.category))],
            trace_comparisons=[item.to_dict() for item in trace_comparisons],
            policy_comparisons=[item.to_dict() for item in policy_comparisons],
            scenario_comparisons=[item.to_dict() for item in scenario_comparisons],
            saturation_diagnosis=saturation,
            classifications=classifications,
            passed=passed,
        )

    def render_text(self, report: SensitivityReport) -> str:
        lines = [
            "# Baseline Sensitivity Analysis",
            "",
            "## Scope",
            f"- Campaign root: {report.campaign_root}",
            f"- Analysis output dir: {report.analysis_output_dir}",
            f"- Audit report present: {str(report.audit_report_present).lower()}",
            f"- Passed: {str(report.passed).lower()}",
            "",
            "## Missing Artifacts",
            _json_dump(report.missing_artifacts).rstrip(),
            "",
            "## Findings",
        ]
        if report.findings:
            for finding in report.findings:
                lines.append(f"- [{finding['severity'].upper()}] {finding['category']}: {finding['description']}")
                for evidence in finding["evidence"]:
                    lines.append(f"  - evidence: {evidence}")
        else:
            lines.append("- No blocking anomalies detected.")
        lines.extend(
            [
                "",
                "## Trace Comparisons",
                _json_dump(report.trace_comparisons).rstrip(),
                "",
                "## Policy Comparisons",
                _json_dump(report.policy_comparisons).rstrip(),
                "",
                "## Scenario Comparisons",
                _json_dump(report.scenario_comparisons).rstrip(),
                "",
                "## Saturation Diagnosis",
                _json_dump(report.saturation_diagnosis).rstrip(),
                "",
                "## Classifications",
                _json_dump(report.classifications).rstrip(),
            ]
        )
        return "\n".join(lines) + "\n"

    def write_outputs(self) -> dict[str, Path]:
        report = self.analyze()
        self.analysis_output_dir.mkdir(parents=True, exist_ok=True)
        report_json = self.analysis_output_dir / "sensitivity-report.json"
        report_text = self.analysis_output_dir / "sensitivity-report.md"
        report_json.write_text(_json_dump(report.to_dict()), encoding="utf-8")
        report_text.write_text(self.render_text(report), encoding="utf-8")
        return {"sensitivity-report.json": report_json, "sensitivity-report.md": report_text}
