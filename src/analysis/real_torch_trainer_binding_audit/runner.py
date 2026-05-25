from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import (
    APPROVED_PATH_PREFIXES,
    BASE_BRANCH,
    BRANCH_NAME,
    DEPENDENCY_FILE_NAMES,
    EXPECTED_PYTHON3,
    FEATURE_ID,
    FORBIDDEN_PATH_PREFIXES,
    READY_NEXT_FEATURE,
    REPAIR_NEXT_FEATURE,
    REPORT_JSON,
    REPORT_MD,
    RealTorchTrainerBindingAuditConfig,
)
from .model import RealTorchTrainerBindingAuditReport, REPAIR_ROUTING
from .report import write_real_torch_trainer_binding_audit_report

REAL_TRAINER_CANDIDATE_NAMES = (
    "DDQNTrainer",
    "TorchRLHoodieLearner",
    "CampaignPolicy",
    "PaperHoodieDuelingNetwork",
    "build_online_network",
    "build_target_network",
    "run_pilot_training",
    "run_campaign_evaluation",
    "run_campaign",
)

REAL_TRAINER_MODULE_HINTS = (
    "src.agents.torchrl_hoodie_learner",
    "src.analysis.full_training_reproduction_campaign",
    "src.analysis.paper_hoodie_network_implementation",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    return [line[3:].strip() for line in output.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    return [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]


def _diff_names(base_branch: str = BASE_BRANCH) -> list[str]:
    return [line for line in _git_output("diff", "--name-only", f"{base_branch}...HEAD").splitlines() if line]


def _approved_paths(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _forbidden_paths(paths: list[str]) -> list[str]:
    forbidden: list[str] = []
    for path in paths:
        if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES) or Path(path).name in DEPENDENCY_FILE_NAMES:
            forbidden.append(path)
    return forbidden


def _run_python_probe(interpreter: Path, code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(interpreter), "-c", code], check=False, capture_output=True, text=True)


def _pip_show_present(interpreter: Path, package_name: str) -> bool:
    result = subprocess.run([str(interpreter), "-m", "pip", "show", package_name], check=False, capture_output=True, text=True)
    return result.returncode == 0 and f"Name: {package_name}" in result.stdout


def _python_environment_summary(config: RealTorchTrainerBindingAuditConfig) -> dict[str, Any]:
    which_python3 = shutil.which("python3") or ""
    expected_python3 = str(config.expected_python3)
    return {
        "which_python3": which_python3,
        "sys_executable": sys.executable,
        "same_interpreter_expected": sys.executable == expected_python3 or which_python3 == expected_python3,
        "expected_python3": expected_python3,
        "expected_python3_exists": config.expected_python3.exists(),
        "torch_probe_interpreter": expected_python3 if config.expected_python3.exists() else sys.executable,
    }


def _torch_availability_summary(config: RealTorchTrainerBindingAuditConfig) -> dict[str, Any]:
    interpreter = config.expected_python3 if config.expected_python3.exists() else Path(sys.executable)
    find_spec_result = _run_python_probe(
        interpreter,
        "import importlib.util; "
        "print(importlib.util.find_spec('torch') is not None); "
        "print(importlib.util.find_spec('torchrl') is not None)",
    )
    find_spec_lines = [line.strip() for line in find_spec_result.stdout.splitlines()]
    torch_find_spec_available = len(find_spec_lines) > 0 and find_spec_lines[0] == "True"
    torchrl_find_spec_available = len(find_spec_lines) > 1 and find_spec_lines[1] == "True"
    torch_version_result = _run_python_probe(interpreter, "import torch; print(torch.__version__)")
    torch_import_available = torch_version_result.returncode == 0
    return {
        "torch_find_spec_available": torch_find_spec_available,
        "torchrl_find_spec_available": torchrl_find_spec_available,
        "torch_import_available": torch_import_available,
        "torch_version": torch_version_result.stdout.strip() if torch_import_available else None,
        "torch_pip_show_present": _pip_show_present(interpreter, "torch"),
        "torchrl_pip_show_present": _pip_show_present(interpreter, "torchrl"),
        "interpreter_used": str(interpreter),
    }


def _feature_060_claim_summary(report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        return {
            "feature_060_report_exists": False,
            "feature_060_final_verdict": None,
            "feature_060_recommended_next_feature": None,
            "feature_060_remaining_blockers": None,
            "feature_060_claims_campaign_execution_passed": False,
        }
    payload = _load_json(report_path)
    verdict = payload.get("final_verdict")
    blockers = payload.get("remaining_blockers")
    return {
        "feature_060_report_exists": True,
        "feature_060_final_verdict": verdict,
        "feature_060_recommended_next_feature": payload.get("recommended_next_feature"),
        "feature_060_remaining_blockers": blockers,
        "feature_060_claims_campaign_execution_passed": verdict == "full_paper_default_training_campaign_execution_passed" and blockers == [],
    }


def _module_imports(tree: ast.AST) -> tuple[set[str], set[str]]:
    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
                imported_names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_modules.add(module)
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
    return imported_modules, imported_names


def _called_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
                if isinstance(func.value, ast.Name):
                    names.add(f"{func.value.id}.{func.attr}")
    return names


def _feature_060_code_binding_summary(runner_path: Path, candidate_names: list[str]) -> dict[str, Any]:
    if not runner_path.exists():
        return {
            "runner_exists": False,
            "runner_imports_torch": False,
            "runner_imports_torchrl": False,
            "runner_imports_real_trainer_candidate": False,
            "runner_instantiates_real_trainer_candidate": False,
            "runner_executes_real_trainer_update_or_fit": False,
            "runner_uses_scalar_fallback_campaign": False,
            "referenced_candidate_names": [],
        }
    source = runner_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules, imported_names = _module_imports(tree)
    calls = _called_names(tree)
    referenced_candidates = sorted(name for name in candidate_names if re.search(rf"\b{re.escape(name)}\b", source))
    imports_real_module = any(
        module == hint or module.startswith(f"{hint}.") for module in imported_modules for hint in REAL_TRAINER_MODULE_HINTS
    )
    imports_real_name = bool(set(candidate_names).intersection(imported_names))
    instantiates = bool(set(candidate_names).intersection(calls))
    trainer_execution_calls = {"update", "fit", "train", "run_pilot", "run_full_candidate", "run_campaign", "run_pilot_training", "run_campaign_evaluation", "_train_batch"}
    executes = bool(calls.intersection(trainer_execution_calls)) and instantiates
    fallback = _simulation_fallback_summary(runner_path)["scalar_fallback_detected"]
    return {
        "runner_exists": True,
        "runner_imports_torch": "torch" in imported_modules or "torch" in imported_names,
        "runner_imports_torchrl": "torchrl" in imported_modules or "torchrl" in imported_names,
        "runner_imports_real_trainer_candidate": imports_real_module or imports_real_name,
        "runner_instantiates_real_trainer_candidate": instantiates,
        "runner_executes_real_trainer_update_or_fit": executes,
        "runner_uses_scalar_fallback_campaign": fallback,
        "referenced_candidate_names": referenced_candidates,
    }


def _candidate_summary(config: RealTorchTrainerBindingAuditConfig, runner_source: str = "") -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for configured_path in config.candidate_paths:
        paths = [configured_path] if configured_path.is_file() else sorted(configured_path.glob("*.py")) if configured_path.exists() else []
        for path in paths:
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            names: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if any(token in node.name for token in ("Trainer", "Learner", "Network", "Policy")) or node.name in REAL_TRAINER_CANDIDATE_NAMES:
                        names.append(node.name)
            if names:
                candidates.append(
                    {
                        "candidate_path": str(path),
                        "candidate_names": sorted(set(names)),
                        "feature_060_references_candidate": any(re.search(rf"\b{re.escape(name)}\b", runner_source) for name in names),
                    }
                )
    feature_060_referenced = sorted(
        {
            name
            for candidate in candidates
            for name in candidate["candidate_names"]
            if re.search(rf"\b{re.escape(name)}\b", runner_source)
        }
    )
    return {
        "candidate_count": len(candidates),
        "candidates": candidates,
        "feature_060_referenced_candidate_names": feature_060_referenced,
    }


def _simulation_fallback_summary(runner_path: Path) -> dict[str, Any]:
    source = runner_path.read_text(encoding="utf-8") if runner_path.exists() else ""
    random_random_used = "random.Random" in source
    manual_replay = "replay: list" in source and ".append(" in source and '"replay"' in source
    manual_scalar_loss = "scalar_weight" in source and "loss = (scalar_weight - target) ** 2" in source
    manual_optimizer = "optimizer_step_count += 1" in source
    manual_target = "target_sync_count" in source and "optimizer_step_count // 2000" in source
    torch_absent = not any(marker in source for marker in ("import torch", "from torch", "torch.", "torch.optim", "nn.Module", "Tensor("))
    scalar_fallback = any((random_random_used, manual_replay, manual_scalar_loss, manual_optimizer, manual_target)) and torch_absent
    return {
        "random_random_used": random_random_used,
        "manual_replay_list_construction": manual_replay,
        "manual_scalar_loss_calculation": manual_scalar_loss,
        "manual_optimizer_step_count_increment": manual_optimizer,
        "manual_target_sync_count_calculation": manual_target,
        "torch_tensor_module_optimizer_absent": torch_absent,
        "scalar_fallback_detected": scalar_fallback,
    }


def _build_prerequisite_tags_verified(config: RealTorchTrainerBindingAuditConfig) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names(config.base_branch)
    all_paths = status_paths + staged_paths + diff_paths
    return [
        {"name": "branch", "verified": branch == BRANCH_NAME, "details": f"git branch --show-current == {BRANCH_NAME}"},
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "base_branch_is_ancestor", "verified": _git_bool("merge-base", "--is-ancestor", config.base_branch, "HEAD"), "details": f"{config.base_branch} is an ancestor of HEAD"},
        {"name": "feature_060_report_present", "verified": config.feature_060_report.exists(), "details": str(config.feature_060_report)},
        {"name": "feature_060_runner_present", "verified": config.feature_060_runner.exists(), "details": str(config.feature_060_runner)},
        {"name": "feature_060_config_present", "verified": config.feature_060_config.exists(), "details": str(config.feature_060_config)},
        {"name": "real_trainer_candidate_inputs_present", "verified": all(path.exists() for path in config.candidate_paths), "details": [str(path) for path in config.candidate_paths]},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(status_paths), "details": "git status --short contains only approved Feature 060A paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 060A paths"},
        {"name": "feature_branch_diff_paths_approved", "verified": _approved_paths(diff_paths), "details": f"git diff --name-only {config.base_branch}...HEAD contains only approved Feature 060A paths"},
        {"name": "forbidden_paths_absent", "verified": not _forbidden_paths(all_paths), "details": _forbidden_paths(all_paths)},
        {"name": "expected_venv_python_available", "verified": config.expected_python3.exists(), "details": str(config.expected_python3)},
    ]


