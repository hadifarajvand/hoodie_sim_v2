from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Any

FIGURE_OUTPUTS = {
    "Figure 7": "figure_7_topology",
    "Figure 8": "figure_8_training_curves",
    "Figure 9": "figure_9_parameter_sweeps",
    "Figure 10": "figure_10_simulation_metrics_partial",
    "Figure 11": "figure_11_lstm_ablation",
}

FIGURE_TITLES = {
    "Figure 7": "Edge Layer Topology",
    "Figure 8": "Training Convergence",
    "Figure 9": "System Behavior & Scalability",
    "Figure 10": "Performance Comparison",
    "Figure 11": "LSTM Ablation Study",
}

DATASET_COLUMNS = [
    "figure_id",
    "subfigure_id",
    "series_name",
    "episode",
    "x_value",
    "y_value",
    "x_unit",
    "y_unit",
    "policy_name",
    "seed",
    "scenario_name",
    "source_kind",
    "source_path",
    "reconstruction_status",
    "limitation",
    "comparison_allowed",
]

FIGURE10_LIMITATION = "Figure 10 PDF extraction lacks full numeric curve targets; export simulation metrics only; no paper-target reconstruction."


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def enforce_figure10_limitation(entry: dict[str, Any]) -> None:
    if entry.get("figure_id") != "Figure 10":
        return
    numeric = entry.get("paper_numeric_target_data", {})
    if not isinstance(numeric, dict):
        numeric = {}
    if entry.get("comparison_ready") is True:
        raise ValueError("Figure 10 is only partially extracted; paper comparison must remain disabled.")
    if entry.get("reconstruction_status") == "full_pdf_extracted":
        raise ValueError("Figure 10 is only partially extracted; full reconstruction status is not allowed.")
    if numeric.get("available") is True:
        raise ValueError("Figure 10 lacks full paper numeric targets; paper_numeric_target_data.available must remain false.")


