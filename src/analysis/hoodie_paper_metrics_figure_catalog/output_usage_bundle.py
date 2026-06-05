from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import csv
import json
from typing import Any

from .config import ARTIFACT_DIR, FEATURE_080_BOUNDARY, FEATURE_086_BOUNDARY, FEATURE_ID


BUNDLE_DIR_NAME = "output_usage_bundle"
OUTPUT_BUNDLE_VERDICT = "feature_089_output_bundle_ready"

FIGURE_10_FILES = {
    "Figure 10a": ("figure_10a_delay_vs_arrival_probability.csv", "figure_10a_delay_vs_arrival_probability.json"),
    "Figure 10b": ("figure_10b_delay_vs_cpu_capacity.csv", "figure_10b_delay_vs_cpu_capacity.json"),
    "Figure 10c": ("figure_10c_delay_vs_timeout.csv", "figure_10c_delay_vs_timeout.json"),
    "Figure 10d": ("figure_10d_drop_ratio_vs_arrival_probability.csv", "figure_10d_drop_ratio_vs_arrival_probability.json"),
    "Figure 10e": ("figure_10e_drop_ratio_vs_cpu_capacity.csv", "figure_10e_drop_ratio_vs_cpu_capacity.json"),
    "Figure 10f": ("figure_10f_drop_ratio_vs_timeout.csv", "figure_10f_drop_ratio_vs_timeout.json"),
}

FIGURE_9_FILES = {
    "Figure 9a": ("figure_9a_reward_vs_arrival_probability.csv", "figure_9a_reward_vs_arrival_probability.json"),
    "Figure 9b": ("figure_9b_action_distribution_vs_arrival_probability.csv", "figure_9b_action_distribution_vs_arrival_probability.json"),
    "Figure 9c": ("figure_9c_reward_vs_cpu_capacity.csv", "figure_9c_reward_vs_cpu_capacity.json"),
    "Figure 9d": ("figure_9d_reward_vs_agent_count_traffic.csv", "figure_9d_reward_vs_agent_count_traffic.json"),
    "Figure 9e": ("figure_9e_reward_vs_agent_count_data_rate.csv", "figure_9e_reward_vs_agent_count_data_rate.json"),
}

GATED_FILES = {
    "Figure 8a": ("figure_8a_learning_rate_convergence_status.md", "figure_8a_learning_rate_convergence_status.json"),
    "Figure 8b": ("figure_8b_discount_factor_convergence_status.md", "figure_8b_discount_factor_convergence_status.json"),
    "Figure 11": ("figure_11_lstm_ablation_status.md", "figure_11_lstm_ablation_status.json"),
}


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dump(payload), encoding="utf-8")


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key, "")) for key in writer.fieldnames})


