from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "060b-bind-full-campaign-real-torch-trainer"
BRANCH_NAME = "060b-bind-full-campaign-real-torch-trainer"
BASE_BRANCH = "060-full-paper-default-training-campaign-execution"
READY_NEXT_FEATURE = "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit"

OUTPUT_DIR = Path("artifacts/analysis/bind-full-campaign-real-torch-trainer")
REPORT_JSON = OUTPUT_DIR / "bind-full-campaign-real-torch-trainer-report.json"
REPORT_MD = OUTPUT_DIR / "bind-full-campaign-real-torch-trainer-report.md"

REPO_VENV_PYTHON = Path(".venv/bin/python")
FEATURE_060A_REPORT = Path("artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json")
FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060_RUNNER = Path("src/analysis/full_paper_default_training_campaign_execution/runner.py")
FEATURE_060_BRIDGE = Path("src/analysis/full_paper_default_training_campaign_execution/real_trainer_bridge.py")

FEATURE_060_ARTIFACTS = {
    "full_campaign_json_report": Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json"),
    "full_campaign_markdown_report": Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md"),
    "training_metrics_json": Path("artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json"),
    "evaluation_metrics_json": Path("artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json"),
    "checkpoint_metadata_json": Path("artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json"),
    "run_manifest_json": Path("artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json"),
}

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/real-torch-trainer-binding-audit/",
    "specs/060a-real-torch-trainer-binding-audit/",
    "specs/060b-bind-full-campaign-real-torch-trainer/",
    "src/analysis/real_torch_trainer_binding_audit/",
    "src/analysis/bind_full_campaign_real_torch_trainer/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "tests/unit/test_real_torch_trainer_binding_audit",
    "tests/unit/test_bind_full_campaign_real_torch_trainer",
    "tests/integration/test_real_torch_trainer_binding_audit",
    "tests/integration/test_bind_full_campaign_real_torch_trainer",
)

FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    ".gitignore",
    "src/environment/",
    "src/policies/",
)
DEPENDENCY_FILE_NAMES = {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "poetry.lock", "uv.lock", "Pipfile"}

REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "prerequisite_tags_verified",
    "feature_060a_audit_verified",
    "torch_environment_summary",
    "real_trainer_binding_summary",
    "feature_060_repair_summary",
    "campaign_execution_summary",
    "training_metrics_summary",
    "evaluation_metrics_summary",
    "artifact_regeneration_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)


@dataclass(frozen=True, slots=True)
class BindFullCampaignRealTorchTrainerConfig:
    feature_id: str = FEATURE_ID
    branch_name: str = BRANCH_NAME
    base_branch: str = BASE_BRANCH
    repo_venv_python: Path = REPO_VENV_PYTHON
    output_dir: Path = OUTPUT_DIR

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 060b-bind-full-campaign-real-torch-trainer")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "branch_name": self.branch_name,
            "base_branch": self.base_branch,
            "repo_venv_python": str(self.repo_venv_python),
            "output_dir": str(self.output_dir),
        }
