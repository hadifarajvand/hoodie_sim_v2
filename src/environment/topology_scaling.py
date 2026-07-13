from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime
from typing import Any

TOPOLOGY_GENERATOR_NAME = "degree-profile-preserving-scaling"
TOPOLOGY_GENERATOR_VERSION = "1.0.0"
PRIMARY_TOPOLOGY_SEED_OFFSET = 20260712
SENSITIVITY_TOPOLOGY_SEED_OFFSETS = (20261712, 20262712)


def approved_topology_seed(agent_count: int, variant_index: int = 0) -> int:
    if variant_index == 0:
        return PRIMARY_TOPOLOGY_SEED_OFFSET + agent_count
    if variant_index in {1, 2}:
        return SENSITIVITY_TOPOLOGY_SEED_OFFSETS[variant_index - 1] + agent_count
    raise ValueError("variant_index must be 0, 1, or 2")


def natural_node_sort_key(node_id: str) -> tuple[int, str]:
    try:
        return (int(node_id), node_id)
    except ValueError:
        return (10**9, node_id)


def hash_a20_matrix(matrix: list[list[int]]) -> str:
    canonical = json.dumps(matrix, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def adjacency_from_matrix(node_ids: tuple[str, ...], matrix: list[list[int]]) -> dict[str, tuple[str, ...]]:
    if any(matrix[index][index] != 0 for index in range(len(node_ids))):
        raise ValueError("Approved Figure_7_adjacency adjacency matrix must have a zero diagonal")
    if any(matrix[row][col] != matrix[col][row] for row in range(len(node_ids)) for col in range(len(node_ids))):
        raise ValueError("Approved Figure_7_adjacency adjacency matrix must be symmetric")
    legal_adjacency: dict[str, tuple[str, ...]] = {}
    for index, row in enumerate(matrix, start=1):
        if any(value not in {0, 1} for value in row):
            raise ValueError("Approved Figure_7_adjacency adjacency matrix must be binary")
        destinations = tuple(str(destination_index) for destination_index, value in enumerate(row, start=1) if value)
        legal_adjacency[str(index)] = destinations
    return legal_adjacency


def adjacency_from_edges(node_ids: tuple[str, ...], edges: set[tuple[int, int]]) -> dict[str, tuple[str, ...]]:
    neighbors: dict[int, set[int]] = {index: set() for index in range(len(node_ids))}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return {
        str(index + 1): tuple(str(destination + 1) for destination in sorted(neighbors[index]))
        for index in range(len(node_ids))
    }


def adjacency_matrix_from_adjacency(node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> list[list[int]]:
    index = {node_id: position for position, node_id in enumerate(node_ids)}
    matrix = [[0 for _ in node_ids] for _ in node_ids]
    for source in node_ids:
        for destination in adjacency.get(source, ()):
            if destination in index:
                matrix[index[source]][index[destination]] = 1
    return matrix


def connected_components(node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> list[tuple[str, ...]]:
    remaining = set(node_ids)
    components: list[tuple[str, ...]] = []
    while remaining:
        start = min(remaining, key=natural_node_sort_key)
        queue = [start]
        visited = {start}
        remaining.remove(start)
        while queue:
            source = queue.pop(0)
            for destination in adjacency.get(source, ()):
                if destination == "cloud" or destination not in remaining:
                    continue
                visited.add(destination)
                remaining.remove(destination)
                queue.append(destination)
        components.append(tuple(sorted(visited, key=natural_node_sort_key)))
    return components


def shortest_path_distances(source: str, node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> dict[str, int]:
    distances = {source: 0}
    queue = [source]
    while queue:
        current = queue.pop(0)
        for destination in adjacency.get(current, ()):
            if destination == "cloud" or destination not in node_ids or destination in distances:
                continue
            distances[destination] = distances[current] + 1
            queue.append(destination)
    if len(distances) != len(node_ids):
        raise ValueError("Disconnected topology cannot compute shortest-path length")
    return distances


def validate_simple_undirected_graph(node_ids: tuple[str, ...], legal_adjacency: dict[str, tuple[str, ...]]) -> None:
    graph_nodes = tuple(node_id for node_id in node_ids if node_id != "cloud")
    for source in graph_nodes:
        destinations = legal_adjacency.get(source, ())
        if source in destinations:
            raise ValueError("Topology must be loop-free")
        for destination in destinations:
            if destination != "cloud" and source not in legal_adjacency.get(destination, ()):
                raise ValueError("Topology adjacency must be symmetric")
    if graph_nodes and len(graph_nodes) > 1 and len(connected_components(graph_nodes, legal_adjacency)) != 1:
        raise ValueError("Topology graph must be connected")


def derive_target_degree_sequence(anchor_degrees: list[int], agent_count: int) -> tuple[int, ...]:
    if agent_count <= 0:
        raise ValueError("agent_count must be positive")
    if not anchor_degrees:
        return tuple()
    observed_min = max(1, min(anchor_degrees))
    observed_max = max(anchor_degrees)
    target: list[int] = []
    if agent_count == 1:
        return (0,)
    if agent_count == len(anchor_degrees):
        return tuple(sorted(anchor_degrees, reverse=True))
    for index in range(agent_count):
        quantile = 0.0 if agent_count == 1 else index / float(agent_count - 1)
        source_position = quantile * float(len(anchor_degrees) - 1)
        lower = int(math.floor(source_position))
        upper = int(math.ceil(source_position))
        if lower == upper:
            interpolated = float(anchor_degrees[lower])
        else:
            weight = source_position - lower
            interpolated = float(anchor_degrees[lower]) * (1.0 - weight) + float(anchor_degrees[upper]) * weight
        degree = int(round(interpolated))
        degree = max(1, min(agent_count - 1, degree))
        degree = max(observed_min, min(observed_max, degree))
        target.append(degree)
    return tuple(sorted(target, reverse=True))


def repair_degree_sequence(target: tuple[int, ...], agent_count: int) -> tuple[int, ...]:
    if agent_count == 1:
        return (0,)
    sequence = [max(1, min(agent_count - 1, int(value))) for value in target]
    target_mean = sum(sequence) / float(len(sequence)) if sequence else 0.0
    seen: set[tuple[int, ...]] = set()
    queue: list[tuple[int, ...]] = [tuple(sorted(sequence, reverse=True))]
    while queue:
        candidate = queue.pop(0)
        if candidate in seen:
            continue
        seen.add(candidate)
        if sum(candidate) % 2 == 0 and is_graphical(candidate):
            return candidate
        for next_candidate in neighbor_sequences(candidate, agent_count, target_mean):
            if next_candidate not in seen:
                queue.append(next_candidate)
    raise ValueError(f"Unable to realize graphical degree sequence for N={agent_count}")


def neighbor_sequences(sequence: tuple[int, ...], agent_count: int, target_mean: float) -> list[tuple[int, ...]]:
    neighbors: list[tuple[tuple[float, int], tuple[int, ...]]] = []
    values = list(sequence)
    for index, degree in enumerate(values):
        if degree < agent_count - 1:
            bumped = list(values)
            bumped[index] += 1
            candidate = tuple(sorted(bumped, reverse=True))
            neighbors.append((sequence_distance(candidate, target_mean), candidate))
        if degree > 1:
            lowered = list(values)
            lowered[index] -= 1
            candidate = tuple(sorted(lowered, reverse=True))
            neighbors.append((sequence_distance(candidate, target_mean), candidate))
    neighbors.sort(key=lambda item: (item[0], item[1]))
    return [candidate for _score, candidate in neighbors[: max(8, len(values))]]


def sequence_distance(sequence: tuple[int, ...], target_mean: float) -> tuple[float, int]:
    return (abs((sum(sequence) / float(len(sequence))) - target_mean), abs(sum(sequence) % 2))


def is_graphical(sequence: tuple[int, ...]) -> bool:
    residual = [degree for degree in sequence if degree > 0]
    while residual:
        residual.sort(reverse=True)
        degree = residual.pop(0)
        if degree < 0 or degree > len(residual):
            return False
        for index in range(degree):
            residual[index] -= 1
            if residual[index] < 0:
                return False
        residual = [value for value in residual if value > 0]
    return True


def havel_hakimi_realization(sequence: tuple[int, ...]) -> set[tuple[int, int]]:
    residual = [(degree, index) for index, degree in enumerate(sequence)]
    edges: set[tuple[int, int]] = set()
    while residual:
        residual.sort(key=lambda item: (-item[0], item[1]))
        degree, node = residual.pop(0)
        if degree == 0:
            continue
        if degree > len(residual):
            raise ValueError("Non-graphical degree sequence during Havel-Hakimi realization")
        for position in range(degree):
            neighbor_degree, neighbor = residual[position]
            if neighbor_degree <= 0:
                raise ValueError("Non-graphical degree sequence during Havel-Hakimi realization")
            edges.add((min(node, neighbor), max(node, neighbor)))
            residual[position] = (neighbor_degree - 1, neighbor)
    return edges


def connect_components_with_degree_preserving_swaps(edges: set[tuple[int, int]], *, node_count: int) -> set[tuple[int, int]]:
    current = set(edges)
    components = components_from_edges(current, node_count)
    if len(components) <= 1:
        return current
    while len(components) > 1:
        left = sorted(components[0])
        right = sorted(components[1])
        bridge_applied = False
        left_edges = [edge for edge in sorted(current) if edge[0] in left and edge[1] in left]
        right_edges = [edge for edge in sorted(current) if edge[0] in right and edge[1] in right]
        for edge_left in left_edges:
            for edge_right in right_edges:
                for first, second in swap_proposals(edge_left, edge_right):
                    if first in current or second in current:
                        continue
                    candidate = set(current)
                    candidate.remove(edge_left)
                    candidate.remove(edge_right)
                    candidate.add(first)
                    candidate.add(second)
                    if is_simple_edge_set(candidate):
                        current = candidate
                        bridge_applied = True
                        break
                if bridge_applied:
                    break
            if bridge_applied:
                break
        if not bridge_applied:
            raise ValueError("Unable to connect topology components via degree-preserving swaps")
        components = components_from_edges(current, node_count)
    return current


def deterministic_double_edge_swaps(edges: set[tuple[int, int]], *, node_count: int, topology_seed: int) -> set[tuple[int, int]]:
    current = set(edges)
    passes = max(1, min(3, node_count // 10 + 1))
    for pass_index in range(passes):
        changed = False
        ordered_edges = sorted(current)
        rotation = 0 if not ordered_edges else (topology_seed + pass_index) % len(ordered_edges)
        rotated = ordered_edges[rotation:] + ordered_edges[:rotation]
        for left_index, edge_left in enumerate(rotated):
            for edge_right in rotated[left_index + 1 :]:
                for first, second in swap_proposals(edge_left, edge_right):
                    if first in current or second in current:
                        continue
                    candidate = set(current)
                    candidate.remove(edge_left)
                    candidate.remove(edge_right)
                    candidate.add(first)
                    candidate.add(second)
                    if not is_simple_edge_set(candidate):
                        continue
                    if len(components_from_edges(candidate, node_count)) != 1:
                        continue
                    current = candidate
                    changed = True
                    break
                if changed:
                    break
            if changed:
                break
        if not changed:
            break
    return current


def swap_proposals(edge_left: tuple[int, int], edge_right: tuple[int, int]) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    a, b = edge_left
    c, d = edge_right
    proposals = []
    for first, second in (
        ((min(a, c), max(a, c)), (min(b, d), max(b, d))),
        ((min(a, d), max(a, d)), (min(b, c), max(b, c))),
    ):
        if len({first[0], first[1], second[0], second[1]}) == 4:
            proposals.append((first, second))
    return tuple(proposals)


def is_simple_edge_set(edges: set[tuple[int, int]]) -> bool:
    return all(left != right for left, right in edges)


def components_from_edges(edges: set[tuple[int, int]], node_count: int) -> list[tuple[int, ...]]:
    adjacency: dict[int, set[int]] = {index: set() for index in range(node_count)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(range(node_count))
    components: list[tuple[int, ...]] = []
    while remaining:
        start = min(remaining)
        queue = [start]
        visited = {start}
        remaining.remove(start)
        while queue:
            source = queue.pop(0)
            for destination in sorted(adjacency[source]):
                if destination in remaining:
                    remaining.remove(destination)
                    visited.add(destination)
                    queue.append(destination)
        components.append(tuple(sorted(visited)))
    return components


def scale_from_anchor(anchor: Any, *, agent_count: int, topology_seed: int) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]], dict[str, Any]]:
    anchor_nodes = tuple(node_id for node_id in anchor.node_ids if node_id != "cloud")
    anchor_degrees = sorted(len(anchor.legal_horizontal_destinations(node_id)) for node_id in anchor_nodes)
    target_sequence = derive_target_degree_sequence(anchor_degrees, agent_count)
    realized_sequence = repair_degree_sequence(target_sequence, agent_count)
    edges = havel_hakimi_realization(realized_sequence)
    edges = connect_components_with_degree_preserving_swaps(edges, node_count=agent_count)
    edges = deterministic_double_edge_swaps(edges, node_count=agent_count, topology_seed=topology_seed)
    node_ids = tuple(str(index) for index in range(1, agent_count + 1))
    metadata = {
        "generator_name": TOPOLOGY_GENERATOR_NAME,
        "generator_version": TOPOLOGY_GENERATOR_VERSION,
        "source_a20_hash": anchor.source_a20_hash(),
        "target_degree_sequence": list(target_sequence),
        "topology_seed": topology_seed,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    return node_ids, adjacency_from_edges(node_ids, edges), metadata


def circle_layout(node_ids: tuple[str, ...], *, radius: float, center_x: float, center_y: float) -> dict[str, tuple[float, float]]:
    if not node_ids:
        return {}
    return {
        node_id: (
            center_x + radius * math.cos((2.0 * math.pi * index) / float(len(node_ids)) - (math.pi / 2.0)),
            center_y + radius * math.sin((2.0 * math.pi * index) / float(len(node_ids)) - (math.pi / 2.0)),
        )
        for index, node_id in enumerate(node_ids)
    }
