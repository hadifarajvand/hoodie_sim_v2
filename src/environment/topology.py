from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

DEFAULT_APPROVED_REGISTRY_PATH = Path("resources/papers/hoodie/recovered/user-approved-assumption-registry.json")
APPROVED_FIGURE_7_ITEM_ID = "Figure_7_adjacency"
TOPOLOGY_GENERATOR_NAME = "modular-five-cluster-v1"
TOPOLOGY_GENERATOR_VERSION = "2.0.0"
TOPOLOGY_RENDERER_NAME = "matplotlib-direct-dual-export"
TOPOLOGY_RENDERER_VERSION = matplotlib.__version__
TOPOLOGY_FIGURE_SIZE_INCHES = (4.4, 4.8)
TOPOLOGY_FIGURE_CANVAS_PX = (440, 480)
TOPOLOGY_PNG_DPI = 300
PRIMARY_TOPOLOGY_SEED_OFFSET = 20260712
SENSITIVITY_TOPOLOGY_SEED_OFFSETS = (20261712, 20262712)
MODULAR_CLUSTER_COUNT = 5


@dataclass(slots=True)
class TopologyGraph:
    node_ids: tuple[str, ...]
    legal_adjacency: dict[str, tuple[str, ...]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        canonical_nodes = tuple(str(node_id) for node_id in self.node_ids)
        if len(set(canonical_nodes)) != len(canonical_nodes):
            raise ValueError("Topology node_ids must be unique")
        normalized_adjacency: dict[str, tuple[str, ...]] = {}
        node_set = set(canonical_nodes)
        for source in canonical_nodes:
            destinations = tuple(str(destination) for destination in self.legal_adjacency.get(source, ()))
            for destination in destinations:
                if destination not in node_set:
                    raise ValueError(f"Topology destination {destination} missing from node_ids")
            normalized_adjacency[source] = tuple(sorted(set(destinations), key=_natural_node_sort_key))
        if not canonical_nodes:
            self.node_ids = canonical_nodes
            self.legal_adjacency = normalized_adjacency
            return
        _validate_simple_graph(canonical_nodes, normalized_adjacency)
        self.node_ids = canonical_nodes
        self.legal_adjacency = normalized_adjacency

    def is_legal_destination(self, source_node_id: str, destination_node_id: str) -> bool:
        allowed = self.legal_adjacency.get(source_node_id, ())
        return destination_node_id in allowed

    def legal_horizontal_destinations(self, source_node_id: str) -> tuple[str, ...]:
        return tuple(
            destination
            for destination in self.legal_adjacency.get(source_node_id, ())
            if destination != "cloud" and destination != source_node_id
        )

    def node_count(self) -> int:
        return len([node_id for node_id in self.node_ids if node_id != "cloud"])

    def adjacency_matrix(self, *, include_cloud: bool = False) -> list[list[int]]:
        nodes = self._graph_nodes(include_cloud=include_cloud)
        return _adjacency_matrix_from_adjacency(nodes, self.legal_adjacency)

    def sorted_degree_sequence(self) -> tuple[int, ...]:
        return tuple(sorted((len(self.legal_horizontal_destinations(node_id)) for node_id in self._graph_nodes()), reverse=True))

    def realized_degree_sequence(self) -> tuple[int, ...]:
        return tuple(len(self.legal_horizontal_destinations(node_id)) for node_id in self._graph_nodes())

    def undirected_edges(self) -> tuple[tuple[str, str], ...]:
        edges: set[tuple[str, str]] = set()
        for source in self._graph_nodes():
            for destination in self.legal_horizontal_destinations(source):
                edges.add(tuple(sorted((source, destination), key=_natural_node_sort_key)))
        return tuple(sorted(edges, key=lambda edge: (_natural_node_sort_key(edge[0]), _natural_node_sort_key(edge[1]))))

    def edge_count(self) -> int:
        return len(self.undirected_edges())

    def density(self) -> float:
        node_count = self.node_count()
        if node_count <= 1:
            return 0.0
        return (2.0 * self.edge_count()) / float(node_count * (node_count - 1))

    def connected_component_count(self) -> int:
        return len(_connected_components(self._graph_nodes(), self.legal_adjacency))

    def is_connected(self) -> bool:
        return self.connected_component_count() == 1

    def clustering_coefficient(self) -> float:
        graph_nodes = self._graph_nodes()
        if not graph_nodes:
            return 0.0
        coefficients: list[float] = []
        for node_id in graph_nodes:
            neighbors = self.legal_horizontal_destinations(node_id)
            degree = len(neighbors)
            if degree < 2:
                coefficients.append(0.0)
                continue
            links = 0
            for left_index in range(degree):
                for right_index in range(left_index + 1, degree):
                    if self.is_legal_destination(neighbors[left_index], neighbors[right_index]):
                        links += 1
            coefficients.append((2.0 * links) / float(degree * (degree - 1)))
        return sum(coefficients) / float(len(coefficients))

    def average_shortest_path_length(self) -> float | None:
        graph_nodes = self._graph_nodes()
        if len(graph_nodes) <= 1:
            return 0.0
        if not self.is_connected():
            return None
        total_distance = 0
        pair_count = 0
        for source in graph_nodes:
            distances = _shortest_path_distances(source, graph_nodes, self.legal_adjacency)
            for destination in graph_nodes:
                if _natural_node_sort_key(source) >= _natural_node_sort_key(destination):
                    continue
                total_distance += distances[destination]
                pair_count += 1
        return total_distance / float(pair_count) if pair_count else 0.0

    def topology_hash(self) -> str:
        payload = {
            "node_ids": list(self._graph_nodes()),
            "adjacency_matrix": self.adjacency_matrix(),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def source_a20_hash(self) -> str:
        source_hash = self.metadata.get("source_a20_hash")
        if isinstance(source_hash, str) and source_hash:
            return source_hash
        return self.topology_hash()

    def export_artifacts(self, output_dir: str | Path) -> dict[str, Any]:
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        adjacency_path = directory / "adjacency.csv"
        edge_list_path = directory / "edge_list.csv"
        topology_json_path = directory / "topology.json"
        svg_path = directory / "topology.svg"
        png_path = directory / "topology_300dpi.png"
        sha_path = directory / "sha256.txt"

        graph_nodes = self._graph_nodes()
        matrix = self.adjacency_matrix()
        with adjacency_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["node_id", *graph_nodes])
            for node_id, row in zip(graph_nodes, matrix, strict=True):
                writer.writerow([node_id, *row])

        with edge_list_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["source", "destination"])
            for source, destination in self.undirected_edges():
                writer.writerow([source, destination])

        coordinate_manifest = _circle_layout_manifest(graph_nodes)
        svg_hash, png_hash, renderer_metadata = self._render_topology_artifacts(
            adjacency=matrix,
            positions=coordinate_manifest,
            svg_path=svg_path,
            png_path=png_path,
            dpi=TOPOLOGY_PNG_DPI,
        )
        metrics = self.metrics(
            coordinate_manifest=coordinate_manifest,
            renderer_metadata=renderer_metadata,
            svg_hash=svg_hash,
            png_hash=png_hash,
        )

        topology_json = {
            "generator": {
                "name": self.metadata.get("generator_name", TOPOLOGY_GENERATOR_NAME),
                "version": self.metadata.get("generator_version", TOPOLOGY_GENERATOR_VERSION),
            },
            "source_a20_hash": self.source_a20_hash(),
            "topology_hash": self.topology_hash(),
            "node_ids": graph_nodes,
            "adjacency_matrix": matrix,
            "edge_list": [list(edge) for edge in self.undirected_edges()],
            "metadata": metrics,
        }
        topology_json_path.write_text(json.dumps(topology_json, indent=2, sort_keys=True), encoding="utf-8")
        sha_path.write_text(f"{self.topology_hash()}\n", encoding="utf-8")
        return {
            "adjacency_csv": str(adjacency_path),
            "edge_list_csv": str(edge_list_path),
            "topology_json": str(topology_json_path),
            "topology_svg": str(svg_path),
            "topology_png": str(png_path),
            "sha256": str(sha_path),
        }

    def metrics(
        self,
        *,
        coordinate_manifest: dict[str, dict[str, float]] | None = None,
        renderer_metadata: dict[str, Any] | None = None,
        svg_hash: str | None = None,
        png_hash: str | None = None,
    ) -> dict[str, Any]:
        graph_nodes = self._graph_nodes()
        component_memberships = _connected_components(graph_nodes, self.legal_adjacency)
        average_shortest_path_length = self.average_shortest_path_length()
        manifest = coordinate_manifest or self.metadata.get("node_coordinates") or _circle_layout_manifest(graph_nodes)
        renderer = renderer_metadata or self.metadata.get("renderer") or _topology_renderer_metadata()
        return {
            "generator_name": self.metadata.get("generator_name", TOPOLOGY_GENERATOR_NAME),
            "generator_version": self.metadata.get("generator_version", TOPOLOGY_GENERATOR_VERSION),
            "source_a20_hash": self.source_a20_hash(),
            "adjacency_hash": self.topology_hash(),
            "N": len(graph_nodes),
            "topology_seed": self.metadata.get("topology_seed"),
            "formula": self.metadata.get(
                "formula",
                "G_N(i,j)=1 iff i!=j and ((i-1) mod 5)==((j-1) mod 5)",
            ),
            "target_degree_sequence": list(self.metadata.get("target_degree_sequence", self.sorted_degree_sequence())),
            "realized_degree_sequence": list(self.realized_degree_sequence()),
            "number_of_edges": self.edge_count(),
            "minimum_degree": min((len(self.legal_horizontal_destinations(node_id)) for node_id in graph_nodes), default=0),
            "maximum_degree": max((len(self.legal_horizontal_destinations(node_id)) for node_id in graph_nodes), default=0),
            "mean_degree": (sum(len(self.legal_horizontal_destinations(node_id)) for node_id in graph_nodes) / float(len(graph_nodes)) if graph_nodes else 0.0),
            "graph_density": self.density(),
            "connected_component_count": len(component_memberships),
            "component_memberships": [list(component) for component in component_memberships],
            "component_sizes": [len(component) for component in component_memberships],
            "average_shortest_path_length": average_shortest_path_length,
            "clustering_coefficient": self.clustering_coefficient(),
            "exact_anchor_match": self.metadata.get("exact_anchor_match"),
            "renderer": renderer,
            "figure_size_inches": [float(value) for value in TOPOLOGY_FIGURE_SIZE_INCHES],
            "figure_canvas_px": [int(value) for value in TOPOLOGY_FIGURE_CANVAS_PX],
            "png_dpi": TOPOLOGY_PNG_DPI,
            "node_coordinates": manifest,
            "svg_hash": svg_hash,
            "png_hash": png_hash,
            "generated_at": self.metadata.get("generated_at", datetime.now(UTC).isoformat()),
        }

    def _graph_nodes(self, *, include_cloud: bool = False) -> tuple[str, ...]:
        if include_cloud:
            return self.node_ids
        return tuple(node_id for node_id in self.node_ids if node_id != "cloud")

    def _render_topology_artifacts(
        self,
        *,
        adjacency: list[list[int]],
        positions: dict[str, dict[str, float]],
        svg_path: Path,
        png_path: Path,
        dpi: int,
    ) -> tuple[str, str, dict[str, Any]]:
        renderer_metadata = _topology_renderer_metadata()
        figure = _create_topology_figure(
            graph_nodes=self._graph_nodes(),
            adjacency=adjacency,
            positions=positions,
            title=_topology_figure_title(self),
        )
        try:
            figure.savefig(
                svg_path,
                format="svg",
                metadata={"Date": None, "Creator": TOPOLOGY_RENDERER_NAME},
            )
            figure.savefig(
                png_path,
                format="png",
                dpi=dpi,
                metadata={"Software": TOPOLOGY_RENDERER_NAME},
            )
        except Exception as exc:
            _safe_remove(svg_path)
            _safe_remove(png_path)
            raise RuntimeError(f"Topology artifact export failed: {exc}") from exc
        finally:
            plt.close(figure)
        _validate_export_file(svg_path, kind="svg")
        _validate_export_file(png_path, kind="png")
        svg_hash = _file_sha256(svg_path)
        png_hash = _file_sha256(png_path)
        return svg_hash, png_hash, renderer_metadata

    @classmethod
    def from_approved_assumption_registry(cls, registry_path: str | Path = DEFAULT_APPROVED_REGISTRY_PATH) -> "TopologyGraph":
        path = Path(registry_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("entries", [])
        figure = next((entry for entry in entries if entry.get("item_id") == APPROVED_FIGURE_7_ITEM_ID), None)
        if figure is None:
            raise ValueError("Approved Figure_7_adjacency assumption is missing from the registry snapshot")
        proposed_value = figure.get("proposed_value") or {}
        matrix = proposed_value.get("adjacency_matrix")
        if not isinstance(matrix, list) or len(matrix) != 20 or any(not isinstance(row, list) or len(row) != 20 for row in matrix):
            raise ValueError("Approved Figure_7_adjacency adjacency matrix must be 20x20")
        node_ids = tuple(str(index) for index in range(1, 21))
        legal_adjacency = _adjacency_from_matrix(node_ids, matrix)
        metadata = {
            "generator_name": "approved-a20-anchor",
            "generator_version": "1.0.0",
            "source_registry_path": str(path),
            "source_a20_hash": _hash_a20_matrix(matrix),
            "target_degree_sequence": list(sorted((sum(int(value) for value in row) for row in matrix), reverse=True)),
            "topology_seed": PRIMARY_TOPOLOGY_SEED_OFFSET + 20,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        return cls(node_ids=node_ids, legal_adjacency=legal_adjacency, metadata=metadata)

    @classmethod
    def for_agent_count(
        cls,
        agent_count: int,
        *,
        registry_path: str | Path = DEFAULT_APPROVED_REGISTRY_PATH,
        topology_seed: int | None = None,
    ) -> "TopologyGraph":
        if agent_count <= 0:
            raise ValueError("agent_count must be positive")
        if agent_count % MODULAR_CLUSTER_COUNT != 0:
            raise ValueError("Approved modular topology requires agent_count divisible by 5")
        anchor = cls.from_approved_assumption_registry(registry_path)
        expected_anchor = _modular_five_cluster_matrix(20)
        approved_anchor = _adjacency_matrix_from_adjacency(anchor._graph_nodes(), anchor.legal_adjacency)
        mismatches = _matrix_mismatches(approved_anchor, expected_anchor)
        if mismatches:
            formatted = ", ".join(f"({row},{col})" for row, col in mismatches[:10])
            raise ValueError(f"Approved A20 matrix does not match modular five-cluster rule: {formatted}")
        source_hash = _hash_a20_matrix(approved_anchor)
        if agent_count == 20:
            topology = cls.from_approved_assumption_registry(registry_path)
            topology.metadata.update(
                {
                    "generator_name": TOPOLOGY_GENERATOR_NAME,
                    "generator_version": TOPOLOGY_GENERATOR_VERSION,
                    "formula": "G_N(i,j)=1 iff i!=j and ((i-1) mod 5)==((j-1) mod 5)",
                    "source_a20_hash": source_hash,
                    "exact_anchor_match": True,
                    "topology_seed": None,
                }
            )
            return topology
        return _build_modular_topology(agent_count=agent_count, source_a20_hash=source_hash)


def approved_topology_seed(agent_count: int, variant_index: int = 0) -> int:
    if variant_index == 0:
        return PRIMARY_TOPOLOGY_SEED_OFFSET + agent_count
    if variant_index in {1, 2}:
        return SENSITIVITY_TOPOLOGY_SEED_OFFSETS[variant_index - 1] + agent_count
    raise ValueError("variant_index must be 0, 1, or 2")


def _build_modular_topology(*, agent_count: int, source_a20_hash: str) -> TopologyGraph:
    matrix = _modular_five_cluster_matrix(agent_count)
    node_ids = tuple(str(index) for index in range(1, agent_count + 1))
    legal_adjacency = _adjacency_from_matrix(node_ids, matrix)
    metadata = {
        "generator_name": TOPOLOGY_GENERATOR_NAME,
        "generator_version": TOPOLOGY_GENERATOR_VERSION,
        "source_a20_hash": source_a20_hash,
        "formula": "G_N(i,j)=1 iff i!=j and ((i-1) mod 5)==((j-1) mod 5)",
        "target_degree_sequence": [agent_count // MODULAR_CLUSTER_COUNT - 1 for _ in range(agent_count)],
        "topology_seed": None,
        "exact_anchor_match": False,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    return TopologyGraph(node_ids=node_ids, legal_adjacency=legal_adjacency, metadata=metadata)


def _validate_simple_graph(node_ids: tuple[str, ...], legal_adjacency: dict[str, tuple[str, ...]]) -> None:
    if any(node_id == "cloud" for node_id in node_ids):
        graph_nodes = tuple(node_id for node_id in node_ids if node_id != "cloud")
    else:
        graph_nodes = node_ids
    for source in graph_nodes:
        destinations = legal_adjacency.get(source, ())
        if source in destinations:
            raise ValueError("Topology must be loop-free")
        for destination in destinations:
            if destination != "cloud" and destination not in node_ids:
                raise ValueError(f"Topology destination {destination} missing from node_ids")


def _adjacency_from_matrix(node_ids: tuple[str, ...], matrix: list[list[int]]) -> dict[str, tuple[str, ...]]:
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


def _adjacency_from_edges(node_ids: tuple[str, ...], edges: set[tuple[int, int]]) -> dict[str, tuple[str, ...]]:
    agent_count = len(node_ids)
    neighbors: dict[int, set[int]] = {index: set() for index in range(agent_count)}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return {
        str(index + 1): tuple(str(destination + 1) for destination in sorted(neighbors[index]))
        for index in range(agent_count)
    }


def _adjacency_matrix_from_adjacency(node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> list[list[int]]:
    index = {node_id: position for position, node_id in enumerate(node_ids)}
    matrix = [[0 for _ in node_ids] for _ in node_ids]
    for source in node_ids:
        for destination in adjacency.get(source, ()):
            if destination not in index:
                continue
            matrix[index[source]][index[destination]] = 1
    return matrix


def _connected_components(node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> list[tuple[str, ...]]:
    remaining = set(node_ids)
    components: list[tuple[str, ...]] = []
    while remaining:
        start = min(remaining, key=_natural_node_sort_key)
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
        components.append(tuple(sorted(visited, key=_natural_node_sort_key)))
    return components


def _shortest_path_distances(source: str, node_ids: tuple[str, ...], adjacency: dict[str, tuple[str, ...]]) -> dict[str, int]:
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


def _derive_target_degree_sequence(anchor_degrees: list[int], agent_count: int) -> tuple[int, ...]:
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


def _repair_degree_sequence(target: tuple[int, ...], agent_count: int) -> tuple[int, ...]:
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
        if sum(candidate) % 2 == 0 and _is_graphical(candidate):
            return candidate
        for next_candidate in _neighbor_sequences(candidate, agent_count, target_mean):
            if next_candidate not in seen:
                queue.append(next_candidate)
    raise ValueError(f"Unable to realize graphical degree sequence for N={agent_count}")


def _neighbor_sequences(sequence: tuple[int, ...], agent_count: int, target_mean: float) -> list[tuple[int, ...]]:
    neighbors: list[tuple[float, tuple[int, ...]]] = []
    values = list(sequence)
    for index, degree in enumerate(values):
        if degree < agent_count - 1:
            bumped = list(values)
            bumped[index] += 1
            candidate = tuple(sorted(bumped, reverse=True))
            neighbors.append((_sequence_distance(candidate, target_mean), candidate))
        if degree > 1:
            lowered = list(values)
            lowered[index] -= 1
            candidate = tuple(sorted(lowered, reverse=True))
            neighbors.append((_sequence_distance(candidate, target_mean), candidate))
    neighbors.sort(key=lambda item: (item[0], item[1]))
    return [candidate for _score, candidate in neighbors[: max(8, len(values))]]


def _sequence_distance(sequence: tuple[int, ...], target_mean: float) -> tuple[float, int]:
    return (abs((sum(sequence) / float(len(sequence))) - target_mean), abs(sum(sequence) % 2))


def _is_graphical(sequence: tuple[int, ...]) -> bool:
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


def _havel_hakimi_realization(sequence: tuple[int, ...]) -> set[tuple[int, int]]:
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
            edge = (min(node, neighbor), max(node, neighbor))
            edges.add(edge)
            residual[position] = (neighbor_degree - 1, neighbor)
    return edges


def _connect_components_with_degree_preserving_swaps(edges: set[tuple[int, int]], *, node_count: int) -> set[tuple[int, int]]:
    current = set(edges)
    components = _components_from_edges(current, node_count)
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
                a, b = edge_left
                c, d = edge_right
                proposals = [
                    ((min(a, c), max(a, c)), (min(b, d), max(b, d))),
                    ((min(a, d), max(a, d)), (min(b, c), max(b, c))),
                ]
                for first, second in proposals:
                    if len({first[0], first[1], second[0], second[1]}) < 4:
                        continue
                    if first in current or second in current:
                        continue
                    candidate = set(current)
                    candidate.remove(edge_left)
                    candidate.remove(edge_right)
                    candidate.add(first)
                    candidate.add(second)
                    if _is_simple_edge_set(candidate):
                        current = candidate
                        bridge_applied = True
                        break
                if bridge_applied:
                    break
            if bridge_applied:
                break
        if not bridge_applied:
            raise ValueError("Unable to connect topology components via degree-preserving swaps")
        components = _components_from_edges(current, node_count)
    return current


def _deterministic_double_edge_swaps(edges: set[tuple[int, int]], *, node_count: int, topology_seed: int) -> set[tuple[int, int]]:
    current = set(edges)
    ordered_edges = sorted(current)
    passes = max(1, min(3, node_count // 10 + 1))
    for pass_index in range(passes):
        changed = False
        ordered_edges = sorted(current)
        rotation = 0 if not ordered_edges else (topology_seed + pass_index) % len(ordered_edges)
        rotated = ordered_edges[rotation:] + ordered_edges[:rotation]
        for left_index, edge_left in enumerate(rotated):
            for edge_right in rotated[left_index + 1 :]:
                proposals = _swap_proposals(edge_left, edge_right)
                for first, second in proposals:
                    if first in current or second in current:
                        continue
                    candidate = set(current)
                    candidate.remove(edge_left)
                    candidate.remove(edge_right)
                    candidate.add(first)
                    candidate.add(second)
                    if not _is_simple_edge_set(candidate):
                        continue
                    if len(_components_from_edges(candidate, node_count)) != 1:
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


def _swap_proposals(edge_left: tuple[int, int], edge_right: tuple[int, int]) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    a, b = edge_left
    c, d = edge_right
    proposals = []
    for first, second in (
        ((min(a, c), max(a, c)), (min(b, d), max(b, d))),
        ((min(a, d), max(a, d)), (min(b, c), max(b, c))),
    ):
        if len({first[0], first[1], second[0], second[1]}) < 4:
            continue
        proposals.append((first, second))
    return tuple(proposals)


def _is_simple_edge_set(edges: set[tuple[int, int]]) -> bool:
    for left, right in edges:
        if left == right:
            return False
    return True


def _components_from_edges(edges: set[tuple[int, int]], node_count: int) -> list[tuple[int, ...]]:
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


def _modular_five_cluster_matrix(agent_count: int) -> list[list[int]]:
    if agent_count % MODULAR_CLUSTER_COUNT != 0:
        raise ValueError("Approved modular topology requires agent_count divisible by 5")
    return [
        [
            1 if row != col and ((row % MODULAR_CLUSTER_COUNT) == (col % MODULAR_CLUSTER_COUNT)) else 0
            for col in range(agent_count)
        ]
        for row in range(agent_count)
    ]


def _matrix_mismatches(actual: list[list[int]], expected: list[list[int]]) -> list[tuple[int, int]]:
    mismatches: list[tuple[int, int]] = []
    for row_index, (actual_row, expected_row) in enumerate(zip(actual, expected, strict=True), start=1):
        for col_index, (actual_value, expected_value) in enumerate(zip(actual_row, expected_row, strict=True), start=1):
            if actual_value != expected_value:
                mismatches.append((row_index, col_index))
    return mismatches


def _hash_a20_matrix(matrix: list[list[int]]) -> str:
    canonical = json.dumps(matrix, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _natural_node_sort_key(node_id: str) -> tuple[int, str]:
    try:
        return (int(node_id), node_id)
    except ValueError:
        return (10**9, node_id)


def _circle_layout(node_ids: tuple[str, ...], *, radius: float, center_x: float, center_y: float) -> dict[str, tuple[float, float]]:
    if not node_ids:
        return {}
    points: dict[str, tuple[float, float]] = {}
    for index, node_id in enumerate(node_ids):
        angle = (2.0 * math.pi * index) / float(len(node_ids)) - (math.pi / 2.0)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points[node_id] = (x, y)
    return points


def _circle_layout_manifest(node_ids: tuple[str, ...]) -> dict[str, dict[str, float]]:
    width_px, height_px = TOPOLOGY_FIGURE_CANVAS_PX
    points = _circle_layout(node_ids, radius=170.0, center_x=220.0, center_y=220.0)
    return {
        node_id: {
            "x_px": round(x, 6),
            "y_px": round(y, 6),
            "x_norm": round(x / float(width_px), 9),
            "y_norm": round(y / float(height_px), 9),
        }
        for node_id, (x, y) in points.items()
    }


def _topology_renderer_metadata() -> dict[str, Any]:
    return {
        "name": TOPOLOGY_RENDERER_NAME,
        "version": TOPOLOGY_RENDERER_VERSION,
        "backend": matplotlib.get_backend(),
        "matplotlib_config_dir": os.environ.get("MPLCONFIGDIR"),
    }


def _topology_figure_title(topology: TopologyGraph) -> str:
    graph_nodes = topology._graph_nodes()
    mean_degree = (
        sum(len(topology.legal_horizontal_destinations(node_id)) for node_id in graph_nodes) / float(len(graph_nodes))
        if graph_nodes else 0.0
    )
    return (
        f'N={topology.node_count()}, edges={topology.edge_count()}, '
        f'mean_degree={mean_degree:.2f}, hash={topology.topology_hash()[:12]}'
    )


def _create_topology_figure(
    *,
    graph_nodes: tuple[str, ...],
    adjacency: list[list[int]],
    positions: dict[str, dict[str, float]],
    title: str,
):
    fig, ax = plt.subplots(figsize=TOPOLOGY_FIGURE_SIZE_INCHES)
    ax.set_xlim(0.0, float(TOPOLOGY_FIGURE_CANVAS_PX[0]))
    ax.set_ylim(float(TOPOLOGY_FIGURE_CANVAS_PX[1]), 0.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=16, color="#111827", pad=10)
    for row_index, source in enumerate(graph_nodes):
        for col_index in range(row_index + 1, len(graph_nodes)):
            if adjacency[row_index][col_index] != 1:
                continue
            destination = graph_nodes[col_index]
            source_pos = positions[source]
            destination_pos = positions[destination]
            ax.plot(
                [source_pos["x_px"], destination_pos["x_px"]],
                [source_pos["y_px"], destination_pos["y_px"]],
                color="#4b5563",
                linewidth=2.0,
                zorder=1,
            )
    for node_id in graph_nodes:
        pos = positions[node_id]
        circle = plt.Circle((pos["x_px"], pos["y_px"]), 15.0, color="#2563eb", zorder=2)
        ax.add_patch(circle)
        ax.text(
            pos["x_px"],
            pos["y_px"] + 1.5,
            node_id,
            color="#ffffff",
            fontsize=12,
            fontfamily="Arial",
            ha="center",
            va="center",
            zorder=3,
        )
    return fig


def _validate_export_file(path: Path, *, kind: str) -> None:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Topology {kind} export failed: file missing or empty at {path}")
    if kind == "png":
        header = path.read_bytes()[:8]
        if header != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Topology png export failed: invalid PNG signature at {path}")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_remove(path: Path) -> None:
    if path.exists():
        path.unlink()
