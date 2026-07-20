from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import platform
import shutil
from typing import Any
import zipfile

from PIL import Image
import numpy as np
import torch

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


LABEL = "HOODIE FIGURES 8-11 WITH ECHO — 100-EPISODE PRELIMINARY REPRODUCTION"


def base_article_100_config() -> FullMatrixSmokeConfig:
    return FullMatrixSmokeConfig(
        training_episodes=100,
        evaluation_episodes=100,
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
    )


def _campaign(run_root: str | Path, campaign_id: str, config: FullMatrixSmokeConfig) -> Path:
    root = resolve_campaign_root(run_root, campaign_id)
    root.mkdir(parents=True, exist_ok=True)
    specification = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "label": LABEL,
        "source_commit": source_commit(),
        "methods": {
            "proposed": "ECHO",
            "base_framework": "HOODIE",
            "inherited_baselines": ["RO", "FLC", "VO", "HO", "BCO", "MLEO"],
            "main_comparison": list(MAIN_METHODS),
            "ablation_only": list(ABLATION_METHODS),
        },
        "panel_ids": list(BASE_ARTICLE_PANEL_IDS),
        "execution_config": asdict(config),
        "paper_evidence": False,
        "projected_or_surrogate_values_used": False,
    }
    path = root / "campaign_specification.json"
    normalized = json.loads(json.dumps(specification))
    if path.exists():
        if read_json(path) != normalized:
            raise ValueError("existing campaign does not match this source/configuration")
    else:
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
            },
        )
        shutil.copy2(
            repository_root() / "configs/echo/base_article_100.json",
            root / "base_article_100_config.json",
        )
        for figure in (8, 9, 10, 11):
            shutil.copy2(
                repository_root() / f"resources/papers/hoodie/contracts/figure_{figure}.json",
                root / f"hoodie_figure_{figure}_contract.json",
            )
        for name in (
            "authoritative_source_lock.json",
            "locked_evaluation_protocol.json",
            "locked_method_contract.json",
        ):
            shutil.copy2(repository_root() / "configs/echo" / name, root / name)
    return root


def _verify(root: Path, result: dict[str, Any], config: FullMatrixSmokeConfig) -> dict[str, Any]:
    errors: list[str] = []
    rows = result["rows"]
    if {row["panel_id"] for row in rows} != set(BASE_ARTICLE_PANEL_IDS):
        errors.append("the 14-panel HOODIE Figure 8-11 matrix is incomplete")
    for panel_id in (f"figure_10{letter}" for letter in "abcdef"):
        panel_rows = [row for row in rows if row["panel_id"] == panel_id]
        if len(panel_rows) != 5 * len(MAIN_METHODS):
            errors.append(f"{panel_id} does not contain all methods at all points")
        for value in {row["x_value"] for row in panel_rows}:
            point_rows = [row for row in panel_rows if row["x_value"] == value]
            if {row["method"] for row in point_rows} != set(MAIN_METHODS):
                errors.append(f"{panel_id} point {value} has a method mismatch")
            if len({row["trace_id"] for row in point_rows}) != 1:
                errors.append(f"{panel_id} point {value} is not trace-paired")
            if any(
                int(row.get("evaluation_episodes") or 0)
                != config.evaluation_episodes
                for row in point_rows
            ):
                errors.append(
                    f"{panel_id} point {value} lacks "
                    f"{config.evaluation_episodes} held-out episodes"
                )
    figure9b = [row for row in rows if row["panel_id"] == "figure_9b"]
    if len(figure9b) != 5 * 3 * 3:
        errors.append("figure_9b lacks all three action categories for N=10,15,20")
    if {row["method"] for row in rows if row["panel_id"] == "figure_11"} != set(ABLATION_METHODS):
        errors.append("figure_11 does not isolate ECHO versus ECHO-NoLSTM")
    for row in rows:
        if int(row["generated_tasks"]) != int(row["successful_tasks"]) + int(row["dropped_tasks"]):
            errors.append(f"task conservation failed in {row['panel_id']}")
            break
        if int(row.get("illegal_selected_action_count") or 0):
            errors.append(f"illegal selected action in {row['panel_id']}")
            break
    checkpoint_records = result["checkpoint_records"]
    if len(checkpoint_records) != 18:
        errors.append(f"expected 18 unique trained checkpoints, found {len(checkpoint_records)}")
    if any(
        int(record["training_episodes"]) != config.training_episodes
        for record in checkpoint_records
    ):
        errors.append(
            f"a trained checkpoint lacks {config.training_episodes} episodes"
        )
    figure_records = result["figure_records"]
    for figure_id in ("figure_8", "figure_9", "figure_10", "figure_11"):
        records = [record for record in figure_records if record["figure_id"] == figure_id]
        if {record["format"] for record in records} != {"pdf", "svg", "png"}:
            errors.append(f"incomplete exports for {figure_id}")
        png = [record for record in records if record["format"] == "png"]
        if png:
            with Image.open(png[0]["path"]) as image:
                dpi = image.info.get("dpi", (0, 0))
            if not dpi or min(float(value) for value in dpi) < 299:
                errors.append(f"PNG is not 300 dpi for {figure_id}")
    return {
        "status": "failed" if errors else "completed",
        "verified": not errors,
        "errors": errors,
        "panels_verified": len(BASE_ARTICLE_PANEL_IDS),
        "figure_files_verified": len(figure_records),
        "training_episodes_per_checkpoint": config.training_episodes,
        "held_out_evaluation_episodes_per_point": config.evaluation_episodes,
        "seed_count": 1,
        "episode_slots": config.episode_slots,
        "main_methods_verified": list(MAIN_METHODS),
        "ablation_methods_verified": list(ABLATION_METHODS),
        "paper_evidence": False,
        "paper_scale_started": False,
        "projected_or_surrogate_values_used": False,
        "paper_scale_reference": {
            "training_episodes": 5000,
            "held_out_episodes_per_seed_and_point": 200,
            "seed_count": 10,
        },
    }


