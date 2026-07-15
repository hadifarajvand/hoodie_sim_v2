from __future__ import annotations

from pathlib import Path

from src.hoodie.experiments.schemas import AggregateRecord
from src.hoodie.rendering.composite_renderer import render_composite
from src.hoodie.rendering.panel_renderer import render_panel


def _dataset() -> list[AggregateRecord]:
    return [AggregateRecord(1, 1, 0, 1.0, 0.0, 1.0, {"delay": 0.0}, {"local": 1}, {"reward": 1.0}, (0.9, 1.1), 1, "offered")]


def test_render_panel_exports_svg_pdf_png(tmp_path: Path) -> None:
    outputs = render_panel(_dataset(), output_stem=tmp_path / "figure_8a")
    assert Path(outputs["svg"]).exists()
    assert Path(outputs["pdf"]).exists()
    assert Path(outputs["png"]).exists()


def test_render_composite_uses_saved_datasets(tmp_path: Path) -> None:
    outputs = render_composite({"figure_8a": _dataset(), "figure_8b": _dataset()}, output_dir=tmp_path)
    assert set(outputs) == {"figure_8a", "figure_8b"}
