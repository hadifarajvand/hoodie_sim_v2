from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from src.agents.double_dqn import DoubleDQNSelector
from src.agents.hoodie_agent import HoodieAgent
from src.agents.hoodie_model import HoodieModel
from src.agents.history_builder import HistoryWindow
from src.agents.torchrl_hoodie_learner import TorchRLHoodieLearner
from src.agents.torchrl_tensor_adapter import TorchRLTensorAdapter
from src.config.config_loader import ConfigLoader
from src.repro.repro_guard import ReproGuard, ReproGuardError
from src.agents.replay_buffer import ReplayBuffer, Transition
from src.agents.target_network import TargetNetwork
from src.policies.policy_interface import PolicyContext
from src.training.delayed_reward_training import DelayedRewardTraining
from src.environment.task import Task


class _StubModel:
    def __init__(self) -> None:
        self.seen_history_lengths: list[int] = []

    def forward(self, history, legal_actions):
        self.seen_history_lengths.append(len(history.observations))
        return {action: float(index) for index, action in enumerate(legal_actions)}


class AgentComponentTests(unittest.TestCase):
    def _base_config_payload(self) -> dict[str, object]:
        return {
            "training": {
                "learning_rate": 0.001,
                "batch_size": 4,
                "replay_buffer_capacity": 32,
                "target_network_update_frequency": 2,
                "episode_count": 2,
                "episode_length": 2,
                "seed_management": {"training_seed": 17, "evaluation_seed": 31},
                "policy_name": "HOODIE",
                "trace_id": "agent-components",
                "trace_mode": "deterministic_seed",
                "device": "cpu",
            },
            "evaluation": {
                "policy_name": "HOODIE",
                "seed": 31,
                "trace_id": "agent-components",
                "episode_count": 2,
                "episode_length": 2,
                "trace_mode": "deterministic_seed",
                "device": "cpu",
            },
            "runtime": {
                "slot_duration": 1,
                "local_service_capacity": 1,
                "public_service_capacity": 1,
                "cloud_service_capacity": 1,
                "timeout_grace_slots": 0,
                "runtime_variant": "density_based",
            },
            "validation": {"policies": ["FLC", "HOODIE"]},
        }

    def test_training_config_exposes_optional_phase_12_fields_without_hidden_defaults(self) -> None:
        config = self._base_config_payload()
        config["training"].update(
            {
                "learner_type": "torchrl",
                "replay_seed": 99,
                "torch_seed": 123,
                "checkpoint_manifest_path": "outputs/checkpoints/manifest.json",
                "checkpoint_state_path": "outputs/checkpoints/state.json",
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

        self.assertEqual(loaded.training.learner_type, "torchrl")
        self.assertEqual(loaded.training.replay_seed, 99)
        self.assertEqual(loaded.training.torch_seed, 123)
        self.assertEqual(str(loaded.training.checkpoint_manifest_path), "outputs/checkpoints/manifest.json")
        self.assertEqual(str(loaded.training.checkpoint_state_path), "outputs/checkpoints/state.json")
        self.assertIn("\"learner_type\": \"torchrl\"", loaded.snapshot)

    def test_optional_phase_12_fields_are_omitted_when_absent(self) -> None:
        config = self._base_config_payload()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

        training_dict = loaded.training.to_dict()
        self.assertNotIn("learner_type", training_dict)
        self.assertNotIn("replay_seed", training_dict)
        self.assertNotIn("torch_seed", training_dict)
        self.assertNotIn("checkpoint_manifest_path", training_dict)
        self.assertNotIn("checkpoint_state_path", training_dict)
        self.assertEqual(loaded.training.learner_type, None)

    def test_torchrl_tensor_adapter_is_deterministic_and_mask_preserving(self) -> None:
        adapter = TorchRLTensorAdapter()
        history = HistoryWindow(
            observations=(
                {"slot": 1, "queue_load": 2, "topology": ("2", "cloud"), "fallback_hints": {"local": 1}},
                {"slot": 2, "queue_load": 3, "load_hint": 4},
            ),
            trace_history=("trace-1", "trace-2"),
        )
        result_a = adapter.adapt(history, {"local": True, "horizontal": False, "vertical": True})
        result_b = adapter.adapt(history, {"local": True, "horizontal": False, "vertical": True})

        self.assertEqual(result_a, result_b)
        self.assertEqual(result_a["legal_actions"], ("local", "vertical"))
        self.assertEqual(result_a["legal_action_index"], {"local": 0, "vertical": 1})
        self.assertEqual(result_a["action_mask"], (1.0, 1.0))
        self.assertEqual(result_a["action_mask_by_name"], {"local": 1.0, "vertical": 1.0})
        self.assertEqual(result_a["schema_version"], 1)
        self.assertEqual(result_a["history_length"], 2)
        self.assertEqual(result_a["trace_history_length"], 2)

    def test_torchrl_tensor_adapter_handles_missing_optional_fields_without_crashing(self) -> None:
        adapter = TorchRLTensorAdapter()
        history = HistoryWindow(observations=({},), trace_history=())
        result = adapter.adapt(history, ("local", "cloud"))

        self.assertEqual(result["legal_actions"], ("local", "cloud"))
        self.assertEqual(result["features"][0:6], (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        self.assertEqual(result["features"][6:], (1.0, 0.0))
        self.assertEqual(result["latest_observation"], {})

    def test_torchrl_tensor_adapter_does_not_require_torch_or_torchrl_imports(self) -> None:
        adapter = TorchRLTensorAdapter()
        history = HistoryWindow(observations=({"slot": 1},), trace_history=("trace",))
        result = adapter.adapt(history, {"local": True})

        self.assertEqual(result["features"][-2:], (1.0, 1.0))
        self.assertIsInstance(result["features"], tuple)
        self.assertIsInstance(result["legal_actions"], tuple)

    def test_torchrl_hoodie_learner_reports_dependency_availability_consistently(self) -> None:
        learner = TorchRLHoodieLearner()

        self.assertEqual(learner.is_available(), learner.__class__.is_available())

    def test_torchrl_hoodie_learner_require_available_matches_dependency_state(self) -> None:
        learner = TorchRLHoodieLearner()

        if learner.is_available():
            learner.require_available()
            return

        with self.assertRaisesRegex(RuntimeError, "torch and/or torchrl are not installed"):
            learner.require_available()

    def test_torchrl_hoodie_learner_scores_only_legal_actions_and_respects_masks(self) -> None:
        learner = TorchRLHoodieLearner()
        adapted_state = {
            "legal_actions": ("local", "horizontal", "vertical"),
            "action_mask_by_name": {"local": 1.0, "horizontal": 0.0, "vertical": 1.0},
            "features": (1.0, 2.0, 3.0),
        }

        scored = learner.score(adapted_state)

        self.assertEqual(scored["legal_actions"], ("local", "horizontal", "vertical"))
        self.assertEqual(scored["action_scores"].keys(), {"local", "vertical"})
        self.assertNotIn("horizontal", scored["action_scores"])

    def test_torchrl_hoodie_learner_update_is_deterministic_and_consumes_replay_transitions(self) -> None:
        learner = TorchRLHoodieLearner()
        transitions = (
            {"action": "local", "reward": 2.0},
            {"action": "local", "reward": -2.0},
            {"action": "horizontal", "reward": 4.0},
        )

        updated = learner.update(transitions, learning_rate=0.25)

        self.assertEqual(updated, 3)
        self.assertAlmostEqual(learner.learned_action_preferences["local"], -0.125)
        self.assertAlmostEqual(learner.learned_action_preferences["horizontal"], 1.0)

    def test_torchrl_hoodie_learner_state_roundtrip_is_deterministic(self) -> None:
        learner = TorchRLHoodieLearner()
        learner.learned_action_preferences = {"local": 1.25, "horizontal": -0.5}

        state = learner.state_dict()
        restored = TorchRLHoodieLearner()
        restored.load_state_dict(state)

        self.assertEqual(restored.state_dict(), state)
        self.assertEqual(restored.learned_action_preferences, learner.learned_action_preferences)

    def test_torchrl_learner_does_not_change_hoodie_agent_behavior(self) -> None:
        baseline_agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.update(({"action": "local", "reward": 10.0},), learning_rate=0.5)

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2}},
            legal_action_mask={"local": True, "horizontal": True},
            trace_history=("trace-1",),
        )

        self.assertEqual(baseline_agent.choose_action(context), "horizontal")

    def test_hoodie_agent_attached_learner_disabled_keeps_default_action_path(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.update(({"action": "local", "reward": 10.0},), learning_rate=0.5)
        agent.attach_learner(learner, enabled=False)

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2}},
            legal_action_mask={"local": True, "horizontal": True},
            trace_history=("trace-1",),
        )

        self.assertEqual(agent.choose_action(context), "horizontal")

    def test_hoodie_agent_learner_enabled_uses_learner_scores(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"local": 10.0, "horizontal": -5.0}})
        agent.attach_learner(learner, enabled=True)

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2}},
            legal_action_mask={"local": True, "horizontal": True},
            trace_history=("trace-1",),
        )

        self.assertEqual(agent.choose_action(context), "local")

    def test_hoodie_agent_learner_enabled_respects_illegal_actions(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"cloud": 100.0, "local": -100.0}})
        agent.attach_learner(learner, enabled=True)

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1}},
            legal_action_mask={"local": True, "cloud": False},
            trace_history=("trace-1",),
        )

        self.assertEqual(agent.choose_action(context), "local")

    def test_hoodie_agent_export_import_preserves_learner_state_when_present(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"local": 3.5}})
        agent.attach_learner(learner, enabled=True)

        exported = agent.export_state()
        restored = HoodieAgent.from_state(exported)

        self.assertIn("learner_state", exported)
        self.assertTrue(exported["learner_enabled"])
        self.assertIsNotNone(restored.learner)
        self.assertTrue(restored.learner_enabled)
        self.assertEqual(restored.learner.state_dict(), learner.state_dict())

    def test_hoodie_agent_export_state_is_deterministic_for_unchanged_agent(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"horizontal": 2.0, "local": 1.0}})
        agent.attach_learner(learner, enabled=True)

        first = agent.export_state()
        second = agent.export_state()

        self.assertEqual(first, second)
        self.assertEqual(first["learner_state"]["schema_version"], 1)
        self.assertEqual(first["learner_state"]["learned_action_preferences"], {"horizontal": 2.0, "local": 1.0})

    def test_hoodie_agent_from_state_rejects_non_mapping_learner_state(self) -> None:
        state = HoodieAgent().export_state()
        state["learner_state"] = ["not", "a", "mapping"]

        with self.assertRaisesRegex(ValueError, "learner_state must be a mapping"):
            HoodieAgent.from_state(state)

    def test_hoodie_agent_from_state_rejects_unsupported_learner_schema_version(self) -> None:
        state = HoodieAgent().export_state()
        state["learner_state"] = {
            "schema_version": 99,
            "learned_action_preferences": {"local": 1.0},
        }

        with self.assertRaisesRegex(ValueError, "Unsupported HoodieAgent state learner_state schema version: 99"):
            HoodieAgent.from_state(state)

    def test_hoodie_agent_from_state_without_learner_state_still_loads(self) -> None:
        agent = HoodieAgent()
        state = agent.export_state()

        restored = HoodieAgent.from_state(state)

        self.assertIsNone(restored.learner)
        self.assertFalse(restored.learner_enabled)
        self.assertEqual(restored.export_state(), state)

    def test_hoodie_agent_learn_from_replay_uses_model_path_by_default(self) -> None:
        agent = HoodieAgent()
        agent.record_transition({"slot": 1}, "local", 2.0, {"slot": 2}, False)
        agent.record_transition({"slot": 2}, "horizontal", -1.0, {"slot": 3}, False)

        updated = agent.learn_from_replay(batch_size=10, learning_rate=0.5)

        self.assertEqual(updated, 2)
        self.assertAlmostEqual(agent.model.learned_action_preferences["local"], 1.0)
        self.assertAlmostEqual(agent.model.learned_action_preferences["horizontal"], -0.5)

    def test_hoodie_agent_learn_from_replay_routes_to_learner_when_enabled(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner.update(({"action": "local", "reward": 9.0},), learning_rate=0.5)
        agent.attach_learner(learner, enabled=True)
        agent.record_transition({"slot": 1}, "local", 2.0, {"slot": 2}, False)
        agent.record_transition({"slot": 2}, "horizontal", -1.0, {"slot": 3}, False)

        updated = agent.learn_from_replay(batch_size=10, learning_rate=0.5)

        self.assertEqual(updated, 2)
        self.assertAlmostEqual(learner.learned_action_preferences["local"], 3.25)
        self.assertAlmostEqual(learner.learned_action_preferences["horizontal"], -0.5)
        self.assertEqual(agent.model.learned_action_preferences, {})

    def test_hoodie_agent_learn_from_replay_uses_model_path_when_learner_disabled(self) -> None:
        agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        agent.attach_learner(learner, enabled=False)
        agent.record_transition({"slot": 1}, "local", 2.0, {"slot": 2}, False)
        agent.record_transition({"slot": 2}, "horizontal", -1.0, {"slot": 3}, False)

        updated = agent.learn_from_replay(batch_size=10, learning_rate=0.5)

        self.assertEqual(updated, 2)
        self.assertEqual(learner.learned_action_preferences, {})
        self.assertAlmostEqual(agent.model.learned_action_preferences["local"], 1.0)
        self.assertAlmostEqual(agent.model.learned_action_preferences["horizontal"], -0.5)

    def test_delayed_reward_transition_reaches_learner_without_changing_reward_semantics(self) -> None:
        handler = DelayedRewardTraining()
        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=10,
            processing_density=1,
            timeout_length=2,
            absolute_deadline_slot=2,
        )

        handler.stage_transition(
            task=task,
            state={"slot": 0},
            action="local",
            next_state={"slot": 1},
            done=False,
        )
        task.terminal_outcome = "completed"
        task.completion_slot = 1
        task.reward_emitted = True

        ready = handler.consume_ready_transition(task)
        self.assertIsNotNone(ready)
        assert ready is not None
        self.assertEqual(ready.reward, -1.0)

        learner_agent = HoodieAgent()
        learner = TorchRLHoodieLearner()
        learner_agent.attach_learner(learner, enabled=True)
        learner_agent.record_transition(ready.state, ready.action, ready.reward, ready.next_state, ready.done)

        updated = learner_agent.learn_from_replay(batch_size=1, learning_rate=0.5)

        self.assertEqual(updated, 1)
        self.assertAlmostEqual(learner.learned_action_preferences["local"], -0.5)

    def test_delayed_reward_transition_uses_model_fallback_when_learner_disabled(self) -> None:
        handler = DelayedRewardTraining()
        task = Task(
            task_id=2,
            source_agent_id=1,
            arrival_slot=0,
            size=10,
            processing_density=1,
            timeout_length=2,
            absolute_deadline_slot=2,
        )

        handler.stage_transition(
            task=task,
            state={"slot": 0},
            action="local",
            next_state={"slot": 1},
            done=False,
        )
        task.terminal_outcome = "completed"
        task.completion_slot = 1
        task.reward_emitted = True

        ready = handler.consume_ready_transition(task)
        self.assertIsNotNone(ready)
        assert ready is not None
        self.assertEqual(ready.reward, -1.0)

        agent = HoodieAgent()
        agent.attach_learner(TorchRLHoodieLearner(), enabled=False)
        agent.record_transition(ready.state, ready.action, ready.reward, ready.next_state, ready.done)

        updated = agent.learn_from_replay(batch_size=1, learning_rate=0.5)

        self.assertEqual(updated, 1)
        self.assertAlmostEqual(agent.model.learned_action_preferences["local"], -0.5)

    def test_repro_guard_only_checks_torchrl_dependencies_for_torchrl_learner_type(self) -> None:
        config = self._base_config_payload()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

        ReproGuard(loaded).validate()

        torchrl_config = self._base_config_payload()
        torchrl_config["training"]["learner_type"] = "torchrl"
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "torchrl_config.json"
            config_path.write_text(json.dumps(torchrl_config, sort_keys=True), encoding="utf-8")
            loaded_torchrl = ConfigLoader.load(config_path)

        guard = ReproGuard(loaded_torchrl)
        if TorchRLHoodieLearner.is_available():
            guard.validate()
            return

        with self.assertRaisesRegex(ReproGuardError, "TorchRL learner requested but torch and/or torchrl are unavailable"):
            guard.validate()

    def test_checkpoint_manifest_schema_is_deterministic_and_versioned(self) -> None:
        from src.evaluation.validation_artifacts import ValidationArtifacts
        from src.evaluation.validation_runner import ValidationPolicyResult, ValidationRunResult
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

        artifacts = ValidationArtifacts(
            validation=ValidationRunResult(
                config_snapshot=loaded.snapshot,
                config_hash=loaded.config_hash,
                baseline_policy_name="FLC",
                policy_order=("FLC", "HOODIE"),
                policy_results=[
                    ValidationPolicyResult(policy_name="FLC", trace_results={"aggregate": {"throughput": 1}}),
                    ValidationPolicyResult(policy_name="HOODIE", trace_results={"aggregate": {"throughput": 2}}),
                ],
            ),
            comparison={"winner": "HOODIE"},
        )
        packager = OutputPackager(output_dir=Path(tmpdir), deterministic=True)
        hoodie_state = {"schema_version": 1, "model": {"learned_action_preferences": {"local": 1.0}}}
        manifest = packager._checkpoint_manifest(
            config=loaded,
            hoodie_state=hoodie_state,
            hoodie_validation_mode="trained",
            training_summaries=[{"episode": 1}],
        )

        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["config_snapshot"], loaded.snapshot)
        self.assertEqual(manifest["config_hash"], loaded.config_hash)
        self.assertEqual(manifest["validation_mode"], "trained")
        self.assertEqual(manifest["hoodie_state_schema_version"], 1)
        self.assertEqual(manifest["checkpoint_state_path"], "hoodie_state.json")
        self.assertEqual(manifest["hoodie_state_path"], "hoodie_state.json")
        self.assertEqual(manifest["training_summaries"], [{"episode": 1}])
        self.assertEqual(artifacts.to_dict()["evaluation_config_snapshot"], loaded.snapshot)

    def test_checkpoint_manifest_records_learner_state_presence_and_version(self) -> None:
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

        hoodie_state = HoodieAgent().export_state()
        learner = TorchRLHoodieLearner()
        learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"local": 1.0}})
        hoodie_state["learner_state"] = learner.state_dict()
        hoodie_state["learner_enabled"] = True

        manifest = OutputPackager(output_dir=Path(tmpdir), deterministic=True)._checkpoint_manifest(
            config=loaded,
            hoodie_state=hoodie_state,
            hoodie_validation_mode="trained",
            training_summaries=None,
        )

        self.assertTrue(manifest["learner_state_present"])
        self.assertEqual(manifest["learner_state_schema_version"], 1)

    def test_checkpoint_manifest_round_trip_and_schema_versioning_for_learner_state(self) -> None:
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)
            hoodie_state = HoodieAgent().export_state()
            learner = TorchRLHoodieLearner()
            learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"local": 1.0}})
            hoodie_state["learner_state"] = learner.state_dict()
            hoodie_state["learner_enabled"] = True

            manifest = OutputPackager(output_dir=Path(tmpdir), deterministic=True)._checkpoint_manifest(
                config=loaded,
                hoodie_state=hoodie_state,
                hoodie_validation_mode="trained",
                training_summaries=[{"episode": 1}],
            )

            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["config_hash"], loaded.config_hash)
            self.assertEqual(manifest["validation_mode"], "trained")
            self.assertEqual(manifest["hoodie_state_schema_version"], 1)
            self.assertEqual(manifest["hoodie_state_path"], "hoodie_state.json")
            self.assertEqual(manifest["checkpoint_state_path"], "hoodie_state.json")
            self.assertTrue(manifest["learner_state_present"])
            self.assertEqual(manifest["learner_state_schema_version"], 1)
            self.assertEqual(manifest["training_summaries"], [{"episode": 1}])

    def test_checkpoint_packaging_without_learner_state_still_works(self) -> None:
        from src.evaluation.validation_artifacts import ValidationArtifacts
        from src.evaluation.validation_runner import ValidationPolicyResult, ValidationRunResult
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

            artifacts = ValidationArtifacts(
                validation=ValidationRunResult(
                    config_snapshot=loaded.snapshot,
                    config_hash=loaded.config_hash,
                    baseline_policy_name="FLC",
                    policy_order=("FLC", "HOODIE"),
                    policy_results=[
                        ValidationPolicyResult(policy_name="FLC", trace_results={"aggregate": {"throughput": 1}}),
                        ValidationPolicyResult(policy_name="HOODIE", trace_results={"aggregate": {"throughput": 2}}),
                    ],
                ),
                comparison={"winner": "HOODIE"},
            )

            packager = OutputPackager(output_dir=Path(tmpdir), deterministic=True)
            result = packager.package(config=loaded, validation_artifacts=artifacts, hoodie_state=HoodieAgent().export_state())

            self.assertIn("hoodie_state_path", result)
            self.assertIn("checkpoint_manifest_path", result)
            hoodie_state_payload = json.loads(Path(result["hoodie_state_path"]).read_text(encoding="utf-8"))
            manifest_payload = json.loads(Path(result["checkpoint_manifest_path"]).read_text(encoding="utf-8"))
            self.assertNotIn("learner_state", hoodie_state_payload)
            self.assertFalse(manifest_payload["learner_state_present"])

    def test_checkpoint_packaging_with_learner_state_is_deterministic_and_preserves_presence_version(self) -> None:
        from src.evaluation.validation_artifacts import ValidationArtifacts
        from src.evaluation.validation_runner import ValidationPolicyResult, ValidationRunResult
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)
            artifacts = ValidationArtifacts(
                validation=ValidationRunResult(
                    config_snapshot=loaded.snapshot,
                    config_hash=loaded.config_hash,
                    baseline_policy_name="FLC",
                    policy_order=("FLC", "HOODIE"),
                    policy_results=[
                        ValidationPolicyResult(policy_name="FLC", trace_results={"aggregate": {"throughput": 1}}),
                        ValidationPolicyResult(policy_name="HOODIE", trace_results={"aggregate": {"throughput": 2}}),
                    ],
                ),
                comparison={"winner": "HOODIE"},
            )
            learner = TorchRLHoodieLearner()
            learner.load_state_dict({"schema_version": 1, "learned_action_preferences": {"local": 1.0}})
            hoodie_state = HoodieAgent().export_state()
            hoodie_state["learner_state"] = learner.state_dict()
            hoodie_state["learner_enabled"] = True

            packager = OutputPackager(output_dir=Path(tmpdir), deterministic=True)
            first = packager.package(config=loaded, validation_artifacts=artifacts, hoodie_state=hoodie_state)
            second = packager.package(config=loaded, validation_artifacts=artifacts, hoodie_state=hoodie_state)

            self.assertEqual(Path(first["hoodie_state_path"]).read_bytes(), Path(second["hoodie_state_path"]).read_bytes())
            self.assertEqual(Path(first["checkpoint_manifest_path"]).read_bytes(), Path(second["checkpoint_manifest_path"]).read_bytes())
            manifest = json.loads(Path(first["checkpoint_manifest_path"]).read_text(encoding="utf-8"))
            self.assertTrue(manifest["learner_state_present"])
            self.assertEqual(manifest["learner_state_schema_version"], 1)

    def test_checkpoint_packaging_is_byte_identical_for_repeated_deterministic_runs(self) -> None:
        from src.evaluation.validation_artifacts import ValidationArtifacts
        from src.evaluation.validation_runner import ValidationPolicyResult, ValidationRunResult
        from src.repro.output_packager import OutputPackager

        config = self._base_config_payload()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)

            artifacts = ValidationArtifacts(
                validation=ValidationRunResult(
                    config_snapshot=loaded.snapshot,
                    config_hash=loaded.config_hash,
                    baseline_policy_name="FLC",
                    policy_order=("FLC", "HOODIE"),
                    policy_results=[
                        ValidationPolicyResult(policy_name="FLC", trace_results={"aggregate": {"throughput": 1}}),
                        ValidationPolicyResult(policy_name="HOODIE", trace_results={"aggregate": {"throughput": 2}}),
                    ],
                ),
                comparison={"winner": "HOODIE"},
            )

            hoodie_state = HoodieAgent().export_state()
            hoodie_state["learner_state"] = TorchRLHoodieLearner().state_dict()
            hoodie_state["learner_enabled"] = False
            packager = OutputPackager(output_dir=Path(tmpdir), deterministic=True)
            first = packager.package(config=loaded, validation_artifacts=artifacts, hoodie_state=hoodie_state)
            second = packager.package(config=loaded, validation_artifacts=artifacts, hoodie_state=hoodie_state)

            self.assertEqual(
                Path(first["hoodie_state_path"]).read_bytes(),
                Path(second["hoodie_state_path"]).read_bytes(),
            )
            self.assertEqual(
                Path(first["checkpoint_manifest_path"]).read_bytes(),
                Path(second["checkpoint_manifest_path"]).read_bytes(),
            )

    def test_hoodie_model_scores_legal_actions_with_deterministic_hints(self) -> None:
        model = HoodieModel()
        scored = model.forward(
            HistoryWindow(
                observations=(
                    {
                        "topology": ("2", "cloud"),
                        "fallback_hints": {"local": 1, "horizontal": 2, "vertical": 3},
                    },
                ),
                trace_history=("trace",),
            ),
            ("local", "horizontal", "vertical"),
        )

        self.assertEqual(scored["vertical"], scored["horizontal"] + 1.0)
        self.assertEqual(scored["horizontal"], scored["local"] + 1.0)

    def test_history_builder_persists_through_agent_path(self) -> None:
        agent = HoodieAgent()
        agent.model = _StubModel()

        context = PolicyContext(
            observation={"slot": 1},
            legal_action_mask={"local": True, "cloud": True},
            trace_history=("trace-1",),
        )

        first_action = agent.choose_action(context)
        second_action = agent.choose_action(
            PolicyContext(
                observation={"slot": 2},
                legal_action_mask={"local": True, "cloud": True},
                trace_history=("trace-1", "trace-2"),
            )
        )

        self.assertEqual(first_action, "cloud")
        self.assertEqual(second_action, "cloud")
        self.assertEqual(agent.history_builder.observation_history, [{"slot": 1}, {"slot": 2}])
        self.assertEqual(agent.history_builder.legal_action_history, [{"local": True, "cloud": True}, {"local": True, "cloud": True}])
        self.assertEqual(agent.model.seen_history_lengths, [1, 2])

    def test_double_dqn_selector_uses_legal_actions_only(self) -> None:
        selector = DoubleDQNSelector()

        chosen = selector.select_action({"local": 1.0, "cloud": 5.0, "public": 4.0}, ("local", "public"))

        self.assertEqual(chosen, "public")
        self.assertEqual(selector.target_value({"local": 1.0, "cloud": 5.0, "public": 4.0}, {"local": 10.0, "public": 7.5}, ("local", "public")), 7.5)

    def test_hoodie_agent_can_choose_non_local_actions_when_scores_favor_them(self) -> None:
        agent = HoodieAgent()
        agent.model.action_biases = {"local": 0.0, "horizontal": 5.0}

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2}},
            legal_action_mask={"local": True, "horizontal": True},
            trace_history=("trace-1",),
        )

        self.assertEqual(agent.choose_action(context), "horizontal")

    def test_hoodie_agent_never_selects_illegal_actions(self) -> None:
        agent = HoodieAgent()
        agent.model.action_biases = {"local": 0.0, "horizontal": 100.0, "vertical": 100.0}

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2, "vertical": 3}},
            legal_action_mask={"local": True, "horizontal": False, "vertical": False},
            trace_history=("trace-1",),
        )

        self.assertEqual(agent.choose_action(context), "local")

    def test_hoodie_agent_is_deterministic_for_fixed_model_state(self) -> None:
        agent = HoodieAgent()
        agent.model.action_biases = {"local": 0.0, "horizontal": 2.0, "vertical": 4.0}

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2, "vertical": 3}},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("trace-1",),
        )

        actions = [agent.choose_action(context) for _ in range(3)]
        self.assertEqual(actions, ["vertical", "vertical", "vertical"])

    def test_learning_updates_change_action_preferences_and_target_sync(self) -> None:
        agent = HoodieAgent()
        agent.model.action_biases = {"local": 0.0, "horizontal": 0.0}

        agent.record_transition(
            state={"slot": 0},
            action="local",
            reward=2.0,
            next_state={"slot": 1},
            done=True,
        )
        learned = agent.learn_from_replay(batch_size=1, learning_rate=0.25)
        before_sync = dict(agent.target_network.parameters)
        agent.sync_target_network()

        self.assertEqual(learned, 1)
        self.assertGreater(agent.model.learned_action_preferences["local"], 0.0)
        self.assertEqual(before_sync, {})
        self.assertEqual(agent.target_network.parameters["learned:local"], agent.model.learned_action_preferences["local"])

    def test_drop_penalty_decreases_action_preference(self) -> None:
        agent = HoodieAgent()
        agent.model.action_biases = {"local": 0.0}

        agent.record_transition(
            state={"slot": 0},
            action="local",
            reward=-40.0,
            next_state={"slot": 1},
            done=True,
        )
        agent.learn_from_replay(batch_size=1, learning_rate=0.25)

        self.assertLess(agent.model.learned_action_preferences["local"], 0.0)

    def test_export_and_import_roundtrip_preserves_scores(self) -> None:
        trained_agent = HoodieAgent()
        trained_agent.model.learned_action_preferences = {"horizontal": 1.5, "local": -0.5}
        trained_agent.model.action_biases = {"horizontal": 0.25}
        trained_agent.model.dueling_dqn.value_weight = 2.0
        trained_agent.sync_target_network()

        state = trained_agent.export_state()
        restored_agent = HoodieAgent.from_state(state)

        context = PolicyContext(
            observation={"slot": 1, "topology": ("2", "cloud"), "fallback_hints": {"local": 1, "horizontal": 2}},
            legal_action_mask={"local": True, "horizontal": True},
            trace_history=("trace-1",),
        )

        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(restored_agent.export_state(), state)
        self.assertEqual(trained_agent.choose_action(context), restored_agent.choose_action(context))
        self.assertEqual(trained_agent.model.forward(trained_agent.history_builder.build(context), ("local", "horizontal")), restored_agent.model.forward(restored_agent.history_builder.build(context), ("local", "horizontal")))
        self.assertEqual(restored_agent.target_network.parameters, trained_agent.target_network.parameters)

    def test_target_network_copy_and_soft_update(self) -> None:
        target = TargetNetwork()

        target.copy_from({"value_weight": 2.0, "bias": 1.0})
        self.assertEqual(target.parameters, {"value_weight": 2.0, "bias": 1.0})

        target.soft_update({"value_weight": 6.0, "bias": 3.0}, tau=0.5)
        self.assertEqual(target.parameters, {"value_weight": 4.0, "bias": 2.0})

    def test_replay_buffer_capacity_and_sample_behavior(self) -> None:
        buffer = ReplayBuffer(capacity=2, seed=7)
        buffer.add(Transition(state={"id": 1}, action="a", reward=1.0, next_state={"id": 2}, done=False))
        buffer.add(Transition(state={"id": 2}, action="b", reward=2.0, next_state={"id": 3}, done=False))
        buffer.add(Transition(state={"id": 3}, action="c", reward=3.0, next_state={"id": 4}, done=True))

        self.assertEqual(len(buffer), 2)
        self.assertEqual([transition.action for transition in buffer.sample(10)], ["b", "c"])

        buffer.reseed(7)
        sampled = [transition.action for transition in buffer.sample(1)]
        self.assertEqual(len(sampled), 1)
        self.assertIn(sampled[0], {"b", "c"})

    def test_replay_buffer_sampling_is_seeded_uniform_random(self) -> None:
        seed = 11
        transitions = (
            Transition(state={"id": 1}, action="a", reward=1.0, next_state={"id": 2}, done=False),
            Transition(state={"id": 2}, action="b", reward=2.0, next_state={"id": 3}, done=False),
            Transition(state={"id": 3}, action="c", reward=3.0, next_state={"id": 4}, done=False),
            Transition(state={"id": 4}, action="d", reward=4.0, next_state={"id": 5}, done=True),
        )
        buffer = ReplayBuffer(capacity=8, seed=seed)
        buffer.extend(transitions)

        sampled_actions = [transition.action for transition in buffer.sample(2)]
        expected_indices = sorted(random.Random(seed).sample(range(len(transitions)), 2))
        expected_actions = [transitions[index].action for index in expected_indices]

        self.assertEqual(sampled_actions, expected_actions)
        self.assertEqual(len(set(sampled_actions)), 2)


if __name__ == "__main__":
    unittest.main()
