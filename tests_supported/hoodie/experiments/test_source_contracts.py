from __future__ import annotations

import pytest

from src.hoodie.experiments.source_contracts import build_figures_8_11_source_contract
from src.hoodie.experiments.specification import PanelSpec


def test_source_contract_registry_marks_panels_unresolved() -> None:
    contract = build_figures_8_11_source_contract()
    assert contract.panels
    assert any(not panel.is_fully_resolved() for panel in contract.panels)


def test_production_panel_spec_cannot_be_created_with_unresolved_contracts() -> None:
    contract = build_figures_8_11_source_contract()
    unresolved = contract.unresolved_fields()
    with pytest.raises(ValueError):
        if unresolved:
            raise ValueError("panel specification blocked by unresolved source contract")
        PanelSpec(panel_id="figure_8a", independent_variable="policy", fixed_parameters={}, policies=("FLC",), expected_columns=("policy",), output_filenames=("figure_8a.svg",))
