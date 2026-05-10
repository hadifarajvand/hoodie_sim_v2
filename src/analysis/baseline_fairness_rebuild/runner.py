from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Any

from src.evaluation.matrix_config import EvaluationMatrixConfig
from src.evaluation.matrix_runner import EvaluationMatrixRunner
from src.evaluation.policy_registry import PolicyRegistry
from src.evaluation.scenario_registry import ScenarioRegistry

from .classify import classify_collapse
from .gates import validate_feature_gates
from .report import DEFAULT_OUTPUT_DIR, BaselineFairnessRebuildReport, write_baseline_fairness_rebuild_report


@dataclass(slots=True)
class BaselineFairnessRebuildRunner:
    output_dir: Path | str | None = None
    gate_paths: tuple[Path, Path, Path] = (
        Path("artifacts/analysis/differential-environment-audit/differential-audit.json"),
        Path("artifacts/analysis/mechanism-repair/repair-summary.json"),
        Path("artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json"),
    )

    def _baseline_policies(self) -> tuple[str, ...]:
        return PolicyRegistry.supported_names()

    def _scenarios(self) -> tuple[str, ...]:
        return ("paper_default", "moderate")

    def _seeds(self) -> tuple[int, ...]:
        return (7,)

    def _matrix_config(self, output_dir: Path) -> EvaluationMatrixConfig:
        return EvaluationMatrixConfig(
            policy_names=self._baseline_policies(),
            scenario_names=self._scenarios(),
            seeds=self._seeds(),
            output_dir=output_dir,
            episode_length=4,
            dependency_change_note="No dependency files changed.",
        )

    def _scenario_traces(self) -> list[dict[str, Any]]:
        traces: list[dict[str, Any]] = []
        for scenario_name in self._scenarios():
            scenario = ScenarioRegistry.resolve(scenario_name, 4)
            traces.append(
                {
                    "scenario_name": scenario_name,
                    "episode_length": scenario.episode_length,
                    "trace_id": f"{scenario_name}-7",
                    "seed": 7,
                }
            )
        return traces

    def _collapse_indicators(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        indicators: list[dict[str, Any]] = []
        for result in results:
            metrics = result.get("final_metrics", {})
            indicators.append(
                {
                    "policy_name": result.get("policy_name"),
                    "scenario_name": result.get("scenario_name"),
                    "signature": f"completed={metrics.get('completed_tasks', 0)}|dropped={metrics.get('dropped_tasks', 0)}|throughput={metrics.get('throughput', 0)}",
                }
            )
        return indicators

    def _fairness_controls(self) -> dict[str, Any]:
        return {
            "shared_environment_interface": "HoodieGymEnvironment via EvaluationMatrixRunner",
            "identical_workload": True,
            "identical_topology": True,
            "identical_deadline_rules": True,
            "identical_reward_timing": True,
            "identical_metric_definitions": True,
        }

    def _source_gate_status(self) -> dict[str, Any]:
        validation = validate_feature_gates(*self.gate_paths)
        return validation.to_dict()

    def run(self) -> BaselineFairnessRebuildReport:
        source_gate_status = self._source_gate_status()
        if not source_gate_status["passed"]:
            raise RuntimeError(f"Feature gates not satisfied: {source_gate_status}")

        output_dir = Path(self.output_dir) if self.output_dir is not None else DEFAULT_OUTPUT_DIR
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix_output_dir = Path(tmpdir) / "matrix"
            matrix_result = EvaluationMatrixRunner(self._matrix_config(matrix_output_dir)).run()

        results = list(matrix_result["results"])
        assessment = classify_collapse(results)
        overall_status = assessment.status if assessment.status in {"collapse_reduced", "collapse_unchanged", "collapse_worsened", "inconclusive"} else "inconclusive"

        report = BaselineFairnessRebuildReport(
            metadata={
                "feature_id": "021-baseline-fairness-rebuild",
                "generated_by": "baseline_fairness_rebuild",
                "deterministic": True,
                "source_refs": [
                    "specs/021-baseline-fairness-rebuild/spec.md",
                    "specs/021-baseline-fairness-rebuild/plan.md",
                    "specs/021-baseline-fairness-rebuild/research.md",
                    "src/evaluation/matrix_runner.py",
                    "src/evaluation/policy_registry.py",
                    "src/evaluation/scenario_registry.py",
                    "src/environment/gym_adapter.py",
                ],
            },
            source_gate_status=source_gate_status,
            baseline_policies_included=list(self._baseline_policies()),
            scenarios_traces_used=self._scenario_traces(),
            fairness_controls=self._fairness_controls(),
            metrics_reused=["completed_tasks", "dropped_tasks", "throughput", "average_delay", "drop_ratio"],
            collapse_indicators=self._collapse_indicators(results),
            anti_collapse_assessment={
                "status": assessment.status,
                "policy_diversity": assessment.policy_diversity,
                "evidence": assessment.notes,
            },
            unchanged_collapse_explanation="Persistent collapse remains a valid mechanism property when policy signatures do not differentiate materially.",
            limitations=[
                "Diagnostic only.",
                "No baseline campaign-scale reproduction was run.",
                "No policy redesign or training foundation work is implied.",
            ],
            no_training_disclaimer="This report does not add training or claim training-driven improvement.",
            no_policy_redesign_disclaimer="This report does not redesign policies or claim that policy redesign is required.",
            no_paper_validity_disclaimer="This report is not a paper-validity or reproduction-completeness claim.",
            reproducibility_details={
                "approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "fixed_seeds": list(self._seeds()),
                "run_count_per_value": 1,
                "trace_order": "policy -> scenario -> seed",
                "output_dir": str(output_dir),
            },
            overall_status=overall_status,
        )
        write_baseline_fairness_rebuild_report(report, output_dir)
        return report
