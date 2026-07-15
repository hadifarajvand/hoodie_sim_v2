from __future__ import annotations

from pathlib import Path

from src.hoodie.experiments.panel_registry import PANEL_REGISTRY
from src.hoodie.experiments.provenance import build_provenance_manifest, provenance_hash
from src.hoodie.experiments.runner import CampaignRunner
from src.hoodie.experiments.specification import ExperimentSpec
from src.hoodie.experiments.trace_registry import TraceRecord, TraceRegistry
from src.reference_model.models import TaskIdentity, TaskWorkload


def _spec(variant: str = "hoodie_lstm") -> ExperimentSpec:
    return ExperimentSpec(campaign_id="campaign-1", experiment_id="experiment-1", policy="HOODIE", variant=variant, seed=7, horizon=10, warmup=2, workload={"task_count": 3})


def _trace() -> TraceRegistry:
    record = TraceRecord(TaskIdentity("task-1", "ea-1", "ea-2"), TaskWorkload(10, 5, 1), 7)
    return TraceRegistry.from_records("trace-a", [record], source_hash="src-hash")


def test_panel_registry_has_required_panels() -> None:
    assert set(PANEL_REGISTRY) == {"figure_8a", "figure_8b", "figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e", "figure_10a", "figure_10b", "figure_10c", "figure_10d", "figure_10e", "figure_10f", "figure_11"}


def test_figure_11_has_both_variants() -> None:
    assert PANEL_REGISTRY["figure_11"].spec.variants == ("hoodie_lstm", "hoodie_no_lstm")


def test_campaign_runner_writes_job(tmp_path: Path) -> None:
    runner = CampaignRunner(campaign_id="campaign-1", output_dir=tmp_path)
    job_dir = runner.run_panel("figure_8a", _spec(), _trace(), source_commit="abc")
    assert (job_dir / "specification.json").exists()
    assert (job_dir / "completion.marker").exists()


def test_provenance_hash_is_stable() -> None:
    manifest = build_provenance_manifest(config_hash="cfg", source_hash="src", trace_hash="trace", checkpoint_hash="chk")
    assert provenance_hash(manifest) == provenance_hash(manifest)
