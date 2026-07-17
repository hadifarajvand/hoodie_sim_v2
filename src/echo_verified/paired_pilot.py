from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Iterable, Sequence
import zipfile

from .kernel import (
    EpisodeResult,
    PairedPhysicalKernel,
    PilotKernelConfig,
    assert_echo_disabled_equivalence,
    episode_result_to_dict,
    generate_trace,
)

PILOT_LABEL = "PAIRED PILOT — NOT PAPER EVIDENCE"
METHODS = ("HOODIE", "ECHO", "ECHO_DISABLED")
DISPLAY_METHODS = ("HOODIE", "ECHO")

SOURCE_LOCK = {
    "echo_tex": {
        "name": "02_ECHO-Article_Current.tex",
        "drive_id": "12fZMZaQykmVJNf3valU4unTQDCQOt9uX",
        "sha256": "636688a47e5cc6185637394192cb98e205eb4baa80f50c64204639b56e82af84",
        "role": "highest_authority",
    },
    "echo_source_zip": {
        "name": "03_ECHO-Article_Current_Source.zip",
        "drive_id": "1KjES9k1VTcuCtdWG7yMox6N1hFlkjt1O",
        "sha256": "6b0e2b1ebaba26fc00ec2759199024323ae0199f5a56c36b8193d2aca6cdbcfa",
        "role": "supporting_source_archive",
    },
    "hoodie_paper": {
        "name": "HOODIE_paper.pdf",
        "drive_id": "13S2Noql_zbeeGoAa5D_S0uK3wgxaimdm",
        "sha256": "362ad3c4f61a69211a572fda6b9238bfeae00686b41233ebc70cbdd19bf558f4",
        "role": "inherited_mechanics_authority",
    },
}

SCENARIOS = {
    "moderate": {
        "arrival_probability": 0.50,
        "timeout_slots": 20,
        "decision_slots": 30,
        "drain_slots": 20,
    },
    "high_tight": {
        "arrival_probability": 0.80,
        "timeout_slots": 8,
        "decision_slots": 30,
        "drain_slots": 20,
    },
}


def _git_sha() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return completed.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable-local-pilot"


def _write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _t_critical_95(df: int) -> float:
    values = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
        16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
        26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
    }
    return values.get(df, 1.96)


def _mean_ci(
    values: Sequence[float], *, lower_bound: float | None = None, upper_bound: float | None = None
) -> tuple[float, float, float]:
    if not values:
        raise ValueError("cannot aggregate an empty series")
    mean = statistics.fmean(values)
    if len(values) == 1:
        return mean, mean, mean
    standard_error = statistics.stdev(values) / math.sqrt(len(values))
    margin = _t_critical_95(len(values) - 1) * standard_error
    low = mean - margin
    high = mean + margin
    if lower_bound is not None:
        low = max(lower_bound, low)
    if upper_bound is not None:
        high = min(upper_bound, high)
    return mean, low, high


def _group_rows(
    rows: Iterable[dict[str, object]], keys: Sequence[str]
) -> dict[tuple[object, ...], list[dict[str, object]]]:
    groups: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = tuple(row[name] for name in keys)
        groups.setdefault(key, []).append(row)
    return groups


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_figures(
    output_root: Path,
    seed_rows: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    import matplotlib.pyplot as plt

    exports: list[dict[str, object]] = []
    for metric, ylabel, stem in (
        ("drop_ratio", "Task-drop ratio", "pilot_drop_ratio"),
        (
            "average_successful_delay_seconds",
            "Successful-task delay (s)",
            "pilot_successful_delay",
        ),
    ):
        scenarios = list(SCENARIOS)
        x = list(range(len(scenarios)))
        width = 0.34
        fig, axis = plt.subplots(figsize=(7.2, 4.4))
        for offset_index, method in enumerate(DISPLAY_METHODS):
            means: list[float] = []
            lower_errors: list[float] = []
            upper_errors: list[float] = []
            for scenario in scenarios:
                values = [
                    float(row[metric])
                    for row in seed_rows
                    if row["scenario"] == scenario and row["method"] == method
                ]
                bounded = metric in {"drop_ratio"}
                mean, low, high = _mean_ci(
                    values,
                    lower_bound=0.0 if bounded else None,
                    upper_bound=1.0 if bounded else None,
                )
                means.append(mean)
                lower_errors.append(mean - low)
                upper_errors.append(high - mean)
            positions = [value + (offset_index - 0.5) * width for value in x]
            axis.bar(
                positions,
                means,
                width=width,
                label=method,
                yerr=[lower_errors, upper_errors],
                capsize=4,
            )
        axis.set_xticks(x, scenarios)
        axis.set_ylabel(ylabel)
        axis.set_title(PILOT_LABEL)
        axis.legend()
        axis.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        for suffix, kwargs in (
            ("pdf", {}),
            ("svg", {}),
            ("png", {"dpi": 300}),
        ):
            path = output_root / "figures" / f"{stem}.{suffix}"
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, **kwargs)
            exports.append(
                {
                    "path": str(path.relative_to(output_root)),
                    "sha256": _hash_file(path),
                    "bytes": path.stat().st_size,
                }
            )
        plt.close(fig)
    return exports


