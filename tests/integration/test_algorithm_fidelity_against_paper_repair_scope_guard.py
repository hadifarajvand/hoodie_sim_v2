from __future__ import annotations

import subprocess


def test_only_allowed_paths_change_relative_to_base() -> None:
    diff = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "reward-signal-state-action-discrimination-repair...HEAD",
        ],
        text=True,
    ).splitlines()
    assert all(
        path.startswith(
            (
                "src/analysis/algorithm_fidelity_against_paper_repair/",
                "tests/unit/test_algorithm_fidelity_against_paper_",
                "tests/integration/test_algorithm_fidelity_against_paper_",
                "artifacts/production/algorithm-fidelity-against-paper-repair/",
            )
        )
        or path in {
            "src/analysis/full_training_reproduction_campaign/config.py",
            "src/analysis/full_training_reproduction_campaign/trainer.py",
            "src/analysis/paper_faithful_simulation_production/runner.py",
            "src/analysis/paper_faithful_simulation_production/simulation_runner.py",
            "specs/082-algorithm-fidelity-against-paper-repair/spec.md",
            "docs/architecture/euls_phase32_algorithm_fidelity_against_paper_repair.md",
        }
        for path in diff
    )
