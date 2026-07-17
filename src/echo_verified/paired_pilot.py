from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
import math
import os
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
    },
    "echo_source_zip": {
        "name": "03_ECHO-Article_Current_Source.zip",
        "drive_id": "1KjES9k1VTcuCtdWG7yMox6N1hFlkjt1O",
        "sha256": "6b0e2b1ebaba26fc00ec2759199024323ae0199f5a56c36b8193d2aca6cdbcfa",
    },
    "hoodie_paper": {
        "name": "HOODIE_paper.pdf",
        "drive_id": "13S2Noql_zbeeGoAa5D_S0uK3wgxaimdm",
        "sha256": "362ad3c4f61a69211a572fda6b9238bfeae00686b41233ebc70cbdd19bf558f4",
    },
}
SCENARIOS = {
    "moderate": {"arrival_probability": 0.50, "timeout_slots": 20},
    "high_tight": {"arrival_probability": 0.80, "timeout_slots": 8},
}


def _git_sha() -> str:
    override = os.environ.get("ECHO_CODE_SHA", "").strip()
    if override:
        return override
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable-local-pilot"


def _json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty CSV refused: {path}")
    fields: list[str] = []
    for row in rows:
        fields.extend(key for key in row if key not in fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def _sha(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _groups(rows: Iterable[dict[str, object]], *keys: str):
    result: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        result.setdefault(tuple(row[key] for key in keys), []).append(row)
    return result


def _ci(values: Sequence[float], bounded: bool = False) -> tuple[float, float, float]:
    mean = statistics.fmean(values)
    if len(values) == 1:
        return mean, mean, mean
    critical = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}.get(len(values)-1, 1.96)
    margin = critical * statistics.stdev(values) / math.sqrt(len(values))
    low, high = mean - margin, mean + margin
    if bounded:
        low, high = max(0.0, low), min(1.0, high)
    return mean, low, high


def _figures(root: Path, seed_rows: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    import matplotlib.pyplot as plt
    exports: list[dict[str, object]] = []
    for metric, ylabel, stem in (
        ("drop_ratio", "Task-drop ratio", "pilot_drop_ratio"),
        ("average_successful_delay_seconds", "Successful-task delay (s)", "pilot_successful_delay"),
    ):
        fig, axis = plt.subplots(figsize=(7.2, 4.4)); width = 0.34
        for method_index, method in enumerate(DISPLAY_METHODS):
            means, lows, highs = [], [], []
            for scenario in SCENARIOS:
                values = [float(row[metric]) for row in seed_rows if row["scenario"] == scenario and row["method"] == method]
                mean, low, high = _ci(values, bounded=metric == "drop_ratio")
                means.append(mean); lows.append(mean-low); highs.append(high-mean)
            positions = [index + (method_index - 0.5) * width for index in range(len(SCENARIOS))]
            axis.bar(positions, means, width=width, label=method, yerr=[lows, highs], capsize=4)
        axis.set_xticks(range(len(SCENARIOS)), list(SCENARIOS)); axis.set_ylabel(ylabel)
        axis.set_title(PILOT_LABEL); axis.legend(); axis.grid(axis="y", alpha=0.25); fig.tight_layout()
        for extension, options in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300})):
            path = root / "figures" / f"{stem}.{extension}"; path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, **options)
            exports.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": _sha(path)})
        plt.close(fig)
    return exports


