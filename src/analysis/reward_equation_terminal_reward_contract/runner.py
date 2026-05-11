from __future__ import annotations

from pathlib import Path

from .report import build_reward_contract_report, write_reward_contract_report


def run_reward_equation_terminal_reward_contract() -> dict[str, Path]:
    report = build_reward_contract_report()
    json_path, markdown_path = write_reward_contract_report(report)
    return {"json": json_path, "markdown": markdown_path}
