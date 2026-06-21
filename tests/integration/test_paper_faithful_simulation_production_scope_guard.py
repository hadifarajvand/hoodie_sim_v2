"""Integration test: scope guard — core simulation semantics untouched."""

from __future__ import annotations

import subprocess

BASE = "081-horizon-aware-reconciliation-integrated-50-100-rerun"
FORBIDDEN = (
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
)


def _changed():
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", f"{BASE}...HEAD"], text=True)
    except subprocess.CalledProcessError:
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def test_reward_and_dependency_files_untouched():
    changed = _changed()
    for f in FORBIDDEN:
        assert f not in changed, f


def test_no_environment_semantic_files_changed():
    changed = _changed()
    env_changed = [f for f in changed if f.startswith("src/environment/")]
    assert not env_changed, f"environment files changed: {env_changed}"
