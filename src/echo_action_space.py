from __future__ import annotations

from dataclasses import dataclass

from src.echo_types import EchoAction, EchoActionMask
from src.environment.topology import TopologyGraph


LOCAL_ACTION_KIND = "local"
HORIZONTAL_ACTION_KIND = "horizontal"
VERTICAL_ACTION_KIND = "vertical"
CLOUD_NODE_ID = "cloud"


@dataclass(frozen=True, slots=True)
class EchoActionSpace:
    source_agent_id: int
    actions: tuple[EchoAction, ...]

    @property
    def count(self) -> int:
        return len(self.actions)

    @property
    def action_ids(self) -> tuple[str, ...]:
        return tuple(action.action_id for action in self.actions)

    def by_id(self, action_id: str) -> EchoAction:
        for action in self.actions:
            if action.action_id == action_id:
                return action
        raise KeyError(action_id)


def build_echo_action_space(topology: TopologyGraph, *, source_agent_id: int) -> EchoActionSpace:
    source_id = str(source_agent_id)
    actions: list[EchoAction] = [
        EchoAction(
            canonical_index=0,
            kind=LOCAL_ACTION_KIND,
            source_agent_id=source_agent_id,
            destination_node_id=source_id,
            action_id="local",
        )
    ]
    for canonical_index, node_id in enumerate(topology.node_ids, start=1):
        kind = HORIZONTAL_ACTION_KIND
        action_id = f"horizontal_{node_id}"
        if node_id == source_id:
            action_id = f"horizontal_self_{node_id}"
        actions.append(
            EchoAction(
                canonical_index=canonical_index,
                kind=kind,
                source_agent_id=source_agent_id,
                destination_node_id=node_id,
                action_id=action_id,
            )
        )
    actions.append(
        EchoAction(
            canonical_index=len(actions),
            kind=VERTICAL_ACTION_KIND,
            source_agent_id=source_agent_id,
            destination_node_id=CLOUD_NODE_ID,
            action_id="cloud",
        )
    )
    return EchoActionSpace(source_agent_id=source_agent_id, actions=tuple(actions))


def build_physical_action_mask(
    action_space: EchoActionSpace,
    topology: TopologyGraph,
    *,
    cloud_enabled: bool = True,
) -> EchoActionMask:
    values: list[int] = []
    allowed_action_ids: list[str] = []
    reasons: dict[str, str] = {}
    source_id = str(action_space.source_agent_id)
    for action in action_space.actions:
        allowed = False
        if action.kind == LOCAL_ACTION_KIND:
            allowed = True
            reasons[action.action_id] = "local execution always legal"
        elif action.kind == VERTICAL_ACTION_KIND:
            allowed = bool(cloud_enabled)
            reasons[action.action_id] = "cloud enabled" if allowed else "cloud disabled"
        elif action.destination_node_id != source_id and topology.is_legal_destination(source_id, action.destination_node_id):
            allowed = True
            reasons[action.action_id] = "topology-connected horizontal destination"
        elif action.destination_node_id == source_id:
            reasons[action.action_id] = "self horizontal destination illegal"
        else:
            reasons[action.action_id] = "disconnected horizontal destination illegal"
        values.append(1 if allowed else 0)
        if allowed:
            allowed_action_ids.append(action.action_id)
    return EchoActionMask(values=tuple(values), allowed_action_ids=tuple(allowed_action_ids), reasons=reasons)