def _archive(root: Path) -> dict[str, object]:
    archive = root.parent / f"{root.name}.zip"; temporary = archive.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                handle.write(path, path.relative_to(root.parent))
    temporary.replace(archive); digest = _sha(archive)
    sidecar = archive.with_suffix(".zip.sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return {"path": str(archive), "bytes": archive.stat().st_size, "sha256": digest, "sha256_sidecar": str(sidecar)}


def run_paired_pilot(*, output_root: Path, seeds: Sequence[int] = (101, 202, 303), episodes_per_seed: int = 6) -> dict[str, object]:
    if episodes_per_seed <= 0 or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("episodes must be positive and seeds non-empty/unique")
    root = output_root.expanduser().resolve(); root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError(f"output root must be empty: {root}")
    tasks: list[dict[str, object]] = []; episodes: list[dict[str, object]] = []; raw: list[dict[str, object]] = []
    equivalence_checks = 0
    for scenario, settings in SCENARIOS.items():
        config = PilotKernelConfig(decision_slots=30, drain_slots=20)
        for seed in seeds:
            for episode_index in range(episodes_per_seed):
                trace_id = f"{scenario}-seed-{seed}-episode-{episode_index:03d}"
                blueprints = generate_trace(
                    seed=seed, episode_index=episode_index, scenario=scenario, config=config,
                    arrival_probability=float(settings["arrival_probability"]), timeout_slots=int(settings["timeout_slots"]),
                )
                results: dict[str, EpisodeResult] = {}
                for method in METHODS:
                    result = PairedPhysicalKernel(
                        method=method, trace_id=trace_id, seed=seed, scenario=scenario,
                        blueprints=blueprints, config=config,
                    ).run()  # type: ignore[arg-type]
                    results[method] = result; raw.append(episode_result_to_dict(result))
                    tasks.extend({"pilot_label": PILOT_LABEL, "episode_index": episode_index, **row} for row in result.tasks)
                    episodes.append({
                        "pilot_label": PILOT_LABEL, "trace_id": trace_id, "scenario": scenario,
                        "seed": seed, "episode_index": episode_index, "method": method,
                        **result.metrics, **result.diagnostics,
                    })
                assert_echo_disabled_equivalence(results["HOODIE"], results["ECHO_DISABLED"])
                equivalence_checks += 1
                if len({tuple(row["task_id"] for row in results[method].tasks) for method in METHODS}) != 1:
                    raise AssertionError("paired task identities differ")

    seed_rows: list[dict[str, object]] = []
    for (scenario, seed, method), rows in sorted(_groups(episodes, "scenario", "seed", "method").items()):
        generated = sum(int(row["generated"]) for row in rows); successful = sum(int(row["successful"]) for row in rows)
        dropped = sum(int(row["dropped"]) for row in rows)
        if generated != successful + dropped:
            raise AssertionError("seed task conservation failed")
        delays = [float(row["successful_delay_seconds"]) for row in tasks if row["scenario"] == scenario and row["seed"] == seed and row["method"] == method and row["successful_delay_seconds"] is not None]
        seed_rows.append({
            "pilot_label": PILOT_LABEL, "scenario": scenario, "seed": seed, "method": method,
            "episodes": len(rows), "generated": generated, "successful": successful, "dropped": dropped,
            "drop_ratio": dropped/generated if generated else 0.0,
            "average_successful_delay_seconds": statistics.fmean(delays) if delays else 0.0,
            "accumulated_reward": sum(float(row["accumulated_reward"]) for row in rows),
            **{metric: statistics.fmean(float(row[metric]) for row in rows) for metric in (
                "route_filter_fraction", "fallback_frequency", "source_queue_order_difference_fraction",
                "completion_estimation_mae_slots", "mean_route_control_ns_per_arrival",
                "mean_queue_control_ns_per_opportunity",
            )},
        })

    aggregate: list[dict[str, object]] = []
    metrics = (
        "drop_ratio", "average_successful_delay_seconds", "route_filter_fraction", "fallback_frequency",
        "source_queue_order_difference_fraction", "completion_estimation_mae_slots",
        "mean_route_control_ns_per_arrival", "mean_queue_control_ns_per_opportunity",
    )
    bounded = {"drop_ratio", "route_filter_fraction", "fallback_frequency", "source_queue_order_difference_fraction"}
    for (scenario, method), rows in sorted(_groups(seed_rows, "scenario", "method").items()):
        for metric in metrics:
            mean, low, high = _ci([float(row[metric]) for row in rows], bounded=metric in bounded)
            aggregate.append({"pilot_label": PILOT_LABEL, "scenario": scenario, "method": method, "metric": metric, "seed_count": len(rows), "mean": mean, "ci95_low": low, "ci95_high": high})

    indexed = {(row["scenario"], row["seed"], row["method"]): row for row in seed_rows}
    paired: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        for seed in seeds:
            echo, hoodie = indexed[(scenario, seed, "ECHO")], indexed[(scenario, seed, "HOODIE")]
            paired.append({
                "pilot_label": PILOT_LABEL, "scenario": scenario, "seed": seed,
                "echo_drop_ratio": echo["drop_ratio"], "hoodie_drop_ratio": hoodie["drop_ratio"],
                "drop_ratio_echo_minus_hoodie": float(echo["drop_ratio"])-float(hoodie["drop_ratio"]),
                "echo_successful_delay_seconds": echo["average_successful_delay_seconds"],
                "hoodie_successful_delay_seconds": hoodie["average_successful_delay_seconds"],
                "delay_echo_minus_hoodie_seconds": float(echo["average_successful_delay_seconds"])-float(hoodie["average_successful_delay_seconds"]),
                **{f"echo_{key}": echo[key] for key in ("generated", "successful", "dropped")},
                **{f"hoodie_{key}": hoodie[key] for key in ("generated", "successful", "dropped")},
            })

    _csv(root/"data/task_records.csv", tasks); _csv(root/"data/episode_metrics.csv", episodes)
    _csv(root/"data/seed_metrics.csv", seed_rows); _csv(root/"data/aggregate_metrics.csv", aggregate)
    _csv(root/"data/paired_differences.csv", paired); _json(root/"data/raw_episode_results.json", raw)
    figures = _figures(root, seed_rows)
    limitations = [
        "Uses a shared deterministic Q-value proxy, not trained Dueling Double-DQN checkpoints.",
        "Validates physical lifecycle and isolated ECHO controls only.",
        "Must not replace manuscript Figures 5–8 or support superiority claims.",
        "Publication evidence remains blocked on full HOODIE learner validation and the locked campaign.",
    ]
    manifest: dict[str, object] = {
        "label": PILOT_LABEL, "status": "PAIRED_PHYSICAL_KERNEL_PILOT_PASSED",
        "paper_evidence": False, "paper_scale_started": False, "full_drl_training_performed": False,
        "code_commit": _git_sha(), "source_lock": SOURCE_LOCK, "methods": list(METHODS),
        "scenarios": SCENARIOS, "seeds": list(seeds), "episodes_per_seed": episodes_per_seed,
        "paired_trace_identity": True, "echo_disabled_equivalence_checks": equivalence_checks,
        "echo_disabled_equivalence_passed": True, "task_conservation_passed": True,
        "destination_fifo": True, "equal_destination_capacity_sharing": True,
        "source_service_non_preemptive": True, "next_slot_destination_admission": True,
        "deadline_slot_completion_is_success": True, "ert_in_neural_observation": False,
        "projected_or_surrogate_values_used": False, "figures": figures, "limitations": limitations,
    }
    report = [f"# {PILOT_LABEL}", "", "Executable integration gate; not publication evidence.", "",
              f"- Status: `{manifest['status']}`", f"- ECHO-disabled checks: {equivalence_checks}",
              "- Projected/surrogate values used: no", "", "## Paired differences", "",
              "| Scenario | Seed | Δ drop ratio | Δ successful delay (s) |", "|---|---:|---:|---:|"]
    report.extend(f"| {row['scenario']} | {row['seed']} | {float(row['drop_ratio_echo_minus_hoodie']):.6f} | {float(row['delay_echo_minus_hoodie_seconds']):.6f} |" for row in paired)
    report.extend(["", "## Limitations", "", *[f"- {item}" for item in limitations]])
    (root/"REPORT.md").write_text("\n".join(report)+"\n", encoding="utf-8")
    manifest["files"] = [
        {"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": _sha(path)}
        for path in sorted(root.rglob("*")) if path.is_file() and path.name != "manifest.json"
    ]
    _json(root/"manifest.json", manifest)
    manifest["archive_external"] = _archive(root)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seeds", default="101,202,303"); parser.add_argument("--episodes-per-seed", type=int, default=6)
    args = parser.parse_args(); seeds = tuple(int(item) for item in args.seeds.split(",") if item.strip())
    print(json.dumps(run_paired_pilot(output_root=args.output_root, seeds=seeds, episodes_per_seed=args.episodes_per_seed), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
