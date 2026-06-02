from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import math


def _is_non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class FormulaRegistryEntry:
    formula_id: str
    formula_name: str
    equation: str
    source: str
    implementation_reference: str
    status: str
    note: str

    def __post_init__(self) -> None:
        if not _is_non_empty_text(self.formula_id):
            raise ValueError("formula_id must be non-empty")
        if not _is_non_empty_text(self.formula_name):
            raise ValueError("formula_name must be non-empty")
        if not _is_non_empty_text(self.equation):
            raise ValueError("equation must be non-empty")
        if not _is_non_empty_text(self.source):
            raise ValueError("source must be non-empty")
        if not _is_non_empty_text(self.implementation_reference):
            raise ValueError("implementation_reference must be non-empty")
        if self.status not in {"implemented", "partial", "missing"}:
            raise ValueError("status must be explicit and recognized")
        if not _is_non_empty_text(self.note):
            raise ValueError("note must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def paper_action_vector(primary_decision: int | bool, destination_kind: str) -> tuple[int, str]:
    decision_bit = int(bool(primary_decision))
    if destination_kind not in {"local", "horizontal", "vertical"}:
        raise ValueError("destination_kind must be one of local, horizontal, vertical")
    if decision_bit == 1 and destination_kind != "local":
        raise ValueError("local decisions must use the local destination kind")
    if decision_bit == 0 and destination_kind == "local":
        raise ValueError("offloading decisions must not use the local destination kind")
    return decision_bit, destination_kind


def compute_private_cost(*, psi_priv: int, t: int) -> int:
    return psi_priv - t + 1


def compute_public_cost(*, destination_completion_slot: int, arrival_slot: int) -> int:
    return destination_completion_slot - arrival_slot + 1


def compute_reward(
    *,
    task_present: bool,
    terminal_status: str,
    phi_value: int | float | None,
    drop_cost: int | float,
) -> float:
    if not task_present:
        return math.nan
    if terminal_status in {"completed_private", "completed_public", "completed_cloud"}:
        if phi_value is None:
            raise ValueError("phi_value is required for successful terminal states")
        return -float(phi_value)
    if terminal_status in {"dropped_timeout", "dropped_unavailable"}:
        return -float(drop_cost)
    raise ValueError("unsupported terminal_status")


def build_formula_registry() -> tuple[FormulaRegistryEntry, ...]:
    return (
        FormulaRegistryEntry(
            formula_id="action_vector",
            formula_name="Hybrid action vector",
            equation="a_n(t) = [d_n^(1)(t), D_n(t)]",
            source="HOODIE base paper, action selection section",
            implementation_reference="src/analysis/hoodie_proposed_method/action_model.py",
            status="implemented",
            note="Paper action vector encoded as local/offload bit plus destination kind.",
        ),
        FormulaRegistryEntry(
            formula_id="private_cost",
            formula_name="Private queue delay cost",
            equation="Phi_priv = psi_priv - t + 1",
            source="HOODIE base paper, private queue cost definition",
            implementation_reference="src/analysis/hoodie_proposed_method/queue_model.py",
            status="implemented",
            note="Used for local processing delay cost.",
        ),
        FormulaRegistryEntry(
            formula_id="public_cost",
            formula_name="Offloaded/public delay cost",
            equation="Phi_pub = destination_completion_slot - arrival_slot + 1",
            source="HOODIE base paper, offloaded/public queue delay definition",
            implementation_reference="src/analysis/hoodie_proposed_method/queue_model.py",
            status="implemented",
            note="Used for offloaded task completion delay.",
        ),
        FormulaRegistryEntry(
            formula_id="reward_model",
            formula_name="Reward/cost mapping",
            equation="reward = NaN for no task; reward = -Phi(t) for success; reward = -C for drop",
            source="HOODIE base paper, reward section",
            implementation_reference="src/analysis/hoodie_proposed_method/reward_model.py",
            status="implemented",
            note="Honest paper reward mapping retained.",
        ),
        FormulaRegistryEntry(
            formula_id="distributed_edge_agent_decision",
            formula_name="Distributed edge-agent decision model",
            equation="agent decision = q(state, action family) with epsilon-greedy selection",
            source="HOODIE base paper, distributed decision section",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            note="The repository exposes the decision interface, but not a full training runtime.",
        ),
        FormulaRegistryEntry(
            formula_id="double_dqn_target",
            formula_name="Double DQN target rule",
            equation="target = Q_target(argmax_a Q_online(s', a))",
            source="HOODIE base paper, Double DQN target update rule",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            note="Target selection is modeled as an interface-level helper.",
        ),
        FormulaRegistryEntry(
            formula_id="dueling_value_advantage",
            formula_name="Dueling DQN value/advantage interface",
            equation="Q(s, a) = V(s) + A(s, a) - mean_a A(s, a)",
            source="HOODIE base paper, dueling architecture section",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            note="The value/advantage interface is present, but it is not a trainable network.",
        ),
        FormulaRegistryEntry(
            formula_id="lstm_forecast_recovery",
            formula_name="LSTM forecast/recovery interface",
            equation="forecast(history) -> next load estimate; recover(delayed_history) -> restored signal",
            source="HOODIE base paper, load forecasting and recovery section",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            note="The interface exists, but the repository does not expose a trained LSTM runtime here.",
        ),
        FormulaRegistryEntry(
            formula_id="replay_memory",
            formula_name="Replay memory interface",
            equation="experience buffer with sampled batches",
            source="HOODIE base paper, experience replay section",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="implemented",
            note="The buffer is a bounded FIFO replay memory with deterministic and random sampling paths.",
        ),
        FormulaRegistryEntry(
            formula_id="epsilon_greedy_schedule",
            formula_name="Epsilon-greedy training schedule",
            equation="epsilon decays from 1.0 to 0.0 across early episodes",
            source="HOODIE base paper, exploration schedule section",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="partial",
            note="The schedule helper exists, but it is not wired into a full trainer loop.",
        ),
        FormulaRegistryEntry(
            formula_id="inference_mode",
            formula_name="Inference mode with epsilon zero",
            equation="epsilon = 0 selects greedy action from Q values",
            source="HOODIE base paper, deployment mode contract",
            implementation_reference="src/analysis/hoodie_proposed_method/learning_model.py",
            status="implemented",
            note="Greedy inference is explicit and does not sample exploration.",
        ),
        FormulaRegistryEntry(
            formula_id="pubsub_recovery_metadata",
            formula_name="Pub-Sub recovery metadata",
            equation="brokered delayed/stale message recovery metadata",
            source="HOODIE base paper, communication recovery section",
            implementation_reference="src/analysis/hoodie_proposed_method/communication_model.py",
            status="implemented",
            note="Broker metadata is explicit and traceable.",
        ),
    )
