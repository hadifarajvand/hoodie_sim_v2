from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from .execution_backend import resolve_execution_device
from .job_matrix import ProductionJobRow

_INSTALLED = False
_ORIGINAL_BUILD_TRAINING: Callable[..., Any] | None = None
_ORIGINAL_BUILD_EVALUATION: Callable[..., Any] | None = None


def build_training_config_with_worker_backend(
    matrix_row: ProductionJobRow,
    source_contract: dict[str, Any],
    *,
    trace_hash: str,
    output_dir: Path | None,
):
    if _ORIGINAL_BUILD_TRAINING is None:  # pragma: no cover
        raise RuntimeError("backend resolution patch is not installed")
    config = _ORIGINAL_BUILD_TRAINING(
        matrix_row,
        source_contract,
        trace_hash=trace_hash,
        output_dir=output_dir,
    )
    device = resolve_execution_device(
        matrix_row.physical_contract.get("backend", "worker-selected")
    )
    return replace(config, device=device)


def build_evaluation_config_with_worker_backend(
    matrix_row: ProductionJobRow,
    source_contract: dict[str, Any],
    *,
    trace_id: str,
    output_dir: Path | None,
):
    if _ORIGINAL_BUILD_EVALUATION is None:  # pragma: no cover
        raise RuntimeError("backend resolution patch is not installed")
    config = _ORIGINAL_BUILD_EVALUATION(
        matrix_row,
        source_contract,
        trace_id=trace_id,
        output_dir=output_dir,
    )
    device = resolve_execution_device(
        matrix_row.physical_contract.get("backend", "worker-selected")
    )
    return replace(config, device=device)


def install_backend_resolution_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_BUILD_TRAINING
    global _ORIGINAL_BUILD_EVALUATION
    if _INSTALLED:
        return

    from . import contract_mapping
    from . import production_campaign
    from . import production_patch

    _ORIGINAL_BUILD_TRAINING = contract_mapping.build_training_config
    _ORIGINAL_BUILD_EVALUATION = contract_mapping.build_evaluation_config

    contract_mapping.build_training_config = build_training_config_with_worker_backend
    contract_mapping.build_evaluation_config = build_evaluation_config_with_worker_backend
    production_patch.build_training_config = build_training_config_with_worker_backend
    production_patch.build_evaluation_config = build_evaluation_config_with_worker_backend
    production_campaign.build_training_config = build_training_config_with_worker_backend
    production_campaign.build_evaluation_config = build_evaluation_config_with_worker_backend
    _INSTALLED = True
