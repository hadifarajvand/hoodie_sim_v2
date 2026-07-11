from __future__ import annotations

import unittest
from pathlib import Path

from src.environment.compute_config import ComputeConfig
from src.environment.runtime_model import (
    SharedRuntimeParameters,
    advance_shared_runtime,
    resolve_runtime_terminal_state,
)
from src.environment.task import Task


class SharedRuntimeModelTests(unittest.TestCase):
    def _task(self) -> Task:
        return Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=8.0,
            processing_density=4.0,
            timeout_length=3,
            absolute_deadline_slot=4,
        )

    def test_destination_specific_service_timing_differs_when_capacity_changes(self) -> None:
        task = self._task()
        compute_config_low = ComputeConfig(cpu_capacity_per_slot_agent=1.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0)
        compute_config_medium = ComputeConfig(cpu_capacity_per_slot_agent=2.0, cpu_capacity_per_slot_edge=2.0, cpu_capacity_per_slot_cloud=2.0)
        compute_config_high = ComputeConfig(cpu_capacity_per_slot_agent=4.0, cpu_capacity_per_slot_edge=4.0, cpu_capacity_per_slot_cloud=4.0)
        
        local = advance_shared_runtime(
            task,
            "local",
            current_slot=1,
            parameters=SharedRuntimeParameters(slot_duration=1),
            compute_config=compute_config_low,
        )
        public = advance_shared_runtime(
            task,
            "public",
            current_slot=1,
            parameters=SharedRuntimeParameters(slot_duration=1),
            compute_config=compute_config_medium,
        )
        cloud = advance_shared_runtime(
            task,
            "cloud",
            current_slot=1,
            parameters=SharedRuntimeParameters(slot_duration=1),
            compute_config=compute_config_high,
        )

        self.assertGreater(local.service_slots, public.service_slots)
        self.assertGreater(public.service_slots, cloud.service_slots)

    def test_offload_timing_remains_one_hop_and_bounded(self) -> None:
        task = self._task()
        compute_config = ComputeConfig()
        public = advance_shared_runtime(
            task,
            "public",
            current_slot=2,
            parameters=SharedRuntimeParameters(),
            compute_config=compute_config,
        )
        cloud = advance_shared_runtime(
            task,
            "cloud",
            current_slot=2,
            parameters=SharedRuntimeParameters(),
            compute_config=compute_config,
        )

        self.assertEqual(public.offload_slots, 1)
        self.assertEqual(cloud.offload_slots, 1)
        self.assertGreaterEqual(public.terminal_slot, task.arrival_slot + 1)
        self.assertGreaterEqual(cloud.terminal_slot, task.arrival_slot + 1)

    def test_terminal_resolution_respects_deadlines_after_runtime_progression(self) -> None:
        completed = self._task()
        resolve_runtime_terminal_state(completed, terminal_slot=3, current_slot=1, parameters=SharedRuntimeParameters())
        self.assertEqual(completed.terminal_outcome, "completed")
        self.assertFalse(completed.drop_flag)
        self.assertTrue(completed.reward_emitted)

        dropped = self._task()
        resolve_runtime_terminal_state(dropped, terminal_slot=7, current_slot=1, parameters=SharedRuntimeParameters())
        self.assertEqual(dropped.terminal_outcome, "dropped")
        self.assertTrue(dropped.drop_flag)
        self.assertTrue(dropped.reward_emitted)

    def test_drain_slot_behavior_can_continue_pending_task_after_action_window(self) -> None:
        task = self._task()
        compute_config = ComputeConfig()
        progress = advance_shared_runtime(
            task,
            "local",
            current_slot=5,
            parameters=SharedRuntimeParameters(),
            compute_config=compute_config,
        )
        self.assertGreater(progress.terminal_slot, task.arrival_slot)
        self.assertGreater(progress.waiting_slots, 0)

    def test_runtime_config_and_capacity_defaults_are_loaded_consistently(self) -> None:
        config_path = Path("configs/runtime_model.yml")
        self.assertTrue(config_path.exists())
        config_text = config_path.read_text()
        self.assertIn("slot_duration: 0.1", config_text)
        self.assertIn("local_service_capacity: 0.5", config_text)
        self.assertIn("public_service_capacity: 0.5", config_text)
        self.assertIn("cloud_service_capacity: 3.0", config_text)
        self.assertIn("timeout_grace_slots: 0", config_text)
        self.assertIn("runtime_variant: density_based", config_text)

        parameters = SharedRuntimeParameters()
        self.assertEqual(parameters.slot_duration, 0.1)
        self.assertEqual(parameters.local_service_capacity, 0.5)
        self.assertEqual(parameters.public_service_capacity, 0.5)
        self.assertEqual(parameters.cloud_service_capacity, 3.0)
        self.assertEqual(parameters.timeout_grace_slots, 0)
        self.assertEqual(parameters.runtime_variant, "density_based")

    def test_runtime_variants_change_delay_values_without_changing_structure(self) -> None:
        task = self._task()
        compute_config = ComputeConfig()
        density = advance_shared_runtime(
            task,
            "local",
            current_slot=1,
            parameters=SharedRuntimeParameters(runtime_variant="density_based"),
            compute_config=compute_config,
        )
        discrete = advance_shared_runtime(
            task,
            "local",
            current_slot=1,
            parameters=SharedRuntimeParameters(runtime_variant="discrete_slot_service"),
            compute_config=compute_config,
        )
        constant = advance_shared_runtime(
            task,
            "local",
            current_slot=1,
            parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=compute_config,
        )

        self.assertNotEqual(density.service_slots, discrete.service_slots)
        self.assertNotEqual(density.service_slots, constant.service_slots)
        self.assertEqual(density.waiting_slots, discrete.waiting_slots)
        self.assertEqual(density.waiting_slots, constant.waiting_slots)
        self.assertEqual(density.offload_slots, discrete.offload_slots)
        self.assertEqual(density.offload_slots, constant.offload_slots)
        self.assertEqual(density.terminal_slot is not None, discrete.terminal_slot is not None)
        self.assertEqual(density.terminal_slot is not None, constant.terminal_slot is not None)

if __name__ == "__main__":
    unittest.main()
