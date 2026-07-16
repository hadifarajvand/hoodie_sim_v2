from __future__ import annotations

from pathlib import Path

from src.hoodie.experiments.contract_mapping import build_environment_config, build_evaluation_config, build_training_config, validate_contract_mapping
from src.hoodie.experiments.job_matrix import build_production_job_matrix
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY


def _row(job_id: str):
    return next(row for row in build_production_job_matrix('figures-8-11-test') if row.job_id == job_id)


def test_figure_8a_episode_count_comes_from_source_contract() -> None:
    row = _row('figure_8a-1-HOODIE-None')
    config = build_training_config(row, PANEL_REGISTRY['figure_8a'].source_contract, trace_hash='trace', output_dir=Path('/tmp'))
    assert config.episode_count == 5000
    assert config.episode_count != 500


def test_figure_11_episode_count_locked() -> None:
    row = _row('figure_11-0-HOODIE-hoodie_lstm')
    config = build_training_config(row, PANEL_REGISTRY['figure_11'].source_contract, trace_hash='trace', output_dir=Path('/tmp'))
    assert config.episode_count == 3000


def test_figure_9a_probability_changes_only_arrival_probability() -> None:
    row = _row('figure_9a-0-HOODIE-None')
    config = build_environment_config(row, PANEL_REGISTRY['figure_9a'].source_contract)
    assert config.arrival_probability == 0.1
    assert config.agent_count == PANEL_REGISTRY['figure_9a'].source_contract['agent_counts'][0]


def test_figure_9c_cpu_changes_cpu_capacity_only() -> None:
    row = _row('figure_9c-0-HOODIE-None')
    config = build_environment_config(row, PANEL_REGISTRY['figure_9c'].source_contract)
    assert config.metadata['cpu_computation_capacity_ghz'] == 4


def test_figure_9d_agent_count_changes_agent_count_only() -> None:
    row = _row('figure_9d-0-HOODIE-None')
    config = build_environment_config(row, PANEL_REGISTRY['figure_9d'].source_contract)
    assert config.agent_count == 10


def test_figure_10_timeout_changes_timeout_only() -> None:
    row = _row('figure_10c-0-HOODIE-None')
    config = build_environment_config(row, PANEL_REGISTRY['figure_10c'].source_contract)
    assert config.timeout_slots > 0


def test_all_training_rows_validate_source_contract() -> None:
    rows = build_production_job_matrix('figures-8-11-test')
    for row in rows:
        if row.job_type == 'training':
            assert validate_contract_mapping(row, PANEL_REGISTRY[row.panel_id].source_contract) == []


def test_all_evaluation_rows_validate_source_contract() -> None:
    rows = build_production_job_matrix('figures-8-11-test')
    for row in rows:
        if row.job_type == 'evaluation':
            assert validate_contract_mapping(row, PANEL_REGISTRY[row.panel_id].source_contract) == []


def test_evaluation_config_uses_locked_validation_episodes() -> None:
    row = _row('figure_10a-0-HOODIE-None')
    config = build_evaluation_config(row, PANEL_REGISTRY['figure_10a'].source_contract, trace_id='trace', output_dir=Path('/tmp'))
    assert config.episode_count == 200



def test_allow_paused_recovery_requires_pause(tmp_path: Path) -> None:
    from src.hoodie.experiments.production_campaign import resume_production_campaign
    import pytest
    with pytest.raises(ValueError):
        resume_production_campaign('figures-8-11-test', tmp_path / 'artifacts' / 'hoodie' / 'campaigns', job_id='figure_8a-1-HOODIE-None', allow_paused_recovery=True)
