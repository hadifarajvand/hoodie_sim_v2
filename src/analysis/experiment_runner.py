"""Experiment runner for parameter-sweep campaigns.

Provides dataclasses and functions to run multiple experiments
(parameter sweeps), collect PilotTrainingResult + training metrics,
and persist results as JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Callable

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, PilotTrainingResult


@dataclass
class ExperimentResult:
    """Result of a single experiment run."""

    config: CampaignConfig
    result: PilotTrainingResult
    training_metrics: dict[str, Any]
    experiment_label: str


@dataclass
class SweepConfig:
    """Configuration for a parameter-sweep campaign.

    Attributes:
        experiments:  Mapping of label -> zero-argument factory that
                      returns a CampaignConfig (e.g. a partial or lambda
                      wrapping a config_templates function).
        episodes:     Training episodes per experiment (default 3).
        episode_length:  Steps per episode (default 50).
        output_dir:   Optional directory for persisting sweep results.
                      When None, results are returned in memory only.
    """

    experiments: dict[str, Callable[[], CampaignConfig]]
    episodes: int = 3
    episode_length: int = 50
    output_dir: str | None = None


def run_experiment(
    config: CampaignConfig,
    episodes: int,
    episode_length: int,
) -> ExperimentResult:
    """Run a single experiment and return its result.

    1.  Creates a DDQNTrainer from *config*.
    2.  Runs pilot training with the given *episodes* and *episode_length*.
    3.  Extracts training metrics via ``training_metrics_to_dict()``.
    4.  Returns an ``ExperimentResult`` (experiment_label is left empty).
    """
    trainer = DDQNTrainer(config)
    result: PilotTrainingResult = trainer.run_pilot(
        episodes=episodes,
        episode_length=episode_length,
    )
    metrics: dict[str, Any] = trainer.training_metrics_to_dict()
    return ExperimentResult(
        config=config,
        result=result,
        training_metrics=metrics,
        experiment_label="",
    )


def run_sweep(sweep_config: SweepConfig) -> list[ExperimentResult]:
    """Run every experiment in *sweep_config* and collect results.

    Iterates through ``sweep_config.experiments``, runs each via
    ``run_experiment``, prints per-episode reward progress to stdout,
    and returns the full list of ``ExperimentResult``.

    If ``sweep_config.output_dir`` is set the results are also persisted
    via ``save_sweep_results``.
    """
    results: list[ExperimentResult] = []

    for label, config_fn in sweep_config.experiments.items():
        config = config_fn()
        experiment_result = run_experiment(
            config,
            episodes=sweep_config.episodes,
            episode_length=sweep_config.episode_length,
        )
        experiment_result.experiment_label = label

        # Print per-episode progress
        rewards: list[float] = experiment_result.training_metrics.get("episode_rewards", [])
        for episode_idx, reward in enumerate(rewards):
            print(
                f"Running {label}... episode {episode_idx}: "
                f"reward={reward}"
            )

        results.append(experiment_result)

    # Persist when an output directory was configured
    if sweep_config.output_dir is not None:
        save_sweep_results(results, sweep_config.output_dir)

    return results


def save_sweep_results(
    results: list[ExperimentResult],
    output_dir: str,
) -> None:
    """Save a list of experiment results as JSON under *output_dir*.

    Writes ``sweep_results.json`` containing a JSON array of objects.
    Each object carries the config dict, result dict, training metrics,
    and experiment label.  Results are sorted by label for deterministic
    output.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    serialized: list[dict[str, Any]] = []
    for er in sorted(results, key=lambda r: r.experiment_label):
        serialized.append(
            {
                "experiment_label": er.experiment_label,
                "config": er.config.to_dict(),
                "result": er.result.to_dict(),
                "training_metrics": dict(er.training_metrics),
            }
        )

    output_file = out_path / "sweep_results.json"
    output_file.write_text(
        json.dumps(serialized, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
