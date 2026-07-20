from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
import platform
import shutil
from typing import Any
import zipfile

import numpy as np
import torch

from .base_article_100 import _verify
from .full_matrix_smoke import (
    ABLATION_METHODS,
    BASE_ARTICLE_PANEL_IDS,
    MAIN_METHODS,
    FullMatrixSmokeConfig,
    _now,
    _run_matrix,
)
from .trained_pilot_io import (
    atomic_json,
    file_sha256,
    read_json,
    repository_root,
    resolve_campaign_root,
    source_commit,
    write_sha256sums,
)


CAMPAIGN_ID = "echo-hoodie-figures-8-11-3000-20260718-001"
LABEL = "author-protocol single-seed reproduction extended with ECHO"


def author_3000_config() -> FullMatrixSmokeConfig:
    return FullMatrixSmokeConfig(
        training_episodes=3_000,
        evaluation_episodes=200,
        episode_slots=110,
        drain_slots=10,
        batch_size=64,
        replay_capacity=10_000,
        target_update_interval=2_000,
        hidden_dims=(1024, 1024, 1024),
        lookback=10,
        lstm_hidden=20,
        learning_rate=7e-7,
        discount_factor=0.99,
        training_curve_interval=250,
    )


def _campaign(run_root: str | Path, campaign_id: str) -> Path:
    if campaign_id != CAMPAIGN_ID:
        raise ValueError(f"locked campaign id is {CAMPAIGN_ID}")
    config = author_3000_config()
    root = resolve_campaign_root(run_root, campaign_id)
    root.mkdir(parents=True, exist_ok=True)
    specification = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "label": LABEL,
        "source_commit": source_commit(),
        "fixed_seeds": [101],
        "methods": {
            "proposed": "ECHO",
            "base_framework": "HOODIE",
            "inherited_baselines": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
            "main_comparison": list(MAIN_METHODS),
            "ablation_only": list(ABLATION_METHODS),
        },
        "panel_ids": list(BASE_ARTICLE_PANEL_IDS),
        "execution_config": asdict(config),
        "execution_guards": {
            "paired_deterministic_traces": True,
            "atomic_resumable_units": True,
            "checkpoint_loads_per_evaluation_point": 1,
            "torch_inference_mode": True,
            "torch_threads_per_worker": 1,
            "max_cpu_workers": 6,
        },
        "paper_evidence": False,
        "projected_or_surrogate_values_used": False,
    }
    path = root / "campaign_specification.json"
    normalized = json.loads(json.dumps(specification))
    if path.exists() and read_json(path) != normalized:
        raise ValueError("existing campaign does not match this commit/configuration")
    if not path.exists():
        atomic_json(path, specification)
        atomic_json(
            root / "environment_manifest.json",
            {
                "created_at": _now(),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "torch": torch.__version__,
                "numpy": np.__version__,
                "device": "cuda" if torch.cuda.is_available() else "cpu",
                "torch_threads": 1,
            },
        )
        shutil.copy2(
            repository_root() / "configs/echo/author_3000.json",
            root / "author_3000_config.json",
        )
        for figure in (8, 9, 10, 11):
            shutil.copy2(
                repository_root()
                / f"resources/papers/hoodie/contracts/figure_{figure}.json",
                root / f"hoodie_figure_{figure}_contract.json",
            )
        for name in (
            "authoritative_source_lock.json",
            "locked_evaluation_protocol.json",
            "locked_method_contract.json",
        ):
            shutil.copy2(repository_root() / "configs/echo" / name, root / name)
    return root


def run_author_3000(run_root: str | Path, campaign_id: str) -> dict[str, Any]:
    torch.set_num_threads(1)
    config = author_3000_config()
    root = _campaign(run_root, campaign_id)
    terminal = root / "terminal_status.json"
    if terminal.exists() and read_json(terminal).get("verified"):
        return {**read_json(terminal), "resumed": True}
    result = _run_matrix(root, config, base_article_numbering=True)
    verification = _verify(root, result, config)
    verification.update(
        {
            "label": LABEL,
            "training_curve_interval": 250,
            "expected_training_curve_samples_per_series": 12,
            "paper_scale_started": True,
        }
    )
    atomic_json(root / "verification_report.json", verification)
    if not verification["verified"]:
        raise ValueError(f"author-3000 verification failed: {verification['errors']}")
    archive = root / "results" / f"{campaign_id}-verified-results.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != archive and "checkpoints" not in path.parts:
                handle.write(path, path.relative_to(root))
    archive_record = {
        "path": str(archive),
        "sha256": file_sha256(archive),
        "bytes": archive.stat().st_size,
    }
    atomic_json(root / "results/archive.json", archive_record)
    terminal_payload = {
        **verification,
        "status": "completed",
        "completed_verification_and_figures": True,
        "completed_at": _now(),
        "campaign_id": campaign_id,
        "campaign_root": str(root),
        "source_commit": source_commit(),
        "archive": archive_record,
    }
    atomic_json(root / "VERIFIED.json", terminal_payload)
    atomic_json(root / "terminal_status.json", terminal_payload)
    write_sha256sums(root)
    return terminal_payload


