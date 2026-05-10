from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Any

from src.evaluation.matrix_config import EvaluationMatrixConfig
from src.evaluation.matrix_runner import EvaluationMatrixRunner

from .classifier import SettingSignature, build_baseline_signature, classify_sensitivity_audit
from .gates import validate_feature_gates
from .report import DEFAULT_OUTPUT_DIR, BaselineRebuildSensitivityAuditReport, write_baseline_rebuild_sensitivity_audit_report
from .settings import (
    FIXED_EPISODE_LENGTHS,
    FIXED_SCENARIOS,
    FIXED_SEEDS,
    REUSED_METRICS,
    SensitivitySetting,
    build_sensitivity_settings,
    supported_baseline_policies,
)


@dataclass(slots=True)
class _AuditRunResult:
    setting: SensitivitySetting
    baseline_signatures: dict[str, str]
    distinct_signatures: int
    reference_match: bool
    status: str
    support_level: str
    note: str

    def to_indicator(self) -> dict[str, Any]:
        return {
            "seed": self.setting.seed,
            "scenario_name": self.setting.scenario_name,
            "episode_length": self.setting.episode_length,
            "status": self.status,
            "support_level": self.support_level,
            "note": self.note,
        }


class BaselineRebuildSensitivityAuditRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        self.gate_paths = (
            Path("artifacts/analysis/differential-environment-audit/differential-audit.json"),
            Path("artifacts/analysis/mechanism-repair/repair-summary.json"),
            Path("artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json"),
            Path("artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json"),
        )

    def _reference_report(self) -> dict[str, Any]:
        import json

        path = self.gate_paths[-1]
        return json.loads(path.read_text(encoding="utf-8"))

    def _reference_signature_set(self, report: dict[str, Any]) -> set[str]:
        return {
            str(item.get("signature"))
            for item in report.get("collapse_indicators", [])
            if item.get("signature") is not None
        }

    def _matrix_run(self, setting: SensitivitySetting) -> list[dict[str, Any]]:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = EvaluationMatrixRunner(
                EvaluationMatrixConfig(
                    policy_names=supported_baseline_policies(),
                    scenario_names=(setting.scenario_name,),
                    seeds=(setting.seed,),
                    output_dir=Path(tmpdir) / "matrix",
                    episode_length=setting.episode_length,
                    dependency_change_note="No dependency files changed.",
                )
            ).run()
            return list(result["results"])

    def _summarize_setting(self, setting: SensitivitySetting, reference_signatures: set[str]) -> _AuditRunResult:
        results = self._matrix_run(setting)
        signatures = {
            str(result["policy_name"]): build_baseline_signature(dict(result.get("final_metrics", {})))
            for result in results
        }
        distinct_signatures = len(set(signatures.values()))
        reference_match = set(signatures.values()) == reference_signatures
        if distinct_signatures <= 1:
            status = "collapse_worsened"
            support_level = "full" if reference_signatures else "none"
            note = "baseline signatures materially collapsed in this setting"
        elif distinct_signatures == len(reference_signatures) and reference_match:
            status = "collapse_unchanged"
            support_level = "full"
            note = "baseline signatures matched the Feature 021 reference profile"
        elif distinct_signatures > len(reference_signatures):
            status = "robust_collapse_reduced"
            support_level = "full"
            note = "reduced collapse survived this setting and improved differentiation"
        elif distinct_signatures < len(reference_signatures):
            status = "fragile_collapse_reduced"
            support_level = "partial"
            note = "this setting reduced differentiation relative to Feature 021"
        else:
            status = "collapse_unchanged"
            support_level = "full"
            note = "baseline diversity remained materially unchanged"
        return _AuditRunResult(setting, signatures, distinct_signatures, reference_match, status, support_level, note)

    def _gate_status(self) -> dict[str, Any]:
        validation = validate_feature_gates(*self.gate_paths)
        return validation.to_dict()

    def run(self) -> BaselineRebuildSensitivityAuditReport:
        source_gate_status = self._gate_status()
        if not source_gate_status["passed"]:
            raise RuntimeError(f"Feature gates not satisfied: {source_gate_status}")

        reference_report = self._reference_report()
        reference_signatures = self._reference_signature_set(reference_report)
        supported_settings = list(build_sensitivity_settings())
        audit_runs = [self._summarize_setting(setting, reference_signatures) for setting in supported_settings]
        setting_signatures = [
            SettingSignature(
                seed=item.setting.seed,
                scenario_name=item.setting.scenario_name,
                episode_length=item.setting.episode_length,
                baseline_signatures=item.baseline_signatures,
                distinct_signatures=item.distinct_signatures,
                reference_match=item.reference_match,
                notes=[item.note],
            )
            for item in audit_runs
        ]
        assessment = classify_sensitivity_audit(
            reference_signatures=reference_report.get("collapse_indicators", []),
            setting_signatures=setting_signatures,
            supported_settings=supported_settings,
        )

        report = BaselineRebuildSensitivityAuditReport(
            metadata={
                "feature_id": "022-baseline-rebuild-sensitivity-audit",
                "generated_by": "baseline_rebuild_sensitivity_audit",
                "deterministic": True,
                "source_refs": [
                    "specs/022-baseline-rebuild-sensitivity-audit/spec.md",
                    "specs/022-baseline-rebuild-sensitivity-audit/plan.md",
                    "specs/022-baseline-rebuild-sensitivity-audit/research.md",
                    "src/evaluation/matrix_runner.py",
                    "src/evaluation/matrix_config.py",
                    "src/evaluation/policy_registry.py",
                    "src/evaluation/scenario_registry.py",
                    "src/environment/gym_adapter.py",
                ],
            },
            source_gate_status=source_gate_status,
            sensitivity_dimensions={
                "seeds": list(FIXED_SEEDS),
                "scenarios": list(FIXED_SCENARIOS),
                "episode_lengths": list(FIXED_EPISODE_LENGTHS),
                "baseline_signature_fields": ["completed_tasks", "dropped_tasks", "throughput", "average_delay"],
            },
            seeds_scenarios_episode_lengths_used={
                "seeds": list(FIXED_SEEDS),
                "scenarios": list(FIXED_SCENARIOS),
                "episode_lengths": list(FIXED_EPISODE_LENGTHS),
                "supported_settings": len(supported_settings),
            },
            fairness_controls={
                "shared_environment_interface": "HoodieGymEnvironment via EvaluationMatrixRunner",
                "identical_workload": True,
                "identical_topology": True,
                "identical_deadline_rules": True,
                "identical_reward_timing": True,
                "identical_metric_definitions": True,
            },
            included_baselines=list(supported_baseline_policies()),
            reused_metrics=list(REUSED_METRICS),
            per_setting_baseline_signatures=[
                {
                    "seed": item.seed,
                    "scenario_name": item.scenario_name,
                    "episode_length": item.episode_length,
                    "baseline_signatures": dict(item.baseline_signatures),
                    "distinct_signatures": item.distinct_signatures,
                    "reference_match": item.reference_match,
                    "notes": list(item.notes),
                }
                for item in setting_signatures
            ],
            collapse_stability_indicators=[item.to_indicator() for item in audit_runs],
            sensitivity_classification=assessment.to_dict(),
            limitations=[
                "Diagnostic only.",
                "No baseline campaign-scale reproduction was run.",
                "Unsupported controls remain inconclusive rather than being fabricated.",
            ],
            no_training_disclaimer="This audit does not add training, DRL, or neural-network code.",
            no_policy_redesign_disclaimer="This audit does not redesign policies or introduce new baseline algorithms.",
            no_metric_change_disclaimer="This audit does not change metric formulas.",
            no_paper_validity_disclaimer="This audit is not a paper-validity or reproduction-completeness claim.",
            reproducibility={
                "approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "fixed_seeds": list(FIXED_SEEDS),
                "deterministic_ordering": "gates -> settings -> policy matrix -> signatures -> classification",
                "run_count_per_value": 1,
                "output_dir": str(self.output_dir),
            },
            overall_status=assessment.status,
        )
        write_baseline_rebuild_sensitivity_audit_report(report, self.output_dir)
        return report


def run_baseline_rebuild_sensitivity_audit(output_dir: Path | str | None = None) -> BaselineRebuildSensitivityAuditReport:
    return BaselineRebuildSensitivityAuditRunner(output_dir=output_dir).run()
