from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments.full_matrix_smoke import (
    ABLATION_METHODS,
    MAIN_METHODS,
    PANEL_IDS,
    FullMatrixSmokeConfig,
)


def test_full_matrix_method_hierarchy_matches_current_manuscript() -> None:
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


def test_full_matrix_contains_all_fifteen_manuscript_panels() -> None:
    assert len(PANEL_IDS) == 15
    assert set(PANEL_IDS) == {
        "figure_5a",
        "figure_5b",
        "figure_6a",
        "figure_6b",
        "figure_6c",
        "figure_6d",
        "figure_6e",
        "figure_7a",
        "figure_7b",
        "figure_7c",
        "figure_7d",
        "figure_7e",
        "figure_7f",
        "figure_8a",
        "figure_8b",
    }


def test_smoke_and_paper_budgets_cannot_be_confused() -> None:
    payload = json.loads(
        Path("configs/echo/full_matrix_smoke.json").read_text(encoding="utf-8")
    )
    smoke = payload["smoke_budget"]
    paper = payload["paper_budget_after_smoke"]
    assert smoke["training_episodes"] == FullMatrixSmokeConfig().training_episodes
    assert smoke["evaluation_episodes_per_point"] == 1
    assert paper["training_episodes"] == 5000
    assert paper["seeds"] == 10
    assert paper["held_out_episodes_per_seed_and_point"] == 200
    assert "NOT PAPER EVIDENCE" in payload["label"]
