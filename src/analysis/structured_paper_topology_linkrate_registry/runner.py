from __future__ import annotations

from pathlib import Path

from .recovery import StructuredPaperTopologyLinkRateRegistryBuilder


def run_structured_paper_topology_linkrate_registry() -> dict[str, Path]:
    repo_root = Path(__file__).resolve().parents[3]
    paper = repo_root / "resources/papers/hoodie/ocr/merged.tex"
    artifact_root = repo_root
    output_root = repo_root
    return StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, output_root).write_outputs()

