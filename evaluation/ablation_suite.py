from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simulation.pipeline import PipelineConfig, run_single_experiment


@dataclass(frozen=True)
class AblationConfig:
    variants: tuple[str, ...] = ("FULL_MODEL", "NO_HEURISTIC", "RANDOM_ROUTING", "CLOUD_DISABLED")


@dataclass(frozen=True)
class AblationThrottle:
    max_runs_cap: int = 4
    sampling_mode: str = "deterministic_subset"
    disable_cartesian_expansion: bool = True


def build_ablation_configs(base_config: PipelineConfig) -> list[tuple[str, PipelineConfig]]:
    normalized = base_config
    if normalized.num_edge_nodes < 2:
        normalized = PipelineConfig(**{**normalized.to_dict(), "num_edge_nodes": 2, "topography": [[0, 1], [1, 0]]})
    configs: list[tuple[str, PipelineConfig]] = []
    configs.append(("FULL_MODEL", normalized))
    configs.append(("NO_HEURISTIC", PipelineConfig(**{**normalized.to_dict(), "phase": 0})))
    configs.append(("RANDOM_ROUTING", PipelineConfig(**{**normalized.to_dict(), "phase": 1})))
    configs.append(("CLOUD_DISABLED", PipelineConfig(**{**normalized.to_dict(), "cloud_capacity": 0.0})))
    return configs


def _deterministic_subset(items: list[tuple[str, PipelineConfig]], cap: int) -> list[tuple[str, PipelineConfig]]:
    if cap <= 0:
        return []
    return items[:cap]


def run_ablation_suite(
    base_config: PipelineConfig,
    output_dir: str | Path,
    throttle: AblationThrottle | None = None,
) -> dict[str, Any]:
    throttle = throttle or AblationThrottle()
    configs = build_ablation_configs(base_config)
    throttled = False
    if throttle.disable_cartesian_expansion and len(configs) > throttle.max_runs_cap:
        configs = _deterministic_subset(configs, throttle.max_runs_cap)
        throttled = True
    results: list[dict[str, Any]] = []
    for name, config in configs:
        result = run_single_experiment(config, policy=name.lower())
        results.append({"variant": name, **result})
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ablation_results.json").write_text(__import__("json").dumps(results, indent=2, sort_keys=True))
    return {
        "results": results,
        "output_dir": output_dir.name,
        "ablation_throttled": throttled,
        "sampling_mode": throttle.sampling_mode,
        "max_runs_cap": throttle.max_runs_cap,
        "variant_count": len(configs),
    }
