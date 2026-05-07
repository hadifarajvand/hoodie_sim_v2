from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import csv
import json
from typing import Any


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(slots=True)
class AuditFinding:
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
class ArtifactInventory:
    campaign_root: str
    campaign_dir: str
    matrix_dir: str
    bundle_dir: str
    trace_dir: str | None
    found_files: list[str]
    missing_files: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "campaign_root": self.campaign_root,
            "campaign_dir": self.campaign_dir,
            "matrix_dir": self.matrix_dir,
            "bundle_dir": self.bundle_dir,
            "trace_dir": self.trace_dir,
            "found_files": list(self.found_files),
            "missing_files": list(self.missing_files),
        }


@dataclass(slots=True)
class AccountingConsistency:
    passed: bool
    expected_runs: int
    discovered_runs: int
    expected_total_tasks: int
    discovered_total_tasks: int
    missing_finalization_detected: bool
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "expected_runs": self.expected_runs,
            "discovered_runs": self.discovered_runs,
            "expected_total_tasks": self.expected_total_tasks,
            "discovered_total_tasks": self.discovered_total_tasks,
            "missing_finalization_detected": self.missing_finalization_detected,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class CampaignAuditReport:
    artifact_inventory: ArtifactInventory
    findings: list[AuditFinding]
    trace_arrival_counts: list[dict[str, object]]
    policy_action_distribution: list[dict[str, object]]
    scenario_differentiation: list[dict[str, object]]
    policy_differentiation: list[dict[str, object]]
    accounting_consistency: AccountingConsistency
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_inventory": self.artifact_inventory.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "trace_arrival_counts": list(self.trace_arrival_counts),
            "policy_action_distribution": list(self.policy_action_distribution),
            "scenario_differentiation": list(self.scenario_differentiation),
            "policy_differentiation": list(self.policy_differentiation),
            "accounting_consistency": self.accounting_consistency.to_dict(),
            "passed": self.passed,
        }