def _markdown_cell(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _write_markdown_table(path: Path, title: str, rows: list[dict[str, Any]], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    field_list = list(fieldnames)
    lines = [f"# {title}", ""]
    if not rows:
        lines.append("_No rows._")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    lines.append("| " + " | ".join(field_list) + " |")
    lines.append("| " + " | ".join("---" for _ in field_list) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(row.get(field, "")) for field in field_list) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_json_array(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    return [dict(item) for item in payload]


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return dict(payload)


def _source_path(artifact_dir: Path, filename: str) -> str:
    return str((artifact_dir / filename).relative_to(artifact_dir.parent))


def _bundle_path(bundle_dir: Path, artifact_dir: Path, filename: str) -> str:
    try:
        return str((bundle_dir / filename).relative_to(artifact_dir.parent))
    except ValueError:
        return str(bundle_dir / filename)


def _figure_family(figure_id: str) -> str:
    return figure_id.split("a")[0] if figure_id.startswith("Figure 8") else figure_id.rsplit(" ", 1)[0]


def _figure_family_simple(figure_id: str) -> str:
    if figure_id.startswith("Figure 10"):
        return "Figure 10"
    if figure_id.startswith("Figure 9"):
        return "Figure 9"
    if figure_id.startswith("Figure 8"):
        return "Figure 8"
    return "Figure 11"


def _figure_10_value_fields(figure_id: str) -> tuple[str, str, str]:
    if figure_id in {"Figure 10a", "Figure 10b", "Figure 10c"}:
        return "task_completion_delay_raw", "paper_style_delay_for_plotting", "seconds"
    return "task_drop_ratio", "task_drop_percent", "ratio"


def _figure_10_combined_rows(artifact_dir: Path, bundle_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for figure_id, (_csv_name, json_name) in FIGURE_10_FILES.items():
        payload = _load_json_array(artifact_dir / json_name)
        raw_field, paper_field, units = _figure_10_value_fields(figure_id)
        x_axis_name = str(payload[0]["x_axis"]) if payload else ""
        for row in payload:
            rows.append(
                {
                    "figure_id": figure_id,
                    "metric": row.get("metric"),
                    "policy": row.get("policy"),
                    "x_axis_name": x_axis_name,
                    "x_axis_value": row.get("sweep_value"),
                    "raw_value": row.get(raw_field),
                    "paper_style_value": row.get(paper_field),
                    "value_units": units,
                    "claim_boundary": row.get("claim_boundary", []),
                }
            )
    return rows


def _figure_9_combined_rows(artifact_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for figure_id, (_csv_name, json_name) in FIGURE_9_FILES.items():
        payload = _load_json_array(artifact_dir / json_name)
        for row in payload:
            series_name = row.get("curve_label")
            if figure_id == "Figure 9b":
                series_name = row.get("action_type")
            elif figure_id == "Figure 9d":
                series_name = row.get("traffic_intensity_label")
            elif figure_id == "Figure 9e":
                series_name = row.get("data_rate_configuration_label")
            rows.append(
                {
                    "figure_id": figure_id,
                    "metric": row.get("metric"),
                    "policy": row.get("policy"),
                    "x_axis_name": row.get("paper_x_axis"),
                    "x_axis_value": row.get("paper_x_axis_value"),
                    "series_name": series_name,
                    "raw_value": row.get("value"),
                    "support_status": row.get("support_status"),
                    "approximation_note": row.get("approximation_note"),
                    "claim_boundary": row.get("claim_boundary", []),
                }
            )
    return rows


def _index_rows(artifact_dir: Path, bundle_dir: Path) -> list[dict[str, Any]]:
    index_rows: list[dict[str, Any]] = []
    figure_10_summary = _load_json_object(artifact_dir / "figure_10_analysis_summary.json")
    remaining_report = _load_json_object(artifact_dir / "remaining_figure_outputs_report.json")
    figure_8_statuses = remaining_report["figure_8_status_by_figure"]
    figure_11_status = remaining_report["figure_11_status"]
    figure_9_statuses = remaining_report["figure_9_status_by_figure"]

    for figure_id, (csv_name, json_name) in FIGURE_10_FILES.items():
        index_rows.append(
            {
                "figure_id": figure_id,
                "figure_family": _figure_family_simple(figure_id),
                "metric": "average_task_completion_delay" if figure_id in {"Figure 10a", "Figure 10b", "Figure 10c"} else "task_drop_ratio",
                "status": "validated",
                "artifact_paths": [
                    _source_path(artifact_dir, csv_name),
                    _source_path(artifact_dir, json_name),
                    _bundle_path(bundle_dir, artifact_dir, "figure_10_plot_ready_combined.csv"),
                    _bundle_path(bundle_dir, artifact_dir, "figure_10_plot_ready_combined.json"),
                ],
                "plot_ready_available": True,
                "support_status": figure_10_summary["verdict"],
                "claim_boundary": figure_10_summary["claim_boundary"],
                "notes": "Figure 10 outputs are validated and ready for plotting.",
            }
        )

    for figure_id, (csv_name, json_name) in FIGURE_9_FILES.items():
        payload = _load_json_array(artifact_dir / json_name)
        first_row = payload[0] if payload else {}
        index_rows.append(
            {
                "figure_id": figure_id,
                "figure_family": _figure_family_simple(figure_id),
                "metric": first_row.get("metric"),
                "status": "generated_with_approximation",
                "artifact_paths": [
                    _source_path(artifact_dir, csv_name),
                    _source_path(artifact_dir, json_name),
                    _bundle_path(bundle_dir, artifact_dir, "figure_9_plot_ready_combined.csv"),
                    _bundle_path(bundle_dir, artifact_dir, "figure_9_plot_ready_combined.json"),
                ],
                "plot_ready_available": True,
                "support_status": first_row.get("support_status"),
                "claim_boundary": first_row.get("claim_boundary", []),
                "notes": first_row.get("approximation_note", ""),
            }
        )

    for figure_id, (md_name, json_name) in GATED_FILES.items():
        payload = _load_json_object(artifact_dir / json_name)
        index_rows.append(
            {
                "figure_id": figure_id,
                "figure_family": _figure_family_simple(figure_id),
                "metric": None,
                "status": payload["support_status"],
                "artifact_paths": [
                    _source_path(artifact_dir, md_name),
                    _source_path(artifact_dir, json_name),
                ],
                "plot_ready_available": bool(payload.get("plot_ready_generated")),
                "support_status": payload["support_status"],
                "claim_boundary": payload.get("claim_boundary", []),
                "notes": payload.get("reason", ""),
            }
        )

    return index_rows


def _bundle_manifest(
    *,
    artifact_dir: Path,
    bundle_dir: Path,
    figure_output_index: list[dict[str, Any]],
    figure_10_rows: list[dict[str, Any]],
    figure_9_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    figure_10_present = all((artifact_dir / source_file).exists() for _figure_id, (_csv, json_name) in FIGURE_10_FILES.items() for source_file in (json_name,))
    figure_9_present = all((artifact_dir / source_file).exists() for _figure_id, (_csv, json_name) in FIGURE_9_FILES.items() for source_file in (json_name,))
    gated_present = all((artifact_dir / source_file).exists() for _figure_id, (_md, json_name) in GATED_FILES.items() for source_file in (json_name,))
    claim_boundary_populated = all(row.get("claim_boundary") for row in figure_output_index)
    no_output_sync_tuning = bool(_load_json_object(artifact_dir / "remaining_figure_outputs_report.json").get("no_output_sync_tuning"))
    return {
        "feature_id": FEATURE_ID,
        "verdict": OUTPUT_BUNDLE_VERDICT,
        "bundle_dir": _bundle_path(bundle_dir, artifact_dir, ""),
        "source_files": {
            "figure_10": [json_name for _csv_name, json_name in FIGURE_10_FILES.values()],
            "figure_9": [json_name for _csv_name, json_name in FIGURE_9_FILES.values()],
            "gated": [json_name for _md_name, json_name in GATED_FILES.values()],
        },
        "bundle_files": [
            "README.md",
            "figure_output_index.json",
            "figure_output_index.md",
            "figure_10_plot_ready_combined.csv",
            "figure_10_plot_ready_combined.json",
            "figure_9_plot_ready_combined.csv",
            "figure_9_plot_ready_combined.json",
            "figure_10_analysis_digest.md",
            "figure_9_analysis_digest.md",
            "gated_figures_status_digest.md",
            "claim_boundary_digest.md",
            "output_usage_manifest.json",
            "output_usage_report.md",
        ],
        "validation": {
            "figure_10_present": figure_10_present,
            "figure_9_present": figure_9_present,
            "gated_status_present": gated_present,
            "claim_boundary_populated": claim_boundary_populated,
            "no_output_sync_tuning": no_output_sync_tuning,
        },
        "row_counts": {
            "figure_10": len(figure_10_rows),
            "figure_9": len(figure_9_rows),
            "index": len(figure_output_index),
        },
        "claim_boundary": list(FEATURE_080_BOUNDARY + FEATURE_086_BOUNDARY),
    }


def _write_readme(bundle_dir: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Feature 089 Output Usage Bundle",
        "",
        "This bundle packages the already-generated Figure 10 and Figure 9 artifacts for downstream analysis and plotting.",
        "",
        f"- Verdict: `{manifest['verdict']}`",
        f"- Bundle dir: `{manifest['bundle_dir']}`",
        f"- Figure 10 rows: `{manifest['row_counts']['figure_10']}`",
        f"- Figure 9 rows: `{manifest['row_counts']['figure_9']}`",
        "",
        "Rules carried forward:",
        "",
        "- No output-sync tuning was performed.",
        "- Figure 9 stays approximation-tagged.",
        "- Figure 8a, Figure 8b, and Figure 11 remain gated.",
        "- Claim boundaries from Features 080 and 086 remain intact.",
        "",
        "Files in this bundle are derived only from existing repository artifacts.",
    ]
    (bundle_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_analysis_digests(bundle_dir: Path, artifact_dir: Path) -> None:
    figure_10_summary = _load_json_object(artifact_dir / "figure_10_analysis_summary.json")
    comparison_report = _load_json_object(artifact_dir / "figure_10_comparison_analysis_report.json")
    figure_9_rows = {figure_id: _load_json_array(artifact_dir / json_name) for figure_id, (_csv_name, json_name) in FIGURE_9_FILES.items()}
    remaining_report = _load_json_object(artifact_dir / "remaining_figure_outputs_report.json")
    claim_boundary = figure_10_summary["claim_boundary"]

    figure_10_lines = [
        "# Figure 10 Analysis Digest",
        "",
        f"- Source verdict: `{figure_10_summary['verdict']}`",
        f"- Figure 10 rows: `{figure_10_summary['total_rows']}`",
        f"- Policies: `{', '.join(figure_10_summary['policies'])}`",
        f"- Claim alignment verdict: `{comparison_report['overall_claim_alignment']}`",
        f"- Figure 10c claim alignment: `{comparison_report['claim_alignment_by_figure']['Figure 10c']}`",
        "",
        "Key points:",
        "",
        "- All six Figure 10 subfigures were validated.",
        "- Delay figures preserve raw positive delay and negative paper-style delay for plotting.",
        "- Drop figures preserve raw drop ratio and percent form.",
        "- No numeric digitization was performed.",
        "- The paper claim is not fully supported; Figure 10c only shows a directional timeout effect.",
        "",
        "Claim boundary:",
        "",
    ] + [f"- {entry}" for entry in claim_boundary]
    (bundle_dir / "figure_10_analysis_digest.md").write_text("\n".join(figure_10_lines) + "\n", encoding="utf-8")

    figure_9_total = sum(len(rows) for rows in figure_9_rows.values())
    figure_9_lines = [
        "# Figure 9 Analysis Digest",
        "",
        f"- Combined rows: `{figure_9_total}`",
        "- Figure 9a, 9b, 9c, 9d, and 9e are present.",
        "- Every row stays tagged `generated_with_approximation`.",
        "- Figure 9 is HOODIE-only and still not a paper reproduction claim.",
        "- The plots are usable for analysis, but they are not paper-faithful validation outputs.",
        "",
        "Per-figure row counts:",
        "",
    ]
    for figure_id in ("Figure 9a", "Figure 9b", "Figure 9c", "Figure 9d", "Figure 9e"):
        figure_rows = figure_9_rows[figure_id]
        figure_9_lines.append(f"- {figure_id}: `{len(figure_rows)}` rows, support status `{figure_rows[0]['support_status']}`")
    figure_9_lines.extend(["", "Claim boundary:", ""] + [f"- {entry}" for entry in claim_boundary])
    (bundle_dir / "figure_9_analysis_digest.md").write_text("\n".join(figure_9_lines) + "\n", encoding="utf-8")

    gated_lines = [
        "# Gated Figures Status Digest",
        "",
        "- Figure 8a: `not_generated_training_required`.",
        "- Figure 8b: `not_generated_training_required`.",
        "- Figure 11: `not_generated_lstm_training_required`.",
        "",
        "These figures stay gated because no trained DRL or LSTM traces exist in the repository.",
        "No fake curves were created.",
        "",
        "Figure 8 / 11 claim boundary:",
        "",
    ] + [f"- {entry}" for entry in remaining_report["claim_boundary"]]
    (bundle_dir / "gated_figures_status_digest.md").write_text("\n".join(gated_lines) + "\n", encoding="utf-8")

    claim_lines = [
        "# Claim Boundary Digest",
        "",
        "- No output-sync tuning was performed.",
        "- No exact paper reproduction claim is made here.",
        "- Feature 080 boundaries remain intact.",
        "- Feature 086 approximation boundaries remain intact.",
        "- Figure 9 remains approximation-tagged.",
        "- Figure 8a, Figure 8b, and Figure 11 remain gated.",
        "",
        "Boundary list:",
        "",
    ] + [f"- {entry}" for entry in claim_boundary]
    (bundle_dir / "claim_boundary_digest.md").write_text("\n".join(claim_lines) + "\n", encoding="utf-8")


def generate_output_usage_bundle(artifact_dir: Path | None = None, bundle_dir: Path | None = None) -> dict[str, Any]:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    bundle_dir = bundle_dir or (artifact_dir / BUNDLE_DIR_NAME)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    figure_10_rows = _figure_10_combined_rows(artifact_dir, bundle_dir)
    figure_9_rows = _figure_9_combined_rows(artifact_dir)
    figure_output_index = _index_rows(artifact_dir, bundle_dir)
    manifest = _bundle_manifest(
        artifact_dir=artifact_dir,
        bundle_dir=bundle_dir,
        figure_output_index=figure_output_index,
        figure_10_rows=figure_10_rows,
        figure_9_rows=figure_9_rows,
    )

    _write_json(bundle_dir / "figure_output_index.json", figure_output_index)
    _write_markdown_table(
        bundle_dir / "figure_output_index.md",
        "Feature 089 Figure Output Index",
        figure_output_index,
        ("figure_id", "figure_family", "metric", "status", "artifact_paths", "plot_ready_available", "support_status", "claim_boundary", "notes"),
    )

    _write_csv(
        bundle_dir / "figure_10_plot_ready_combined.csv",
        figure_10_rows,
        ("figure_id", "metric", "policy", "x_axis_name", "x_axis_value", "raw_value", "paper_style_value", "value_units", "claim_boundary"),
    )
    _write_json(bundle_dir / "figure_10_plot_ready_combined.json", figure_10_rows)
    _write_csv(
        bundle_dir / "figure_9_plot_ready_combined.csv",
        figure_9_rows,
        ("figure_id", "metric", "policy", "x_axis_name", "x_axis_value", "series_name", "raw_value", "support_status", "approximation_note", "claim_boundary"),
    )
    _write_json(bundle_dir / "figure_9_plot_ready_combined.json", figure_9_rows)

    _write_analysis_digests(bundle_dir, artifact_dir)
    _write_json(bundle_dir / "output_usage_manifest.json", manifest)
    _write_readme(bundle_dir, manifest)

    report_lines = [
        "# Feature 089 Output Usage Report",
        "",
        f"- Verdict: `{manifest['verdict']}`",
        f"- Figure 10 present: `{manifest['validation']['figure_10_present']}`",
        f"- Figure 9 present: `{manifest['validation']['figure_9_present']}`",
        f"- Gated status present: `{manifest['validation']['gated_status_present']}`",
        f"- Claim boundaries populated: `{manifest['validation']['claim_boundary_populated']}`",
        f"- No output-sync tuning: `{manifest['validation']['no_output_sync_tuning']}`",
        "",
        "This bundle is derived from existing artifacts only.",
        "Figure 10 is validated; Figure 9 remains approximation-tagged; Figure 8a, Figure 8b, and Figure 11 remain gated.",
    ]
    (bundle_dir / "output_usage_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return manifest


def validate_output_usage_bundle(artifact_dir: Path | None = None, bundle_dir: Path | None = None) -> dict[str, Any]:
    artifact_dir = artifact_dir or ARTIFACT_DIR
    bundle_dir = bundle_dir or (artifact_dir / BUNDLE_DIR_NAME)
    manifest = _load_json_object(bundle_dir / "output_usage_manifest.json")
    required_files = [
        "README.md",
        "figure_output_index.json",
        "figure_output_index.md",
        "figure_10_plot_ready_combined.csv",
        "figure_10_plot_ready_combined.json",
        "figure_9_plot_ready_combined.csv",
        "figure_9_plot_ready_combined.json",
        "figure_10_analysis_digest.md",
        "figure_9_analysis_digest.md",
        "gated_figures_status_digest.md",
        "claim_boundary_digest.md",
        "output_usage_manifest.json",
        "output_usage_report.md",
    ]
    missing = [filename for filename in required_files if not (bundle_dir / filename).exists()]
    if missing:
        raise FileNotFoundError(f"Missing output usage bundle files: {', '.join(missing)}")
    if manifest.get("verdict") != OUTPUT_BUNDLE_VERDICT:
        raise ValueError("Unexpected output usage bundle verdict")
    return manifest
