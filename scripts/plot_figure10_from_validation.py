from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


BASELINE_POLICIES = ["RO", "FLC", "VO", "HO", "BCO", "MLEO"]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    return json.loads(path.read_text())


def _load_summary_rows(input_dir: Path) -> list[dict[str, Any]]:
    summary = _load_json(input_dir / "figure10_policy_metrics_summary.json")
    rows = summary.get("summary_rows", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError("figure10_policy_metrics_summary.json must contain non-empty summary_rows")
    return rows


def _load_readiness(input_dir: Path) -> dict[str, Any]:
    return _load_json(input_dir / "figure10_policy_readiness.json")


def _validate_input(input_dir: Path, summary_rows: list[dict[str, Any]], readiness: dict[str, Any]) -> None:
    if not input_dir.exists():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    required = [
        input_dir / "figure10_policy_metrics_summary.json",
        input_dir / "figure10_policy_readiness.json",
        input_dir / "figure10_validation_manifest.json",
        input_dir / "figure10_run_config_snapshot.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required validation files: {missing}")
    plotted_policies = {row.get("policy_name") for row in summary_rows}
    missing_policies = [policy for policy in BASELINE_POLICIES if policy not in plotted_policies]
    if missing_policies:
        raise ValueError(f"missing baseline policies in summary_rows: {missing_policies}")
    if "HOODIE" in plotted_policies:
        raise ValueError("HOODIE must not be plotted in baseline-only mode")
    regimes = {row.get("regime_id") for row in summary_rows}
    if not {"delay", "drop_ratio"}.issubset(regimes):
        raise ValueError(f"missing required regimes: expected delay and drop_ratio, observed {sorted(regimes)}")
    for regime_id in ("delay", "drop_ratio"):
        regime_policies = {row.get("policy_name") for row in summary_rows if row.get("regime_id") == regime_id}
        missing_regime_policies = [policy for policy in BASELINE_POLICIES if policy not in regime_policies]
        if missing_regime_policies:
            raise ValueError(
                f"missing baseline policies in {regime_id} regime: {missing_regime_policies}"
            )
    for row in summary_rows:
        for key in ("mean_average_computation_delay", "mean_drop_ratio"):
            if row.get(key) is None:
                raise ValueError(f"missing plotted metric {key} for row {row}")
    if readiness.get("figure10_data_ready") is True:
        return


def _policy_rows(summary_rows: list[dict[str, Any]], regime_id: str) -> list[dict[str, Any]]:
    rows = [row for row in summary_rows if row.get("regime_id") == regime_id]
    rows.sort(key=lambda row: BASELINE_POLICIES.index(row.get("policy_name")))
    return rows


def _plot_metric(ax, rows: list[dict[str, Any]], metric_key: str, title: str, ylabel: str) -> None:
    x = [row["policy_name"] for row in rows]
    y = [row[metric_key] for row in rows]
    ax.bar(x, y, color="#4C78A8")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)


