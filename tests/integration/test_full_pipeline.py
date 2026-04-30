from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path
from src.cli import main as cli_main
from src.config.config_freeze import FrozenConfig, FrozenConfigError
from src.config.config_loader import ConfigLoader, ConfigLoaderError
from src.run_pipeline import run_pipeline, run_validation_only
from src.policies.policy_interface import PolicyContext


class FullPipelineTests(unittest.TestCase):
    def _config_payload(self) -> dict[str, object]:
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
                "trace_id": "pipeline",
                "trace_mode": "deterministic_seed",
                "device": "cpu",
            },
            "evaluation": {
                "policy_name": "HOODIE",
                "seed": 31,
                "trace_id": "pipeline",
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
            "validation": {
                "policies": ["FLC", "HOODIE"],
            },
        }

    def _ro_actions(
        self,
        *,
        evaluation_seed: int,
        validation_policy_seed: int | None,
        trace_id: str,
        episode_length: int,
    ) -> list[str]:
        config = self._config_payload()
        config["evaluation"]["seed"] = evaluation_seed
        config["evaluation"]["trace_id"] = trace_id
        config["evaluation"]["episode_length"] = episode_length
        config["training"]["seed_management"]["evaluation_seed"] = evaluation_seed
        config["training"]["trace_id"] = trace_id
        config["training"]["episode_length"] = episode_length
        validation_section = {"policies": ["FLC", "RO"]}
        if validation_policy_seed is not None:
            validation_section["policy_seed"] = validation_policy_seed
        config["validation"] = validation_section

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded = ConfigLoader.load(config_path)
            from src.run_pipeline import _build_validation_policies

            ro_policy = _build_validation_policies(loaded, object())["RO"]
            context = PolicyContext(
                observation={"slot": 1},
                legal_action_mask={"local": True, "cloud": True},
                trace_history=("trace",),
            )
            return [ro_policy.choose_action(context) for _ in range(5)]

    def _write_config(self, directory: Path) -> Path:
        config_path = directory / "pipeline_config.json"
        config_path.write_text(json.dumps(self._config_payload(), sort_keys=True), encoding="utf-8")
        return config_path

    def _read_run_bytes(self, run_dir: Path) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in sorted(run_dir.iterdir()) if path.is_file()}

    def test_end_to_end_reproducibility(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir_a, tempfile.TemporaryDirectory() as tmpdir_b:
            config_a = self._write_config(Path(tmpdir_a))
            config_b = self._write_config(Path(tmpdir_b))

            result_a = run_pipeline(config_a, Path(tmpdir_a), deterministic=True)
            result_b = run_pipeline(config_b, Path(tmpdir_b), deterministic=True)

            run_dir_a = Path(result_a.package["run_dir"])
            run_dir_b = Path(result_b.package["run_dir"])

            self.assertEqual(self._read_run_bytes(run_dir_a), self._read_run_bytes(run_dir_b))
            self.assertEqual(result_a.package["run_id"], result_b.package["run_id"])

    def test_deterministic_mode_produces_identical_exported_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self._write_config(Path(tmpdir))
            first = run_pipeline(config_path, Path(tmpdir), deterministic=True)
            second = run_pipeline(config_path, Path(tmpdir), deterministic=True)

            first_bytes = self._read_run_bytes(Path(first.package["run_dir"]))
            second_bytes = self._read_run_bytes(Path(second.package["run_dir"]))
            self.assertEqual(first_bytes, second_bytes)

    def test_config_integrity_after_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigLoader.load(self._write_config(Path(tmpdir)))
            frozen = FrozenConfig(config)
            config.training.batch_size = 8
            with self.assertRaises(FrozenConfigError):
                frozen.ensure_unchanged()

    def test_no_hidden_state_across_repeated_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir_a, tempfile.TemporaryDirectory() as tmpdir_b:
            config_path_a = self._write_config(Path(tmpdir_a))
            config_path_b = self._write_config(Path(tmpdir_b))

            first = run_pipeline(config_path_a, Path(tmpdir_a), deterministic=True)
            second = run_pipeline(config_path_b, Path(tmpdir_b), deterministic=True)

            self.assertEqual(self._read_run_bytes(Path(first.package["run_dir"])), self._read_run_bytes(Path(second.package["run_dir"])))

    def test_cli_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = self._write_config(root)
            validation_exit = cli_main(["validation", "--config", str(config_path), "--output-dir", str(root), "--deterministic"])
            analysis_exit = cli_main(["analysis", "--config", str(config_path), "--output-dir", str(root), "--deterministic"])
            self.assertEqual(validation_exit, 0)
            self.assertEqual(analysis_exit, 0)

            run_dirs = sorted((root / "outputs").iterdir())
            self.assertTrue(run_dirs)
            packaged = run_dirs[-1]
            self.assertTrue((packaged / "metadata.json").exists())
            self.assertTrue((packaged / "validation_artifacts.json").exists())
            self.assertTrue((packaged / "report.json").exists())
            self.assertTrue((packaged / "plots.json").exists())

    def test_configured_policy_set_is_respected_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {"policies": ["HOODIE", "FLC"]}
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            result = run_pipeline(config_path, root, deterministic=True)
            metadata = json.loads(Path(result.package["metadata_path"]).read_text(encoding="utf-8"))

            self.assertEqual(result.validation.validation.policy_order, ("HOODIE", "FLC"))
            self.assertEqual(result.validation.validation.baseline_policy_name, "HOODIE")
            self.assertEqual(metadata["validation_policy_names"], ["HOODIE", "FLC"])
            self.assertEqual(metadata["policy_order"], ["HOODIE", "FLC"])

    def test_unsupported_policy_name_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {"policies": ["FLC", "NOT_REAL"]}
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Unsupported validation policy: NOT_REAL"):
                run_pipeline(config_path, root, deterministic=True)

    def test_duplicate_policy_names_fail_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {"policies": ["HOODIE", "HOODIE"]}
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            with self.assertRaisesRegex(ConfigLoaderError, "duplicates|must not contain duplicates"):
                run_pipeline(config_path, root, deterministic=True)

    def test_single_policy_validation_runs_without_compared_policies(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {"policies": ["HOODIE"]}
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            result = run_pipeline(config_path, root, deterministic=True)
            metadata = json.loads(Path(result.package["metadata_path"]).read_text(encoding="utf-8"))
            validation_data = json.loads(Path(result.package["validation_path"]).read_text(encoding="utf-8"))

            self.assertEqual(result.validation.validation.policy_order, ("HOODIE",))
            self.assertEqual(result.validation.validation.baseline_policy_name, "HOODIE")
            self.assertEqual(result.analysis.compared_policies, [])
            self.assertEqual(validation_data["policy_results"]["compared_policies"], [])
            self.assertEqual(metadata["validation_policy_names"], ["HOODIE"])

    def test_trained_pipeline_packages_hoodie_state_and_marks_trained_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config["training"]["learner_type"] = "learner_adapter"
            config["training"]["episode_count"] = 2
            config["training"]["episode_length"] = 2
            config["evaluation"]["episode_count"] = 2
            config["evaluation"]["episode_length"] = 2
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            result = run_pipeline(config_path, root, run_training=True, deterministic=True)
            metadata = json.loads(Path(result.package["metadata_path"]).read_text(encoding="utf-8"))
            hoodie_state_path = Path(result.package["hoodie_state_path"])
            hoodie_state = json.loads(hoodie_state_path.read_text(encoding="utf-8"))

            self.assertEqual(metadata["hoodie_validation_mode"], "trained")
            self.assertEqual(hoodie_state["schema_version"], 1)
            self.assertEqual(metadata["hoodie_state_schema_version"], 1)
            self.assertIn("learned_action_preferences", hoodie_state["model"])
            self.assertTrue(hoodie_state_path.exists())

    def test_trained_pipeline_packages_learner_state_and_checkpoint_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config["training"]["learner_type"] = "learner_adapter"
            config["training"]["episode_count"] = 2
            config["training"]["episode_length"] = 2
            config["evaluation"]["episode_count"] = 2
            config["evaluation"]["episode_length"] = 2
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            result = run_pipeline(config_path, root, run_training=True, deterministic=True)
            metadata = json.loads(Path(result.package["metadata_path"]).read_text(encoding="utf-8"))
            hoodie_state = json.loads(Path(result.package["hoodie_state_path"]).read_text(encoding="utf-8"))
            checkpoint_manifest = json.loads(Path(result.package["checkpoint_manifest_path"]).read_text(encoding="utf-8"))

            self.assertIn("schema_version", hoodie_state)
            self.assertIn("model", hoodie_state)
            self.assertIn("target_network", hoodie_state)
            self.assertIn("learner_state", hoodie_state)
            self.assertIn("learner_enabled", hoodie_state)
            self.assertTrue(checkpoint_manifest["learner_state_present"])
            self.assertEqual(checkpoint_manifest["learner_state_schema_version"], 1)
            self.assertEqual(checkpoint_manifest["hoodie_state_path"], "hoodie_state.json")
            self.assertEqual(checkpoint_manifest["checkpoint_state_path"], "hoodie_state.json")
            self.assertEqual(metadata["hoodie_state_schema_version"], hoodie_state["schema_version"])
            self.assertEqual(checkpoint_manifest["hoodie_state_schema_version"], hoodie_state["schema_version"])
            self.assertEqual(metadata["hoodie_validation_mode"], "trained")

    def test_deterministic_training_packaging_is_byte_identical_across_repeated_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir_a, tempfile.TemporaryDirectory() as tmpdir_b:
            root_a = Path(tmpdir_a)
            root_b = Path(tmpdir_b)
            config_a = self._config_payload()
            config_b = self._config_payload()
            for config in (config_a, config_b):
                config["validation"] = {
                    "policies": ["FLC", "HOODIE"],
                    "topology": {
                        "node_ids": ["1", "2", "cloud"],
                        "legal_adjacency": {
                            "1": ["2", "cloud"],
                            "2": ["1", "cloud"],
                        },
                    },
                }
                config["training"]["learner_type"] = "learner_adapter"
                config["training"]["episode_count"] = 2
                config["training"]["episode_length"] = 2
                config["evaluation"]["episode_count"] = 2
                config["evaluation"]["episode_length"] = 2

            config_path_a = root_a / "pipeline_config.json"
            config_path_b = root_b / "pipeline_config.json"
            config_path_a.write_text(json.dumps(config_a, sort_keys=True), encoding="utf-8")
            config_path_b.write_text(json.dumps(config_b, sort_keys=True), encoding="utf-8")

            result_a = run_pipeline(config_path_a, root_a, run_training=True, deterministic=True)
            result_b = run_pipeline(config_path_b, root_b, run_training=True, deterministic=True)

            self.assertEqual(self._read_run_bytes(Path(result_a.package["run_dir"])), self._read_run_bytes(Path(result_b.package["run_dir"])))
            self.assertTrue(Path(result_a.package["hoodie_state_path"]).exists())
            self.assertTrue(Path(result_b.package["hoodie_state_path"]).exists())
            self.assertTrue(Path(result_a.package["checkpoint_manifest_path"]).exists())
            self.assertTrue(Path(result_b.package["checkpoint_manifest_path"]).exists())
            manifest_a = json.loads(Path(result_a.package["checkpoint_manifest_path"]).read_text(encoding="utf-8"))
            manifest_b = json.loads(Path(result_b.package["checkpoint_manifest_path"]).read_text(encoding="utf-8"))
            self.assertTrue(manifest_a["learner_state_present"])
            self.assertTrue(manifest_b["learner_state_present"])
            self.assertEqual(manifest_a["learner_state_schema_version"], 1)
            self.assertEqual(manifest_b["learner_state_schema_version"], 1)

    def test_validation_only_uses_fresh_hoodie_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config_path = root / "pipeline_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            result = run_validation_only(config_path, root, deterministic=True)
            metadata = json.loads(Path(result["metadata_path"]).read_text(encoding="utf-8"))

            self.assertEqual(metadata["hoodie_validation_mode"], "fresh")
            self.assertNotIn("hoodie_state_path", result)
            self.assertNotIn("checkpoint_manifest_path", result)

    def test_validation_only_can_reload_exported_hoodie_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config["training"]["episode_count"] = 2
            config["training"]["episode_length"] = 2
            config["evaluation"]["episode_count"] = 2
            config["evaluation"]["episode_length"] = 2
            config["training"]["learner_type"] = "learner_adapter"
            config_path = root / "trained_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            trained = run_pipeline(config_path, root, run_training=True, deterministic=True)
            hoodie_state_path = Path(trained.package["hoodie_state_path"])
            trained_state = json.loads(hoodie_state_path.read_text(encoding="utf-8"))
            self.assertIn("learner_state", trained_state)
            self.assertIn("learner_enabled", trained_state)

            reloaded_config = dict(config)
            reloaded_config["validation"] = dict(config["validation"])
            reloaded_config["validation"]["hoodie_state_path"] = str(hoodie_state_path)
            reload_config_path = root / "reload_config.json"
            reload_config_path.write_text(json.dumps(reloaded_config, sort_keys=True), encoding="utf-8")

            result = run_validation_only(reload_config_path, root, deterministic=True)
            metadata = json.loads(Path(result["metadata_path"]).read_text(encoding="utf-8"))

            self.assertEqual(metadata["hoodie_validation_mode"], "trained")
            self.assertEqual(Path(reload_config_path).read_text(encoding="utf-8"), json.dumps(reloaded_config, sort_keys=True))

    def test_validation_only_missing_checkpoint_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "hoodie_state_path": str(root / "missing_hoodie_state.json"),
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config_path = root / "missing_checkpoint_config.json"
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            with self.assertRaisesRegex(FileNotFoundError, "HOODIE state checkpoint does not exist"):
                run_validation_only(config_path, root, deterministic=True)

            self.assertFalse((root / "outputs").exists())

    def test_validation_only_packaging_is_byte_identical_for_explicit_trained_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = self._config_payload()
            config["validation"] = {
                "policies": ["FLC", "HOODIE"],
                "topology": {
                    "node_ids": ["1", "2", "cloud"],
                    "legal_adjacency": {
                        "1": ["2", "cloud"],
                        "2": ["1", "cloud"],
                    },
                },
            }
            config["training"]["learner_type"] = "learner_adapter"
            config["training"]["episode_count"] = 2
            config["training"]["episode_length"] = 2
            config["evaluation"]["episode_count"] = 2
            config["evaluation"]["episode_length"] = 2
            trained_config_path = root / "trained_config.json"
            trained_config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")

            trained = run_pipeline(trained_config_path, root, run_training=True, deterministic=True)
            hoodie_state_path = Path(trained.package["hoodie_state_path"])

            reloaded_config = dict(config)
            reloaded_config["validation"] = dict(config["validation"])
            reloaded_config["validation"]["hoodie_state_path"] = str(hoodie_state_path)
            reload_config_path = root / "reload_config.json"
            reload_config_path.write_text(json.dumps(reloaded_config, sort_keys=True), encoding="utf-8")

            first = run_validation_only(reload_config_path, root, deterministic=True)
            second = run_validation_only(reload_config_path, root, deterministic=True)

            self.assertEqual(self._read_run_bytes(Path(first["run_dir"])), self._read_run_bytes(Path(second["run_dir"])))
            self.assertEqual(
                Path(first["validation_path"]).read_bytes(),
                Path(second["validation_path"]).read_bytes(),
            )
            self.assertEqual(
                Path(first["metadata_path"]).read_bytes(),
                Path(second["metadata_path"]).read_bytes(),
            )
            self.assertEqual(json.loads(Path(first["metadata_path"]).read_text(encoding="utf-8"))["hoodie_validation_mode"], "trained")

    def test_missing_hoodie_still_runs_and_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = None
            for seed in range(1, 300):
                config = self._config_payload()
                config["validation"] = {"policies": ["FLC", "RO"], "policy_seed": seed}
                config["evaluation"]["seed"] = seed
                config["training"]["seed_management"]["evaluation_seed"] = seed
                config_path = root / f"pipeline_{seed}.json"
                config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
                try:
                    result = run_pipeline(config_path, root, deterministic=True)
                    break
                except ValueError as exc:
                    if "Topology-backed destination required for offload actions" not in str(exc):
                        raise
            self.assertIsNotNone(result)

            self.assertEqual(result.validation.validation.policy_order, ("FLC", "RO"))
            self.assertEqual(result.validation.validation.baseline_policy_name, "FLC")
            self.assertEqual([policy.policy_name for policy in result.analysis.compared_policies], ["RO"])

    def test_policy_order_changes_baseline_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir_a, tempfile.TemporaryDirectory() as tmpdir_b:
            root_a = Path(tmpdir_a)
            root_b = Path(tmpdir_b)
            config_a = self._config_payload()
            config_b = self._config_payload()
            config_a["validation"] = {"policies": ["FLC", "HOODIE"]}
            config_b["validation"] = {"policies": ["HOODIE", "FLC"]}
            path_a = root_a / "pipeline_config.json"
            path_b = root_b / "pipeline_config.json"
            path_a.write_text(json.dumps(config_a, sort_keys=True), encoding="utf-8")
            path_b.write_text(json.dumps(config_b, sort_keys=True), encoding="utf-8")

            result_a = run_pipeline(path_a, root_a, deterministic=True)
            result_b = run_pipeline(path_b, root_b, deterministic=True)

            self.assertEqual(result_a.validation.validation.baseline_policy_name, "FLC")
            self.assertEqual(result_a.validation.validation.policy_order, ("FLC", "HOODIE"))
            self.assertEqual(result_b.validation.validation.baseline_policy_name, "HOODIE")
            self.assertEqual(result_b.validation.validation.policy_order, ("HOODIE", "FLC"))

    def test_config_hash_changes_with_policy_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_a = self._config_payload()
            config_b = self._config_payload()
            config_a["validation"] = {"policies": ["FLC", "HOODIE"]}
            config_b["validation"] = {"policies": ["HOODIE", "FLC"]}
            path_a = root / "pipeline_a.json"
            path_b = root / "pipeline_b.json"
            path_a.write_text(json.dumps(config_a, sort_keys=True), encoding="utf-8")
            path_b.write_text(json.dumps(config_b, sort_keys=True), encoding="utf-8")

            loaded_a = ConfigLoader.load(path_a)
            loaded_b = ConfigLoader.load(path_b)

            self.assertNotEqual(loaded_a.config_hash, loaded_b.config_hash)
            self.assertNotEqual(loaded_a.snapshot, loaded_b.snapshot)

    def test_deterministic_packaging_holds_for_same_config_and_policy_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir_a, tempfile.TemporaryDirectory() as tmpdir_b:
            root_a = Path(tmpdir_a)
            root_b = Path(tmpdir_b)
            config_a = self._config_payload()
            config_b = self._config_payload()
            config_a["validation"] = {"policies": ["HOODIE", "FLC"]}
            config_b["validation"] = {"policies": ["HOODIE", "FLC"]}
            config_path_a = root_a / "pipeline_config.json"
            config_path_b = root_b / "pipeline_config.json"
            config_path_a.write_text(json.dumps(config_a, sort_keys=True), encoding="utf-8")
            config_path_b.write_text(json.dumps(config_b, sort_keys=True), encoding="utf-8")

            result_a = run_pipeline(config_path_a, root_a, deterministic=True)
            result_b = run_pipeline(config_path_b, root_b, deterministic=True)

            self.assertEqual(
                self._read_run_bytes(Path(result_a.package["run_dir"])),
                self._read_run_bytes(Path(result_b.package["run_dir"])),
            )
            self.assertNotIn("hoodie_state_path", result_a.package)
            self.assertNotIn("checkpoint_manifest_path", result_a.package)

    def test_packaged_validation_artifacts_expose_full_and_evaluation_config_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = self._write_config(root)

            result = run_pipeline(config_path, root, deterministic=True)
            metadata = json.loads(Path(result.package["metadata_path"]).read_text(encoding="utf-8"))
            validation_payload = json.loads(Path(result.package["validation_path"]).read_text(encoding="utf-8"))

            self.assertIn("config_hash", metadata)
            self.assertIn("config_snapshot", metadata)
            self.assertIn("hoodie_validation_mode", metadata)
            self.assertEqual(metadata["config_snapshot"], validation_payload["full_config_snapshot"])
            self.assertEqual(metadata["config_hash"], validation_payload["full_config_hash"])
            self.assertIn("evaluation_config_snapshot", validation_payload)
            self.assertIn("evaluation_config_hash", validation_payload)
            self.assertNotEqual(validation_payload["evaluation_config_snapshot"], validation_payload["full_config_snapshot"])
            self.assertNotEqual(validation_payload["evaluation_config_hash"], validation_payload["full_config_hash"])
            self.assertEqual(validation_payload["policy_results"]["baseline"]["trace_results"]["aggregate"], result.validation.validation.policy_results[0].trace_results["aggregate"])
            self.assertEqual(validation_payload["policy_results"]["compared_policies"][0]["trace_results"]["aggregate"], result.validation.validation.policy_results[1].trace_results["aggregate"])
            self.assertEqual(metadata["validation_policy_names"], ["FLC", "HOODIE"])

    def test_validation_artifacts_keep_full_and_evaluation_provenance_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = self._write_config(root)

            result = run_pipeline(config_path, root, deterministic=True)
            validation_payload = json.loads(Path(result.package["validation_path"]).read_text(encoding="utf-8"))

            self.assertIn("full_config_snapshot", validation_payload)
            self.assertIn("full_config_hash", validation_payload)
            self.assertIn("evaluation_config_snapshot", validation_payload)
            self.assertIn("evaluation_config_hash", validation_payload)
            self.assertNotEqual(validation_payload["full_config_snapshot"], validation_payload["evaluation_config_snapshot"])
            self.assertNotEqual(validation_payload["full_config_hash"], validation_payload["evaluation_config_hash"])

    def test_ro_reproducible_choices_under_same_seed_and_global_state_independence(self) -> None:
        first_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=1234,
            trace_id="trace-a",
            episode_length=2,
        )
        second_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=1234,
            trace_id="trace-b",
            episode_length=2,
        )

        self.assertEqual(first_actions, second_actions)

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = self._config_payload()
            config["validation"] = {"policies": ["FLC", "RO"], "policy_seed": 1234}
            config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
            loaded_one = ConfigLoader.load(config_path)
            loaded_two = ConfigLoader.load(config_path)
            from src.run_pipeline import _build_validation_policies

            self.assertEqual(_build_validation_policies(loaded_one, object())["RO"].seed, _build_validation_policies(loaded_two, object())["RO"].seed)

    def test_ro_reproducible_choices_ignore_episode_length(self) -> None:
        first_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=1234,
            trace_id="trace-a",
            episode_length=2,
        )
        second_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=1234,
            trace_id="trace-a",
            episode_length=7,
        )

        self.assertEqual(first_actions, second_actions)

    def test_ro_can_differ_under_different_policy_seeds(self) -> None:
        first_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=1234,
            trace_id="trace-a",
            episode_length=2,
        )
        second_actions = self._ro_actions(
            evaluation_seed=31,
            validation_policy_seed=5678,
            trace_id="trace-a",
            episode_length=2,
        )

        self.assertNotEqual(first_actions, second_actions)


if __name__ == "__main__":
    unittest.main()