class CampaignAudit:
    def __init__(self, campaign_root: Path):
        self.campaign_root = Path(campaign_root)
        self.campaign_dir = self.campaign_root / "campaign"
        self.matrix_dir = self.campaign_root / "matrix"
        self.bundle_dir = self.campaign_root / "bundle"
        self.trace_dir = self.matrix_dir / "traces"
        self._policy_outcomes_cache: dict[str, dict[str, Any]] | None = None
        self._scenario_outcomes_cache: dict[str, dict[str, Any]] | None = None

    def _matrix_result_files(self) -> list[Path]:
        if not self.matrix_dir.exists():
            return []
        return sorted(path for path in self.matrix_dir.glob("*.json") if path.is_file())

    def _found_files(self) -> list[str]:
        files: list[str] = []
        for path in self._matrix_result_files():
            files.append(path.relative_to(self.campaign_root).as_posix())
        matrix_summary = self.matrix_dir / "matrix-summary.csv"
        if matrix_summary.exists():
            files.append(matrix_summary.relative_to(self.campaign_root).as_posix())
        for name in ("campaign-manifest.json", "campaign-summary.json", "policy-summary.json", "scenario-summary.json", "determinism-check.json", "README.md"):
            path = self.campaign_dir / name
            if path.exists():
                files.append(path.relative_to(self.campaign_root).as_posix())
        if self.bundle_dir.exists():
            for path in sorted(self.bundle_dir.rglob("*")):
                if path.is_file():
                    files.append(path.relative_to(self.campaign_root).as_posix())
        if self.trace_dir.exists():
            for path in sorted(self.trace_dir.rglob("*")):
                if path.is_file():
                    files.append(path.relative_to(self.campaign_root).as_posix())
        return sorted(dict.fromkeys(files))

    def _missing_files(self) -> list[str]:
        required = [
            "matrix/matrix-summary.csv",
            "campaign/campaign-summary.json",
            "campaign/determinism-check.json",
            "bundle/manifest.json",
            "bundle/validation-summary.json",
        ]
        missing: list[str] = []
        for rel_path in required:
            if not (self.campaign_root / rel_path).exists():
                missing.append(rel_path)
        return sorted(missing)

    def _inventory(self) -> ArtifactInventory:
        trace_dir = self.trace_dir if self.trace_dir.exists() else None
        return ArtifactInventory(
            campaign_root=self.campaign_root.as_posix(),
            campaign_dir=self.campaign_dir.as_posix(),
            matrix_dir=self.matrix_dir.as_posix(),
            bundle_dir=self.bundle_dir.as_posix(),
            trace_dir=trace_dir.as_posix() if trace_dir is not None else None,
            found_files=self._found_files(),
            missing_files=self._missing_files(),
        )

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _trace_files(self) -> list[Path]:
        if not self.trace_dir.exists():
            return []
        return sorted(path for path in self.trace_dir.glob("*.json") if path.is_file())

    def _read_matrix_summary(self) -> list[dict[str, Any]]:
        path = self.matrix_dir / "matrix-summary.csv"
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

    def _read_campaign_summary(self) -> dict[str, Any]:
        path = self.campaign_dir / "campaign-summary.json"
        return self._read_json(path) if path.exists() else {}

    def _read_determinism_check(self) -> dict[str, Any]:
        path = self.campaign_dir / "determinism-check.json"
        return self._read_json(path) if path.exists() else {}

    def _read_policy_summary(self) -> list[dict[str, Any]]:
        path = self.campaign_dir / "policy-summary.json"
        return list(self._read_json(path)) if path.exists() else []

    def _read_scenario_summary(self) -> list[dict[str, Any]]:
        path = self.campaign_dir / "scenario-summary.json"
        return list(self._read_json(path)) if path.exists() else []

    def _read_matrix_results(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for path in self._matrix_result_files():
            results.append(self._read_json(path))
        return results

    def _trace_arrival_counts(self) -> list[dict[str, object]]:
        counts: list[dict[str, object]] = []
        for trace_path in self._trace_files():
            payload = self._read_json(trace_path)
            tasks = list(payload.get("tasks", []))
            arrivals: dict[int, int] = {}
            for task in tasks:
                arrival_slot = int(task.get("arrival_slot", 0))
                arrivals[arrival_slot] = arrivals.get(arrival_slot, 0) + 1
            counts.append(
                {
                    "trace_id": payload.get("trace_id", trace_path.stem),
                    "scenario_name": str(payload.get("metadata", {}).get("scenario_name", "")),
                    "seed": int(payload.get("seed", 0)),
                    "task_count": len(tasks),
                    "arrival_counts": [{"arrival_slot": slot, "count": arrivals[slot]} for slot in sorted(arrivals)],
                }
            )
        return counts

    def _trace_signature_by_seed(self) -> dict[int, dict[str, Any]]:
        signatures: dict[int, dict[str, Any]] = {}
        for trace_path in self._trace_files():
            payload = self._read_json(trace_path)
            seed = int(payload.get("seed", 0))
            scenario_name = str(payload.get("metadata", {}).get("scenario_name", ""))
            tasks = list(payload.get("tasks", []))
            arrival_distribution: dict[int, int] = {}
            for task in tasks:
                arrival_slot = int(task.get("arrival_slot", 0))
                arrival_distribution[arrival_slot] = arrival_distribution.get(arrival_slot, 0) + 1
            signatures[seed] = {
                "trace_id": payload.get("trace_id", trace_path.stem),
                "scenario_name": scenario_name,
                "seed": seed,
                "task_count": len(tasks),
                "arrival_distribution": arrival_distribution,
                "arrival_counts": [{"arrival_slot": slot, "count": arrival_distribution[slot]} for slot in sorted(arrival_distribution)],
            }
        return signatures

    def _policy_outcome_signatures(self) -> dict[str, dict[str, Any]]:
        signatures: dict[str, dict[str, Any]] = {}
        for result in self._read_matrix_results():
            policy_name = str(result.get("policy_name", ""))
            scenario_name = str(result.get("scenario_name", ""))
            final_metrics = dict(result.get("final_metrics", {}))
            raw_records = list(final_metrics.get("raw_records", []))
            action_distribution: dict[str, int] = {}
            outcome_distribution: dict[str, int] = {}
            for record in raw_records:
                action = str(record.get("selected_action", "unknown"))
                outcome = str(record.get("terminal_outcome", "unknown"))
                action_distribution[action] = action_distribution.get(action, 0) + 1
                outcome_distribution[outcome] = outcome_distribution.get(outcome, 0) + 1
            key = policy_name
            if key not in signatures:
                signatures[key] = {
                    "policy_name": policy_name,
                    "scenarios": [],
                    "action_distribution": {},
                    "outcome_distribution": {},
                    "signature": [],
                }
            signatures[key]["scenarios"].append(scenario_name)
            for action, count in action_distribution.items():
                signatures[key]["action_distribution"][action] = signatures[key]["action_distribution"].get(action, 0) + count
            for outcome, count in outcome_distribution.items():
                signatures[key]["outcome_distribution"][outcome] = signatures[key]["outcome_distribution"].get(outcome, 0) + count
        for item in signatures.values():
            item["scenarios"] = sorted(dict.fromkeys(item["scenarios"]))
            item["signature"] = [
                sorted(item["action_distribution"].items()),
                sorted(item["outcome_distribution"].items()),
            ]
        return signatures

    def _policy_action_distribution(self) -> list[dict[str, object]]:
        distributions: list[dict[str, object]] = []
        for policy_name, signature in sorted(self._policy_outcome_signatures().items()):
            distributions.append(
                {
                    "policy_name": policy_name,
                    "action_distribution": sorted(signature["action_distribution"].items()),
                    "outcome_distribution": sorted(signature["outcome_distribution"].items()),
                    "scenarios": list(signature["scenarios"]),
                }
            )
        return distributions

    def _scenario_outcome_signatures(self) -> dict[str, dict[str, Any]]:
        signatures: dict[str, dict[str, Any]] = {}
        for result in self._read_matrix_results():
            scenario_name = str(result.get("scenario_name", ""))
            policy_name = str(result.get("policy_name", ""))
            final_metrics = dict(result.get("final_metrics", {}))
            raw_records = list(final_metrics.get("raw_records", []))
            key = scenario_name
            if key not in signatures:
                signatures[key] = {
                    "scenario_name": scenario_name,
                    "policies": [],
                    "task_count": 0,
                    "action_distribution": {},
                    "outcome_distribution": {},
                    "signature": [],
                }
            signatures[key]["policies"].append(policy_name)
            signatures[key]["task_count"] += int(final_metrics.get("total_tasks", 0))
            for record in raw_records:
                action = str(record.get("selected_action", "unknown"))
                outcome = str(record.get("terminal_outcome", "unknown"))
                signatures[key]["action_distribution"][action] = signatures[key]["action_distribution"].get(action, 0) + 1
                signatures[key]["outcome_distribution"][outcome] = signatures[key]["outcome_distribution"].get(outcome, 0) + 1
        for item in signatures.values():
            item["policies"] = sorted(dict.fromkeys(item["policies"]))
            item["signature"] = [
                sorted(item["action_distribution"].items()),
                sorted(item["outcome_distribution"].items()),
                item["task_count"],
            ]
        return signatures

    def _trace_comparison(self) -> list[dict[str, object]]:
        comparisons: list[dict[str, object]] = []
        paper_default = {item["seed"]: item for item in self._trace_arrival_counts() if item["scenario_name"] == "paper_default"}
        moderate = {item["seed"]: item for item in self._trace_arrival_counts() if item["scenario_name"] == "moderate"}
        shared_seeds = sorted(set(paper_default) & set(moderate))
        for seed in shared_seeds:
            paper_item = paper_default[seed]
            moderate_item = moderate[seed]
            paper_arrivals = paper_item["arrival_counts"]
            moderate_arrivals = moderate_item["arrival_counts"]
            identical = paper_item["task_count"] == moderate_item["task_count"] and paper_arrivals == moderate_arrivals
            same_count = paper_item["task_count"] == moderate_item["task_count"]
            comparisons.append(
                {
                    "seed": seed,
                    "paper_default_trace_id": paper_item["trace_id"],
                    "moderate_trace_id": moderate_item["trace_id"],
                    "paper_default_task_count": paper_item["task_count"],
                    "moderate_task_count": moderate_item["task_count"],
                    "paper_default_arrival_counts": paper_arrivals,
                    "moderate_arrival_counts": moderate_arrivals,
                    "comparison": (
                        "identical"
                        if identical
                        else "same_count_but_different_slots"
                        if same_count
                        else "different_count"
                    ),
                }
            )
        return comparisons

    def _scenario_differentiation(self, scenario_summary: list[dict[str, Any]]) -> list[dict[str, object]]:
        if not scenario_summary:
            return []
        delays = [float(item.get("mean_average_delay", 0.0)) for item in scenario_summary]
        task_totals = [int(item.get("total_tasks", 0)) for item in scenario_summary]
        spread_delay = max(delays) - min(delays) if delays else 0.0
        spread_tasks = max(task_totals) - min(task_totals) if task_totals else 0
        status = "weak" if spread_delay < 0.25 and spread_tasks == 0 else "clear"
        return [
            {
                "status": status,
                "mean_average_delay_spread": spread_delay,
                "total_tasks_spread": spread_tasks,
                "scenario_count": len(scenario_summary),
            }
        ]

    def _policy_differentiation(self, policy_summary: list[dict[str, Any]]) -> list[dict[str, object]]:
        if not policy_summary:
            return []
        delays = [float(item.get("mean_average_delay", 0.0)) for item in policy_summary]
        task_totals = [int(item.get("total_tasks", 0)) for item in policy_summary]
        spread_delay = max(delays) - min(delays) if delays else 0.0
        spread_tasks = max(task_totals) - min(task_totals) if task_totals else 0
        status = "weak" if spread_delay < 0.75 and spread_tasks == 0 else "clear"
        return [
            {
                "status": status,
                "mean_average_delay_spread": spread_delay,
                "total_tasks_spread": spread_tasks,
                "policy_count": len(policy_summary),
            }
        ]

    def _findings(
        self,
        campaign_summary: dict[str, Any],
        policy_summary: list[dict[str, Any]],
        scenario_summary: list[dict[str, Any]],
        matrix_results: list[dict[str, Any]],
        determinism_check: dict[str, Any],
        missing_files: list[str],
    ) -> list[AuditFinding]:
        findings: list[AuditFinding] = []

        if missing_files:
            findings.append(
                AuditFinding(
                    category="missing_required_files",
                    severity="critical",
                    description="One or more required campaign artifacts are missing.",
                    evidence=list(missing_files),
                )
            )

        if float(campaign_summary.get("mean_drop_ratio", 0.0)) >= 0.5:
            findings.append(
                AuditFinding(
                    category="high_drop_ratio",
                    severity="warning",
                    description="Campaign drop ratio is unusually high.",
                    evidence=["campaign-summary.json:mean_drop_ratio"],
                )
            )

        if scenario_summary:
            scenario_delays = [float(item.get("mean_average_delay", 0.0)) for item in scenario_summary]
            scenario_tasks = [int(item.get("total_tasks", 0)) for item in scenario_summary]
            if max(scenario_delays) - min(scenario_delays) < 0.25 and max(scenario_tasks) - min(scenario_tasks) == 0:
                findings.append(
                    AuditFinding(
                        category="weak_scenario_differentiation",
                        severity="warning",
                        description="Scenario outcomes are nearly indistinguishable across the campaign.",
                        evidence=["scenario-summary.json"],
                    )
                )

        trace_counts = self._trace_arrival_counts()
        if trace_counts:
            counts_by_pair: dict[str, int] = {}
            for item in trace_counts:
                pair_key = f"{item['scenario_name']}::{item['seed']}"
                counts_by_pair[pair_key] = counts_by_pair.get(pair_key, 0) + int(item["task_count"])
            expected_pairs = {f"{item['scenario_name']}::{item['seed']}" for item in trace_counts}
            if len(counts_by_pair) != len(expected_pairs):
                findings.append(
                    AuditFinding(
                        category="trace_arrival_count_inconsistency",
                        severity="warning",
                        description="Trace arrival counts were not uniquely attributable to scenario/seed pairs.",
                        evidence=["matrix/traces"],
                    )
                )

        if policy_summary:
            policy_delays = [float(item.get("mean_average_delay", 0.0)) for item in policy_summary]
            policy_tasks = [int(item.get("total_tasks", 0)) for item in policy_summary]
            if max(policy_delays) - min(policy_delays) < 0.75 and max(policy_tasks) - min(policy_tasks) == 0:
                findings.append(
                    AuditFinding(
                        category="weak_policy_differentiation",
                        severity="warning",
                        description="Policy outcomes are nearly indistinguishable across the campaign.",
                        evidence=["policy-summary.json"],
                    )
                )

        policy_signatures = self._policy_outcome_signatures()
        if policy_signatures:
            duplicate_signatures: dict[str, list[str]] = {}
            for policy_name, signature in policy_signatures.items():
                signature_key = json.dumps(signature["signature"], sort_keys=True)
                duplicate_signatures.setdefault(signature_key, []).append(policy_name)
            for policies in duplicate_signatures.values():
                if len(policies) > 1:
                    findings.append(
                        AuditFinding(
                            category="identical_policy_signature",
                            severity="warning",
                            description="Multiple policies share the same action and outcome signature.",
                            evidence=policies,
                        )
                    )

        trace_comparisons = self._trace_comparison()
        if trace_comparisons:
            for comparison in trace_comparisons:
                findings.append(
                    AuditFinding(
                        category="moderate_vs_paper_default_trace_comparison",
                        severity="informational",
                        description=(
                            f"Seed {comparison['seed']} comparison is {comparison['comparison']}."
                        ),
                        evidence=[
                            f"paper_default:{comparison['paper_default_trace_id']}",
                            f"moderate:{comparison['moderate_trace_id']}",
                        ],
                    )
                )

        scenario_signatures = self._scenario_outcome_signatures()

        if determinism_check:
            if not determinism_check.get("passed", False):
                findings.append(
                    AuditFinding(
                        category="determinism_issue",
                        severity="critical",
                        description="Campaign determinism validation reported a failure.",
                        evidence=["determinism-check.json"],
                    )
                )

        accounting = self._accounting_consistency(matrix_results, campaign_summary)
        if not accounting.passed or accounting.missing_finalization_detected:
            findings.append(
                AuditFinding(
                    category="accounting_inconsistency",
                    severity="critical",
                    description="Campaign totals do not reconcile cleanly with the underlying matrix records.",
                    evidence=["campaign-summary.json", "matrix-summary.csv"],
                )
            )

        return findings

    def _accounting_consistency(self, matrix_results: list[dict[str, Any]], campaign_summary: dict[str, Any]) -> AccountingConsistency:
        expected_runs = len(matrix_results)
        discovered_runs = int(campaign_summary.get("result_count", expected_runs))
        expected_total_tasks = sum(int(result.get("final_metrics", {}).get("total_tasks", 0)) for result in matrix_results)
        discovered_total_tasks = int(campaign_summary.get("total_tasks", expected_total_tasks))
        missing_finalization_detected = expected_runs != discovered_runs or expected_total_tasks != discovered_total_tasks
        notes: list[str] = []
        if expected_runs != discovered_runs:
            notes.append("result_count does not match discovered matrix runs")
        if expected_total_tasks != discovered_total_tasks:
            notes.append("total_tasks does not match sum of matrix result totals")
        return AccountingConsistency(
            passed=not missing_finalization_detected,
            expected_runs=expected_runs,
            discovered_runs=discovered_runs,
            expected_total_tasks=expected_total_tasks,
            discovered_total_tasks=discovered_total_tasks,
            missing_finalization_detected=missing_finalization_detected,
            notes=notes,
        )

    def run(self) -> CampaignAuditReport:
        inventory = self._inventory()
        campaign_summary = self._read_campaign_summary()
        policy_summary = self._read_policy_summary()
        scenario_summary = self._read_scenario_summary()
        matrix_results = self._read_matrix_results()
        determinism_check = self._read_determinism_check()
        trace_arrival_counts = self._trace_arrival_counts()
        policy_action_distribution = self._policy_action_distribution()
        findings = self._findings(
            campaign_summary,
            policy_summary,
            scenario_summary,
            matrix_results,
            determinism_check,
            inventory.missing_files,
        )
        accounting = self._accounting_consistency(matrix_results, campaign_summary)
        passed = accounting.passed and not any(finding.severity == "critical" for finding in findings)
        return CampaignAuditReport(
            artifact_inventory=inventory,
            findings=sorted(findings, key=lambda finding: (finding.severity, finding.category)),
            trace_arrival_counts=trace_arrival_counts,
            policy_action_distribution=policy_action_distribution,
            scenario_differentiation=self._scenario_differentiation(scenario_summary),
            policy_differentiation=self._policy_differentiation(policy_summary),
            accounting_consistency=accounting,
            passed=passed,
        )

    def render_text(self, report: CampaignAuditReport) -> str:
        lines = [
            "# Campaign Result Sanity Audit",
            "",
            "## Artifact Inventory",
            f"- Campaign root: {report.artifact_inventory.campaign_root}",
            f"- Campaign directory: {report.artifact_inventory.campaign_dir}",
            f"- Matrix directory: {report.artifact_inventory.matrix_dir}",
            f"- Bundle directory: {report.artifact_inventory.bundle_dir}",
            f"- Trace directory: {report.artifact_inventory.trace_dir or 'missing'}",
            f"- Found files: {len(report.artifact_inventory.found_files)}",
            f"- Missing files: {len(report.artifact_inventory.missing_files)}",
            "",
            "## Findings",
        ]
        if report.findings:
            for finding in report.findings:
                lines.append(f"- [{finding.severity.upper()}] {finding.category}: {finding.description}")
                for evidence in finding.evidence:
                    lines.append(f"  - evidence: {evidence}")
        else:
            lines.append("- No anomalies detected.")
        lines.extend(
            [
                "",
                "## Trace Arrival Counts",
                _json_dump(report.trace_arrival_counts).rstrip(),
                "",
                "## Policy Action Distribution",
                _json_dump(report.policy_action_distribution).rstrip(),
                "",
                "## Scenario Differentiation",
                _json_dump(report.scenario_differentiation).rstrip(),
                "",
                "## Policy Differentiation",
                _json_dump(report.policy_differentiation).rstrip(),
                "",
                "## Accounting Consistency",
                _json_dump(report.accounting_consistency.to_dict()).rstrip(),
                "",
                f"Passed: {str(report.passed).lower()}",
            ]
        )
        return "\n".join(lines) + "\n"

    def write_outputs(self, output_dir: Path, report: CampaignAuditReport) -> dict[str, Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = {
            "audit-report.json": output_dir / "audit-report.json",
            "audit-report.txt": output_dir / "audit-report.txt",
        }
        outputs["audit-report.json"].write_text(_json_dump(report.to_dict()), encoding="utf-8")
        outputs["audit-report.txt"].write_text(self.render_text(report), encoding="utf-8")
        return outputs

    def audit(self) -> CampaignAuditReport:
        return self.run()
