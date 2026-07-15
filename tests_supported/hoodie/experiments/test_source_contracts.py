from __future__ import annotations

from src.hoodie.experiments.source_contracts import build_figures_8_11_source_contract
from src.hoodie.experiments.specification import PanelSpec


def test_source_contract_registry_marks_panels_resolved() -> None:
    contract = build_figures_8_11_source_contract()
    assert contract.panels
    assert all(panel.is_fully_resolved() for panel in contract.panels)
    assert contract.resolved_panel_count() == len(contract.panels)
    assert contract.unresolved_fields() == []


def test_production_panel_spec_can_be_created_with_resolved_contracts() -> None:
    contract = build_figures_8_11_source_contract()
    assert contract.unresolved_fields() == []
    spec = PanelSpec(
        panel_id="figure_8a",
        independent_variable="policy",
        fixed_parameters={},
        policies=("FLC",),
        expected_columns=("policy",),
        output_filenames=("figure_8a.svg",),
    )
    assert spec.panel_id == "figure_8a"
