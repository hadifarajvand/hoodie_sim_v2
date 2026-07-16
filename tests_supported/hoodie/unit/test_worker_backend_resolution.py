from __future__ import annotations

import pytest

from src.hoodie.experiments.execution_backend import (
    backend_family,
    resolve_execution_device,
)
from src.hoodie.experiments.matrix_patch import install_matrix_patch


def test_corrected_matrix_uses_portable_backend_contract() -> None:
    install_matrix_patch()
    from src.hoodie.experiments import job_matrix

    rows = job_matrix.build_production_job_matrix("backend-test")
    assert rows
    assert {
        row.physical_contract.get("backend") for row in rows
    } == {"worker-selected"}


def test_worker_selected_backend_defaults_to_cpu(monkeypatch) -> None:
    monkeypatch.delenv("HOODIE_DEVICE", raising=False)
    assert resolve_execution_device("worker-selected") == "cpu"
    assert backend_family("cpu") == "cpu"


def test_worker_selected_backend_accepts_explicit_device(monkeypatch) -> None:
    monkeypatch.setenv("HOODIE_DEVICE", "cuda:1")
    assert resolve_execution_device("worker-selected") == "cuda:1"
    assert backend_family("cuda:1") == "cuda"


def test_fixed_backend_rejects_conflicting_worker_override(monkeypatch) -> None:
    monkeypatch.setenv("HOODIE_DEVICE", "mps")
    with pytest.raises(ValueError, match="conflicts with fixed matrix backend"):
        resolve_execution_device("cpu")


def test_invalid_backend_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("HOODIE_DEVICE", "tpu")
    with pytest.raises(ValueError, match="unsupported HOODIE execution device"):
        resolve_execution_device("worker-selected")