@dataclass(slots=True)
class PaperFigureDatasetBuilder:
    entries: list[dict[str, Any]]

    @classmethod
    def from_report(cls, report_or_payload: Any) -> "PaperFigureDatasetBuilder":
        payload = report_or_payload.to_dict() if hasattr(report_or_payload, "to_dict") else dict(report_or_payload)
        entries = [entry for entry in payload.get("figure_entries", []) if isinstance(entry, dict)]
        return cls(entries=entries)

    def build_payloads(self) -> dict[str, dict[str, Any]]:
        payloads: dict[str, dict[str, Any]] = {}
        for entry in self.entries:
            figure_id = str(entry.get("figure_id", ""))
            if figure_id not in FIGURE_OUTPUTS:
                continue
            enforce_figure10_limitation(entry)
            rows = self._rows_for_entry(entry)
            payloads[figure_id] = {
                "figure_id": figure_id,
                "title": entry.get("title", ""),
                "reconstruction_status": self._reconstruction_status(entry),
                "comparison_allowed": bool(entry.get("comparison_ready")) and figure_id != "Figure 10",
                "limitation_level": entry.get("limitation_level", self._limitation_level(entry)),
                "limitations": self._limitations(entry),
                "source_artifacts": list(entry.get("source_artifacts", []) or []),
                "paper_extraction_source": dict(entry.get("paper_extraction_source", {}) or {}),
                "rows": rows,
            }
        return payloads

    def manifest(self, output_dir: Path) -> dict[str, Any]:
        payloads = self.build_payloads()
        figures: dict[str, dict[str, str]] = {}
        for figure_id in sorted(payloads):
            stem = FIGURE_OUTPUTS[figure_id]
            figures[figure_id] = {
                "json": (output_dir / f"{stem}.json").as_posix(),
                "csv": (output_dir / f"{stem}.csv").as_posix(),
                "png": (output_dir / f"{stem}.png").as_posix(),
            }
        return {"figures": figures, "figure_10_limitation": FIGURE10_LIMITATION}

    def _rows_for_entry(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        figure_id = str(entry.get("figure_id", ""))
        if figure_id == "Figure 8":
            return self._figure8_rows(entry)
        if figure_id == "Figure 9":
            return self._figure9_rows(entry)
        if figure_id == "Figure 10":
            return self._figure10_rows(entry)
        if figure_id == "Figure 11":
            return self._figure11_rows(entry)
        return [self._status_row(entry)]

    @staticmethod
    def _truncate_episodes(values: list[Any], limit: int = 20) -> list[tuple[int, Any]]:
        return list(enumerate(values[:limit], start=1))

    def _episode_row(self, entry: dict[str, Any], *, subfigure_id: str, series_name: str, episode: int, y_value: Any, x_unit: str = "episode", y_unit: str = "value", source_kind: str = "simulation_artifact") -> dict[str, Any]:
        row = self._base_row(entry)
        row.update(
            {
                "subfigure_id": subfigure_id,
                "series_name": series_name,
                "episode": episode,
                "x_value": episode,
                "y_value": y_value,
                "x_unit": x_unit,
                "y_unit": y_unit,
                "source_kind": source_kind,
                "comparison_allowed": bool(entry.get("comparison_ready")) and entry.get("figure_id") != "Figure 10",
            }
        )
        return row

    def _figure8_rows(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        metrics = entry.get("extracted_artifact_metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        reward_series = metrics.get("episode_reward_means", []) or []
        if reward_series:
            return [
                self._episode_row(
                    entry,
                    subfigure_id="8-training-curve",
                    series_name="reward",
                    episode=episode,
                    y_value=value,
                    y_unit="reward",
                )
                for episode, value in self._truncate_episodes(list(reward_series))
            ]
        return [self._status_row(entry)]

    def _figure11_rows(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        metrics = entry.get("extracted_artifact_metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        reward_series = metrics.get("reward_per_episode", []) or []
        if reward_series:
            return [
                self._episode_row(
                    entry,
                    subfigure_id="11-lstm-ablation",
                    series_name="delay",
                    episode=episode,
                    y_value=value,
                    y_unit="delay",
                )
                for episode, value in self._truncate_episodes(list(reward_series))
            ]
        return [self._status_row(entry)]

    def _base_row(self, entry: dict[str, Any]) -> dict[str, Any]:
        return {
            "figure_id": entry.get("figure_id", ""),
            "subfigure_id": "",
            "series_name": "status",
            "episode": "",
            "x_value": "",
            "y_value": "",
            "x_unit": "",
            "y_unit": "",
            "policy_name": "",
            "seed": "",
            "scenario_name": "",
            "source_kind": "pdf_extracted" if self._reconstruction_status(entry) == "full_pdf_extracted" else "simulation_artifact",
            "source_path": ";".join(str(path) for path in entry.get("source_artifacts", []) or []),
            "reconstruction_status": self._reconstruction_status(entry),
            "limitation": " | ".join(self._limitations(entry)),
            "comparison_allowed": bool(entry.get("comparison_ready")) and entry.get("figure_id") != "Figure 10",
        }

    def _status_row(self, entry: dict[str, Any]) -> dict[str, Any]:
        row = self._base_row(entry)
        row.update(
            {
                "series_name": "support_status",
                "y_value": entry.get("support_status", "unknown"),
                "source_kind": "pdf_extracted",
            }
        )
        return row

    def _figure9_rows(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        metrics = entry.get("extracted_artifact_metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        rows: list[dict[str, Any]] = []
        action_distributions = metrics.get("action_distribution_by_policy", []) or []
        if action_distributions:
            for policy_bucket in action_distributions:
                policy_name = str(policy_bucket.get("policy_name", "unknown"))
                for action_row in policy_bucket.get("action_distribution", []) or []:
                    row = self._base_row(entry)
                    row.update(
                        {
                            "subfigure_id": "9b",
                            "series_name": str(action_row.get("action", "unknown")),
                            "episode": "",
                            "x_value": policy_name,
                            "y_value": action_row.get("count", 0),
                            "x_unit": "policy",
                            "y_unit": "action_count",
                            "policy_name": policy_name,
                            "source_kind": "simulation_artifact",
                        }
                    )
                    rows.append(row)
        if not rows:
            return [self._status_row(entry)]
        return rows

    def _figure10_rows(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        metrics = entry.get("extracted_artifact_metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        rows: list[dict[str, Any]] = []
        for metric_name, y_unit in (("mean_average_delay", "slots"), ("mean_drop_ratio", "ratio")):
            for item in metrics.get("by_policy", []) or []:
                row = self._base_row(entry)
                row.update(
                    {
                        "subfigure_id": "10-simulation-metrics-partial",
                        "series_name": metric_name,
                        "x_value": item.get("key", "unknown"),
                        "y_value": item.get(metric_name, 0.0),
                        "x_unit": "policy",
                        "y_unit": y_unit,
                        "policy_name": item.get("key", "unknown"),
                        "source_kind": "simulation_artifact",
                        "limitation": FIGURE10_LIMITATION,
                    }
                )
                rows.append(row)
        return rows or [self._status_row(entry)]

    @staticmethod
    def _reconstruction_status(entry: dict[str, Any]) -> str:
        if entry.get("reconstruction_status"):
            return str(entry["reconstruction_status"])
        if entry.get("figure_id") == "Figure 10":
            return "partial_pdf_extracted"
        if entry.get("figure_id") in {"Figure 7", "Figure 8", "Figure 9", "Figure 11"}:
            return "full_pdf_extracted"
        return "unsupported"

    def _limitation_level(self, entry: dict[str, Any]) -> str:
        status = self._reconstruction_status(entry)
        if status == "full_pdf_extracted":
            return "none"
        if status == "partial_pdf_extracted":
            return "partial"
        return "blocked"

    def _limitations(self, entry: dict[str, Any]) -> list[str]:
        limitations = [str(item) for item in entry.get("caveats", []) or []]
        if entry.get("figure_id") == "Figure 10":
            limitations.insert(0, FIGURE10_LIMITATION)
        if entry.get("missing_artifacts"):
            limitations.append("missing_artifacts: " + ",".join(str(item) for item in entry.get("missing_artifacts", []) or []))
        return list(dict.fromkeys(limitations))


def write_paper_figure_datasets(report_or_payload: Any, output_dir: Path | str) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    builder = PaperFigureDatasetBuilder.from_report(report_or_payload)
    payloads = builder.build_payloads()
    manifest: dict[str, Any] = {"figures": {}, "figure_10_limitation": FIGURE10_LIMITATION}
    limitations: dict[str, list[str]] = {}
    provenance: dict[str, dict[str, Any]] = {}
    for figure_id in sorted(payloads):
        payload = payloads[figure_id]
        stem = FIGURE_OUTPUTS[figure_id]
        json_path = output_path / f"{stem}.json"
        csv_path = output_path / f"{stem}.csv"
        json_path.write_text(_json_dump(payload), encoding="utf-8")
        _write_csv(payload["rows"], csv_path)
        manifest["figures"][figure_id] = {"json": json_path.as_posix(), "csv": csv_path.as_posix()}
        limitations[figure_id] = list(payload["limitations"])
        provenance[figure_id] = {
            "reconstruction_status": payload["reconstruction_status"],
            "source_artifacts": payload["source_artifacts"],
            "paper_extraction_source": payload["paper_extraction_source"],
            "comparison_allowed": payload["comparison_allowed"],
        }
    (output_path / "manifest.json").write_text(_json_dump(manifest), encoding="utf-8")
    (output_path / "limitations.json").write_text(_json_dump(limitations), encoding="utf-8")
    (output_path / "provenance.json").write_text(_json_dump(provenance), encoding="utf-8")
    return manifest


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in DATASET_COLUMNS})
