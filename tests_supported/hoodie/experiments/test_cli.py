from __future__ import annotations

from src.hoodie.experiments.cli import main


def test_validate_contracts_cli_runs() -> None:
    assert main(['validate-contracts']) == 0


def test_list_panels_cli_runs() -> None:
    assert main(['list-panels']) == 0
