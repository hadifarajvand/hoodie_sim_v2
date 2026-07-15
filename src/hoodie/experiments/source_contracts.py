from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

SOURCE_CONTRACT_PATH = Path("artifacts/hoodie/source_contracts/figures_8_11_source_contract.json")


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
    source_status: str = "paper_explicit"

    def is_fully_resolved(self) -> bool:
        return not self.unresolved_fields


@dataclass(frozen=True, slots=True)
class Figures811SourceContract:
    panels: tuple[PanelSourceContract, ...]
    source_path: str = str(SOURCE_CONTRACT_PATH)

    def unresolved_fields(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for panel in self.panels:
            for field in panel.unresolved_fields:
                rows.append(
                    {
                        "panel_id": panel.panel_id,
                        "field": field.field,
                        "searched_sources": list(field.searched_sources),
                        "reason": field.reason,
                    }
                )
        return rows

    def resolved_panel_count(self) -> int:
        return sum(1 for panel in self.panels if panel.is_fully_resolved())

    def summary(self) -> dict[str, Any]:
        return {
            "panel_count": len(self.panels),
            "resolved_panel_count": self.resolved_panel_count(),
            "unresolved_field_count": len(self.unresolved_fields()),
            "source_path": self.source_path,
        }


def _load_source_contract_payload() -> dict[str, Any]:
    if not SOURCE_CONTRACT_PATH.exists():
        raise FileNotFoundError(f"missing source contract artifact: {SOURCE_CONTRACT_PATH}")
    return json.loads(SOURCE_CONTRACT_PATH.read_text(encoding="utf-8"))


def _panel_from_payload(payload: dict[str, Any]) -> PanelSourceContract:
    fixed_topology = payload.get("fixed_topology", {})
    if not isinstance(fixed_topology, dict):
        fixed_topology = {"value": fixed_topology}
    return PanelSourceContract(
        panel_id=payload["panel_id"],
        scientific_question=payload["scientific_question"],
        independent_variable=payload["independent_variable"],
        independent_values=tuple(payload.get("independent_values", ())),
        dependent_metric=payload.get("dependent_metric", ""),
        compared_policies=tuple(payload.get("compared_policies", ())),
        fixed_topology=fixed_topology,
        unresolved_fields=tuple(
            UnresolvedSourceField(
                field=item["field"],
                searched_sources=tuple(item.get("searched_sources", ())),
                reason=item["reason"],
            )
            for item in payload.get("unresolved_fields", ())
        ),
        source_citation=payload.get("source_citation", ""),
        confidence_level=float(payload.get("confidence_level", 0.95)),
        source_status=payload.get("source_status", "paper_explicit"),
    )


def build_figures_8_11_source_contract() -> Figures811SourceContract:
    payload = _load_source_contract_payload()
    panel_payloads = payload.get("panels") or payload.get("figures") or ()
    panels = tuple(_panel_from_payload(panel) for panel in panel_payloads)
    return Figures811SourceContract(panels=panels, source_path=str(SOURCE_CONTRACT_PATH))


def write_figures_8_11_source_contract(path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(SOURCE_CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return destination
