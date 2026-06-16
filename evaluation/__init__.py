from .ablation_suite import AblationConfig, build_ablation_configs, run_ablation_suite
from .evaluation_pipeline import EvaluationConsistencyError, EvaluationGuard, EvaluationGuardTriggered, EvaluationPaths, run_evaluation_pipeline, run_smoke_test
from .experimental_design import ExperimentConfig, ExperimentalCell, generate_experiment_matrix
from .fairness_validator import (
    FairnessCheckResult,
    FairnessValidationFailure,
    inject_asymmetric_workload_and_validate,
    fairness_report_from_json,
    run_fairness_validation,
    validate_equal_workload,
    validate_resource_parity,
    validate_seed_alignment,
)
from .hypotheses import Hypothesis, HypothesisRegistry
from .statistical_tests import (
    StatisticalSummary,
    cohens_d,
    compute_confidence_interval_95,
    compute_mean_std,
    one_way_anova,
    t_test_independent,
)

__all__ = [
    "AblationConfig",
    "build_ablation_configs",
    "run_ablation_suite",
    "EvaluationConsistencyError",
    "EvaluationGuard",
    "EvaluationGuardTriggered",
    "EvaluationPaths",
    "run_evaluation_pipeline",
    "run_smoke_test",
    "ExperimentConfig",
    "ExperimentalCell",
    "generate_experiment_matrix",
    "FairnessCheckResult",
    "FairnessValidationFailure",
    "inject_asymmetric_workload_and_validate",
    "fairness_report_from_json",
    "run_fairness_validation",
    "validate_equal_workload",
    "validate_resource_parity",
    "validate_seed_alignment",
    "Hypothesis",
    "HypothesisRegistry",
    "StatisticalSummary",
    "cohens_d",
    "compute_confidence_interval_95",
    "compute_mean_std",
    "one_way_anova",
    "t_test_independent",
]
