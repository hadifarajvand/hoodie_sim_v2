from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import re
from typing import Any

GENERATED_FIGURE_OUTPUT_DIR = Path("artifacts/analysis/generated-paper-figures")
GENERATED_FIGURE_FILES = {
    "Figure 8": GENERATED_FIGURE_OUTPUT_DIR / "figure_8_reward_timecourse.png",
    "Figure 9": GENERATED_FIGURE_OUTPUT_DIR / "figure_9_parameter_sweep.png",
    "Figure 10": GENERATED_FIGURE_OUTPUT_DIR / "figure_10_offloading_schemes.png",
    "Figure 11": GENERATED_FIGURE_OUTPUT_DIR / "figure_11_lstm_comparison.png",
}


FIGURE_IDS = ("Figure 7", "Figure 8", "Figure 9", "Figure 10", "Figure 11")


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(base: Path, path: Path) -> str:
    return path.relative_to(base).as_posix()


def _normalize_snippet(text: str, limit: int = 700) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized[:limit]


@dataclass(slots=True)
class PaperEvidenceSnippet:
    source_path: str
    figure_id: str
    snippet_index: int
    char_offset: int
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "figure_id": self.figure_id,
            "snippet_index": self.snippet_index,
            "char_offset": self.char_offset,
            "text": self.text,
        }


@dataclass(slots=True)
class FigureEntry:
    figure_id: str
    title: str
    paper_claim_type: str
    paper_ocr_evidence: list[dict[str, object]]
    support_status: str
    comparison_ready: bool
    paper_caption_supported_metadata: dict[str, object]
    paper_numeric_target_data: dict[str, object]
    artifact_backed_reproduction_data: dict[str, object]
    extracted_artifact_metrics: dict[str, object]
    missing_artifacts: list[str]
    caveats: list[str]
    source_artifacts: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "figure_id": self.figure_id,
            "title": self.title,
            "paper_claim_type": self.paper_claim_type,
            "paper_ocr_evidence": list(self.paper_ocr_evidence),
            "support_status": self.support_status,
            "comparison_ready": self.comparison_ready,
            "paper_caption_supported_metadata": dict(self.paper_caption_supported_metadata),
            "paper_numeric_target_data": dict(self.paper_numeric_target_data),
            "artifact_backed_reproduction_data": dict(self.artifact_backed_reproduction_data),
            "extracted_artifact_metrics": dict(self.extracted_artifact_metrics),
            "missing_artifacts": list(self.missing_artifacts),
            "caveats": list(self.caveats),
            "source_artifacts": list(self.source_artifacts),
        }


@dataclass(slots=True)
class PaperFigureExtractionReport:
    input_paper_path: str
    input_artifact_root: str
    output_dir: str
    paper_source_inventory: dict[str, object]
    artifact_inventory: dict[str, object]
    paper_evidence_inventory: list[dict[str, object]]
    figure_entries: list[dict[str, object]]
    global_warnings: list[str]
    unsupported_requirements: list[str]
    comparison_readiness: dict[str, object]
    reproducibility_notes: list[str]
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "input_paper_path": self.input_paper_path,
            "input_artifact_root": self.input_artifact_root,
            "output_dir": self.output_dir,
            "paper_source_inventory": dict(self.paper_source_inventory),
            "artifact_inventory": dict(self.artifact_inventory),
            "paper_evidence_inventory": list(self.paper_evidence_inventory),
            "figure_entries": list(self.figure_entries),
            "global_warnings": list(self.global_warnings),
            "unsupported_requirements": list(self.unsupported_requirements),
            "comparison_readiness": dict(self.comparison_readiness),
            "reproducibility_notes": list(self.reproducibility_notes),
            "passed": self.passed,
        }


