from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.slot_engine import SlotEngine
from src.environment.runtime_model import SharedRuntimeParameters


class SlotEngineBoundaryTests(unittest.TestCase):
    def test_slot_engine_no_longer_exposes_controller_api(self) -> None:
        engine = SlotEngine()

        self.assertFalse(hasattr(engine, "run_slot"))
        self.assertFalse(hasattr(engine, "slot_flow"))
        self.assertFalse(hasattr(engine, "slot_flow_names"))

    def test_gym_environment_step_advances_slots(self) -> None:
        env = HoodieGymEnvironment(
            episode_length=2,
            topology=None,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="FLC",
        )

        observation, info = env.reset(seed=1)
        self.assertIsInstance(observation, dict)
        self.assertIn("trace_id", info)

        _next_obs, _reward, _terminated, _truncated, step_info = env.step("local")
        self.assertEqual(step_info["slot"], 1)
        self.assertGreaterEqual(env.current_slot, 1)


if __name__ == "__main__":
    unittest.main()
