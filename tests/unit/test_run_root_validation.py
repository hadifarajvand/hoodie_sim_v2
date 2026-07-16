from __future__ import annotations

import importlib.util
from pathlib import Path
import shlex
from types import SimpleNamespace


MODULE_PATH = (
    Path(__file__).parents[2] / "scripts" / "hoodie" / "validate_run_root.py"
)
SPEC = importlib.util.spec_from_file_location("validate_run_root", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_repository_path_is_rejected(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(VALIDATOR, "repository_root", lambda: repo)

    result = VALIDATOR.validate_run_root(
        str(repo / "runs"),
        minimum_free_gib=1,
        minimum_free_fraction=0.01,
    )

    assert result["passed"] is False
    assert "run root must be outside the Git repository" in result["errors"]


def test_writable_external_path_and_atomic_replace_pass(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    run_root = tmp_path / "external" / "hoodie-runs"
    repo.mkdir()
    monkeypatch.setattr(VALIDATOR, "repository_root", lambda: repo)
    monkeypatch.setattr(
        VALIDATOR.shutil,
        "disk_usage",
        lambda _path: SimpleNamespace(
            total=100 * VALIDATOR.GIB,
            used=10 * VALIDATOR.GIB,
            free=90 * VALIDATOR.GIB,
        ),
    )

    result = VALIDATOR.validate_run_root(
        str(run_root),
        minimum_free_gib=20,
        minimum_free_fraction=0.10,
    )

    assert result["passed"] is True
    assert result["outside_repository"] is True
    assert result["write_read_verified"] is True
    assert result["atomic_replace_verified"] is True
    assert not tuple(run_root.glob(".hoodie-root-probe-*"))


def test_low_disk_fails_before_probe(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    run_root = tmp_path / "external"
    repo.mkdir()
    monkeypatch.setattr(VALIDATOR, "repository_root", lambda: repo)
    monkeypatch.setattr(
        VALIDATOR.shutil,
        "disk_usage",
        lambda _path: SimpleNamespace(
            total=100 * VALIDATOR.GIB,
            used=95 * VALIDATOR.GIB,
            free=5 * VALIDATOR.GIB,
        ),
    )

    result = VALIDATOR.validate_run_root(
        str(run_root),
        minimum_free_gib=20,
        minimum_free_fraction=0.10,
    )

    assert result["passed"] is False
    assert result["write_read_verified"] is False
    assert any("insufficient free space" in error for error in result["errors"])


def test_env_file_is_sourceable_and_quoted(tmp_path: Path) -> None:
    env_file = tmp_path / "selected root" / ".hoodie-run-root.env"
    resolved_root = str(tmp_path / "output root")

    VALIDATOR._write_env_file(env_file, resolved_root)

    assert env_file.read_text(encoding="utf-8") == (
        f"export HOODIE_RUN_ROOT={shlex.quote(resolved_root)}\n"
    )
