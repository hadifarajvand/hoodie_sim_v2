from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from src.hoodie.experiments.distributed import (
    backend_provenance_audit,
    build_shard_plan,
    export_shards,
    finalize_campaign,
    import_shard_results,
    run_shard,
    write_shard_plan,
)
from src.hoodie.experiments.contract_mapping import build_training_config
from src.hoodie.experiments.job_matrix import build_production_job_matrix
from src.hoodie.experiments.panel_registry import PANEL_REGISTRY

CAMPAIGN_ID = "figures-8-11-7587c7c6382c"


class DistributedExecutionTests(unittest.TestCase):
    def test_shard_plan_covers_full_matrix_deterministically(self) -> None:
        first = build_shard_plan(CAMPAIGN_ID, training_workers=3, evaluation_workers=4)
        second = build_shard_plan(CAMPAIGN_ID, training_workers=3, evaluation_workers=4)
        self.assertEqual(first.to_dict()["matrix_hash"], second.to_dict()["matrix_hash"])
        self.assertEqual(first.to_dict()["shard_assignments"], second.to_dict()["shard_assignments"])
        rows = build_production_job_matrix(CAMPAIGN_ID)
        assigned = [job_id for shard in first.shard_assignments for job_id in shard.job_ids]
        self.assertEqual(len(assigned), len(rows))
        self.assertEqual(set(assigned), {row.job_id for row in rows})
        self.assertEqual(sum(1 for row in rows if row.job_type == "training"), 48)
        self.assertEqual(sum(1 for row in rows if row.job_type == "evaluation"), 236)
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_figure_8a_uses_source_contracted_training_episodes(self) -> None:
        row = next(row for row in build_production_job_matrix(CAMPAIGN_ID) if row.panel_id == "figure_8a")
        config = build_training_config(row, PANEL_REGISTRY[row.panel_id].source_contract, trace_hash="trace", output_dir=Path("/tmp/out"))
        self.assertEqual(config.episode_count, 5000)
        self.assertEqual(config.episode_length, 110)

    def test_export_run_import_and_conflict_rejection(self) -> None:
        plan = build_shard_plan(CAMPAIGN_ID, training_workers=2, evaluation_workers=2)
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plan_path = write_shard_plan(plan, tmp_path / "plan.json")
            bundles = export_shards(CAMPAIGN_ID, plan_path, tmp_path / "bundles")
            bundle = bundles[0]
            result = run_shard(bundle, tmp_path / "work")
            result_bundle = tmp_path / "work" / "results" / "result_bundle.json"
            with patch("src.hoodie.experiments.distributed.CAMPAIGN_ROOT", tmp_path / "campaigns"):
                imported = import_shard_results(CAMPAIGN_ID, result_bundle)
                self.assertTrue(imported["imported"])
                repeat = import_shard_results(CAMPAIGN_ID, result_bundle)
                self.assertEqual(repeat["shard_id"], result["shard_id"])
                conflict = json.loads(result_bundle.read_text(encoding="utf-8"))
                conflict["result_hash"] = "deadbeef"
                conflict_path = tmp_path / "conflict.json"
                conflict_path.write_text(json.dumps(conflict, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    import_shard_results(CAMPAIGN_ID, conflict_path)

    def test_backend_provenance_audit_writes_report(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            campaign_dir = tmp_path / "campaigns" / CAMPAIGN_ID / "jobs" / "job-a" / "internal_checkpoints"
            campaign_dir.mkdir(parents=True, exist_ok=True)
            (campaign_dir / "latest.json").write_text(json.dumps({"checkpoint_id": "abc123", "checkpoint_path": "x/checkpoint.pt", "updated_at": 1.0}) + "\n", encoding="utf-8")
            with patch("src.hoodie.experiments.distributed.CAMPAIGN_ROOT", tmp_path / "campaigns"):
                report = backend_provenance_audit(CAMPAIGN_ID)
                self.assertTrue(report["current_host_can_reload_checkpoint"])
                self.assertIn("environment", report)
                audit_path = Path("artifacts/hoodie/implementation_run/campaign/backend_provenance_audit.json")
                self.assertTrue(audit_path.exists())

    def test_legacy_checkpoint_backend_is_treated_as_unknown(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            checkpoint_root = tmp_path / "campaigns" / CAMPAIGN_ID / "jobs" / "job-a" / "internal_checkpoints"
            checkpoint_root.mkdir(parents=True, exist_ok=True)
            legacy_path = checkpoint_root / "latest.json"
            legacy_path.write_text(json.dumps({"checkpoint_id": "abc123", "checkpoint_path": str(checkpoint_root / "abc123" / "checkpoint.pt")}) + "\n", encoding="utf-8")
            with patch("src.hoodie.experiments.distributed.CAMPAIGN_ROOT", tmp_path / "campaigns"):
                report = backend_provenance_audit(CAMPAIGN_ID)
                self.assertEqual(report["checkpoint_backend"], None)
                self.assertTrue(report["checkpoint_loadable"])

    def test_finalize_campaign_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            campaign_dir = tmp_path / "campaigns" / CAMPAIGN_ID
            campaign_dir.mkdir(parents=True, exist_ok=True)
            with patch("src.hoodie.experiments.distributed.CAMPAIGN_ROOT", tmp_path / "campaigns"):
                with patch("src.hoodie.experiments.distributed.campaign_status", return_value={"campaign_id": CAMPAIGN_ID, "total": 284, "pending_jobs": 0, "running_jobs": 0, "blocked_dependency_jobs": 0, "interrupted_resumable_jobs": 0, "current_scientifically_incomplete_jobs": 0, "completed_jobs": 284, "failed_jobs": 0, "stale_jobs": 0, "corrupt_jobs": 0}):
                    with patch("src.hoodie.experiments.distributed.aggregate_campaign", return_value={"status": "ok"}):
                        with patch("src.hoodie.experiments.distributed.verify_campaign", return_value={"status": "ok"}):
                            with patch("src.hoodie.experiments.distributed.render_campaign", return_value={"status": "ok"}):
                                with patch("src.hoodie.experiments.distributed.export_bundle", return_value={"status": "ok"}):
                                    with patch("src.hoodie.experiments.distributed.verify_bundle", return_value={"status": "ok"}):
                                        (campaign_dir / "job_plan.json").write_text("[]\n", encoding="utf-8")
                                        first = finalize_campaign(CAMPAIGN_ID)
                                        second = finalize_campaign(CAMPAIGN_ID)
                                        self.assertEqual(first["status"], "completed")
                                        self.assertEqual(second["status"], "completed")
                                        self.assertTrue((campaign_dir / "finalization" / "status.json").exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
