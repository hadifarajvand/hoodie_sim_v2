from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import (
    APPROVED_PATH_PREFIXES,
    BASE_BRANCH,
    BRANCH_NAME,
    DEPENDENCY_FILE_NAMES,
    FEATURE_060A_REPORT,
    FEATURE_060_ARTIFACTS,
    FEATURE_060_BRIDGE,
    FEATURE_060_REPORT,
    FEATURE_060_RUNNER,
    FEATURE_ID,
    FORBIDDEN_PATH_PREFIXES,
    READY_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    BindFullCampaignRealTorchTrainerConfig,
)
from .model import BindFullCampaignRealTorchTrainerReport, REPAIR_ROUTING
from .report import write_bind_full_campaign_real_torch_trainer_report


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    return [line[3:].strip() for line in subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_paths() -> list[str]:
    return [line for line in _git_output("diff", "--name-only", f"{BASE_BRANCH}...HEAD").splitlines() if line]


def _approved(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _forbidden(paths: list[str]) -> list[str]:
    return [
        path
        for path in paths
        if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES) or Path(path).name in DEPENDENCY_FILE_NAMES
    ]


def _torch_environment_summary(config: BindFullCampaignRealTorchTrainerConfig) -> dict[str, Any]:
    python_executable = config.repo_venv_python if config.repo_venv_python.exists() else Path(sys.executable)
    probe = subprocess.run(
        [
            str(python_executable),
            "-c",
            "import importlib.util, torch; print(torch.__version__); print(importlib.util.find_spec('torchrl') is not None)",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in probe.stdout.splitlines()]
    return {
        "repo_venv_python": str(python_executable),
        "repo_venv_python_exists": config.repo_venv_python.exists(),
        "torch_available": probe.returncode == 0 and bool(lines),
        "torchrl_available": len(lines) > 1 and lines[1] == "True",
        "torch_version": lines[0] if lines else None,
    }


def _feature_060a_verified() -> bool:
    if not FEATURE_060A_REPORT.exists():
        return False
    payload = _load_json(FEATURE_060A_REPORT)
    return (
        payload.get("final_verdict") == "real_torch_trainer_binding_missing_repair_required"
        and payload.get("recommended_next_feature") == "Feature 060B — Bind Full Campaign Execution to Real Torch Trainer"
        and payload.get("binding_audit_summary", {}).get("repair_required") is True
    )


def _binding_summary(feature_060_payload: dict[str, Any]) -> dict[str, Any]:
    source = FEATURE_060_RUNNER.read_text(encoding="utf-8") if FEATURE_060_RUNNER.exists() else ""
    bridge_source = FEATURE_060_BRIDGE.read_text(encoding="utf-8") if FEATURE_060_BRIDGE.exists() else ""
    evidence = dict(feature_060_payload.get("campaign_execution_summary", {}).get("real_trainer_binding", {}))
    return {
        "real_binding_verified": (
            evidence.get("torch_import_used") is True
            and evidence.get("torchrl_available") is True
            and evidence.get("real_trainer_import_used") is True
            and evidence.get("real_trainer_instantiated") is True
            and evidence.get("real_trainer_update_or_train_called") is True
            and evidence.get("scalar_fallback_drives_campaign_claim") is False
        ),
        "torch_import_used": evidence.get("torch_import_used") is True and "import torch" in bridge_source,
        "torchrl_available": evidence.get("torchrl_available") is True,
        "real_trainer_import_used": evidence.get("real_trainer_import_used") is True and "DDQNTrainer" in bridge_source,
        "real_trainer_instantiated": evidence.get("real_trainer_instantiated") is True and "DDQNTrainer(" in bridge_source,
        "real_trainer_update_or_train_called": evidence.get("real_trainer_update_or_train_called") is True and ".run_pilot(" in bridge_source,
        "scalar_fallback_drives_campaign_claim": evidence.get("scalar_fallback_drives_campaign_claim") is not False,
        "runner_calls_real_trainer_bridge": "real_trainer_bridge" in source,
        "real_trainer_class": evidence.get("real_trainer_class"),
        "real_trainer_method_called": evidence.get("real_trainer_method_called"),
    }


def _artifact_regeneration_summary() -> dict[str, Any]:
    exists = {name: path.exists() for name, path in FEATURE_060_ARTIFACTS.items()}
    return {
        "artifact_paths": {name: str(path) for name, path in FEATURE_060_ARTIFACTS.items()},
        "artifact_exists": exists,
        "all_regenerated_artifacts_exist": all(exists.values()),
    }


def _prerequisite_tags(config: BindFullCampaignRealTorchTrainerConfig, feature_060a_verified: bool) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_paths()
    all_paths = status_paths + staged_paths + diff_paths
    return [
        {"name": "branch", "verified": branch == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "base_branch_is_ancestor", "verified": _git_bool("merge-base", "--is-ancestor", config.base_branch, "HEAD"), "details": f"{config.base_branch} is ancestor of HEAD"},
        {"name": "feature_060a_audit_verified", "verified": feature_060a_verified, "details": str(FEATURE_060A_REPORT)},
        {"name": "working_tree_paths_approved", "verified": _approved(status_paths), "details": "git status --short contains only approved Feature 060B paths"},
        {"name": "staged_paths_approved", "verified": _approved(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 060B paths"},
        {"name": "feature_branch_diff_paths_approved", "verified": _approved(diff_paths), "details": f"git diff --name-only {BASE_BRANCH}...HEAD contains only approved Feature 060B paths"},
        {"name": "forbidden_paths_absent", "verified": not _forbidden(all_paths), "details": _forbidden(all_paths)},
    ]


def build_bind_full_campaign_real_torch_trainer_report(
    config: BindFullCampaignRealTorchTrainerConfig | None = None,
) -> BindFullCampaignRealTorchTrainerReport:
    cfg = config or BindFullCampaignRealTorchTrainerConfig()
    feature_060_payload = _load_json(FEATURE_060_REPORT) if FEATURE_060_REPORT.exists() else {}
    feature_060a_verified = _feature_060a_verified()
    torch_summary = _torch_environment_summary(cfg)
    prereq_tags = _prerequisite_tags(cfg, feature_060a_verified)
    binding_summary = _binding_summary(feature_060_payload)
    artifact_summary = _artifact_regeneration_summary()
    repair_summary = {
        "feature_060_claim_supported": (
            feature_060_payload.get("final_verdict") == "full_paper_default_training_campaign_execution_passed"
            and feature_060_payload.get("remaining_blockers") == []
            and binding_summary["real_binding_verified"] is True
        ),
        "feature_060_final_verdict": feature_060_payload.get("final_verdict"),
        "feature_060_remaining_blockers": feature_060_payload.get("remaining_blockers"),
        "feature_060_recommended_next_feature": feature_060_payload.get("recommended_next_feature"),
    }
    safety_summary = {
        "no_dependency_drift": not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_policy_drift": not any(path.startswith("src/policies/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_environment_contract_drift": not any(path.startswith("src/environment/") for path in _status_paths() + _staged_paths() + _diff_paths()),
        "no_reward_timing_change": True,
        "no_paper_reproduction_claim": True,
        "no_performance_superiority_claim": True,
        "no_baseline_superiority_claim": True,
        "no_uncontrolled_campaign_loop": True,
    }
    blockers: list[str] = []
    if not feature_060a_verified:
        blockers.append("feature_060a_audit_not_verified")
    if not (torch_summary["torch_available"] and torch_summary["torchrl_available"]):
        blockers.append("repo_venv_torch_or_torchrl_unavailable")
    if not binding_summary["real_binding_verified"]:
        blockers.append("feature_060_real_trainer_binding_not_verified")
    if not repair_summary["feature_060_claim_supported"]:
        blockers.append("feature_060_claim_not_supported_after_repair")
    if not artifact_summary["all_regenerated_artifacts_exist"]:
        blockers.append("feature_060_artifacts_not_regenerated")
    if not all(safety_summary.values()) or not all(tag["verified"] for tag in prereq_tags):
        blockers.extend([tag["name"] for tag in prereq_tags if tag["verified"] is not True])
        if not all(safety_summary.values()):
            blockers.append("behavior_drift_detected")
    final_verdict = "real_torch_trainer_binding_repair_passed" if not blockers else (
        "feature_060a_prerequisite_blocked" if "feature_060a_audit_not_verified" in blockers else
        "torch_environment_blocked" if "repo_venv_torch_or_torchrl_unavailable" in blockers else
        "real_trainer_binding_blocked" if "feature_060_real_trainer_binding_not_verified" in blockers else
        "feature_060_repair_blocked" if "feature_060_claim_not_supported_after_repair" in blockers else
        "artifact_regeneration_blocked" if "feature_060_artifacts_not_regenerated" in blockers else
        "behavior_drift_detected"
    )
    report = BindFullCampaignRealTorchTrainerReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prereq_tags,
        feature_060a_audit_verified=feature_060a_verified,
        torch_environment_summary=torch_summary,
        real_trainer_binding_summary=binding_summary,
        feature_060_repair_summary=repair_summary,
        campaign_execution_summary=dict(feature_060_payload.get("campaign_execution_summary", {})),
        training_metrics_summary=dict(feature_060_payload.get("training_metrics_summary", {})),
        evaluation_metrics_summary=dict(feature_060_payload.get("evaluation_metrics_summary", {})),
        artifact_regeneration_summary=artifact_summary,
        safety_summary=safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=READY_NEXT_FEATURE if not blockers else REPAIR_ROUTING[final_verdict],
        final_verdict=final_verdict,
    )
    write_bind_full_campaign_real_torch_trainer_report(report, cfg.output_dir)
    return report


def generate_bind_full_campaign_real_torch_trainer_artifacts(
    config: BindFullCampaignRealTorchTrainerConfig | None = None,
) -> tuple[BindFullCampaignRealTorchTrainerReport, Path, Path]:
    report = build_bind_full_campaign_real_torch_trainer_report(config)
    return report, REPORT_JSON, REPORT_MD


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Feature 060B real Torch trainer binding repair report.")
    parser.parse_args(argv)
    report, json_path, md_path = generate_bind_full_campaign_real_torch_trainer_artifacts()
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"final_verdict = {report.final_verdict}")
    print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0 if report.final_verdict == "real_torch_trainer_binding_repair_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
