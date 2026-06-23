"""Unit tests: per-EA distributed baseline structure + guards (no proposed method)."""

from __future__ import annotations

import inspect

from src.analysis.per_EA_distributed_baseline.config import (
    EXECUTION_ENV_CONFIRMATION,
    build_distributed_config,
)
from src.analysis.per_EA_distributed_baseline.distributed_trainer import DistributedTrainer
from src.analysis.per_EA_distributed_baseline import distributed_runner as runner
from src.analysis.per_EA_distributed_baseline import distributed_trainer, distributed_evaluator, reporting
from src.analysis.per_EA_distributed_baseline.paper_fidelity_audit import build_paper_distributed_agent_audit


def _trainer():
    return DistributedTrainer(build_distributed_config(), epsilon_decay_episodes=2)


def test_one_model_target_optimizer_replay_per_EA():
    t = _trainer()
    assert len(t.agents) == 20
    assert len({id(n) for n in t.online_networks()}) == 20
    assert len({id(n) for n in t.target_networks()}) == 20
    assert len({id(o) for o in t.optimizers()}) == 20
    assert len({id(r) for r in t.replay_buffers()}) == 20


def test_per_agent_epsilon_and_target_sync():
    t = _trainer()
    for a in t.agents:
        assert a.exploration is not None
        assert a.exploration.schedule_unit == "episode"
        assert a.config.target_update_contract.target_update_unit == "episode"
        assert a.config.target_update_contract.update_frequency == 2000
        assert a.per_task_credit_assignment is True


def test_full_campaign_requires_flag_and_env(monkeypatch):
    # no flag -> refuse
    import io
    import contextlib

    monkeypatch.delenv(EXECUTION_ENV_CONFIRMATION, raising=False)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = runner.run(dry_run=False, smoke=False, execute_full=False, emit_json=False)
    assert rc == 0
    assert "disabled by default" in buf.getvalue()

    # flag but no env -> refuse (must not execute)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = runner.run(dry_run=False, smoke=False, execute_full=True, emit_json=False)
    assert "disabled by default" in buf.getvalue()
    assert runner._execution_authorized(True) is False


def test_execution_authorized_only_with_both(monkeypatch):
    monkeypatch.setenv(EXECUTION_ENV_CONFIRMATION, "1")
    assert runner._execution_authorized(True) is True
    assert runner._execution_authorized(False) is False
    monkeypatch.setenv(EXECUTION_ENV_CONFIRMATION, "0")
    assert runner._execution_authorized(True) is False


def test_paper_audit_core_exact_and_no_proposed_method():
    audit = build_paper_distributed_agent_audit()
    assert audit["all_core_per_EA_items_exact"] is True
    assert audit["no_proposed_method"] is True


def test_no_proposed_method_logic_present():
    # Guard: the distributed baseline must not contain proposed-method keywords.
    forbidden = ("EDF", "LSTF", "earliest_deadline", "least_slack", "reward_shaping", "queue_replacement")
    for mod in (distributed_trainer, distributed_evaluator, reporting, runner):
        src = inspect.getsource(mod)
        for kw in forbidden:
            assert kw not in src, f"{kw} found in {mod.__name__}"


def test_config_is_paper_faithful():
    c = build_distributed_config()
    assert c.num_agents == 20
    assert c.episode_length == 110
    assert c.learning_rate == 7e-7
    assert c.gamma == 0.99
    assert c.batch_size == 64
    assert c.replay_memory_capacity == 10_000
    assert c.credit_assignment == "per_task_delayed_reward"
    assert c.reconciliation_profile == "horizon_aware_recovered_reward_event"
    assert 5000 not in c.smoke_budgets
