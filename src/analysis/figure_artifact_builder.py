from __future__ import annotations

from pathlib import Path
import csv
import json
from typing import Any

FIGURE_SLUGS = {
    "Figure 7": "figure_7_topology_partial",
    "Figure 8": "figure_8_training_curves",
    "Figure 9": "figure_9_parameter_sweeps",
    "Figure 10": "figure_10_simulation_metrics_partial",
    "Figure 11": "figure_11_lstm_ablation",
}

FIGURE_TITLES = {
    "Figure 7": "Edge Topology",
    "Figure 8": "Training Convergence",
    "Figure 9": "System Behavior & Scalability",
    "Figure 10": "Performance Comparison",
    "Figure 11": "LSTM Ablation Study",
}

FIGURE10_LIMITATION = "Figure 10 PDF extraction lacks full numeric curve targets; export simulation metrics only; no paper-target reconstruction."


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _figure_title(figure_id: str) -> str:
    return FIGURE_TITLES.get(figure_id, figure_id)


def _base_row(entry: dict[str, Any]) -> dict[str, Any]:
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
        "source_kind": "pdf_extracted" if entry.get("reconstruction_status") == "full_pdf_extracted" else "simulation_artifact",
        "source_path": ";".join(str(path) for path in entry.get("source_artifacts", []) or []),
        "reconstruction_status": entry.get("reconstruction_status", "unsupported"),
        "limitation": " | ".join(str(item) for item in entry.get("caveats", []) or []),
        "comparison_allowed": bool(entry.get("comparison_ready")) and entry.get("figure_id") != "Figure 10",
    }


def _status_row(entry: dict[str, Any]) -> dict[str, Any]:
    row = _base_row(entry)
    row.update(
        {
            "series_name": "support_status",
            "y_value": entry.get("support_status", "unknown"),
            "source_kind": "pdf_extracted",
        }
    )
    return row


