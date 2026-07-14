from __future__ import annotations

from dataclasses import dataclass

from src.echo_types import EchoAction, EchoActionMask
from src.environment.topology import TopologyGraph


LOCAL_ACTION_KIND = "local"
HORIZONTAL_ACTION_KIND = "horizontal"
VERTICAL_ACTION_KIND = "vertical"
CLOUD_NODE_ID = "cloud"
DEFAULT_MAX_EDGE_AGENTS = 30


@dataclass(frozen=True, slots=True)
class EchoActionSpace:
    source_agent_id: int
    actions: tuple[EchoAction, ...]
    max_edge_agents: int = DEFAULT_MAX_EDGE_AGENTS

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


def build_echo_action_space(
    topology: TopologyGraph,
    *,
    source_agent_id: int,
    max_edge_agents: int = DEFAULT_MAX_EDGE_AGENTS,
) -> EchoActionSpace:
    """Build the fixed canonical output required by the scalability protocol.

    Output position 0 is local execution, positions 1..N_max are horizontal
    destination slots, and the final position is cloud execution.  Nodes that
    are absent from a smaller topology remain in the output and are disabled by
    ``build_physical_action_mask``.  A separate checkpoint may therefore be
    trained for each N without changing tensor dimensions or action meaning.
    """

    if max_edge_agents <= 0:
        raise ValueError("max_edge_agents must be positive")
    if topology.node_count() > max_edge_agents:
        raise ValueError(
            f"Topology has {topology.node_count()} EAs but the canonical action "
            f"space supports at most {max_edge_agents}"
        )
    source_id = str(source_agent_id)
    if source_id not in topology.node_ids:
        raise ValueError(f"Source EA {source_id} is absent from the topology")

    actions: list[EchoAction] = [
        EchoAction(
            canonical_index=0,
            kind=LOCAL_ACTION_KIND,
            source_agent_id=source_agent_id,
            destination_node_id=source_id,
            action_id="local",
        )
    ]
    for destination_index in range(1, max_edge_agents + 1):
        node_id = str(destination_index)
        action_id = f"horizontal_{node_id}"
        if node_id == source_id:
            action_id = f"horizontal_self_{node_id}"
        actions.append(
            EchoAction(
                canonical_index=destination_index,
                kind=HORIZONTAL_ACTION_KIND,
                source_agent_id=source_agent_id,
                destination_node_id=node_id,
                action_id=action_id,
            )
        )
    actions.append(
        EchoAction(
            canonical_index=max_edge_agents + 1,
            kind=VERTICAL_ACTION_KIND,
            source_agent_id=source_agent_id,
            destination_node_id=CLOUD_NODE_ID,
            action_id="cloud",
        )
    )
    return EchoActionSpace(
        source_agent_id=source_agent_id,
        actions=tuple(actions),
        max_edge_agents=max_edge_agents,
    )


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
    present_nodes = set(topology.node_ids)

    for action in action_space.actions:
        allowed = False
        if action.kind == LOCAL_ACTION_KIND:
            allowed = True
            reasons[action.action_id] = "local execution always legal"
        elif action.kind == VERTICAL_ACTION_KIND:
            allowed = bool(cloud_enabled)
            reasons[action.action_id] = "cloud enabled" if allowed else "cloud disabled"
        elif action.destination_node_id not in present_nodes:
            reasons[action.action_id] = "destination slot belongs to an absent padded node"
        elif action.destination_node_id == source_id:
            reasons[action.action_id] = "self horizontal destination illegal"
        elif topology.is_legal_destination(source_id, action.destination_node_id):
            allowed = True
            reasons[action.action_id] = "topology-connected horizontal destination"
        else:
            reasons[action.action_id] = "disconnected horizontal destination illegal"
        values.append(1 if allowed else 0)
        if allowed:
            allowed_action_ids.append(action.action_id)

    return EchoActionMask(
        values=tuple(values),
        allowed_action_ids=tuple(allowed_action_ids),
        reasons=reasons,
    )