class PaperFigureExtractor:
    def __init__(self, paper_path: Path, artifact_root: Path, output_dir: Path):
        self.paper_path = Path(paper_path)
        self.artifact_root = Path(artifact_root)
        self.output_dir = Path(output_dir)
        self.campaign_dir = self.artifact_root / "campaign"
        self.matrix_dir = self.artifact_root / "matrix"
        self.trace_dir = self.matrix_dir / "traces"
        self.audit_report_path = self.artifact_root / "audit" / "audit-report.json"
        self.sensitivity_report_path = self.artifact_root / "sensitivity" / "sensitivity-report.json"

    def _paper_text(self) -> str:
        return self.paper_path.read_text(encoding="utf-8") if self.paper_path.exists() else ""

    def _paper_source_inventory(self, evidence: list[PaperEvidenceSnippet]) -> dict[str, object]:
        return {
            "input_paper_path": self.paper_path.as_posix(),
            "exists": self.paper_path.exists(),
            "figure_ids_requested": list(FIGURE_IDS),
            "evidence_snippet_count": len(evidence),
        }

    def _evidence_for_figure(self, figure_id: str, text: str) -> list[PaperEvidenceSnippet]:
        number = figure_id.split()[-1]
        patterns = [
            rf"FIGURE\s+{number}\.\s*.*",
            rf"Fig\.\s*{number}[a-z]?\s+[^.\n]*(?:\.[^\n]*)?",
            rf"Fig\.\s*{number}[a-z]?",
        ]
        snippets: list[PaperEvidenceSnippet] = []
        seen_offsets: set[int] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(match.start() - 220, 0)
                end = min(match.end() + 420, len(text))
                if start in seen_offsets:
                    continue
                seen_offsets.add(start)
                snippets.append(
                    PaperEvidenceSnippet(
                        source_path=self.paper_path.as_posix(),
                        figure_id=figure_id,
                        snippet_index=len(snippets),
                        char_offset=start,
                        text=_normalize_snippet(text[start:end]),
                    )
                )
                if len(snippets) >= 4:
                    break
            if snippets:
                break
        if not snippets and text:
            keyword = {
                "Figure 7": "Edge layer topology",
                "Figure 8": "Learning rate",
                "Figure 9": "task arrival probability",
                "Figure 10": "average delay",
                "Figure 11": "LSTM",
            }[figure_id]
            offset = text.lower().find(keyword.lower())
            if offset >= 0:
                snippets.append(
                    PaperEvidenceSnippet(
                        source_path=self.paper_path.as_posix(),
                        figure_id=figure_id,
                        snippet_index=0,
                        char_offset=max(offset - 220, 0),
                        text=_normalize_snippet(text[max(offset - 220, 0): min(offset + 520, len(text))]),
                    )
                )
        return snippets

    def _all_evidence(self, text: str) -> dict[str, list[PaperEvidenceSnippet]]:
        return {figure_id: self._evidence_for_figure(figure_id, text) for figure_id in FIGURE_IDS}

    def _artifact_inventory(self) -> dict[str, object]:
        required = [
            "campaign/campaign-summary.json",
            "campaign/policy-summary.json",
            "campaign/scenario-summary.json",
            "campaign/determinism-check.json",
            "matrix/matrix-summary.csv",
        ]
        missing = [path for path in required if not (self.artifact_root / path).exists()]
        campaign_files = sorted(_rel(self.artifact_root, path) for path in self.campaign_dir.glob("*.json")) if self.campaign_dir.exists() else []
        matrix_files = sorted(_rel(self.artifact_root, path) for path in self.matrix_dir.glob("*.json")) if self.matrix_dir.exists() else []
        trace_files = sorted(_rel(self.artifact_root, path) for path in self.trace_dir.glob("*.json")) if self.trace_dir.exists() else []
        return {
            "input_artifact_root": self.artifact_root.as_posix(),
            "exists": self.artifact_root.exists(),
            "campaign_files": campaign_files,
            "matrix_summary_path": "matrix/matrix-summary.csv" if (self.matrix_dir / "matrix-summary.csv").exists() else None,
            "matrix_result_files": matrix_files,
            "trace_files": trace_files,
            "audit_report_path": _rel(self.artifact_root, self.audit_report_path) if self.audit_report_path.exists() else None,
            "sensitivity_report_path": _rel(self.artifact_root, self.sensitivity_report_path) if self.sensitivity_report_path.exists() else None,
            "missing_required_files": missing,
        }

    def _matrix_summary_rows(self) -> list[dict[str, str]]:
        path = self.matrix_dir / "matrix-summary.csv"
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

    def _matrix_results(self) -> list[dict[str, Any]]:
        if not self.matrix_dir.exists():
            return []
        return [_read_json(path, {}) for path in sorted(self.matrix_dir.glob("*.json")) if path.is_file()]

    def _trace_metadata(self) -> list[dict[str, object]]:
        metadata: list[dict[str, object]] = []
        if not self.trace_dir.exists():
            return metadata
        for path in sorted(self.trace_dir.glob("*.json")):
            payload = _read_json(path, {})
            tasks = list(payload.get("tasks", []))
            meta = dict(payload.get("metadata", {}))
            metadata.append(
                {
                    "trace_id": str(payload.get("trace_id", path.stem)),
                    "scenario_name": str(meta.get("scenario_name", "")),
                    "seed": int(payload.get("seed", 0)),
                    "task_count": len(tasks),
                    "configured_arrival_probability": meta.get("configured_arrival_probability"),
                    "timeout_slots": meta.get("timeout_slots"),
                    "task_size_mbits_min": meta.get("task_size_mbits_min"),
                    "task_size_mbits_max": meta.get("task_size_mbits_max"),
                    "source_artifact": _rel(self.artifact_root, path),
                }
            )
        return metadata

    def _action_distribution(self) -> list[dict[str, object]]:
        counts: dict[str, dict[str, int]] = {}
        for result in self._matrix_results():
            policy = str(result.get("policy_name", "unknown"))
            counts.setdefault(policy, {})
            records = list(dict(result.get("final_metrics", {})).get("raw_records", []))
            for record in records:
                action = str(record.get("selected_action", "unknown"))
                counts[policy][action] = counts[policy].get(action, 0) + 1
        return [
            {
                "policy_name": policy,
                "action_distribution": [{"action": action, "count": counts[policy][action]} for action in sorted(counts[policy])],
            }
            for policy in sorted(counts)
        ]

    def _figure10_metrics(self) -> dict[str, object]:
        rows = self._matrix_summary_rows()
        by_policy: dict[str, dict[str, Any]] = {}
        by_scenario: dict[str, dict[str, Any]] = {}
        by_policy_scenario: dict[str, dict[str, Any]] = {}
        by_seed: dict[str, dict[str, Any]] = {}
        per_run: list[dict[str, object]] = []
        for row in rows:
            policy = str(row.get("policy_name", ""))
            scenario = str(row.get("scenario_name", ""))
            seed = str(row.get("seed", ""))
            average_delay = float(row.get("average_delay", 0.0))
            drop_ratio = float(row.get("drop_ratio", 0.0))
            completed = int(row.get("completed_tasks", 0))
            dropped = int(row.get("dropped_tasks", 0))
            total = int(row.get("total_tasks", 0))
            per_run.append(
                {
                    "policy_name": policy,
                    "scenario_name": scenario,
                    "seed": int(seed) if seed else 0,
                    "average_delay": average_delay,
                    "drop_ratio": drop_ratio,
                    "completed_tasks": completed,
                    "dropped_tasks": dropped,
                    "total_tasks": total,
                }
            )
            for key, target in (
                (policy, by_policy),
                (scenario, by_scenario),
                (f"{policy}::{scenario}", by_policy_scenario),
                (seed, by_seed),
            ):
                bucket = target.setdefault(key, {"count": 0, "average_delay_sum": 0.0, "drop_ratio_sum": 0.0, "completed_tasks": 0, "dropped_tasks": 0, "total_tasks": 0})
                bucket["count"] += 1
                bucket["average_delay_sum"] += average_delay
                bucket["drop_ratio_sum"] += drop_ratio
                bucket["completed_tasks"] += completed
                bucket["dropped_tasks"] += dropped
                bucket["total_tasks"] += total

        def finalize(mapping: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
            finalized = []
            for key in sorted(mapping):
                item = mapping[key]
                count = int(item["count"])
                finalized.append(
                    {
                        "key": key,
                        "count": count,
                        "mean_average_delay": item["average_delay_sum"] / count if count else 0.0,
                        "mean_drop_ratio": item["drop_ratio_sum"] / count if count else 0.0,
                        "completed_tasks": int(item["completed_tasks"]),
                        "dropped_tasks": int(item["dropped_tasks"]),
                        "total_tasks": int(item["total_tasks"]),
                    }
                )
            return finalized

        return {
            "by_policy": finalize(by_policy),
            "by_scenario": finalize(by_scenario),
            "by_policy_scenario": finalize(by_policy_scenario),
            "by_seed": finalize(by_seed),
            "per_run": sorted(per_run, key=lambda item: (str(item["policy_name"]), str(item["scenario_name"]), int(item["seed"]))),
        }

    def _training_artifact_summary(self) -> dict[str, object]:
        feature060_dir = Path("artifacts/analysis/full-paper-default-training-campaign-execution")
        training_metrics = _read_json(feature060_dir / "training-metrics.json", {})
        evaluation_metrics = _read_json(feature060_dir / "evaluation-metrics.json", {})
        feature060_report = _read_json(feature060_dir / "full-paper-default-training-campaign-report.json", {})
        campaign_report = _read_json(self.campaign_dir / "training-campaign-report.json", {})
        reward_summary = training_metrics.get("reward_summary", {}) if isinstance(training_metrics, dict) else {}
        figure11_meta = {
            "lstm_hidden_size": feature060_report.get("campaign_config", {}).get("lstm_hidden_size"),
            "lstm_num_layers": feature060_report.get("campaign_config", {}).get("lstm_num_layers"),
            "evaluation_reward_count": evaluation_metrics.get("reward", {}).get("reward_bearing_transition_count"),
        }
        return {
            "reward_summary": reward_summary if isinstance(reward_summary, dict) else {},
            "figure11_metadata": figure11_meta,
            "feature060_report_present": bool(feature060_report),
            "campaign_report_present": bool(campaign_report),
        }

    def _generated_figure_path(self, figure_id: str) -> Path | None:
        path = GENERATED_FIGURE_FILES.get(figure_id)
        if path is None:
            return None
        return path if path.exists() else None

    def _warning_categories(self) -> list[str]:
        warnings: set[str] = set()
        audit = _read_json(self.audit_report_path, {})
        for finding in list(audit.get("findings", [])):
            category = str(finding.get("category", ""))
            if category in {"high_drop_ratio", "weak_scenario_differentiation", "identical_policy_signature"}:
                warnings.add(category)
        sensitivity = _read_json(self.sensitivity_report_path, {})
        for finding in list(sensitivity.get("findings", [])):
            category = str(finding.get("category", ""))
            if category in {"scenario_output_collapsed", "policy_behavior_collapsed", "near_identical_outcome_behavior", "saturation_dominant"}:
                warnings.add(category)
        for classification in list(sensitivity.get("classifications", [])):
            if classification in {"scenario_output_collapsed", "policy_behavior_collapsed", "near_identical_outcome_behavior", "saturation_dominant"}:
                warnings.add(str(classification))
        trace_statuses = sorted({str(item.get("comparison", "")) for item in list(sensitivity.get("trace_comparisons", [])) if item.get("comparison")})
        if trace_statuses:
            warnings.add("trace_comparison_status:" + ",".join(trace_statuses))
        return sorted(warnings)

    def _source_artifacts(self, names: list[str]) -> list[str]:
        return sorted(name for name in names if (self.artifact_root / name).exists())

    def _figure_entry(self, figure_id: str, evidence: list[PaperEvidenceSnippet], warnings: list[str]) -> FigureEntry:
        evidence_dicts = [item.to_dict() for item in evidence]
        common_missing_numeric = ["paper_numeric_curve_values"]
        if figure_id == "Figure 7":
            trace_meta = self._trace_metadata()
            ea_counts = sorted({item.get("source_artifact") for item in trace_meta if item.get("source_artifact")})
            return FigureEntry(
                figure_id=figure_id,
                title="Edge layer topology graph of matrix G with 20 EAs",
                paper_claim_type="topology_caption",
                paper_ocr_evidence=evidence_dicts,
                support_status="partially_supported",
                comparison_ready=False,
                paper_caption_supported_metadata={"ea_count": 20, "matrix_name": "G"},
                paper_numeric_target_data={"available": False, "missing": ["topology_adjacency_edges"]},
                artifact_backed_reproduction_data={"trace_metadata_available": bool(trace_meta)},
                extracted_artifact_metrics={"observed_trace_file_count": len(trace_meta)},
                missing_artifacts=["topology_adjacency_edges"],
                caveats=[
                    "EA count is supported by OCR metadata, but no committed artifact explicitly encodes graph edges.",
                    "Trace file count does not validate EA topology size.",
                ],
                source_artifacts=ea_counts[:10],
            )
        if figure_id == "Figure 8":
            training_summary = self._training_artifact_summary()
            reward_summary = training_summary.get("reward_summary", {})
            generated_path = self._generated_figure_path(figure_id)
            has_reward_summary = isinstance(reward_summary, dict) and bool(reward_summary)
            has_generated = generated_path is not None
            missing = [] if has_generated else ["training_episode_reward_curves", "reward_by_learning_rate", "reward_by_discount_factor", "true_hoodie_drl_training_logs"]
            source_artifacts = self._source_artifacts([
                "../analysis/full-paper-default-training-campaign-execution/training-metrics.json",
            ])
            if generated_path is not None:
                source_artifacts.append(generated_path.as_posix())
            return FigureEntry(
                figure_id=figure_id,
                title="Accumulated reward time-course by learning rate and discount factor",
                paper_claim_type="training_curve_caption",
                paper_ocr_evidence=evidence_dicts,
                support_status="supported" if has_generated else ("partially_supported" if has_reward_summary else "unsupported"),
                comparison_ready=has_generated,
                paper_caption_supported_metadata={"dimensions": ["learning_rate", "discount_factor", "training_episode"]},
                paper_numeric_target_data={"available": has_generated, "missing": [] if has_generated else common_missing_numeric},
                artifact_backed_reproduction_data={"available": has_reward_summary or has_generated, "generated_png": generated_path.as_posix() if generated_path else None},
                extracted_artifact_metrics={"reward_summary": reward_summary} if has_reward_summary else {},
                missing_artifacts=missing,
                caveats=[] if has_generated else ["Current baseline campaign artifacts do not contain full HOODIE DRL training reward curves or hyperparameter sweeps."],
                source_artifacts=source_artifacts,
            )
        if figure_id == "Figure 9":
            action_distribution = self._action_distribution()
            generated_path = self._generated_figure_path(figure_id)
            has_generated = generated_path is not None
            missing = [] if has_generated else [
                "average_reward_by_task_arrival_probability",
                "reward_by_drl_agent_count",
                "reward_by_cpu_capacity",
                "reward_by_agent_count_traffic_scenario",
                "reward_by_offloading_data_rate",
                "true_hoodie_drl_validation_rewards",
            ]
            status = "supported" if has_generated else ("partially_supported" if action_distribution else "unsupported")
            source_artifacts = [_rel(self.artifact_root, path) for path in self._matrix_result_files()[:10]]
            if generated_path is not None:
                source_artifacts.append(generated_path.as_posix())
            return FigureEntry(
                figure_id=figure_id,
                title="HOODIE behavior insights under varying system parameters",
                paper_claim_type="behavior_and_scalability_context",
                paper_ocr_evidence=evidence_dicts,
                support_status=status,
                comparison_ready=has_generated,
                paper_caption_supported_metadata={"subfigures": ["9a", "9b", "9c", "9d", "9e"]},
                paper_numeric_target_data={"available": has_generated, "missing": [] if has_generated else common_missing_numeric},
                artifact_backed_reproduction_data={"action_distribution_available": bool(action_distribution), "generated_png": generated_path.as_posix() if generated_path else None},
                extracted_artifact_metrics={"action_distribution_by_policy": action_distribution},
                missing_artifacts=missing,
                caveats=[] if has_generated else ["Action distributions are artifact-backed, but reward sweeps and true HOODIE learned-agent curves are missing."],
                source_artifacts=source_artifacts,
            )
        if figure_id == "Figure 10":
            metrics = self._figure10_metrics()
            generated_path = self._generated_figure_path(figure_id)
            has_generated = generated_path is not None
            missing = [] if has_generated else ["cpu_capacity_sweep_artifacts", "timeout_sweep_artifacts", "structured_paper_numeric_curve_values"]
            if not metrics["per_run"] and not has_generated:
                missing.append("matrix_summary_metrics")
            trace_meta = self._trace_metadata()
            arrival_probabilities = sorted({str(item.get("configured_arrival_probability")) for item in trace_meta if item.get("configured_arrival_probability") is not None})
            status = "supported" if has_generated else ("partially_supported" if metrics["per_run"] else "unsupported")
            source_artifacts = ["matrix/matrix-summary.csv"]
            if generated_path is not None:
                source_artifacts.append(generated_path.as_posix())
            return FigureEntry(
                figure_id=figure_id,
                title="Performance comparison of HOODIE and six baselines",
                paper_claim_type="baseline_metric_comparison",
                paper_ocr_evidence=evidence_dicts,
                support_status=status,
                comparison_ready=has_generated,
                paper_caption_supported_metadata={"metrics": ["average_delay", "drop_ratio"], "paper_delay_convention": "negative"},
                paper_numeric_target_data={"available": has_generated, "missing": [] if has_generated else ["structured_paper_numeric_curve_values"]},
                artifact_backed_reproduction_data={"matrix_metrics_available": bool(metrics["per_run"]), "arrival_probabilities_from_traces": arrival_probabilities, "generated_png": generated_path.as_posix() if generated_path else None},
                extracted_artifact_metrics=metrics,
                missing_artifacts=missing,
                caveats=[] if has_generated else ["Repository average_delay values are preserved as stored; the paper states average delay is negative by convention."],
                source_artifacts=source_artifacts,
            )
        training_summary = self._training_artifact_summary()
        figure11_meta = training_summary.get("figure11_metadata", {})
        generated_path = self._generated_figure_path(figure_id)
        has_figure11_meta = isinstance(figure11_meta, dict) and any(value is not None for value in figure11_meta.values())
        has_generated = generated_path is not None
        missing = [] if has_generated else ["hoodie_lstm_training_delay_curve", "hoodie_without_lstm_training_delay_curve", "training_episode_delay_logs"]
        source_artifacts = self._source_artifacts([
            "../analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
        ])
        if generated_path is not None:
            source_artifacts.append(generated_path.as_posix())
        return FigureEntry(
            figure_id=figure_id,
            title="Average task delay of HOODIE with vs without LSTM",
            paper_claim_type="lstm_ablation_training_curve_caption",
            paper_ocr_evidence=evidence_dicts,
            support_status="supported" if has_generated else ("partially_supported" if has_figure11_meta else "unsupported"),
            comparison_ready=has_generated,
            paper_caption_supported_metadata={"dimensions": ["training_episode", "with_lstm", "without_lstm"]},
            paper_numeric_target_data={"available": has_generated, "missing": [] if has_generated else common_missing_numeric},
            artifact_backed_reproduction_data={"available": has_figure11_meta or has_generated, "generated_png": generated_path.as_posix() if generated_path else None},
            extracted_artifact_metrics={"lstm_metadata": figure11_meta} if has_figure11_meta else {},
            missing_artifacts=missing,
            caveats=[] if has_generated else ["Current artifacts do not include HOODIE with-LSTM and without-LSTM training delay curves."],
            source_artifacts=source_artifacts,
        )

    def _matrix_result_files(self) -> list[Path]:
        if not self.matrix_dir.exists():
            return []
        return sorted(path for path in self.matrix_dir.glob("*.json") if path.is_file())

    def extract(self) -> PaperFigureExtractionReport:
        text = self._paper_text()
        evidence_by_figure = self._all_evidence(text)
        evidence = [snippet for figure_id in FIGURE_IDS for snippet in evidence_by_figure[figure_id]]
        warnings = self._warning_categories()
        artifact_inventory = self._artifact_inventory()
        entries = [self._figure_entry(figure_id, evidence_by_figure[figure_id], warnings).to_dict() for figure_id in FIGURE_IDS]
        unsupported = sorted({item for entry in entries for item in list(entry["missing_artifacts"])})
        ready_figures = [entry["figure_id"] for entry in entries if entry["comparison_ready"]]
        blocked_figures = [entry["figure_id"] for entry in entries if not entry["comparison_ready"]]
        global_warnings = sorted(set(warnings + ["Do not claim paper reproduction validity from this scaffold."]))
        if any(
            entry["figure_id"] in {"Figure 8", "Figure 11"}
            and any(item in entry["missing_artifacts"] for item in (
                "training_episode_reward_curves",
                "reward_by_learning_rate",
                "reward_by_discount_factor",
                "hoodie_lstm_training_delay_curve",
                "hoodie_without_lstm_training_delay_curve",
                "training_episode_delay_logs",
            ))
            for entry in entries
        ):
            global_warnings.append("Current baseline artifacts do not contain true HOODIE DRL training curves.")
        passed = bool(text) and not artifact_inventory["missing_required_files"]
        return PaperFigureExtractionReport(
            input_paper_path=self.paper_path.as_posix(),
            input_artifact_root=self.artifact_root.as_posix(),
            output_dir=self.output_dir.as_posix(),
            paper_source_inventory=self._paper_source_inventory(evidence),
            artifact_inventory=artifact_inventory,
            paper_evidence_inventory=[item.to_dict() for item in evidence],
            figure_entries=entries,
            global_warnings=sorted(dict.fromkeys(global_warnings)),
            unsupported_requirements=unsupported,
            comparison_readiness={
                "full_paper_comparison_ready": False,
                "ready_figures": ready_figures,
                "blocked_figures": blocked_figures,
                "reason": "At least one required paper numeric target or committed artifact class is missing.",
            },
            reproducibility_notes=[
                "Existing paper and campaign artifacts are read-only inputs.",
                "Outputs contain no timestamps.",
                "No simulations, training, plotting, or image digitization are performed.",
            ],
            passed=passed,
        )

    def render_markdown(self, report: PaperFigureExtractionReport) -> str:
        payload = report.to_dict()
        lines = [
            "# Paper Figure Artifact Extraction",
            "",
            "## Summary",
            f"- Paper source: {payload['input_paper_path']}",
            f"- Artifact root: {payload['input_artifact_root']}",
            f"- Full paper comparison ready: {str(payload['comparison_readiness']['full_paper_comparison_ready']).lower()}",
            "",
            "## Figure Support",
        ]
        for entry in payload["figure_entries"]:
            lines.extend(
                [
                    f"- {entry['figure_id']}: {entry['support_status']} (comparison_ready={str(entry['comparison_ready']).lower()})",
                    f"  - title: {entry['title']}",
                    f"  - missing: {', '.join(entry['missing_artifacts']) if entry['missing_artifacts'] else 'none'}",
                ]
            )
        lines.extend(
            [
                "",
                "## Global Warnings",
            ]
        )
        for warning in payload["global_warnings"]:
            lines.append(f"- {warning}")
        lines.extend(
            [
                "",
                "## Unsupported Requirements",
            ]
        )
        for requirement in payload["unsupported_requirements"]:
            lines.append(f"- {requirement}")
        lines.extend(
            [
                "",
                "## Machine-Readable Figure Entries",
                "```json",
                _json_dump(payload["figure_entries"]).rstrip(),
                "```",
            ]
        )
        return "\n".join(lines) + "\n"

    def write_outputs(self) -> dict[str, Path]:
        report = self.extract()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "paper-figure-extraction.json"
        md_path = self.output_dir / "paper-figure-extraction.md"
        json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
        md_path.write_text(self.render_markdown(report), encoding="utf-8")
        return {"paper-figure-extraction.json": json_path, "paper-figure-extraction.md": md_path}