def _build_metadata(
    *,
    input_dir: Path,
    output_dir: Path,
    label: str,
    summary_rows: list[dict[str, Any]],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    manifest = _load_json(input_dir / "figure10_validation_manifest.json")
    summary = _load_json(input_dir / "figure10_policy_metrics_summary.json")
    run_config = _load_json(input_dir / "figure10_run_config_snapshot.json")
    policies = sorted({row.get("policy_name") for row in summary_rows if row.get("policy_name") != "HOODIE"})
    regimes = sorted({row.get("regime_id") for row in summary_rows})
    runtime_parameter_diagnostics = summary.get("runtime_parameter_diagnostics") or run_config.get(
        "runtime_parameter_diagnostics", []
    )
    return {
        "plot_scope": "baseline_validation_only",
        "figure_claim": "not_full_official_figure10",
        "hoodie_included": False,
        "hoodie_reason": "trained HOODIE checkpoint unavailable",
        "simulation_rerun": False,
        "source_input_dir": str(input_dir),
        "source_files": {
            "summary_json": str(input_dir / "figure10_policy_metrics_summary.json"),
            "readiness_json": str(input_dir / "figure10_policy_readiness.json"),
            "manifest_json": str(input_dir / "figure10_validation_manifest.json"),
            "run_config_snapshot": str(input_dir / "figure10_run_config_snapshot.json"),
        },
        "output_dir": str(output_dir),
        "output_files": {
            "delay_png": str(output_dir / "figure10_baseline_delay.png"),
            "drop_ratio_png": str(output_dir / "figure10_baseline_drop_ratio.png"),
            "combined_png": str(output_dir / "figure10_baseline_combined.png"),
            "metadata_json": str(output_dir / "figure10_baseline_plot_metadata.json"),
        },
        "label": label,
        "policies_plotted": policies,
        "regimes_plotted": regimes,
        "baseline_validation_ready": readiness.get("baseline_validation_ready"),
        "figure10_data_ready": readiness.get("figure10_data_ready"),
        "runtime_parameter_diagnostics": runtime_parameter_diagnostics,
        "warning": "Runtime parameter diagnostics exist; this plot must not be presented as paper-faithful final reproduction.",
        "paper_performance_claims_made": False,
        "manifest_diagnostic_only": manifest.get("diagnostic_only"),
        "run_config_snapshot": run_config,
        "readiness_snapshot": readiness,
    }


def generate_plots(input_dir: str | Path, output_dir: str | Path, label: str) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = _load_json(input_dir / "figure10_policy_metrics_summary.json")
    readiness = _load_readiness(input_dir)
    summary_rows = _load_summary_rows(input_dir)
    _validate_input(input_dir, summary_rows, readiness)

    delay_rows = _policy_rows(summary_rows, "delay")
    drop_rows = _policy_rows(summary_rows, "drop_ratio")

    delay_fig, delay_ax = plt.subplots(figsize=(8, 4.5))
    _plot_metric(
        delay_ax,
        delay_rows,
        "mean_average_computation_delay",
        "Baseline validation only - delay regime - HOODIE not included",
        "Mean computation delay",
    )
    delay_fig.suptitle("Baseline validation only - HOODIE not included", fontsize=12, y=1.02)
    delay_fig.tight_layout()
    delay_fig.savefig(output_dir / "figure10_baseline_delay.png", dpi=200, bbox_inches="tight")
    plt.close(delay_fig)

    drop_fig, drop_ax = plt.subplots(figsize=(8, 4.5))
    _plot_metric(
        drop_ax,
        drop_rows,
        "mean_drop_ratio",
        "Baseline validation only - drop-ratio regime - HOODIE not included",
        "Mean drop ratio",
    )
    drop_fig.suptitle("Baseline validation only - HOODIE not included", fontsize=12, y=1.02)
    drop_fig.tight_layout()
    drop_fig.savefig(output_dir / "figure10_baseline_drop_ratio.png", dpi=200, bbox_inches="tight")
    plt.close(drop_fig)

    combined_fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    _plot_metric(
        axes[0],
        delay_rows,
        "mean_average_computation_delay",
        "Delay regime - Baseline validation only - HOODIE not included",
        "Mean computation delay",
    )
    _plot_metric(
        axes[1],
        drop_rows,
        "mean_drop_ratio",
        "Drop-ratio regime - Baseline validation only - HOODIE not included",
        "Mean drop ratio",
    )
    axes[1].set_xlabel("Policy")
    combined_fig.suptitle("Baseline validation only - HOODIE not included", fontsize=13, y=0.995)
    combined_fig.tight_layout()
    combined_fig.savefig(output_dir / "figure10_baseline_combined.png", dpi=200, bbox_inches="tight")
    plt.close(combined_fig)

    metadata = _build_metadata(
        input_dir=input_dir,
        output_dir=output_dir,
        label=label,
        summary_rows=summary_rows,
        readiness=readiness,
    )
    (output_dir / "figure10_baseline_plot_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--label", default="baseline-validation-only")
    args = parser.parse_args(argv)
    generate_plots(args.input_dir, args.output_dir, args.label)
    print(f"plot metadata written to {Path(args.output_dir) / 'figure10_baseline_plot_metadata.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
