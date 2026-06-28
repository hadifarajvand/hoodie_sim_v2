"""
Phase 0, Part 4: Verify service delay computation matches paper-derived manual calculations.

Paper parameters (Table 4):
- Task size: [2, 2.1, ..., 5] Mbits
- Processing density: 0.297 Gcyc/Mbit
- EA private/public capacity: 0.5 Gcyc/slot (5 GHz × 0.1 sec)
- Cloud capacity: 3.0 Gcyc/slot (30 GHz × 0.1 sec)
- Slot duration: 0.1 sec
"""

import math
import unittest

from src.environment.task import Task
from src.environment.compute_config import ComputeConfig
from src.environment.runtime_model import (
    SharedRuntimeParameters,
    compute_service_delay,
    resolve_destination_kind,
)


class TestServiceDelayManualCalculation(unittest.TestCase):
    """Verify compute_service_delay matches paper-derived manual calculations."""

    def setUp(self) -> None:
        """Use paper-derived default capacities."""
        self.compute_config = ComputeConfig(
            cpu_capacity_per_slot_agent=0.5,
            cpu_capacity_per_slot_edge=0.5,
            cpu_capacity_per_slot_cloud=3.0,
        )
        self.parameters = SharedRuntimeParameters()
        self.processing_density = 0.297  # Gcyc/Mbit (from paper)

    def _make_task(self, size_mbits: float) -> Task:
        """Create a task with given size and default processing density."""
        cycles = size_mbits * self.processing_density
        return Task(
            task_id=1,
            source_agent_id=1,
            size=size_mbits,
            processing_density=self.processing_density,
            cycles_required=cycles,
            arrival_slot=0,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

    def test_min_task_size_local_delay(self) -> None:
        """Minimum paper task size (2 Mbits) on local (0.5 Gcyc/slot)."""
        task = self._make_task(2.0)
        cycles = 2.0 * 0.297  # = 0.594 Gcyc
        expected_slots = max(1, int(math.ceil(cycles / 0.5)))  # ceil(0.594/0.5) = ceil(1.188) = 2
        delay = compute_service_delay(task, "local", self.parameters, self.compute_config)
        self.assertEqual(delay, expected_slots)

    def test_max_task_size_local_delay(self) -> None:
        """Maximum paper task size (5 Mbits) on local (0.5 Gcyc/slot)."""
        task = self._make_task(5.0)
        cycles = 5.0 * 0.297  # = 1.485 Gcyc
        expected_slots = max(1, int(math.ceil(cycles / 0.5)))  # ceil(1.485/0.5) = ceil(2.97) = 3
        delay = compute_service_delay(task, "local", self.parameters, self.compute_config)
        self.assertEqual(delay, expected_slots)

    def test_mid_task_size_local_delay(self) -> None:
        """Mid paper task size (3.5 Mbits) on local (0.5 Gcyc/slot)."""
        task = self._make_task(3.5)
        cycles = 3.5 * 0.297  # = 1.0395 Gcyc
        expected_slots = max(1, int(math.ceil(cycles / 0.5)))  # ceil(1.0395/0.5) = ceil(2.079) = 3
        delay = compute_service_delay(task, "local", self.parameters, self.compute_config)
        self.assertEqual(delay, expected_slots)

    def test_min_task_size_cloud_delay(self) -> None:
        """Minimum paper task size (2 Mbits) on cloud (3.0 Gcyc/slot)."""
        task = self._make_task(2.0)
        cycles = 2.0 * 0.297  # = 0.594 Gcyc
        expected_slots = max(1, int(math.ceil(cycles / 3.0)))  # ceil(0.594/3.0) = ceil(0.198) = 1
        delay = compute_service_delay(task, "cloud", self.parameters, self.compute_config)
        self.assertEqual(delay, expected_slots)

    def test_max_task_size_cloud_delay(self) -> None:
        """Maximum paper task size (5 Mbits) on cloud (3.0 Gcyc/slot)."""
        task = self._make_task(5.0)
        cycles = 5.0 * 0.297  # = 1.485 Gcyc
        expected_slots = max(1, int(math.ceil(cycles / 3.0)))  # ceil(1.485/3.0) = ceil(0.495) = 1
        delay = compute_service_delay(task, "cloud", self.parameters, self.compute_config)
        self.assertEqual(delay, expected_slots)

    def test_edge_same_as_local_delay(self) -> None:
        """Edge/public capacity is same as local (0.5 Gcyc/slot), so delays match."""
        task = self._make_task(4.0)
        local_delay = compute_service_delay(task, "local", self.parameters, self.compute_config)
        edge_delay = compute_service_delay(task, "public", self.parameters, self.compute_config)
        self.assertEqual(local_delay, edge_delay)

    def test_cloud_faster_than_local(self) -> None:
        """Cloud (3.0 Gcyc/slot) must be faster than local (0.5 Gcyc/slot)."""
        task = self._make_task(5.0)
        local_delay = compute_service_delay(task, "local", self.parameters, self.compute_config)
        cloud_delay = compute_service_delay(task, "cloud", self.parameters, self.compute_config)
        self.assertLess(cloud_delay, local_delay)


class TestComputeCapacityVerification(unittest.TestCase):
    """Verify ComputeConfig uses paper-derived capacity values."""

    def test_default_agent_capacity(self) -> None:
        """Default agent capacity must be 0.5 Gcyc/slot (paper-derived: 5 GHz × 0.1 sec)."""
        config = ComputeConfig()
        self.assertEqual(config.cpu_capacity_per_slot_agent, 0.5)

    def test_default_edge_capacity(self) -> None:
        """Default edge capacity must be 0.5 Gcyc/slot."""
        config = ComputeConfig()
        self.assertEqual(config.cpu_capacity_per_slot_edge, 0.5)

    def test_default_cloud_capacity(self) -> None:
        """Default cloud capacity must be 3.0 Gcyc/slot (paper-derived: 30 GHz × 0.1 sec)."""
        config = ComputeConfig()
        self.assertEqual(config.cpu_capacity_per_slot_cloud, 3.0)

    def test_capacity_for_local(self) -> None:
        """capacity_for('local') must return agent capacity."""
        config = ComputeConfig()
        self.assertEqual(config.capacity_for("local"), 0.5)

    def test_capacity_for_public(self) -> None:
        """capacity_for('public') must return edge capacity."""
        config = ComputeConfig()
        self.assertEqual(config.capacity_for("public"), 0.5)

    def test_capacity_for_cloud(self) -> None:
        """capacity_for('cloud') must return cloud capacity."""
        config = ComputeConfig()
        self.assertEqual(config.capacity_for("cloud"), 3.0)

    def test_capacity_for_raises_on_unknown(self) -> None:
        """capacity_for must raise ValueError for unknown destination kinds."""
        config = ComputeConfig()
        with self.assertRaises(ValueError):
            config.capacity_for("mars")


class TestResolveDestinationKind(unittest.TestCase):
    """Verify destination kind resolution matches paper semantics."""

    def test_local_action_resolves_local(self) -> None:
        """Local action must resolve to 'local' destination kind."""
        self.assertEqual(resolve_destination_kind(None, "local"), "local")
        self.assertEqual(resolve_destination_kind(None, "compute_local"), "local")

    def test_vertical_action_resolves_cloud(self) -> None:
        """Vertical action must resolve to 'cloud' destination kind."""
        self.assertEqual(resolve_destination_kind(None, "vertical"), "cloud")
        self.assertEqual(resolve_destination_kind(None, "offload_vertical"), "cloud")

    def test_horizontal_action_resolves_public(self) -> None:
        """Horizontal action must resolve to 'public' destination kind."""
        self.assertEqual(resolve_destination_kind(None, "horizontal"), "public")
        self.assertEqual(resolve_destination_kind(None, "offload_horizontal"), "public")

    def test_explicit_kind_takes_precedence(self) -> None:
        """Explicit destination kind must take precedence over action-based."""
        self.assertEqual(resolve_destination_kind("cloud", "local"), "cloud")


if __name__ == "__main__":
    unittest.main()
