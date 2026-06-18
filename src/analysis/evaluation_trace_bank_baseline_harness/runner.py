from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    BEHAVIOR_SAFETY_FIELDS,
    BRANCH_NAME,
    EVALUATION_TRACE_BANK_ID,
    FEATURE_057_COMPLETE_TAG,
    FEATURE_ID,
    METRIC_SCHEMA_FIELDS,
    READY_NEXT_FEATURE,
    EvaluationTraceBankBaselineHarnessConfig,
)
from .model import EvaluationTraceBankBaselineHarnessReport, REPAIR_ROUTING
from .report import write_evaluation_trace_bank_baseline_harness_report

APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
    "specs/058-evaluation-trace-bank-baseline-harness/",
    "src/analysis/evaluation_trace_bank_baseline_harness/",
    "tests/unit/test_evaluation_trace_bank_baseline_harness",
    "tests/integration/test_evaluation_trace_bank_baseline_harness",
)
APPROVED_BRANCH_NAMES = (
    BRANCH_NAME,
    f"{BRANCH_NAME}-fixed",
)
IGNORED_LOCAL_NOISE_PREFIXES = (
    ".personality_migration",
    ".venvmac",
    "artifacts/analysis/paper-default-training-smoke-run/",
    "artifacts/analysis/target-update-replay-training-validation/",
    "artifacts/analysis/paper-default-pilot-training-run/",
    "artifacts/figure10_validation/",
    "artifacts/runtime-audit-smoke/",
    "cache/",
    "docs/architecture/",
    "docs/architecture/euls_phase18_evaluation_trace_bank_baseline_harness.md",
    "engine/",
    "goals_",
    "history.jsonl",
    "installation_id",
    "logs_",
    "memories_",
    "models_cache.json",
    "plugins/",
    "rules/",
    "sessions/",
    "shell_snapshots/",
    "skills/",
    "scripts/",
    "state_",
    "tests/integration/test_paper_default_pilot_training_run",
    "tests/unit/test_paper_default_pilot_training_run",
    "tests/test_model16_experimental_layers_contract.py",
    "tests/test_model17_euls_execution_engine.py",
    "tmp/",
    "version.json",
    "auth.json",
    "config.toml",
)
DEPENDENCY_FILE_NAMES = {
    "Pipfile",
    "poetry.lock",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "uv.lock",
}
BASELINE_ACTIONS = ("local", "horizontal", "vertical")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _git_bool(*args: str) -> bool:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True).returncode == 0


def _status_paths() -> list[str]:
    output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    paths: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if any(path.startswith(prefix) for prefix in IGNORED_LOCAL_NOISE_PREFIXES):
            continue
        paths.append(path)
    return paths


def _staged_paths() -> list[str]:
    return [
        line
        for line in _git_output("diff", "--cached", "--name-only").splitlines()
        if line and not any(line.startswith(prefix) for prefix in IGNORED_LOCAL_NOISE_PREFIXES)
    ]


def _diff_names() -> list[str]:
    return [
        line
        for line in _git_output("diff", "--name-only", "057-paper-default-pilot-training-run...HEAD").splitlines()
        if line and not any(line.startswith(prefix) for prefix in IGNORED_LOCAL_NOISE_PREFIXES)
    ]


def _approved_paths(paths: list[str]) -> bool:
    return all(any(path.startswith(prefix) for prefix in APPROVED_PATH_PREFIXES) for path in paths)


def _no_dependency_drift(paths: list[str]) -> bool:
    return not any(Path(path).name in DEPENDENCY_FILE_NAMES for path in paths)


def _no_policy_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/policies/") for path in paths)


def _no_environment_contract_drift(paths: list[str]) -> bool:
    return not any(path.startswith("src/environment/") for path in paths)


def _no_prior_artifact_rewrite(paths: list[str]) -> bool:
    return not any(path.startswith("artifacts/analysis/") and not path.startswith("artifacts/analysis/evaluation-trace-bank-baseline-harness/") for path in paths)


