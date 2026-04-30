from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from src.analysis.analysis_runner import AnalysisRunResult
from src.analysis.plot_builder import PlotBuilder
from src.analysis.report_builder import ReportBuilder
from src.evaluation.validation_artifacts import ValidationArtifacts

from src.config.config_loader import UnifiedConfig


@dataclass(slots=True)
class OutputPackager:
    output_dir: Path
    deterministic: bool = False
    timestamp: str | None = None

    def _resolved_timestamp(self) -> str:
        if self.timestamp is not None:
            return self.timestamp
        if self.deterministic:
            return "1970-01-01T00:00:00+00:00"
        return datetime.now(timezone.utc).isoformat()

    def _run_id(self, config: UnifiedConfig, timestamp: str) -> str:
        if self.deterministic:
            return config.config_hash[:16]
        return f"{config.config_hash[:16]}-{timestamp.replace(':', '').replace('+', '').replace('-', '')}"

    @staticmethod
    def _checkpoint_manifest(
        *,
        config: UnifiedConfig,
        hoodie_state: dict[str, Any],
        hoodie_validation_mode: str,
        training_summaries: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        learner_state = hoodie_state.get("learner_state")
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "config_snapshot": config.snapshot,
            "config_hash": config.config_hash,
            "validation_mode": hoodie_validation_mode,
            "hoodie_state_schema_version": hoodie_state.get("schema_version", 1),
            "hoodie_state_path": "hoodie_state.json",
            "checkpoint_state_path": "hoodie_state.json",
            "learner_state_present": learner_state is not None,
        }
        if learner_state is not None:
            if not isinstance(learner_state, dict):
                raise ValueError("hoodie_state learner_state must be a mapping")
            manifest["learner_state_schema_version"] = learner_state.get("schema_version", 1)
        if training_summaries is not None:
            manifest["training_summaries"] = training_summaries
        if "policy_name" in hoodie_state:
            manifest["policy_name"] = hoodie_state["policy_name"]
        return manifest

    def package(
        self,
        *,
        config: UnifiedConfig,
        validation_artifacts: ValidationArtifacts,
        analysis_result: AnalysisRunResult | None = None,
        training_summaries: list[dict[str, Any]] | None = None,
        hoodie_state: dict[str, Any] | None = None,
        hoodie_validation_mode: str = "fresh",
    ) -> dict[str, str]:
        timestamp = self._resolved_timestamp()
        run_id = self._run_id(config, timestamp)
        run_dir = self.output_dir / "outputs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        validation_payload = validation_artifacts.to_dict()
        validation_payload["full_config_snapshot"] = config.snapshot
        validation_payload["full_config_hash"] = config.config_hash
        validation_payload["evaluation_config_snapshot"] = validation_artifacts.validation.config_snapshot
        validation_payload["evaluation_config_hash"] = validation_artifacts.validation.config_hash
        metadata = {
            "run_id": run_id,
            "timestamp": timestamp,
            "deterministic": self.deterministic,
            "config_hash": config.config_hash,
            "config_snapshot": config.snapshot,
            "training_seed": config.training.seed_management.training_seed,
            "evaluation_seed": config.training.seed_management.evaluation_seed,
            "runtime_variant": config.runtime["runtime_variant"],
            "validation_policy_names": list(config.validation_policies),
            "policy_order": validation_artifacts.validation.policy_order,
        }
        if training_summaries is not None:
            metadata["training_summaries"] = training_summaries
        metadata["hoodie_validation_mode"] = hoodie_validation_mode
        if hoodie_state is not None:
            metadata["hoodie_state_schema_version"] = hoodie_state.get("schema_version", 1)

        metadata_path = run_dir / "metadata.json"
        validation_path = run_dir / "validation_artifacts.json"
        hoodie_state_path = run_dir / "hoodie_state.json"
        checkpoint_manifest_path = run_dir / "checkpoint_manifest.json"
        report_path = run_dir / "report.json"
        plots_path = run_dir / "plots.json"

        metadata_path.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
        validation_path.write_text(json.dumps(validation_payload, sort_keys=True), encoding="utf-8")
        if hoodie_state is not None:
            hoodie_state_payload = {
                key: hoodie_state[key]
                for key in sorted(hoodie_state)
                if key != "learner_state"
            }
            if "learner_state" in hoodie_state:
                learner_state = hoodie_state["learner_state"]
                if not isinstance(learner_state, dict):
                    raise ValueError("hoodie_state learner_state must be a mapping")
                hoodie_state_payload["learner_state"] = {
                    key: learner_state[key]
                    for key in sorted(learner_state)
                }
            hoodie_state_path.write_text(json.dumps(hoodie_state_payload, sort_keys=True), encoding="utf-8")
            checkpoint_manifest = self._checkpoint_manifest(
                config=config,
                hoodie_state=hoodie_state_payload,
                hoodie_validation_mode=hoodie_validation_mode,
                training_summaries=training_summaries,
            )
            checkpoint_manifest_path.write_text(json.dumps(checkpoint_manifest, sort_keys=True), encoding="utf-8")
        if analysis_result is not None:
            report_payload = ReportBuilder(analysis_result).to_dict()
            plots_payload = PlotBuilder(analysis_result).build_payload()
            report_path.write_text(
                json.dumps({"report": report_payload, "config_hash": config.config_hash}, sort_keys=True),
                encoding="utf-8",
            )
            plots_path.write_text(
                json.dumps({"plots": plots_payload, "config_hash": config.config_hash}, sort_keys=True),
                encoding="utf-8",
            )

        result = {
            "run_dir": str(run_dir),
            "metadata_path": str(metadata_path),
            "validation_path": str(validation_path),
            "timestamp": timestamp,
            "run_id": run_id,
        }
        if hoodie_state is not None:
            result["hoodie_state_path"] = str(hoodie_state_path)
            result["checkpoint_manifest_path"] = str(checkpoint_manifest_path)
        if analysis_result is not None:
            result["report_path"] = str(report_path)
            result["plots_path"] = str(plots_path)
        return result

    @staticmethod
    def load_validation_artifacts(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))