def author_3000_status(run_root: str | Path, campaign_id: str) -> dict[str, Any]:
    root = resolve_campaign_root(run_root, campaign_id)
    if not root.exists():
        return {"status": "not_started", "campaign_id": campaign_id}
    terminal = root / "terminal_status.json"
    if terminal.exists():
        return read_json(terminal)
    progress = [read_json(path) for path in (root / "checkpoints").glob("*/progress.json")]
    return {
        "status": "running_or_resumable",
        "campaign_id": campaign_id,
        "campaign_root": str(root),
        "completed_checkpoints": len(list((root / "checkpoints").glob("*/COMPLETED.json"))),
        "expected_checkpoints": 18,
        "completed_training_episodes": sum(int(row.get("completed_episodes", 0)) for row in progress),
        "expected_training_episodes": 54_000,
        "completed_evaluation_points": len(list((root / "evaluation_cache").glob("*.json"))),
        "expected_evaluation_points": 108,
        "held_out_episodes_per_completed_point": 200,
        "resumable": True,
    }


def _iso_seconds(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


def author_3000_preflight(
    run_root: str | Path,
    campaign_id: str,
    reference_campaign_id: str | None = None,
) -> dict[str, Any]:
    config = author_3000_config()
    payload: dict[str, Any] = {
        "status": "ready_for_user_approval",
        "starts_scientific_campaign": False,
        "campaign_id": campaign_id,
        "source_commit": source_commit(),
        "cpu_count": __import__("os").cpu_count(),
        "torch_threads_per_worker": 1,
        "max_cpu_workers": 6,
        "contract": {
            "panels": 14,
            "checkpoints": 18,
            "training_episodes_total": 18 * config.training_episodes,
            "evaluation_points": 108,
            "held_out_episodes_per_point": config.evaluation_episodes,
            "figure_exports": 12,
            "training_curve_samples": list(range(250, 3001, 250)),
        },
        "approval_required_before_command": (
            f"hoodie-experiments echo-author-figures-3000 --run-root {run_root} "
            f"--campaign-id {campaign_id}"
        ),
    }
    if reference_campaign_id:
        reference = resolve_campaign_root(run_root, reference_campaign_id)
        stage = reference / "stages/training_completed.json"
        caches = sorted((reference / "evaluation_cache").glob("*.json"), key=lambda p: p.stat().st_mtime)
        spec = reference / "campaign_specification.json"
        if stage.exists() and spec.exists():
            created = _iso_seconds(read_json(reference / "environment_manifest.json")["created_at"])
            training_end = _iso_seconds(read_json(stage)["at"])
            training_seconds_per_episode = (training_end - created) / 1_800
            projected_training = training_seconds_per_episode * 54_000
            estimate = {
                "reference_campaign_id": reference_campaign_id,
                "reference_training_seconds_per_episode": training_seconds_per_episode,
                "projected_training_hours_single_process": projected_training / 3600,
            }
            if len(caches) >= 2:
                seconds_per_point_100 = (
                    caches[-1].stat().st_mtime - caches[0].stat().st_mtime
                ) / (len(caches) - 1)
                projected_evaluation = seconds_per_point_100 * 2 * 108
                estimate.update(
                    {
                        "reference_evaluation_seconds_per_100_episode_point": seconds_per_point_100,
                        "projected_evaluation_hours_single_process": projected_evaluation / 3600,
                        "projected_total_days_single_process": (
                            projected_training + projected_evaluation
                        ) / 86_400,
                    }
                )
            payload["reference_estimate"] = estimate
    if "reference_estimate" not in payload:
        compact_reference = read_json(
            repository_root()
            / "docs/echo/REFERENCE_100_PROGRESS_20260720.json"
        )
        training_seconds_per_episode = (
            float(compact_reference["training_elapsed_seconds_observed"]) / 1_800
        )
        evaluation_seconds_per_point = (
            float(
                compact_reference[
                    "evaluation_first_to_last_cache_seconds_observed"
                ]
            )
            / max(1, int(compact_reference["completed_evaluation_points"]) - 1)
        )
        projected_training = training_seconds_per_episode * 54_000
        projected_evaluation = evaluation_seconds_per_point * 2 * 108
        payload["reference_estimate"] = {
            "reference_campaign_id": compact_reference["campaign_id"],
            "reference_kind": "repository_compact_progress_evidence",
            "reference_training_seconds_per_episode": training_seconds_per_episode,
            "reference_evaluation_seconds_per_100_episode_point": evaluation_seconds_per_point,
            "projected_training_hours_single_process": projected_training / 3600,
            "projected_evaluation_hours_single_process": projected_evaluation / 3600,
            "projected_total_days_single_process": (
                projected_training + projected_evaluation
            )
            / 86_400,
        }
    return payload