def _series_rows(entry: dict[str, Any], *, subfigure_id: str, series_name: str, values: list[Any], y_unit: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode, value in enumerate(values[:20], start=1):
        row = _base_row(entry)
        row.update(
            {
                "subfigure_id": subfigure_id,
                "series_name": series_name,
                "episode": episode,
                "x_value": episode,
                "y_value": value,
                "x_unit": "episode",
                "y_unit": y_unit,
            }
        )
        rows.append(row)
    return rows


def _entry_rows(entry: dict[str, Any]) -> list[dict[str, Any]]:
    figure_id = str(entry.get("figure_id", ""))
    metrics = entry.get("extracted_artifact_metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}

    if figure_id == "Figure 7":
        rows = []
        observed_trace_file_count = metrics.get("observed_trace_file_count")
        if observed_trace_file_count is not None:
            row = _base_row(entry)
            row.update(
                {
                    "subfigure_id": "7-topology-caption",
                    "series_name": "observed_trace_file_count",
                    "x_value": "trace_files",
                    "y_value": observed_trace_file_count,
                    "x_unit": "artifact_class",
                    "y_unit": "count",
                    "source_kind": "simulation_artifact",
                }
            )
            rows.append(row)
        return rows or [_status_row(entry)]

    if figure_id == "Figure 8":
        rows = _series_rows(entry, subfigure_id="8-training-curve", series_name="reward", values=list(metrics.get("episode_reward_means", []) or []), y_unit="reward")
        return rows or [_status_row(entry)]

    if figure_id == "Figure 9":
        rows: list[dict[str, Any]] = []
        for policy_bucket in metrics.get("action_distribution_by_policy", []) or []:
            policy_name = str(policy_bucket.get("policy_name", "unknown"))
            for action_row in policy_bucket.get("action_distribution", []) or []:
                row = _base_row(entry)
                row.update(
                    {
                        "subfigure_id": "9b",
                        "series_name": str(action_row.get("action", "unknown")),
                        "x_value": policy_name,
                        "y_value": action_row.get("count", 0),
                        "x_unit": "policy",
                        "y_unit": "action_count",
                        "policy_name": policy_name,
                        "source_kind": "simulation_artifact",
                    }
                )
                rows.append(row)
        return rows or [_status_row(entry)]

    if figure_id == "Figure 10":
        rows = []
        for row in metrics.get("by_policy", []) or []:
            rows.append(
                {
                    "figure_id": figure_id,
                    "subfigure_id": "10-simulation-metrics-partial",
                    "series_name": "mean_average_delay",
                    "episode": "",
                    "x_value": row.get("key", "unknown"),
                    "y_value": row.get("mean_average_delay", 0.0),
                    "x_unit": "policy",
                    "y_unit": "slots",
                    "policy_name": row.get("key", "unknown"),
                    "seed": "",
                    "scenario_name": "",
                    "source_kind": "simulation_artifact",
                    "source_path": ";".join(str(path) for path in entry.get("source_artifacts", []) or []),
                    "reconstruction_status": entry.get("reconstruction_status", "partial_pdf_extracted"),
                    "limitation": FIGURE10_LIMITATION,
                    "comparison_allowed": False,
                }
            )
            rows.append(
                {
                    "figure_id": figure_id,
                    "subfigure_id": "10-simulation-metrics-partial",
                    "series_name": "mean_drop_ratio",
                    "episode": "",
                    "x_value": row.get("key", "unknown"),
                    "y_value": row.get("mean_drop_ratio", 0.0),
                    "x_unit": "policy",
                    "y_unit": "ratio",
                    "policy_name": row.get("key", "unknown"),
                    "seed": "",
                    "scenario_name": "",
                    "source_kind": "simulation_artifact",
                    "source_path": ";".join(str(path) for path in entry.get("source_artifacts", []) or []),
                    "reconstruction_status": entry.get("reconstruction_status", "partial_pdf_extracted"),
                    "limitation": FIGURE10_LIMITATION,
                    "comparison_allowed": False,
                }
            )
        return rows or [_status_row(entry)]

    if figure_id == "Figure 8":
        rows = _series_rows(entry, subfigure_id="8-training-curve", series_name="reward", values=list(metrics.get("episode_reward_means", []) or metrics.get("reward_per_episode", []) or []), y_unit="reward")
        return rows or [_status_row(entry)]

    if figure_id == "Figure 9":
        rows: list[dict[str, Any]] = []
        for key in ["completion_rate_by_destination", "topology_usage_stats"]:
            data = metrics.get(key, {}) or {}
            for subkey, value in data.items():
                row = _base_row(entry)
                row.update({
                    "subfigure_id": "9-validation",
                    "series_name": key,
                    "episode": "",
                    "x_value": subkey,
                    "y_value": value,
                    "x_unit": "category",
                    "y_unit": "value",
                    "source_kind": "simulation_artifact",
                })
                rows.append(row)
        return rows or [_status_row(entry)]

    if figure_id == "Figure 10":
        rows = []
        for row in metrics.get("per_run", []) or []:
            rows.append({
                "figure_id": figure_id,
                "subfigure_id": "10-reconstructed",
                "series_name": "average_delay",
                "episode": "",
                "x_value": row.get("scenario_name", "unknown"),
                "y_value": row.get("average_delay", 0.0),
                "x_unit": "scenario",
                "y_unit": "slots",
                "policy_name": row.get("policy_name", "unknown"),
                "seed": row.get("seed", ""),
                "scenario_name": row.get("scenario_name", ""),
                "source_kind": "simulation_artifact",
                "source_path": ";".join(str(path) for path in entry.get("source_artifacts", []) or []),
                "reconstruction_status": entry.get("reconstruction_status", "partial_pdf_extracted"),
                "limitation": FIGURE10_LIMITATION,
                "comparison_allowed": False,
            })
        return rows or [_status_row(entry)]

    if figure_id == "Figure 11":
        rows = _series_rows(entry, subfigure_id="11-lstm-ablation", series_name="delay", values=list(metrics.get("average_delays", []) or []), y_unit="delay")
        return rows or [_status_row(entry)]

    return [_status_row(entry)]


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) or ["status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _status_png(entry: dict[str, Any], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis("off")
    missing = entry.get("missing_artifacts", []) or []
    caveats = entry.get("caveats", []) or []
    text = "\n".join(
        [
            str(entry.get("figure_id", "Figure")),
            _figure_title(str(entry.get("figure_id", ""))),
            str(entry.get("title", "")),
            f"support_status: {entry.get('support_status', 'unknown')}",
            "",
            "No paper reproduction curve fabricated.",
            "Missing: " + (", ".join(str(item) for item in missing[:5]) if missing else "none"),
            "Caveat: " + (str(caveats[0]) if caveats else "none"),
        ]
    )
    ax.text(0.04, 0.92, text, va="top", ha="left", fontsize=11, wrap=True, family="monospace")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure7_png(rows: list[dict[str, Any]], entry: dict[str, Any], path: Path) -> None:
    if not rows:
        _status_png(entry, path)
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [str(row.get("x_value", "trace_files")) for row in rows]
    values = [float(row.get("y_value", 0.0) or 0.0) for row in rows]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color="#4C78A8")
    ax.set_title("Figure 7 artifact: topology support status")
    ax.set_ylabel("count")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure8_png(rows: list[dict[str, Any]], entry: dict[str, Any], path: Path) -> None:
    numeric_rows = []
    for row in rows:
        try:
            episode = int(row.get("episode", 0) or 0)
            value = float(row.get("y_value", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        numeric_rows.append((episode, value))
    if not numeric_rows:
        _status_png(entry, path)
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    episodes = [episode for episode, _value in numeric_rows]
    values = [value for _episode, value in numeric_rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(episodes, values, marker="o", linewidth=1.8, color="#4C78A8")
    ax.set_title("Figure 8 artifact: training curve")
    ax.set_xlabel("episode")
    ax.set_ylabel("reward")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure9_png(rows: list[dict[str, Any]], entry: dict[str, Any], path: Path) -> None:
    numeric_rows = []
    for row in rows:
        try:
            policy = str(row["policy_name"])
            value = int(row.get("y_value", 0) or 0)
        except (TypeError, ValueError, KeyError):
            continue
        numeric_rows.append((policy, value))
    if not numeric_rows:
        _status_png(entry, path)
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    policies = sorted({policy for policy, _value in numeric_rows})
    totals = {policy: 0 for policy in policies}
    for policy, value in numeric_rows:
        totals[policy] += value
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(policies, [totals[policy] for policy in policies], color="#4C78A8")
    ax.set_title("Figure 9 artifact: action counts by policy")
    ax.set_ylabel("action count")
    ax.set_xlabel("policy")
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure10_png(rows: list[dict[str, Any]], entry: dict[str, Any], path: Path) -> None:
    if not rows:
        _status_png(entry, path)
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    policies = [str(row["policy_name"]) for row in rows if row.get("series_name") == "mean_average_delay"]
    delays = [float(row.get("y_value", 0.0) or 0.0) for row in rows if row.get("series_name") == "mean_average_delay"]
    drops = [float(row.get("y_value", 0.0) or 0.0) for row in rows if row.get("series_name") == "mean_drop_ratio"]
    drop_policies = [str(row["policy_name"]) for row in rows if row.get("series_name") == "mean_drop_ratio"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(policies, delays, color="#4C78A8")
    axes[0].set_title("Mean average delay")
    axes[0].tick_params(axis="x", rotation=35)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].bar(drop_policies, drops, color="#F58518")
    axes[1].set_title("Mean drop ratio")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].grid(axis="y", alpha=0.25)
    fig.suptitle("Figure 10 artifact: baseline metrics by policy")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure11_png(rows: list[dict[str, Any]], entry: dict[str, Any], path: Path) -> None:
    numeric_rows = []
    for row in rows:
        try:
            episode = int(row.get("episode", 0) or 0)
            value = float(row.get("y_value", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        numeric_rows.append((episode, value))
    if not numeric_rows:
        _status_png(entry, path)
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    episodes = [episode for episode, _value in numeric_rows]
    values = [value for _episode, value in numeric_rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(episodes, values, marker="o", linewidth=1.8, color="#F58518")
    ax.set_title("Figure 11 artifact: LSTM ablation")
    ax.set_xlabel("episode")
    ax.set_ylabel("delay")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _write_png(entry: dict[str, Any], rows: list[dict[str, Any]], path: Path) -> None:
    figure_id = str(entry.get("figure_id", ""))
    if figure_id == "Figure 7":
        _figure7_png(rows, entry, path)
    elif figure_id == "Figure 8":
        _figure8_png(rows, entry, path)
    elif figure_id == "Figure 9":
        _figure9_png(rows, entry, path)
    elif figure_id == "Figure 10":
        _figure10_png(rows, entry, path)
    elif figure_id == "Figure 11":
        _figure11_png(rows, entry, path)
    else:
        _status_png(entry, path)


def write_figure_artifacts(report_or_payload: Any, output_dir: Path | str) -> dict[str, dict[str, str]]:
    payload = report_or_payload.to_dict() if hasattr(report_or_payload, "to_dict") else dict(report_or_payload)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, str]] = {}
    entries = list(payload.get("figure_entries", []))
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        figure_id = str(entry.get("figure_id", ""))
        slug = FIGURE_SLUGS.get(figure_id)
        if slug is None:
            continue
        rows = _entry_rows(entry)
        json_path = output_path / f"{slug}.json"
        csv_path = output_path / f"{slug}.csv"
        png_path = output_path / f"{slug}.png"
        json_path.write_text(_json_dump(entry), encoding="utf-8")
        _write_csv(rows, csv_path)
        _write_png(entry, rows, png_path)
        manifest[figure_id] = {
            "json": json_path.as_posix(),
            "csv": csv_path.as_posix(),
            "png": png_path.as_posix(),
        }
    (output_path / "figure-artifact-manifest.json").write_text(_json_dump(manifest), encoding="utf-8")
    return manifest
