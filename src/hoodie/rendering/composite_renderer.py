from __future__ import annotations

from pathlib import Path

from .panel_renderer import render_panel
from src.hoodie.experiments.schemas import AggregateRecord


def render_composite(panels: dict[str, list[AggregateRecord]], *, output_dir: Path) -> dict[str, dict[str, str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, dict[str, str]] = {}
    for panel_id, dataset in sorted(panels.items()):
        rendered[panel_id] = render_panel(dataset, output_stem=output_dir / panel_id)
    return rendered
