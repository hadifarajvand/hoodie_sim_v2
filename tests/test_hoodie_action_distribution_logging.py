from pathlib import Path
import json

from analysis.hoodie_action_distribution import (
    normalize_action_category,
    aggregate_action_distribution,
    write_action_distribution_outputs,
)


def test_normalize_known_and_unknown():
    assert normalize_action_category({"action_type": "local"}) == "local"
    assert normalize_action_category({"action_name": "do_horizontal_move"}) == "horizontal"
    assert normalize_action_category({"action": 2}) == "unknown"


def test_aggregate_and_write(tmp_path):
    records = [
        {"action_type": "local"},
        {"action_name": "horizontal_move"},
        {"action_name": "vertical_move"},
        {"action": 9},
    ]
    agg = aggregate_action_distribution(records, policy_name="HOODIE")
    assert agg["total_actions"] == 4
    assert agg["unknown_count"] == 1
    out = write_action_distribution_outputs(records, tmp_path, label="test", policy_name="HOODIE")
    assert Path(out["csv"]).exists()
    assert Path(out["json"]).exists()
    meta = json.loads(Path(out["metadata"]).read_text())
    assert meta["official_figure_claim"] is False
    # ensure canonical filenames are used
    assert Path(tmp_path / "hoodie_action_distribution.csv").exists()
    assert Path(tmp_path / "hoodie_action_distribution.json").exists()
    assert Path(tmp_path / "hoodie_action_distribution_metadata.json").exists()