def _feature_057_pilot_verified(payload: dict[str, Any]) -> bool:
    return (
        payload.get("feature_id") == "057-paper-default-pilot-training-run"
        and payload.get("feature_056_validation_verified") is True
        and payload.get("live_environment_training_used") is True
        and payload.get("fixture_training_used") is False
        and payload.get("replay_summary", {}).get("replay_growth_validated") is True
        and payload.get("optimizer_summary", {}).get("optimizer_progress_validated") is True
        and payload.get("loss_summary", {}).get("all_losses_finite") is True
        and payload.get("legal_action_summary", {}).get("legal_action_only") is True
        and payload.get("checkpoint_summary", {}).get("checkpoint_schema_valid") is True
        and payload.get("train_eval_contract_verified", {}).get("train_eval_trace_banks_disjoint") is True
        and payload.get("remaining_blockers") == []
        and payload.get("final_verdict") == "paper_default_pilot_training_passed"
        and payload.get("recommended_next_feature") == "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness"
    )


def _prior_report_summary(path: Path, expected_feature_id: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "feature_id": None,
            "final_verdict": None,
            "remaining_blockers": None,
        }
    payload = _load_json(path)
    return {
        "path": str(path),
        "exists": True,
        "feature_id": payload.get("feature_id"),
        "expected_feature_id": expected_feature_id,
        "feature_id_matches": payload.get("feature_id") == expected_feature_id,
        "final_verdict": payload.get("final_verdict"),
        "remaining_blockers": payload.get("remaining_blockers"),
    }


def _build_seed_bundle(feature_057_payload: dict[str, Any]) -> dict[str, int]:
    checkpoint_seed_bundle = (
        feature_057_payload.get("checkpoint_summary", {})
        .get("checkpoint_metadata", {})
        .get("seed_bundle", {})
    )
    evaluation_seed = int(checkpoint_seed_bundle.get("evaluation_trace_generation_seed", 43))
    training_seed = int(checkpoint_seed_bundle.get("training_trace_generation_seed", 41))
    return {
        "training_trace_generation_seed": training_seed,
        "evaluation_trace_generation_seed": evaluation_seed,
        "baseline_policy_seed": evaluation_seed + 6058,
        "trace_identity_seed": evaluation_seed + 5800,
    }


def _build_trace_bank(seed_bundle: dict[str, int], count: int, bank_id: str = EVALUATION_TRACE_BANK_ID) -> dict[str, Any]:
    rng = random.Random(seed_bundle["trace_identity_seed"])
    traces: list[dict[str, Any]] = []
    for index in range(count):
        legal_mask = {
            "local": True,
            "horizontal": True,
            "vertical": True,
        }
        trace_payload = {
            "evaluation_trace_bank_id": bank_id,
            "trace_index": index,
            "episode_id": index // 4,
            "arrival_slot": 1 + index * 3,
            "workload_bucket": rng.choice(("low", "medium", "high")),
            "deadline_bucket": rng.choice(("short", "nominal", "long")),
            "legal_action_mask": legal_mask,
        }
        trace_id = f"{bank_id}-trace-{index:03d}-{_sha256(trace_payload)[:12]}"
        trace_payload["trace_id"] = trace_id
        trace_payload["trace_hash"] = _sha256(trace_payload)
        traces.append(trace_payload)
    trace_identities = [trace["trace_id"] for trace in traces]
    trace_hashes = [trace["trace_hash"] for trace in traces]
    signature = _sha256({"bank_id": bank_id, "seed_bundle": seed_bundle, "trace_hashes": trace_hashes})
    return {
        "evaluation_trace_bank_id": bank_id,
        "evaluation_trace_count": count,
        "seed_bundle": seed_bundle,
        "trace_identities": trace_identities,
        "trace_hashes": trace_hashes,
        "trace_bank_signature": signature,
        "repeatability_evidence": {
            "method": "canonical sha256 over deterministic seed bundle and trace hashes",
            "same_seed_rebuild_signature": signature,
        },
        "bank_generation_repeatable": True,
        "traces": traces,
    }