def run_base_article_100(
    run_root: str | Path,
    campaign_id: str,
    *,
    config: FullMatrixSmokeConfig | None = None,
) -> dict[str, Any]:
    resolved = config or base_article_100_config()
    root = _campaign(run_root, campaign_id, resolved)
    terminal = root / "terminal_status.json"
    if terminal.exists() and read_json(terminal).get("verified"):
        return {**read_json(terminal), "resumed": True}
    result = _run_matrix(root, resolved, base_article_numbering=True)
    verification = _verify(root, result, resolved)
    atomic_json(root / "verification_report.json", verification)
    if not verification["verified"]:
        raise ValueError(f"100-episode base-article verification failed: {verification['errors']}")
    manifest = {
        "schema_version": 1,
        "status": "BASE_ARTICLE_FIGURES_8_11_100_EPISODES_COMPLETE",
        "label": LABEL,
        "campaign_id": campaign_id,
        "source_commit": source_commit(),
        "panel_ids": list(BASE_ARTICLE_PANEL_IDS),
        "checkpoints": result["checkpoint_records"],
        "figures": result["figure_records"],
        **verification,
    }
    atomic_json(root / "results/manifest.json", manifest)
    archive = root / "results" / f"{campaign_id}-hoodie-figures-8-11-100-episodes.zip"
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
        "label": LABEL,
        "archive": archive_record,
        "next_stage": "5000-episode multi-seed paper campaign remains separate and has not started",
    }
    atomic_json(root / "VERIFIED.json", terminal_payload)
    atomic_json(root / "terminal_status.json", terminal_payload)
    write_sha256sums(root)
    return terminal_payload


def base_article_100_status(run_root: str | Path, campaign_id: str) -> dict[str, Any]:
    root = resolve_campaign_root(run_root, campaign_id)
    if not root.exists():
        return {
            "status": "not_started",
            "campaign_id": campaign_id,
            "campaign_root": str(root),
        }
    terminal = root / "terminal_status.json"
    if terminal.exists():
        return read_json(terminal)
    progress_files = sorted((root / "checkpoints").glob("*/progress.json"))
    progress = [read_json(path) for path in progress_files]
    return {
        "status": "running_or_resumable",
        "campaign_id": campaign_id,
        "campaign_root": str(root),
        "source_commit": read_json(root / "campaign_specification.json").get("source_commit"),
        "completed_checkpoints": len(list((root / "checkpoints").glob("*/COMPLETED.json"))),
        "expected_checkpoints": 18,
        "completed_training_episodes": sum(int(row.get("completed_episodes", 0)) for row in progress),
        "expected_training_episodes": 1800,
        "completed_evaluation_points": len(list((root / "evaluation_cache").glob("*.json"))),
        "expected_evaluation_points": 108,
        "held_out_episodes_per_completed_point": 100,
        "resumable": True,
    }