def _zip_tree(output_root: Path) -> Path:
    archive = output_root.parent / f"{output_root.name}.zip"
    temporary = archive.with_suffix(".zip.tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(output_root.rglob("*")):
            if path.is_file():
                handle.write(path, path.relative_to(output_root.parent))
    temporary.replace(archive)
    return archive


def run_paired_pilot(
    *,
    output_root: Path,
    seeds: Sequence[int] = (101, 202, 303),
    episodes_per_seed: int = 6,
) -> dict[str, object]:
    if episodes_per_seed <= 0:
        raise ValueError("episodes_per_seed must be positive")
    if len(set(seeds)) != len(seeds) or not seeds:
        raise ValueError("seeds must be non-empty and unique")

    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise ValueError(f"output root must be empty: {output_root}")

    task_rows: list[dict[str, object]] = []
    episode_rows: list[dict[str, object]] = []
    raw_results: list[dict[str, object]] = []
    equivalence_checks = 0

    for scenario, settings in SCENARIOS.items():
        config = PilotKernelConfig(
            decision_slots=int(settings["decision_slots"]),
            drain_slots=int(settings["drain_slots"]),
        )
        for seed in seeds:
            for episode_index in range(episodes_per_seed):
                trace_id = f"{scenario}-seed-{seed}-episode-{episode_index:03d}"
                blueprints = generate_trace(
                    seed=seed,
                    episode_index=episode_index,
                    scenario=scenario,
                    config=config,
                    arrival_probability=float(settings["arrival_probability"]),
                    timeout_slots=int(settings["timeout_slots"]),
                )
                by_method: dict[str, EpisodeResult] = {}
                for method in METHODS:
                    result = PairedPhysicalKernel(
                        method=method,  # type: ignore[arg-type]
                        trace_id=trace_id,
                        seed=seed,
                        scenario=scenario,
                        blueprints=blueprints,
                        config=config,
                    ).run()
                    by_method[method] = result
                    raw_results.append(episode_result_to_dict(result))
                    for row in result.tasks:
                        task_rows.append(
                            {
                                "pilot_label": PILOT_LABEL,
                                "episode_index": episode_index,
                                **row,
                            }
                        )
                    episode_rows.append(
                        {
                            "pilot_label": PILOT_LABEL,
                            "trace_id": trace_id,
                            "scenario": scenario,
                            "seed": seed,
                            "episode_index": episode_index,
                            "method": method,
                            **result.metrics,
                            **result.diagnostics,
                        }
                    )
                assert_echo_disabled_equivalence(
                    by_method["HOODIE"], by_method["ECHO_DISABLED"]
                )
                equivalence_checks += 1
                task_ids = {
                    method: tuple(row["task_id"] for row in by_method[method].tasks)
                    for method in METHODS
                }
                if len(set(task_ids.values())) != 1:
                    raise AssertionError("paired methods did not receive identical task IDs")

    seed_rows: list[dict[str, object]] = []
    for (scenario, seed, method), rows in sorted(
        _group_rows(episode_rows, ("scenario", "seed", "method")).items()
    ):
        generated = sum(int(row["generated"]) for row in rows)
        successful = sum(int(row["successful"]) for row in rows)
        dropped = sum(int(row["dropped"]) for row in rows)
        if generated != successful + dropped:
            raise AssertionError("seed-level task conservation failed")
        successful_delays = [
            float(task["successful_delay_seconds"])
            for task in task_rows
            if task["scenario"] == scenario
            and task["seed"] == seed
            and task["method"] == method
            and task["successful_delay_seconds"] is not None
        ]
        seed_rows.append(
            {
                "pilot_label": PILOT_LABEL,
                "scenario": scenario,
                "seed": seed,
                "method": method,
                "episodes": len(rows),
                "generated": generated,
                "successful": successful,
                "dropped": dropped,
                "drop_ratio": dropped / generated if generated else 0.0,
                "average_successful_delay_seconds": (
                    statistics.fmean(successful_delays) if successful_delays else 0.0
                ),
                "accumulated_reward": sum(
                    float(row["accumulated_reward"]) for row in rows
                ),
                "route_filter_fraction": statistics.fmean(
                    float(row["route_filter_fraction"]) for row in rows
                ),
                "fallback_frequency": statistics.fmean(
                    float(row["fallback_frequency"]) for row in rows
                ),
                "source_queue_order_difference_fraction": statistics.fmean(
                    float(row["source_queue_order_difference_fraction"])
                    for row in rows
                ),
                "completion_estimation_mae_slots": statistics.fmean(
                    float(row["completion_estimation_mae_slots"]) for row in rows
                ),
                "mean_route_control_ns_per_arrival": statistics.fmean(
                    float(row["mean_route_control_ns_per_arrival"]) for row in rows
                ),
                "mean_queue_control_ns_per_opportunity": statistics.fmean(
                    float(row["mean_queue_control_ns_per_opportunity"])
                    for row in rows
                ),
            }
        )

    aggregate_rows: list[dict[str, object]] = []
    for (scenario, method), rows in sorted(
        _group_rows(seed_rows, ("scenario", "method")).items()
    ):
        for metric in (
            "drop_ratio",
            "average_successful_delay_seconds",
            "route_filter_fraction",
            "fallback_frequency",
            "source_queue_order_difference_fraction",
            "completion_estimation_mae_slots",
            "mean_route_control_ns_per_arrival",
            "mean_queue_control_ns_per_opportunity",
        ):
            bounded = metric in {
                "drop_ratio",
                "route_filter_fraction",
                "fallback_frequency",
                "source_queue_order_difference_fraction",
            }
            mean, low, high = _mean_ci(
                [float(row[metric]) for row in rows],
                lower_bound=0.0 if bounded else None,
                upper_bound=1.0 if bounded else None,
            )
            aggregate_rows.append(
                {
                    "pilot_label": PILOT_LABEL,
                    "scenario": scenario,
                    "method": method,
                    "metric": metric,
                    "seed_count": len(rows),
                    "mean": mean,
                    "ci95_low": low,
                    "ci95_high": high,
                }
            )

    paired_rows: list[dict[str, object]] = []
    seed_by_key = {
        (str(row["scenario"]), int(row["seed"]), str(row["method"])): row
        for row in seed_rows
    }
    for scenario in SCENARIOS:
        for seed in seeds:
            echo = seed_by_key[(scenario, seed, "ECHO")]
            hoodie = seed_by_key[(scenario, seed, "HOODIE")]
            paired_rows.append(
                {
                    "pilot_label": PILOT_LABEL,
                    "scenario": scenario,
                    "seed": seed,
                    "echo_drop_ratio": echo["drop_ratio"],
                    "hoodie_drop_ratio": hoodie["drop_ratio"],
                    "drop_ratio_echo_minus_hoodie": float(echo["drop_ratio"])
                    - float(hoodie["drop_ratio"]),
                    "echo_successful_delay_seconds": echo[
                        "average_successful_delay_seconds"
                    ],
                    "hoodie_successful_delay_seconds": hoodie[
                        "average_successful_delay_seconds"
                    ],
                    "delay_echo_minus_hoodie_seconds": float(
                        echo["average_successful_delay_seconds"]
                    )
                    - float(hoodie["average_successful_delay_seconds"]),
                    "echo_generated": echo["generated"],
                    "echo_successful": echo["successful"],
                    "echo_dropped": echo["dropped"],
                    "hoodie_generated": hoodie["generated"],
                    "hoodie_successful": hoodie["successful"],
                    "hoodie_dropped": hoodie["dropped"],
                }
            )

    _write_csv(output_root / "data" / "task_records.csv", task_rows)
    _write_csv(output_root / "data" / "episode_metrics.csv", episode_rows)
    _write_csv(output_root / "data" / "seed_metrics.csv", seed_rows)
    _write_csv(output_root / "data" / "aggregate_metrics.csv", aggregate_rows)
    _write_csv(output_root / "data" / "paired_differences.csv", paired_rows)
    _write_json(output_root / "data" / "raw_episode_results.json", raw_results)

    figure_exports = _write_figures(output_root, seed_rows)
    code_sha = _git_sha()
    generated = sum(int(row["generated"]) for row in seed_rows if row["method"] == "HOODIE")
    manifest: dict[str, object] = {
        "label": PILOT_LABEL,
        "status": "PAIRED_PHYSICAL_KERNEL_PILOT_PASSED",
        "paper_evidence": False,
        "paper_scale_started": False,
        "full_drl_training_performed": False,
        "purpose": "physical lifecycle and ECHO-control integration gate",
        "code_commit": code_sha,
        "source_lock": SOURCE_LOCK,
        "methods": list(METHODS),
        "scenarios": SCENARIOS,
        "seeds": list(seeds),
        "episodes_per_seed": episodes_per_seed,
        "paired_trace_identity": True,
        "echo_disabled_equivalence_checks": equivalence_checks,
        "echo_disabled_equivalence_passed": True,
        "task_conservation_passed": True,
        "paired_hoodie_task_count": generated,
        "destination_fifo": True,
        "equal_destination_capacity_sharing": True,
        "source_service_non_preemptive": True,
        "next_slot_destination_admission": True,
        "deadline_slot_completion_is_success": True,
        "ert_in_neural_observation": False,
        "projected_or_surrogate_values_used": False,
        "figures": figure_exports,
        "limitations": [
            "This bounded pilot uses a shared deterministic Q-value proxy, not trained Dueling Double-DQN checkpoints.",
            "It validates physical lifecycle and isolated ECHO controls only.",
            "It must not replace manuscript Figures 5–8 or support superiority claims.",
            "Publication evidence remains blocked on HOODIE learner validation, full ECHO integration, paired training, and the locked 10-seed x 200-held-out-episode campaign.",
        ],
    }
    _write_json(output_root / "manifest.json", manifest)

    report_lines = [
        f"# {PILOT_LABEL}",
        "",
        "This output is an executable integration gate, not publication evidence.",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Seeds: {', '.join(str(seed) for seed in seeds)}",
        f"- Episodes per seed and scenario: {episodes_per_seed}",
        f"- ECHO-disabled equivalence checks: {equivalence_checks}",
        "- Projected/surrogate values used: no",
        "- Full DRL training performed: no",
        "",
        "## Seed-level paired differences",
        "",
        "| Scenario | Seed | Δ drop ratio (ECHO−HOODIE) | Δ successful delay, s |",
        "|---|---:|---:|---:|",
    ]
    for row in paired_rows:
        report_lines.append(
            f"| {row['scenario']} | {row['seed']} | "
            f"{float(row['drop_ratio_echo_minus_hoodie']):.6f} | "
            f"{float(row['delay_echo_minus_hoodie_seconds']):.6f} |"
        )
    report_lines.extend(
        [
            "",
            "## Scientific boundary",
            "",
            *[f"- {item}" for item in manifest["limitations"]],  # type: ignore[index]
        ]
    )
    (output_root / "REPORT.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    files = []
    for path in sorted(output_root.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": str(path.relative_to(output_root)),
                    "bytes": path.stat().st_size,
                    "sha256": _hash_file(path),
                }
            )
    manifest["files"] = files
    _write_json(output_root / "manifest.json", manifest)
    archive = _zip_tree(output_root)
    archive_sha = _hash_file(archive)
    sidecar = archive.with_suffix(archive.suffix + ".sha256")
    sidecar.write_text(f"{archive_sha}  {archive.name}\n", encoding="utf-8")
    manifest["archive_external"] = {
        "path": str(archive),
        "bytes": archive.stat().st_size,
        "sha256": archive_sha,
        "sha256_sidecar": str(sidecar),
        "note": "The archive hash is external because an archive cannot contain its own final hash.",
    }
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seeds", default="101,202,303")
    parser.add_argument("--episodes-per-seed", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seeds = tuple(int(value.strip()) for value in args.seeds.split(",") if value.strip())
    result = run_paired_pilot(
        output_root=args.output_root,
        seeds=seeds,
        episodes_per_seed=args.episodes_per_seed,
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