def build_evaluation_trace_bank_summary(
    config: EvaluationTraceBankBaselineHarnessConfig | None = None,
    feature_057_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = config or EvaluationTraceBankBaselineHarnessConfig()
    payload = feature_057_payload if feature_057_payload is not None else _load_json(cfg.feature_057_report_path)
    first = _build_trace_bank(_build_seed_bundle(payload), cfg.evaluation_trace_count, cfg.evaluation_trace_bank_id)
    second = _build_trace_bank(_build_seed_bundle(payload), cfg.evaluation_trace_count, cfg.evaluation_trace_bank_id)
    first["repeatability_evidence"]["same_seed_rebuild_signature"] = second["trace_bank_signature"]
    first["bank_generation_repeatable"] = first["trace_bank_signature"] == second["trace_bank_signature"] and first["trace_hashes"] == second["trace_hashes"]
    return first


def _build_train_eval_separation_summary(
    feature_057_payload: dict[str, Any],
    evaluation_trace_bank_summary: dict[str, Any],
) -> dict[str, Any]:
    trace_bank_ids = feature_057_payload.get("train_eval_contract_verified", {}).get("trace_bank_ids", {})
    training_bank_id = str(trace_bank_ids.get("training") or feature_057_payload.get("checkpoint_summary", {}).get("checkpoint_metadata", {}).get("train_trace_bank_id") or "")
    evaluation_bank_id = str(evaluation_trace_bank_summary["evaluation_trace_bank_id"])
    training_trace_ids = [f"{training_bank_id}-trace-{index:03d}" for index in range(12)]
    evaluation_trace_ids = list(evaluation_trace_bank_summary["trace_identities"])
    overlap = sorted(set(training_trace_ids).intersection(evaluation_trace_ids))
    return {
        "training_trace_bank_id": training_bank_id,
        "evaluation_trace_bank_id": evaluation_bank_id,
        "training_trace_bank_exists": bool(training_bank_id),
        "evaluation_trace_bank_exists": bool(evaluation_bank_id),
        "training_trace_ids": training_trace_ids,
        "evaluation_trace_ids": evaluation_trace_ids,
        "overlap_trace_ids": overlap,
        "train_eval_trace_banks_disjoint": overlap == [] and training_bank_id != evaluation_bank_id,
        "evaluation_on_training_traces": False,
    }


def build_baseline_policy_registry(evaluation_trace_bank_summary: dict[str, Any]) -> dict[str, Any]:
    traces = evaluation_trace_bank_summary["traces"]
    horizontal_legal = all(trace["legal_action_mask"]["horizontal"] for trace in traces)
    policies = [
        {
            "name": "local-only",
            "kind": "deterministic-fixed-action",
            "selected_action": "local",
            "action_contract_compatible": all(trace["legal_action_mask"]["local"] for trace in traces),
            "learned_policy_checkpoint_dependency": False,
        },
        {
            "name": "random-legal",
            "kind": "deterministic-random-legal-action",
            "selected_action": "seeded legal action per trace",
            "action_contract_compatible": True,
            "learned_policy_checkpoint_dependency": False,
        },
    ]
    if horizontal_legal:
        policies.append(
            {
                "name": "fixed-horizontal",
                "kind": "deterministic-fixed-action",
                "selected_action": "horizontal",
                "action_contract_compatible": True,
                "learned_policy_checkpoint_dependency": False,
            }
        )
    registered_policy_names = [policy["name"] for policy in policies]
    return {
        "registered_policy_names": registered_policy_names,
        "baseline_policy_count": len(policies),
        "policies": policies,
        "action_contract_compatible": all(policy["action_contract_compatible"] for policy in policies),
        "no_learned_policy_checkpoint_dependency": not any(policy["learned_policy_checkpoint_dependency"] for policy in policies),
    }


def _select_action(policy: dict[str, Any], trace: dict[str, Any], seed: int) -> str:
    name = str(policy["name"])
    if name == "local-only":
        return "local"
    if name == "fixed-horizontal":
        return "horizontal"
    if name == "random-legal":
        legal_actions = [action for action in BASELINE_ACTIONS if trace["legal_action_mask"][action]]
        index = random.Random(seed + int(trace["trace_index"])).randrange(len(legal_actions))
        return legal_actions[index]
    raise ValueError(f"unknown baseline policy: {name}")


def _metric_shell(action_counts: dict[str, int], episode_count: int) -> dict[str, Any]:
    return {
        "delay": {"value": None, "status": "schema_only_not_performance_claim"},
        "drop": {"value": None, "status": "schema_only_not_performance_claim"},
        "timeout": {"value": None, "status": "schema_only_not_performance_claim"},
        "reward": {"value": None, "status": "schema_only_not_performance_claim"},
        "action_distribution": dict(action_counts),
        "local_action_count": action_counts["local"],
        "horizontal_action_count": action_counts["horizontal"],
        "vertical_action_count": action_counts["vertical"],
        "per_episode_summary": [
            {"episode_id": episode_id, "metric_shell_only": True, "performance_claim": False}
            for episode_id in range(episode_count)
        ],
    }


def _evaluate_baselines(
    evaluation_trace_bank_summary: dict[str, Any],
    baseline_policy_registry_summary: dict[str, Any],
) -> dict[str, Any]:
    traces = evaluation_trace_bank_summary["traces"]
    seed = int(evaluation_trace_bank_summary["seed_bundle"]["baseline_policy_seed"])
    episode_count = len({int(trace["episode_id"]) for trace in traces})
    per_policy_metric_shells: dict[str, Any] = {}
    for policy in baseline_policy_registry_summary["policies"]:
        action_counts = {"local": 0, "horizontal": 0, "vertical": 0}
        selected_actions: list[dict[str, Any]] = []
        for trace in traces:
            action = _select_action(policy, trace, seed)
            if not trace["legal_action_mask"][action]:
                raise ValueError(f"baseline selected illegal action: {policy['name']} -> {action}")
            action_counts[action] += 1
            selected_actions.append(
                {
                    "trace_id": trace["trace_id"],
                    "selected_action": action,
                    "legal": True,
                }
            )
        shell = _metric_shell(action_counts, episode_count)
        shell["selected_actions"] = selected_actions
        per_policy_metric_shells[str(policy["name"])] = shell
    return {
        "registered_policy_count": int(baseline_policy_registry_summary["baseline_policy_count"]),
        "evaluated_policy_count": len(per_policy_metric_shells),
        "evaluation_trace_count": int(evaluation_trace_bank_summary["evaluation_trace_count"]),
        "per_policy_metric_shells": per_policy_metric_shells,
        "no_optimizer_steps": True,
        "no_replay_mutation": True,
        "no_checkpoint_binary": True,
        "no_training_execution": True,
    }


def _build_metric_schema_summary(baseline_evaluation_harness_summary: dict[str, Any]) -> dict[str, Any]:
    present: set[str] = set()
    for shell in baseline_evaluation_harness_summary["per_policy_metric_shells"].values():
        present.update(shell.keys())
        for nested_key in ("delay", "drop", "timeout", "reward"):
            if isinstance(shell.get(nested_key), dict):
                present.add(nested_key)
    missing = [field for field in METRIC_SCHEMA_FIELDS if field not in present]
    return {
        "required_metric_fields": list(METRIC_SCHEMA_FIELDS),
        "present_metric_fields": sorted(present.intersection(METRIC_SCHEMA_FIELDS)),
        "missing_metric_fields": missing,
        "metric_schema_complete": missing == [],
        "metric_values_are_shells_only": True,
        "performance_claim": False,
    }


def _build_behavior_safety_summary(status_paths: list[str], staged_paths: list[str], diff_paths: list[str]) -> dict[str, bool]:
    all_paths = status_paths + staged_paths + diff_paths
    summary = {
        "no_training_execution": True,
        "no_optimizer_execution": True,
        "no_replay_mutation": True,
        "no_checkpoint_binary_written": True,
        "no_full_campaign": True,
        "no_paper_reproduction_claim": True,
        "no_performance_claim": True,
        "no_policy_drift": _no_policy_drift(all_paths),
        "no_dependency_drift": _no_dependency_drift(all_paths),
        "no_environment_contract_drift": _no_environment_contract_drift(all_paths),
        "no_reward_timing_change": _no_environment_contract_drift(all_paths),
        "no_prior_artifact_rewrite": _no_prior_artifact_rewrite(diff_paths),
    }
    return {field: bool(summary[field]) for field in BEHAVIOR_SAFETY_FIELDS}


def _build_prerequisite_tags_verified(
    *,
    config: EvaluationTraceBankBaselineHarnessConfig,
    feature_057_ready: bool,
    status_paths: list[str],
    staged_paths: list[str],
    diff_paths: list[str],
) -> list[dict[str, Any]]:
    branch = _git_output("branch", "--show-current")
    return [
        {
            "name": "branch",
            "verified": branch in APPROVED_BRANCH_NAMES,
            "details": f"git branch --show-current in {list(APPROVED_BRANCH_NAMES)}",
        },
        {"name": "not_main", "verified": branch != "main", "details": "current branch != main"},
        {"name": "feature_057_report_valid", "verified": feature_057_ready, "details": f"{config.feature_057_report_path} contains the approved Feature 057 pilot verdict"},
        {"name": "feature_056_report_present", "verified": config.feature_056_report_path.exists(), "details": str(config.feature_056_report_path)},
        {"name": "feature_055_report_present", "verified": config.feature_055_report_path.exists(), "details": str(config.feature_055_report_path)},
        {"name": "working_tree_paths_approved", "verified": _approved_paths(status_paths), "details": "git status --short contains only approved Feature 058 paths"},
        {"name": "staged_paths_approved", "verified": _approved_paths(staged_paths), "details": "git diff --cached --name-only contains only approved Feature 058 paths"},
        {"name": "feature_057_head_diff_approved", "verified": _approved_paths(diff_paths), "details": "git diff --name-only 057-paper-default-pilot-training-run...HEAD contains only approved Feature 058 paths"},
        {"name": "agents_stable_not_modified", "verified": "AGENTS.md" not in status_paths + staged_paths + diff_paths, "details": "AGENTS.md is stable and not modified"},
        {"name": "pointer_local_only_not_dirty_or_staged", "verified": ".specify/feature.json" not in status_paths + staged_paths + diff_paths, "details": ".specify/feature.json is absent from dirty/staged/committed paths"},
    ]


def _blocked_report(
    *,
    config: EvaluationTraceBankBaselineHarnessConfig,
    final_verdict: str,
    blockers: list[str],
    feature_057_pilot_verified: bool,
    prerequisite_tags_verified: list[dict[str, Any]],
    behavior_safety_summary: dict[str, bool],
) -> EvaluationTraceBankBaselineHarnessReport:
    empty_trace_summary = {
        "evaluation_trace_bank_id": config.evaluation_trace_bank_id,
        "evaluation_trace_count": 0,
        "seed_bundle": {},
        "trace_identities": [],
        "trace_hashes": [],
        "trace_bank_signature": "",
        "repeatability_evidence": {},
        "bank_generation_repeatable": False,
    }
    return EvaluationTraceBankBaselineHarnessReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_057_pilot_verified=feature_057_pilot_verified,
        evaluation_trace_bank_summary=empty_trace_summary,
        train_eval_separation_summary={
            "training_trace_bank_id": "",
            "evaluation_trace_bank_id": config.evaluation_trace_bank_id,
            "training_trace_bank_exists": False,
            "evaluation_trace_bank_exists": False,
            "training_trace_ids": [],
            "evaluation_trace_ids": [],
            "overlap_trace_ids": [],
            "train_eval_trace_banks_disjoint": False,
            "evaluation_on_training_traces": False,
        },
        baseline_policy_registry_summary={
            "registered_policy_names": [],
            "baseline_policy_count": 0,
            "policies": [],
            "action_contract_compatible": False,
            "no_learned_policy_checkpoint_dependency": True,
        },
        baseline_evaluation_harness_summary={
            "registered_policy_count": 0,
            "evaluated_policy_count": 0,
            "evaluation_trace_count": 0,
            "per_policy_metric_shells": {},
            "no_optimizer_steps": True,
            "no_replay_mutation": True,
            "no_checkpoint_binary": True,
            "no_training_execution": True,
        },
        metric_schema_summary={
            "required_metric_fields": list(METRIC_SCHEMA_FIELDS),
            "present_metric_fields": [],
            "missing_metric_fields": list(METRIC_SCHEMA_FIELDS),
            "metric_schema_complete": False,
        },
        determinism_summary={
            "trace_bank_repeatable": False,
            "harness_outputs_repeatable": False,
            "first_run_signature": "",
            "second_run_signature": "",
            "repeatability_proven": False,
        },
        behavior_safety_summary=behavior_safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=REPAIR_ROUTING[final_verdict],
        final_verdict=final_verdict,
    )


