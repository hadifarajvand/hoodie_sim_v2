from __future__ import annotations

import json
from pathlib import Path

from src.hoodie.experiments.cli_v2 import build_parser, main


def test_required_echo_commands_are_exposed() -> None:
    parser = build_parser()
    actions = next(
        action
        for action in parser._actions
        if action.__class__.__name__ == "_SubParsersAction"
    )
    required = {
        "echo-train",
        "echo-eval",
        "echo-diff",
        "echo-pilot",
        "echo-status",
        "echo-verify-run",
    }
    assert required <= set(actions.choices)


def test_missing_campaign_reports_campaign_not_found(
    tmp_path: Path, capsys
) -> None:
    missing = tmp_path / "outside" / "campaigns" / "missing"
    exit_code = main(["aggregate", "--campaign-dir", str(missing.resolve())])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_type"] == "campaign_not_found"
    assert "storage" not in json.dumps(payload).lower()
    assert "status_json" not in payload
