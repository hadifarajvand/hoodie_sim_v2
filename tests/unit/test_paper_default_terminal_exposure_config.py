from __future__ import annotations

import unittest

from src.analysis.paper_default_terminal_exposure_probe import TerminalExposureProbeConfig


class PaperDefaultTerminalExposureConfigUnitTests(unittest.TestCase):
    def test_probe_config_uses_paper_default_t_110(self) -> None:
        config = TerminalExposureProbeConfig()
        self.assertEqual(config.feature_id, "042-paper-default-terminal-exposure-probe")
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.slot_duration_seconds, 0.1)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(config.node_count, 20)
        self.assertEqual(config.seeds, [0, 1, 2])
        self.assertEqual(
            config.strategies,
            (
                "environment_default_policy_probe",
                "force_local_legal_probe",
                "force_horizontal_legal_probe",
                "force_vertical_legal_probe",
                "mixed_legal_round_robin_probe",
            ),
        )
        self.assertTrue(config.no_training)
        self.assertTrue(config.no_runtime_mutation)

    def test_probe_config_preserves_timeout_20_slots(self) -> None:
        with self.assertRaises(ValueError):
            TerminalExposureProbeConfig(timeout_slots=19)

    def test_probe_config_rejects_wrong_episode_length(self) -> None:
        with self.assertRaises(ValueError):
            TerminalExposureProbeConfig(episode_length=20)

    def test_probe_strategies_include_local_horizontal_vertical_mixed(self) -> None:
        config = TerminalExposureProbeConfig()
        self.assertIn("force_local_legal_probe", config.strategies)
        self.assertIn("force_horizontal_legal_probe", config.strategies)
        self.assertIn("force_vertical_legal_probe", config.strategies)
        self.assertIn("mixed_legal_round_robin_probe", config.strategies)


if __name__ == "__main__":
    unittest.main()
