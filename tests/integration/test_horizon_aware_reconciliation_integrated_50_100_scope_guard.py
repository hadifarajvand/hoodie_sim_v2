"""Integration tests: scope guard for Feature 081 (forbidden paths untouched)."""

from __future__ import annotations

import subprocess

BASE = "080-paper-faithful-simulation-production-pipeline"
FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


def _changed_files() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", f"{BASE}...HEAD"], text=True
        )
    except subprocess.CalledProcessError:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def test_no_forbidden_paths_modified():
    changed = _changed_files()
    offenders = [f for f in changed if any(f.startswith(p) for p in FORBIDDEN_PREFIXES)]
    assert not offenders, f"forbidden paths modified: {offenders}"


def test_no_reward_timing_or_replay_hash_modified():
    changed = _changed_files()
    assert "src/environment/reward_timing.py" not in changed
    assert "src/environment/replay_hash.py" not in changed