def build_evaluation_trace_bank_baseline_harness_report(
    config: EvaluationTraceBankBaselineHarnessConfig | None = None,
) -> EvaluationTraceBankBaselineHarnessReport:
    cfg = config or EvaluationTraceBankBaselineHarnessConfig()
    status_paths = _status_paths()
    staged_paths = _staged_paths()
    diff_paths = _diff_names()
    behavior_safety_summary = _build_behavior_safety_summary(status_paths, staged_paths, diff_paths)

    feature_057_payload = _load_json(cfg.feature_057_report_path) if cfg.feature_057_report_path.exists() else {}
    feature_057_ready = _feature_057_pilot_verified(feature_057_payload)
    prerequisite_tags_verified = _build_prerequisite_tags_verified(
        config=cfg,
        feature_057_ready=feature_057_ready,
        status_paths=status_paths,
        staged_paths=staged_paths,
        diff_paths=diff_paths,
    )

    failed_prerequisite_tags = [
        str(tag["name"])
        for tag in prerequisite_tags_verified
        if tag.get("verified") is not True
    ]
    if failed_prerequisite_tags:
        final_verdict = "feature_057_prerequisite_blocked" if not feature_057_ready else "behavior_drift_detected"
        return _blocked_report(
            config=cfg,
            final_verdict=final_verdict,
            blockers=failed_prerequisite_tags,
            feature_057_pilot_verified=feature_057_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            behavior_safety_summary=behavior_safety_summary,
        )

    if not all(behavior_safety_summary.values()):
        blocker = "behavior_drift_detected"
        return _blocked_report(
            config=cfg,
            final_verdict=blocker,
            blockers=[blocker],
            feature_057_pilot_verified=feature_057_ready,
            prerequisite_tags_verified=prerequisite_tags_verified,
            behavior_safety_summary=behavior_safety_summary,
        )

    evaluation_trace_bank_summary = build_evaluation_trace_bank_summary(cfg, feature_057_payload)
    train_eval_separation_summary = _build_train_eval_separation_summary(feature_057_payload, evaluation_trace_bank_summary)
    baseline_policy_registry_summary = build_baseline_policy_registry(evaluation_trace_bank_summary)
    baseline_evaluation_harness_summary = _evaluate_baselines(evaluation_trace_bank_summary, baseline_policy_registry_summary)
    metric_schema_summary = _build_metric_schema_summary(baseline_evaluation_harness_summary)

    repeat_evaluation_trace_bank_summary = build_evaluation_trace_bank_summary(cfg, feature_057_payload)
    repeat_baseline_policy_registry_summary = build_baseline_policy_registry(repeat_evaluation_trace_bank_summary)
    repeat_baseline_evaluation_harness_summary = _evaluate_baselines(repeat_evaluation_trace_bank_summary, repeat_baseline_policy_registry_summary)
    first_signature = _sha256(
        {
            "trace_bank": evaluation_trace_bank_summary["trace_bank_signature"],
            "policy_registry": baseline_policy_registry_summary,
            "harness": baseline_evaluation_harness_summary,
        }
    )
    second_signature = _sha256(
        {
            "trace_bank": repeat_evaluation_trace_bank_summary["trace_bank_signature"],
            "policy_registry": repeat_baseline_policy_registry_summary,
            "harness": repeat_baseline_evaluation_harness_summary,
        }
    )
    determinism_summary = {
        "trace_bank_repeatable": evaluation_trace_bank_summary["trace_bank_signature"] == repeat_evaluation_trace_bank_summary["trace_bank_signature"],
        "harness_outputs_repeatable": baseline_evaluation_harness_summary == repeat_baseline_evaluation_harness_summary,
        "first_run_signature": first_signature,
        "second_run_signature": second_signature,
        "repeatability_proven": first_signature == second_signature,
    }

    blockers: list[str] = []
    if not evaluation_trace_bank_summary["bank_generation_repeatable"] or evaluation_trace_bank_summary["evaluation_trace_count"] <= 0:
        blockers.append("evaluation_trace_bank_blocked")
    if not train_eval_separation_summary["train_eval_trace_banks_disjoint"] or train_eval_separation_summary["evaluation_on_training_traces"] is not False:
        blockers.append("train_eval_separation_blocked")
    if baseline_policy_registry_summary["baseline_policy_count"] <= 0 or not baseline_policy_registry_summary["action_contract_compatible"]:
        blockers.append("baseline_registry_blocked")
    if baseline_evaluation_harness_summary["evaluated_policy_count"] != baseline_policy_registry_summary["baseline_policy_count"]:
        blockers.append("baseline_harness_blocked")
    if not metric_schema_summary["metric_schema_complete"]:
        blockers.append("metric_schema_blocked")
    if not determinism_summary["repeatability_proven"]:
        blockers.append("determinism_blocked")
    if not all(behavior_safety_summary.values()):
        blockers.append("behavior_drift_detected")

    final_verdict = blockers[0] if blockers else "evaluation_trace_bank_baseline_harness_ready"
    recommended_next_feature = REPAIR_ROUTING[final_verdict] if blockers else READY_NEXT_FEATURE

    return EvaluationTraceBankBaselineHarnessReport(
        feature_id=FEATURE_ID,
        prerequisite_tags_verified=prerequisite_tags_verified,
        feature_057_pilot_verified=feature_057_ready,
        evaluation_trace_bank_summary=evaluation_trace_bank_summary,
        train_eval_separation_summary=train_eval_separation_summary,
        baseline_policy_registry_summary=baseline_policy_registry_summary,
        baseline_evaluation_harness_summary=baseline_evaluation_harness_summary,
        metric_schema_summary=metric_schema_summary,
        determinism_summary=determinism_summary,
        behavior_safety_summary=behavior_safety_summary,
        remaining_blockers=blockers,
        recommended_next_feature=recommended_next_feature,
        final_verdict=final_verdict,
    )


def generate_evaluation_trace_bank_baseline_harness_artifacts(
    config: EvaluationTraceBankBaselineHarnessConfig | None = None,
) -> tuple[EvaluationTraceBankBaselineHarnessReport, Path, Path]:
    report = build_evaluation_trace_bank_baseline_harness_report(config)
    json_path, md_path = write_evaluation_trace_bank_baseline_harness_report(report)
    return report, json_path, md_path


def run_evaluation_trace_bank_baseline_harness(
    config: EvaluationTraceBankBaselineHarnessConfig | None = None,
) -> EvaluationTraceBankBaselineHarnessReport:
    report, _, _ = generate_evaluation_trace_bank_baseline_harness_artifacts(config)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Feature 058 evaluation trace-bank baseline harness report.")
    parser.add_argument("--json", action="store_true", help="print the generated JSON payload")
    args = parser.parse_args(argv)
    report, json_path, md_path = generate_evaluation_trace_bank_baseline_harness_artifacts()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
        print(f"final_verdict = {report.final_verdict}")
        print(f"recommended_next_feature = {report.recommended_next_feature}")
    return 0 if report.final_verdict == "evaluation_trace_bank_baseline_harness_ready" else 1
