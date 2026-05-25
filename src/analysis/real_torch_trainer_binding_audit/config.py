from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "060a-real-torch-trainer-binding-audit"
BRANCH_NAME = "060a-real-torch-trainer-binding-audit"
BASE_BRANCH = "060-full-paper-default-training-campaign-execution"
READY_NEXT_FEATURE = "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit"
REPAIR_NEXT_FEATURE = "Feature 060B — Bind Full Campaign Execution to Real Torch Trainer"

OUTPUT_DIR = Path("artifacts/analysis/real-torch-trainer-binding-audit")
REPORT_JSON = OUTPUT_DIR / "real-torch-trainer-binding-audit-report.json"
REPORT_MD = OUTPUT_DIR / "real-torch-trainer-binding-audit-report.md"

EXPECTED_PYTHON3 = Path("src/.venvmac/bin/python3")
FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060_RUNNER = Path("src/analysis/full_paper_default_training_campaign_execution/runner.py")
FEATURE_060_CONFIG = Path("src/analysis/full_paper_default_training_campaign_execution/config.py")

REAL_TRAINER_CANDIDATE_PATHS = (
    Path("src/agents/torchrl_hoodie_learner.py"),
    Path("src/analysis/full_training_reproduction_campaign"),
    Path("src/analysis/paper_hoodie_network_implementation"),
)

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/real-torch-trainer-binding-audit/",
    "specs/060a-real-torch-trainer-binding-audit/",
    "src/analysis/real_torch_trainer_binding_audit/",
    "tests/unit/test_real_torch_trainer_binding_audit",
    "tests/integration/test_real_torch_trainer_binding_audit",
)

FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    ".gitignore",
    "src/environment/",
    "src/policies/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/full-paper-default-training-campaign-gate/",
    "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
    "artifacts/analysis/paper-default-pilot-training-run/",
    "artifacts/analysis/target-update-replay-training-validation/",
    "artifacts/analysis/paper-default-training-smoke-run/",
)

DEPENDENCY_FILE_NAMES = {
    "Pipfile",
    "poetry.lock",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "uv.lock",
}

REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "prerequisite_tags_verified",
    "python_environment_summary",
    "torch_availability_summary",
    "feature_060_claim_summary",
    "feature_060_code_binding_summary",
    "real_trainer_candidate_summary",
    "simulation_fallback_summary",
    "binding_audit_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)


@dataclass(frozen=True, slots=True)
class RealTorchTrainerBindingAuditConfig:
    feature_id: str = FEATURE_ID
    branch_name: str = BRANCH_NAME
    base_branch: str = BASE_BRANCH
    output_dir: Path = OUTPUT_DIR
    report_json: Path = REPORT_JSON
    report_md: Path = REPORT_MD
    expected_python3: Path = EXPECTED_PYTHON3
    feature_060_report: Path = FEATURE_060_REPORT
    feature_060_runner: Path = FEATURE_060_RUNNER
    feature_060_config: Path = FEATURE_060_CONFIG
    candidate_paths: tuple[Path, ...] = REAL_TRAINER_CANDIDATE_PATHS

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 060a-real-torch-trainer-binding-audit")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must remain 060a-real-torch-trainer-binding-audit")
        if self.base_branch != BASE_BRANCH:
            raise ValueError("Feature 060A must diff against the Feature 060 branch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "branch_name": self.branch_name,
            "base_branch": self.base_branch,
            "output_dir": str(self.output_dir),
            "report_json": str(self.report_json),
            "report_md": str(self.report_md),
            "expected_python3": str(self.expected_python3),
            "feature_060_report": str(self.feature_060_report),
            "feature_060_runner": str(self.feature_060_runner),
            "feature_060_config": str(self.feature_060_config),
            "candidate_paths": [str(path) for path in self.candidate_paths],
        }
