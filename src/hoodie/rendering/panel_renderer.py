from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

from src.hoodie.experiments.schemas import AggregateRecord


def render_panel(dataset: list[AggregateRecord], *, output_stem: Path) -> dict[str, str]:
    x = list(range(len(dataset)))
    y = [record.completion_ratio for record in dataset]
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, y, marker="o")
    ax.set_xlabel("index")
    ax.set_ylabel("completion_ratio")
    svg = output_stem.with_suffix(".svg")
    pdf = output_stem.with_suffix(".pdf")
    png = output_stem.with_suffix(".png")
    fig.savefig(svg)
    fig.savefig(pdf)
    fig.savefig(png, dpi=300)
    plt.close(fig)
    return {"svg": str(svg), "pdf": str(pdf), "png": str(png)}
