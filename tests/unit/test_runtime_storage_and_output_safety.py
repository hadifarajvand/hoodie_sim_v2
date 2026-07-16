from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from src.hoodie.experiments import runtime_paths


GIB = 1024**3


def test_external_run_root_rejects_repository_subdirectory(
    tmp_path: Path, monkeypatch
) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    monkeypatch.setattr(runtime_paths, "REPOSITORY_ROOT", repository)
    monkeypatch.setenv("HOODIE_RUN_ROOT", str(repository / "runs"))
    with pytest.raises(RuntimeError, match="outside the Git repository"):
        runtime_paths.assert_external_run_root(minimum_free_gb=1)


def test_external_run_root_checks_disk_reserve(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repo"
    external = tmp_path / "external"
    repository.mkdir()
    external.mkdir()
    monkeypatch.setattr(runtime_paths, "REPOSITORY_ROOT", repository)
    monkeypatch.setenv("HOODIE_RUN_ROOT", str(external))
    monkeypatch.setattr(
        "shutil.disk_usage",
        lambda _path: SimpleNamespace(total=10 * GIB, used=9 * GIB, free=512 * 1024**2),
    )
    with pytest.raises(RuntimeError, match="insufficient free space"):
        runtime_paths.assert_external_run_root(minimum_free_gb=1)


def test_bounded_command_retains_only_configured_tail(tmp_path: Path) -> None:
    output = tmp_path / "tail.txt"
    command = [
        sys.executable,
        "scripts/hoodie/run_bounded_command.py",
        "--output",
        str(output),
        "--max-bytes",
        "1024",
        "--",
        sys.executable,
        "-c",
        "import sys; sys.stdout.write('x' * 100000 + 'END')",
    ]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    summary = json.loads(completed.stdout)
    assert summary["observed_output_bytes"] == 100003
    assert summary["retained_output_bytes"] == 1024
    assert output.stat().st_size == 1024
    assert output.read_bytes().endswith(b"END")


def test_operator_scripts_do_not_use_unbounded_tee_or_destructive_bundle_reset() -> None:
    campaign = Path("scripts/hoodie/corrected_campaign.sh").read_text(encoding="utf-8")
    worker = Path("scripts/hoodie/run_shard_worker.sh").read_text(encoding="utf-8")
    assert "| tee" not in campaign
    assert "| tee" not in worker
    assert "rm -rf" not in campaign
    assert "rm -rf" not in worker
    assert "HOODIE_RUN_ROOT" in campaign
    assert "HOODIE_RUN_ROOT" in worker
