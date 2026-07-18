from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments.base_article_100 import base_article_100_config
from src.hoodie.experiments.cli_v2 import build_parser
from src.hoodie.experiments.full_matrix_smoke import (
    ABLATION_METHODS,
    BASE_ARTICLE_PANEL_IDS,
    MAIN_METHODS,
)


def test_base_article_100_uses_original_figure_8_to_11_panel_ids() -> None:
    assert len(BASE_ARTICLE_PANEL_IDS) == 14
    assert set(BASE_ARTICLE_PANEL_IDS) == {
        "figure_8a",
        "figure_8b",
        "figure_9a",
        "figure_9b",
        "figure_9c",
        "figure_9d",
        "figure_9e",
        "figure_10a",
        "figure_10b",
        "figure_10c",
        "figure_10d",
        "figure_10e",
        "figure_10f",
        "figure_11",
    }


def test_base_article_100_budget_is_preliminary_but_uses_full_architecture() -> None:
    config = base_article_100_config()
    assert config.training_episodes == 100
    assert config.evaluation_episodes == 100
    assert config.episode_slots == 110
    assert config.hidden_dims == (1024, 1024, 1024)
    assert config.lookback == 10
    assert config.lstm_hidden == 20
    payload = json.loads(
        Path("configs/echo/base_article_100.json").read_text(encoding="utf-8")
    )
    assert payload["scientific_scope"]["paper_evidence"] is False
    assert payload["scientific_scope"]["projected_or_surrogate_values_used"] is False


def test_base_article_100_preserves_method_hierarchy() -> None:
    assert MAIN_METHODS == (
        "ECHO",
        "HOODIE",
        "RO",
        "FLC",
        "VO",
        "HO",
        "BCO",
        "MLEO",
    )
    assert ABLATION_METHODS == ("ECHO", "ECHO-NoLSTM")


def test_base_article_100_cli_is_registered() -> None:
    args = build_parser().parse_args(
        [
            "echo-base-figures-100",
            "--run-root",
            "/tmp/results",
            "--campaign-id",
            "campaign",
        ]
    )
    assert args.command == "echo-base-figures-100"
    status_args = build_parser().parse_args(
        [
            "echo-base-figures-100-status",
            "--run-root",
            "/tmp/results",
            "--campaign-id",
            "campaign",
        ]
    )
    assert status_args.command == "echo-base-figures-100-status"
