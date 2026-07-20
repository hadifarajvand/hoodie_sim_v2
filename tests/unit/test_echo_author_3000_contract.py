from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments.author_3000 import (
    CAMPAIGN_ID,
    LABEL,
    author_3000_config,
    author_3000_preflight,
)
from src.hoodie.experiments.cli_v2 import build_parser
from src.hoodie.experiments.full_matrix_smoke import (
    ABLATION_METHODS,
    BASE_ARTICLE_PANEL_IDS,
    MAIN_METHODS,
)


def test_author_3000_locked_scientific_contract() -> None:
    config = author_3000_config()
    assert config.training_episodes == 3_000
    assert config.evaluation_episodes == 200
    assert config.episode_slots == 110
    assert config.drain_slots == 10
    assert config.hidden_dims == (1024, 1024, 1024)
    assert config.lookback == 10
    assert config.lstm_hidden == 20
    assert config.training_curve_interval == 250
    assert len(BASE_ARTICLE_PANEL_IDS) == 14
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


def test_author_3000_locked_json_matches_code() -> None:
    payload = json.loads(Path("configs/echo/author_3000.json").read_text())
    assert payload["campaign_id"] == CAMPAIGN_ID
    assert payload["label"] == LABEL
    assert payload["budget"]["learned_checkpoints"] == 18
    assert payload["budget"]["evaluation_points"] == 108
    assert payload["verification"][
        "projected_interpolated_extrapolated_synthetic_or_surrogate_values"
    ] is False


def test_author_3000_cli_and_preflight_are_approval_gated(tmp_path: Path) -> None:
    parser = build_parser()
    for command in (
        "echo-author-figures-3000",
        "echo-author-figures-3000-status",
        "echo-author-figures-3000-preflight",
    ):
        args = parser.parse_args(
            [command, "--run-root", str(tmp_path), "--campaign-id", CAMPAIGN_ID]
        )
        assert args.command == command
    report = author_3000_preflight(tmp_path, CAMPAIGN_ID)
    assert report["status"] == "ready_for_user_approval"
    assert report["starts_scientific_campaign"] is False
    assert report["contract"]["training_episodes_total"] == 54_000
    assert report["contract"]["training_curve_samples"] == list(
        range(250, 3001, 250)
    )
    assert report["reference_estimate"]["projected_total_days_single_process"] > 20
