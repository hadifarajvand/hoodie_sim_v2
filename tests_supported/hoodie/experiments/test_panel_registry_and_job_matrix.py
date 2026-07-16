from __future__ import annotations

from src.hoodie.experiments.job_matrix import build_production_job_matrix
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY


def test_panel_registry_matches_figures_8_11() -> None:
    assert set(PANEL_REGISTRY) == {
        'figure_8a', 'figure_8b', 'figure_9a', 'figure_9b', 'figure_9c', 'figure_9d', 'figure_9e',
        'figure_10a', 'figure_10b', 'figure_10c', 'figure_10d', 'figure_10e', 'figure_10f', 'figure_11'
    }
    assert PANEL_REGISTRY['figure_8a'].spec.independent_variable == 'training_episode'
    assert PANEL_REGISTRY['figure_10a'].spec.policies == ('HOODIE', 'FLC', 'RO', 'HO', 'VO', 'BCO', 'MLEO')
    assert PANEL_REGISTRY['figure_11'].spec.variants == ('hoodie_lstm', 'hoodie_no_lstm')
    assert PANEL_REGISTRY['figure_11'].spec.output_filenames == ('figure_11.svg', 'figure_11.pdf', 'figure_11.png')


def test_job_matrix_has_expected_scientific_units() -> None:
    rows = build_production_job_matrix('figures-8-11-production')
    assert rows
    assert any(row.panel_id == 'figure_11' and row.variant == 'hoodie_lstm' for row in rows)
    assert any(row.panel_id == 'figure_11' and row.variant == 'hoodie_no_lstm' for row in rows)
    assert any(row.panel_id == 'figure_10a' and row.policy == 'HOODIE' for row in rows)
    assert len({row.scientific_unit_id for row in rows}) == len(rows)
