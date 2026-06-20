from __future__ import annotations

from subprocess import run


def test_only_allowed_feature_paths_appear_in_diff():
    result = run(
        ["git", "diff", "--name-only", "067-terminal-lifecycle-accounting-50-100-comparison...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    forbidden_prefixes = (
        "src/environment/",
        "src/dal/",
        "src/policies/",
        "src/environment/reward_timing.py",
        "src/environment/replay_hash.py",
        "requirements",
        "pyproject.toml",
        "poetry.lock",
        "uv.lock",
        "AGENTS.md",
        ".specify/feature.json",
        "src/analysis/staged_training_budget_learning_curve/",
        "src/analysis/final_review_release_gate_batch/",
        "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
        "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
        "src/analysis/terminal_lifecycle_accounting_50_100_comparison/",
    )
    assert not any(path.startswith(prefix) for path in paths for prefix in forbidden_prefixes)
