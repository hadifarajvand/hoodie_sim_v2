from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

@dataclass(frozen=True, slots=True)
class UnresolvedSourceField:
    field: str
    searched_sources: tuple[str, ...]
    reason: str

@dataclass(frozen=True, slots=True)
class PanelSourceContract:
    panel_id: str
    scientific_question: str
    independent_variable: str
    independent_values: tuple[str, ...] = ()
    dependent_metric: str = ""
    compared_policies: tuple[str, ...] = ()
    fixed_topology: dict[str, Any] = field(default_factory=dict)
    unresolved_fields: tuple[UnresolvedSourceField, ...] = ()
    source_citation: str = ""
    confidence_level: float = 0.95

    def is_fully_resolved(self) -> bool:
        return not self.unresolved_fields

@dataclass(frozen=True, slots=True)
class Figures811SourceContract:
    panels: tuple[PanelSourceContract, ...]

    def unresolved_fields(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for panel in self.panels:
            for field in panel.unresolved_fields:
                rows.append({"panel_id": panel.panel_id, "field": field.field, "searched_sources": list(field.searched_sources), "reason": field.reason})
        return rows

    def to_dict(self) -> dict[str, Any]:
        return {"panels": [panel.__dict__ if hasattr(panel, "__dict__") else {**panel.__dict__} for panel in self.panels]}


def build_figures_8_11_source_contract() -> Figures811SourceContract:
    unresolved = (
        UnresolvedSourceField("independent_values", ("docs/reports/2026-07-01-hoodie-paper-to-code-gap-audit.md", "docs/plans/2026-06-28-phase1-master-paper-faithful-hoodie-reproduction-plan.md"), "panel grid not fully extractable from accessible repository docs"),
        UnresolvedSourceField("fixed_topology", ("docs/analysis/hoodie_superiority_gap.md",), "exact panel-specific topology contract not isolated in canonical docs"),
    )
    panels = tuple(
        PanelSourceContract(
            panel_id=panel_id,
            scientific_question=f"Engineering smoke reproduction contract for {panel_id}",
            independent_variable="policy" if panel_id in {"figure_8a", "figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e"} else "seed",
            dependent_metric="reward",
            compared_policies=("FLC", "RO", "HO", "VO", "BCO", "MLEO"),
            unresolved_fields=unresolved,
            source_citation="docs/reports/2026-07-01-hoodie-paper-to-code-gap-audit.md",
        )
        for panel_id in ("figure_8a", "figure_8b", "figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e", "figure_10a", "figure_10b", "figure_10c", "figure_10d", "figure_10e", "figure_10f", "figure_11")
    )
    return Figures811SourceContract(panels=panels)


def write_figures_8_11_source_contract(path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    contract = build_figures_8_11_source_contract()
    payload = {
        "panels": [
            {
                "panel_id": panel.panel_id,
                "scientific_question": panel.scientific_question,
                "independent_variable": panel.independent_variable,
                "independent_values": list(panel.independent_values),
                "dependent_metric": panel.dependent_metric,
                "compared_policies": list(panel.compared_policies),
                "fixed_topology": panel.fixed_topology,
                "unresolved_fields": [field.__dict__ if hasattr(field, "__dict__") else {"field": field.field, "searched_sources": list(field.searched_sources), "reason": field.reason} for field in panel.unresolved_fields],
                "source_citation": panel.source_citation,
                "confidence_level": panel.confidence_level,
            }
            for panel in contract.panels
        ]
    }
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