def _binding_blockers(
    *,
    torch_summary: dict[str, Any],
    claim_summary: dict[str, Any],
    binding_summary: dict[str, Any],
    fallback_summary: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not binding_summary["runner_imports_torch"]:
        blockers.append("feature_060_runner_missing_torch_import")
    if not binding_summary["runner_imports_torchrl"]:
        blockers.append("feature_060_runner_missing_torchrl_import")
    if not binding_summary["runner_imports_real_trainer_candidate"]:
        blockers.append("feature_060_runner_missing_real_trainer_import")
    if not binding_summary["runner_instantiates_real_trainer_candidate"]:
        blockers.append("feature_060_runner_missing_real_trainer_instantiation")
    if not binding_summary["runner_executes_real_trainer_update_or_fit"]:
        blockers.append("feature_060_runner_missing_real_trainer_update_fit_train_call")
    if binding_summary["runner_uses_scalar_fallback_campaign"] or fallback_summary["scalar_fallback_detected"]:
        blockers.append("feature_060_runner_uses_scalar_fallback_campaign")
    if fallback_summary["torch_tensor_module_optimizer_absent"]:
        blockers.append("feature_060_runner_absent_torch_tensor_module_optimizer_execution")
    if claim_summary["feature_060_claims_campaign_execution_passed"] and blockers:
        blockers.append("feature_060_claim_not_supported_by_real_trainer_binding")
    if not all(
        torch_summary[key]
        for key in (
            "torch_find_spec_available",
            "torchrl_find_spec_available",
            "torch_import_available",
            "torch_pip_show_present",
            "torchrl_pip_show_present",
        )
    ):
        blockers.append("torch_or_torchrl_unavailable_in_probe_interpreter")
    return blockers


def build_real_torch_trainer_binding_audit_report(
    config: RealTorchTrainerBindingAuditConfig | None = None,
) -> RealTorchTrainerBindingAuditReport:
    cfg = config or RealTorchTrainerBindingAuditConfig()
    prerequisite_tags_verified = _build_prerequisite_tags_verified(cfg)
    failed_scope_tags = [
        str(tag["name"])
        for tag in prerequisite_tags_verified
        if tag.get("verified") is not True
        and tag.get("name")
        in {
            "branch",
            "not_main",
            "base_branch_is_ancestor",
            "working_tree_paths_approved",
            "staged_paths_approved",
            "feature_branch_diff_paths_approved",
            "forbidden_paths_absent",
        }
    ]
    python_summary = _python_environment_summary(cfg)
    torch_summary = _torch_availability_summary(cfg)
    claim_summary = _feature_060_claim_summary(cfg.feature_060_report)
    runner_source = cfg.feature_060_runner.read_text(encoding="utf-8") if cfg.feature_060_runner.exists() else ""
    candidate_summary = _candidate_summary(cfg, runner_source=runner_source)
    candidate_names = sorted({name for candidate in candidate_summary["candidates"] for name in candidate["candidate_names"]} | set(REAL_TRAINER_CANDIDATE_NAMES))
    binding_summary = _feature_060_code_binding_summary(cfg.feature_060_runner, candidate_names)
    fallback_summary = _simulation_fallback_summary(cfg.feature_060_runner)

    environment_supports_real_binding = all(
        torch_summary[key]
        for key in (
            "torch_find_spec_available",
            "torchrl_find_spec_available",
            "torch_import_available",
            "torch_pip_show_present",
            "torchrl_pip_show_present",
        )
    )
    real_binding_verified = (
        environment_supports_real_binding
        and binding_summary["runner_imports_torch"]
        and binding_summary["runner_imports_torchrl"]
        and binding_summary["runner_imports_real_trainer_candidate"]
        and binding_summary["runner_instantiates_real_trainer_candidate"]
        and binding_summary["runner_executes_real_trainer_update_or_fit"]
        and not binding_summary["runner_uses_scalar_fallback_campaign"]
        and not fallback_summary["scalar_fallback_detected"]
        and not fallback_summary["torch_tensor_module_optimizer_absent"]
    )
    feature_060_claim_supported = claim_summary["feature_060_claims_campaign_execution_passed"] and real_binding_verified
    binding_blockers = _binding_blockers(
        torch_summary=torch_summary,
        claim_summary=claim_summary,
        binding_summary=binding_summary,
        fallback_summary=fallback_summary,
    )

    if failed_scope_tags:
        final_verdict = "audit_scope_blocked"
        blockers = failed_scope_tags
    elif not claim_summary["feature_060_report_exists"]:
        final_verdict = "feature_060_artifact_missing"
        blockers = ["feature_060_report_missing"]
    elif not binding_summary["runner_exists"] or not cfg.feature_060_config.exists():
        final_verdict = "feature_060_code_missing"
        blockers = [
            name
            for name, present in (
                ("feature_060_runner_missing", binding_summary["runner_exists"]),
                ("feature_060_config_missing", cfg.feature_060_config.exists()),
            )
            if not present
        ]
    elif not environment_supports_real_binding:
        final_verdict = "torch_environment_blocked"
        blockers = [blocker for blocker in binding_blockers if blocker == "torch_or_torchrl_unavailable_in_probe_interpreter"]
    elif real_binding_verified:
        final_verdict = "real_torch_trainer_binding_verified"
        blockers = []
    else:
        final_verdict = "real_torch_trainer_binding_missing_repair_required"
        blockers = [blocker for blocker in binding_blockers if blocker != "torch_or_torchrl_unavailable_in_probe_interpreter"]

    recommended_next_feature = READY_NEXT_FEATURE if final_verdict == "real_torch_trainer_binding_verified" else REPAIR_ROUTING[final_verdict]
    binding_audit_summary = {
        "environment_supports_real_binding": environment_supports_real_binding,
        "real_binding_verified": real_binding_verified,
        "feature_060_claim_supported": feature_060_claim_supported,
        "repair_required": final_verdict != "real_torch_trainer_binding_verified",
        "repair_feature": None if final_verdict == "real_torch_trainer_binding_verified" else REPAIR_NEXT_FEATURE,
    }

    report = RealTorchTrainerBindingAuditReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        python_environment_summary=python_summary,
        torch_availability_summary=torch_summary,
        feature_060_claim_summary=claim_summary,
        feature_060_code_binding_summary=binding_summary,
        real_trainer_candidate_summary=candidate_summary,
        simulation_fallback_summary=fallback_summary,
        binding_audit_summary=binding_audit_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )
    write_real_torch_trainer_binding_audit_report(report, cfg.output_dir)
    return report


def generate_real_torch_trainer_binding_audit_artifacts(
    config: RealTorchTrainerBindingAuditConfig | None = None,
) -> tuple[RealTorchTrainerBindingAuditReport, Path, Path]:
    report = build_real_torch_trainer_binding_audit_report(config)
    return report, REPORT_JSON, REPORT_MD


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Feature 060A real Torch trainer binding audit.")
    parser.parse_args(argv)
    report, json_path, md_path = generate_real_torch_trainer_binding_audit_artifacts()
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"final_verdict = {report.final_verdict}")
    print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
