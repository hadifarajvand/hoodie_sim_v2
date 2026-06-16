from __future__ import annotations

import json
from pathlib import Path

from engine.dal import AgentRegistry, EdgeAgent, EdgeAgentState, PolicyBindingRegistry
from engine.euls_core import ActionDecision, SimulationScenario, TaskArrivalSpec
from engine.execution_engine import DeterministicSimulationEngine
from engine.policies import FIFOPolicy, SJFPolicy


class EdgeOnePolicy:
    name = "EDGE_ONE"

    def select_action(self, state):
        return ActionDecision.edge(1, self.name)


def _scenario(seed: int = 11) -> SimulationScenario:
    return SimulationScenario(
        scenario_id="dal",
        seed=seed,
        horizon=6,
        num_edge_nodes=2,
        edge_cpu_slots=(1.0, 1.0),
        cloud_cpu_slots=1.0,
        task_size_range=(1, 2),
        deadline_range=(4, 8),
        workload=TaskArrivalSpec(arrival_rate=1.0),
        topology={"type": "static"},
        policy_name="FIFO",
    )


def _registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(EdgeAgent(EdgeAgentState(agent_id=0), FIFOPolicy()))
    registry.register(EdgeAgent(EdgeAgentState(agent_id=1), EdgeOnePolicy()))
    return registry


def test_agent_isolation(tmp_path: Path) -> None:
    engine = DeterministicSimulationEngine(_scenario(), FIFOPolicy(), tmp_path / "run", agent_registry=_registry())
    engine.run()
    a0 = engine.agent_registry.get(0)
    a1 = engine.agent_registry.get(1)
    assert a0 is not None and a1 is not None
    assert a0.state.agent_id == 0
    assert a1.state.agent_id == 1
    assert a0.state.queue_reference is not a1.state.queue_reference
    assert a0.state.cpu_slots == 1
    assert a1.state.cpu_slots == 1


def test_determinism(tmp_path: Path) -> None:
    registry_a = _registry()
    registry_b = _registry()
    result_a = DeterministicSimulationEngine(_scenario(seed=21), FIFOPolicy(), tmp_path / "a", agent_registry=registry_a).run()
    result_b = DeterministicSimulationEngine(_scenario(seed=21), FIFOPolicy(), tmp_path / "b", agent_registry=registry_b).run()
    trace_a = json.loads(Path(result_a["trace_path"]).read_text())
    trace_b = json.loads(Path(result_b["trace_path"]).read_text())
    assert result_a["event_hash"] == result_b["event_hash"]
    assert trace_a["events"] == trace_b["events"]


def test_policy_binding_correctness(tmp_path: Path) -> None:
    agent = EdgeAgent(EdgeAgentState(agent_id=1), None)
    agent.bind_policy(EdgeOnePolicy())
    decision = agent.decide({"task_id": 3}, {"state": {"queue_lengths": {1: 0}}})
    assert decision.kind == "EDGE"
    assert decision.target_node == 1
    assert decision.label == "EDGE_1"


def test_euls_fallback_matches_baseline(tmp_path: Path) -> None:
    scenario = _scenario(seed=33)
    baseline = DeterministicSimulationEngine(scenario, FIFOPolicy(), tmp_path / "baseline")
    fallback = DeterministicSimulationEngine(scenario, FIFOPolicy(), tmp_path / "fallback", agent_registry=None)
    result_base = baseline.run()
    result_fallback = fallback.run()
    assert result_base["event_hash"] == result_fallback["event_hash"]


def test_policy_binding_registry_ordering() -> None:
    bindings = PolicyBindingRegistry()
    bindings.bind(2, SJFPolicy())
    bindings.bind(0, FIFOPolicy())
    assert list(bindings.items())[0][0] == 0
    assert list(bindings.items())[1][0] == 2
