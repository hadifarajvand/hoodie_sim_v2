from __future__ import annotations

import argparse
import csv
import json
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent


@dataclass
class FigureManifest:
    diagnostic_only: bool
    paper_performance_claims_made: bool
    input_artifact_dir: str
    figure_dir: str
    data_dir: str
    blockers: list[str]
    warnings: list[str]
    figures: dict[str, str]


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _fig8_episode_outcomes(trace_dir: Path, output_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    rows = _load_csv(trace_dir / "episode_metrics_summary.csv")
    xs = [int(r["episode_id"]) for r in rows]
    completed = [float(r["completion_ratio"]) for r in rows]
    dropped = [float(r["drop_ratio"]) for r in rows]
    pending = [float(r["pending_tasks"]) / max(1.0, float(r["total_tasks"])) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(xs, completed, label="completion")
    ax.plot(xs, dropped, label="drop")
    ax.plot(xs, pending, label="pending")
    ax.set_title("Figure 8 Diagnostic Preview: Episode Outcomes")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Ratio")
    ax.legend()
    fig.tight_layout()
    path = output_dir / "figures" / "figure_8_episode_outcomes.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    data_rows = [{"episode_id": x, "completion_ratio": c, "drop_ratio": d, "pending_ratio": p} for x, c, d, p in zip(xs, completed, dropped, pending)]
    return str(path), data_rows


def _fig9_latency(trace_dir: Path, output_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    rows = _load_csv(trace_dir / "episode_metrics_summary.csv")
    xs = [int(r["episode_id"]) for r in rows]
    latency = [float(r["average_latency"]) for r in rows]
    waiting = [float(r["average_waiting_time"]) for r in rows]
    service = [float(r["average_service_time"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(xs, latency, label="latency")
    ax.plot(xs, waiting, label="waiting")
    ax.plot(xs, service, label="service")
    ax.set_title("Figure 9 Diagnostic Preview: Episode Time Metrics")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Seconds")
    ax.legend()
    fig.tight_layout()
    path = output_dir / "figures" / "figure_9_latency_wait_service.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    data_rows = [{"episode_id": x, "average_latency": a, "average_waiting_time": b, "average_service_time": c} for x, a, b, c in zip(xs, latency, waiting, service)]
    return str(path), data_rows


def _fig10_actions(trace_dir: Path, output_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    rows = _load_csv(trace_dir / "policy_action_summary.csv")
    metrics = {r["metric"]: r["value"] for r in rows}
    by_type = {
        "local": int(metrics.get("local_action_count", 0) or 0),
        "horizontal_edge": int(metrics.get("horizontal_action_count", 0) or 0),
        "vertical_cloud": int(metrics.get("vertical_cloud_action_count", 0) or 0),
    }
    labels = list(by_type.keys())
    counts = [int(by_type[k]) for k in labels]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, counts, color=["#4c78a8", "#f58518", "#54a24b"])
    ax.set_title("Figure 10 Diagnostic Preview: Action Distribution and Legality")
    ax.set_ylabel("Count")
    fig.tight_layout()
    path = output_dir / "figures" / "figure_10_action_legality.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    data_rows = [{"action_type": k, "count": int(v)} for k, v in by_type.items()]
    return str(path), data_rows


def _fig11_state(trace_dir: Path, output_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    summary = json.loads((trace_dir / "state_lstm_summary.json").read_text())
    state_dim = summary.get("state_dim_max") or summary.get("state_dim_min") or 0
    forecast_counts = summary.get("predicted_next_load_method_counts", {})
    forecast_count = int(forecast_counts.get("persistence_baseline", 0) or forecast_counts.get("lstm_forecast", 0) or 0)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(["state_dim", "load_len", "forecast_count"], [state_dim, summary.get("active_load_vector_length", 0), forecast_count], color=["#4c78a8", "#f58518", "#54a24b"])
    ax.set_title("Figure 11 Diagnostic Preview: State/LSTM Readiness")
    ax.set_ylabel("Value")
    fig.tight_layout()
    path = output_dir / "figures" / "figure_11_state_lstm_readiness.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    data_rows = [
        {"metric": "state_dim", "value": state_dim},
        {"metric": "active_load_vector_length", "value": summary.get("active_load_vector_length")},
        {"metric": "forecast_count", "value": forecast_count},
        {"metric": "paper_lstm_forecast_false_count", "value": summary.get("paper_lstm_forecast_false_count")},
    ]
    return str(path), data_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", default="artifacts/phase5_figures")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    figure_dir = output_dir / "figures"
    data_dir = output_dir / "data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    blockers = []
    warnings = []
    report_path = input_dir / "phase4_validation_report.json"
    if not report_path.exists():
        raise SystemExit("phase4_validation_report.json is required")
    report = json.loads(report_path.read_text())
    if report.get("paper_performance_claims_made"):
        blockers.append("paper_performance_claims_made must remain false")
    if report.get("invalid_action_ratio") != 0.0:
        warnings.append("invalid_action_ratio is not zero")
    if report.get("predicted_next_load_method_counts", {}).get("persistence_baseline", 0):
        warnings.append("predicted_next_load still uses persistence_baseline")

    fig8_path, fig8_rows = _fig8_episode_outcomes(input_dir, output_dir)
    fig9_path, fig9_rows = _fig9_latency(input_dir, output_dir)
    fig10_path, fig10_rows = _fig10_actions(input_dir, output_dir)
    fig11_path, fig11_rows = _fig11_state(input_dir, output_dir)

    _write_csv(data_dir / "figure_8_episode_outcomes.csv", fig8_rows)
    _write_csv(data_dir / "figure_9_latency_wait_service.csv", fig9_rows)
    _write_csv(data_dir / "figure_10_action_distribution.csv", fig10_rows)
    _write_csv(data_dir / "figure_11_state_lstm_readiness.csv", fig11_rows)

    manifest = FigureManifest(
        diagnostic_only=True,
        paper_performance_claims_made=False,
        input_artifact_dir=str(input_dir),
        figure_dir=str(figure_dir),
        data_dir=str(data_dir),
        blockers=blockers,
        warnings=warnings,
        figures={
            "figure_8": fig8_path,
            "figure_9": fig9_path,
            "figure_10": fig10_path,
            "figure_11": fig11_path,
        },
    )
    (output_dir / "figure_manifest.json").write_text(json.dumps(manifest.__dict__, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
