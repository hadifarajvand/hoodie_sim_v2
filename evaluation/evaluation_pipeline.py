from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ablation_suite import AblationThrottle, run_ablation_suite
from .fairness_validator import FairnessValidationFailure, inject_asymmetric_workload_and_validate, run_fairness_validation
from .hypotheses import HypothesisRegistry
from .statistical_tests import cohens_d, compute_confidence_interval_95, compute_mean_std, one_way_anova, t_test_independent
from simulation.pipeline import PipelineConfig, run_single_experiment


class EvaluationConsistencyError(RuntimeError):
    pass


class EvaluationGuardTriggered(RuntimeError):
    pass


@dataclass(frozen=True)
class EvaluationGuard:
    max_execution_time_s: float = 30.0
    max_memory_proxy_runs: int = 250
    ablation_explosion_threshold: int = 32


@dataclass(frozen=True)
class EvaluationPaths:
    input_dir: str
    output_dir: str


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _load_results(experiment_dir: Path) -> list[dict[str, Any]]:
    raw_results = experiment_dir / "raw_results.json"
    summary = experiment_dir / "summary.json"
    if raw_results.exists():
        return list(_read_json(raw_results))
    if summary.exists():
        data = _read_json(summary)
        return list(data.get("rows", []))
    raise FileNotFoundError(f"no experiment results found in {experiment_dir}")


def _metric_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, list[float]]]:
    policy_alias = {
        "fifo_only": "fifo",
        "random_routing": "random",
        "heuristic_routing": "heuristic",
        "full_model": "heuristic",
        "no_heuristic": "fifo",
        "cloud_disabled": "fifo",
    }
    grouped: dict[tuple[str, str], dict[str, list[float]]] = {}
    for row in rows:
        policy = policy_alias.get(str(row["policy"]).lower(), str(row["policy"]).lower())
        key = (str(row["scenario"]), policy)
        metrics = row.get("metrics", {})
        bucket = grouped.setdefault(key, {"latency": [], "drop_ratio": [], "utilization": []})
        if metrics.get("average_latency") is not None:
            bucket["latency"].append(float(metrics["average_latency"]))
        if metrics.get("offloading_breakdown"):
            off = metrics["offloading_breakdown"]
            total = max(1, sum(int(v) for v in off.values()))
            bucket["drop_ratio"].append(float(off.get("cloud", 0) + off.get("neighbor", 0)) / total)
        if metrics.get("utilization"):
            util = metrics["utilization"]
            bucket["utilization"].append(float(sum(util.values()) / max(1, len(util))))
    return grouped


def _hypothesis_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    registry = HypothesisRegistry()
    metrics = _metric_map(rows)
    by_scenario: dict[str, dict[str, dict[str, list[float]]]] = {}
    for (scenario, policy), values in metrics.items():
        by_scenario.setdefault(scenario, {})[policy] = values
    results: list[dict[str, Any]] = []
    for hypothesis in registry.list():
        base_policy = hypothesis.baseline
        comp_policy = hypothesis.comparison_policy
        metric = hypothesis.metric
        for scenario, policies in sorted(by_scenario.items()):
            if base_policy not in policies or comp_policy not in policies:
                continue
            baseline_samples = policies[base_policy][metric]
            comp_samples = policies[comp_policy][metric]
            base_summary = compute_mean_std(baseline_samples).to_dict()
            comp_summary = compute_mean_std(comp_samples).to_dict()
            test = t_test_independent(comp_samples, baseline_samples)
            effect = cohens_d(comp_samples, baseline_samples)
            ci = compute_confidence_interval_95(comp_samples)
            direction_ok = None
            if base_summary["mean"] is not None and comp_summary["mean"] is not None:
                if hypothesis.direction == "less":
                    direction_ok = comp_summary["mean"] < base_summary["mean"]
                elif hypothesis.direction == "greater":
                    direction_ok = comp_summary["mean"] > base_summary["mean"]
            results.append(
                {
                    "scenario": scenario,
                    "hypothesis": hypothesis.name,
                    "metric": metric,
                    "baseline_policy": base_policy,
                    "comparison_policy": comp_policy,
                    "baseline_mean": base_summary["mean"],
                    "comparison_mean": comp_summary["mean"],
                    "direction": hypothesis.direction,
                    "direction_supported": direction_ok,
                    "t_test": test,
                    "cohens_d": effect,
                    "ci95_low": ci[0],
                    "ci95_high": ci[1],
                }
            )
    anova_input = {}
    if by_scenario:
        first_scenario = next(iter(by_scenario))
        for policy, metrics_by_name in by_scenario[first_scenario].items():
            anova_input[policy] = metrics_by_name["latency"]
    return {"rows": results, "anova": one_way_anova(anova_input), "hypotheses": registry.to_dict()}


def _select_smoke_inputs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return rows
    chosen: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (str(row.get("scenario")), str(row.get("policy")))
        if key in seen:
            continue
        seen.add(key)
        chosen.append(row)
        if len(chosen) >= 1:
            break
    return chosen


def _validate_required_fields(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = {"scenario", "policy", "seed", "metrics", "config_hash", "workload_signature", "resource_signature", "event_hash"}
    missing = []
    for idx, row in enumerate(rows):
        absent = sorted(field for field in required if field not in row)
        if absent:
            missing.append({"index": idx, "missing": absent})
    return {"passed": not missing, "missing": missing}


def _build_summary_from_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["scenario"]), str(row["policy"])), []).append(row)
    summary_rows: list[dict[str, Any]] = []
    for (scenario, policy), values in sorted(grouped.items()):
        latencies = [float(v["metrics"]["average_latency"]) for v in values if v["metrics"]["average_latency"] is not None]
        waits = [float(v["metrics"]["average_waiting_time"]) for v in values if v["metrics"]["average_waiting_time"] is not None]
        services = [float(v["metrics"]["average_service_time"]) for v in values if v["metrics"]["average_service_time"] is not None]
        local_ratio = [float(v["metrics"]["offloading_breakdown"]["local"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        neighbor_ratio = [float(v["metrics"]["offloading_breakdown"]["neighbor"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        cloud_ratio = [float(v["metrics"]["offloading_breakdown"]["cloud"]) / max(1, sum(v["metrics"]["offloading_breakdown"].values())) for v in values]
        util_means = [sum(v["metrics"]["utilization"].values()) / len(v["metrics"]["utilization"]) for v in values]
        summary_rows.append(
            {
                "scenario": scenario,
                "policy": policy,
                "runs": len(values),
                "latency_mean": compute_mean_std(latencies).mean,
                "latency_variance": compute_mean_std(latencies).variance,
                "latency_stddev": compute_mean_std(latencies).stddev,
                "latency_ci95_low": compute_confidence_interval_95(latencies)[0],
                "latency_ci95_high": compute_confidence_interval_95(latencies)[1],
                "waiting_mean": compute_mean_std(waits).mean,
                "waiting_variance": compute_mean_std(waits).variance,
                "service_mean": compute_mean_std(services).mean,
                "service_variance": compute_mean_std(services).variance,
                "offloading_local_mean": compute_mean_std(local_ratio).mean,
                "offloading_neighbor_mean": compute_mean_std(neighbor_ratio).mean,
                "offloading_cloud_mean": compute_mean_std(cloud_ratio).mean,
                "utilization_mean": compute_mean_std(util_means).mean,
                "utilization_variance": compute_mean_std(util_means).variance,
                "utilization_stddev": compute_mean_std(util_means).stddev,
            }
        )
    return summary_rows


def _consistency_report(raw_rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]], enriched_summary: dict[str, Any]) -> dict[str, Any]:
    required_fields = _validate_required_fields(raw_rows)
    derived_summary = _build_summary_from_rows(raw_rows)
    drift = []
    summary_by_key = {(row["scenario"], row["policy"]): row for row in summary_rows}
    derived_by_key = {(row["scenario"], row["policy"]): row for row in derived_summary}
    for key in sorted(summary_by_key):
        if key not in derived_by_key:
            drift.append({"key": key, "reason": "missing_derived_summary"})
            continue
        left = summary_by_key[key]
        right = derived_by_key[key]
        for metric in ("latency_mean", "waiting_mean", "service_mean", "utilization_mean"):
            lv = left.get(metric)
            rv = right.get(metric)
            if lv is None or rv is None:
                continue
            if not math.isclose(float(lv), float(rv), rel_tol=1e-9, abs_tol=1e-9):
                drift.append({"key": key, "metric": metric, "summary": lv, "derived": rv})
    passed = required_fields["passed"] and not drift and enriched_summary.get("status") == "passed"
    return {"passed": passed, "missing_fields": required_fields["missing"], "metric_drift": drift}


def _safety_guard(batch_size: int, guard: EvaluationGuard, elapsed_s: float, ablation_variant_count: int) -> dict[str, Any]:
    triggered = False
    reasons: list[str] = []
    if elapsed_s > guard.max_execution_time_s:
        triggered = True
        reasons.append("max_execution_time")
    if batch_size > guard.max_memory_proxy_runs:
        triggered = True
        reasons.append("max_memory_proxy")
    if ablation_variant_count > guard.ablation_explosion_threshold:
        triggered = True
        reasons.append("ablation_explosion")
    return {"evaluation_guard_triggered": triggered, "reason_codes": reasons, "batch_size": batch_size, "elapsed_s": elapsed_s}


def _emit_reports(
    output_dir: Path,
    *,
    raw_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    enriched: dict[str, Any],
    fairness: dict[str, Any] | None = None,
    hypotheses: dict[str, Any] | None = None,
    ablation: dict[str, Any] | None = None,
    consistency: dict[str, Any] | None = None,
    safety: dict[str, Any] | None = None,
) -> None:
    _write_json(output_dir / "raw_results.json", raw_rows)
    _write_json(output_dir / "summary_rows.json", summary_rows)
    _write_json(output_dir / "summary.json", {"rows": summary_rows, "config_count": len({row["scenario"] for row in summary_rows}), "run_count": len(summary_rows)})
    _write_json(output_dir / "enriched_summary.json", enriched)
    if fairness is not None:
        _write_json(output_dir / "fairness_report.json", fairness)
    if hypotheses is not None:
        _write_json(output_dir / "hypothesis_report.json", hypotheses)
    if ablation is not None:
        _write_json(output_dir / "ablation_report.json", ablation)
    if consistency is not None:
        _write_json(output_dir / "consistency_report.json", consistency)
    if safety is not None:
        _write_json(output_dir / "safety_guard_report.json", safety)


def run_smoke_test(base_config: PipelineConfig, output_dir: str | Path) -> dict[str, Any]:
    smoke_config = PipelineConfig(
        **{
            **base_config.to_dict(),
            "run_id": "smoke",
            "seed": base_config.seed,
            "phase": 0,
            "task_count": 1,
            "num_edge_nodes": 1,
            "horizon": 1,
            "smoke_only": True,
        }
    )
    result = run_single_experiment(smoke_config, policy="fifo_only")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "raw_results.json": [result],
        "summary.json": {"rows": _build_summary_from_rows([result]), "config_count": 1, "run_count": 1},
    }
    for name, data in payload.items():
        (output_dir / name).write_text(json.dumps(data, indent=2, sort_keys=True))
    enriched = {
        "status": "passed",
        "smoke": True,
        "source_experiment_dir": "smoke",
        "rows": [result],
    }
    _write_json(output_dir / "enriched_summary.json", enriched)
    return {"result": result, "output_dir": str(output_dir), "enriched_summary": enriched}


def run_evaluation_pipeline(
    experiment_dir: str | Path,
    output_dir: str | Path | None = None,
    *,
    guard: EvaluationGuard | None = None,
    ablation_throttle: AblationThrottle | None = None,
    run_injection_test: bool = True,
) -> dict[str, Any]:
    start = time.perf_counter()
    guard = guard or EvaluationGuard()
    ablation_throttle = ablation_throttle or AblationThrottle()
    experiment_dir = Path(experiment_dir)
    output_dir = Path(output_dir) if output_dir is not None else experiment_dir / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_results(experiment_dir)
    raw_rows = _select_smoke_inputs(rows) if len(rows) <= 1 else rows
    fairness = run_fairness_validation(raw_rows, fail_fast=True)
    if not fairness["passed"]:
        report = {"status": "failed", "fairness": fairness, "source_experiment_dir": "experiment_suite"}
        _emit_reports(output_dir, raw_rows=raw_rows, summary_rows=_build_summary_from_rows(raw_rows), enriched=report, fairness=report)
        raise FairnessValidationFailure("fairness validation failed")
    adversarial = None
    if run_injection_test:
        adversarial = inject_asymmetric_workload_and_validate(raw_rows, fail_fast=False)
        if adversarial["passed"]:
            raise FairnessValidationFailure("adversarial fairness injection did not fail as expected")

    hypotheses = _hypothesis_results(raw_rows)
    ablation_base = PipelineConfig(
        run_id="evaluation_ablation",
        seed=0,
        mode="paper_faithful",
        phase=0,
        num_edge_nodes=2,
        horizon=8,
        arrival_probability=0.5,
        task_count=8,
        topography=[[0, 1], [1, 0]],
        smoke_only=True,
    )
    ablation = run_ablation_suite(
        ablation_base,
        output_dir / "ablation",
        throttle=ablation_throttle,
    )
    ablation["source_experiment_dir"] = "experiment_suite"

    summary_rows = _build_summary_from_rows(raw_rows)
    summary_payload = {"rows": summary_rows, "config_count": len({row["scenario"] for row in raw_rows}), "run_count": len(raw_rows)}
    enriched = {
        "status": "passed",
        "fairness": fairness,
        "fairness_injection": adversarial,
        "hypotheses": hypotheses,
        "ablation": ablation,
        "source_experiment_dir": "experiment_suite",
    }

    consistency = _consistency_report(raw_rows, summary_rows, enriched)
    elapsed = time.perf_counter() - start
    safety = _safety_guard(len(raw_rows), guard, elapsed, int(ablation.get("variant_count", 0)))
    if safety["evaluation_guard_triggered"]:
        enriched["status"] = "failed"
        enriched["guard"] = safety
        _emit_reports(
            output_dir,
            raw_rows=raw_rows,
            summary_rows=raw_rows,
            enriched=enriched,
            fairness=fairness,
            hypotheses=hypotheses,
            ablation=ablation,
            consistency=consistency,
            safety=safety,
        )
        raise EvaluationGuardTriggered(",".join(safety["reason_codes"]))

    if not consistency["passed"]:
        enriched["status"] = "failed"
        _emit_reports(
            output_dir,
            raw_rows=raw_rows,
            summary_rows=raw_rows,
            enriched=enriched,
            fairness=fairness,
            hypotheses=hypotheses,
            ablation=ablation,
            consistency=consistency,
            safety=safety,
        )
        raise EvaluationConsistencyError("raw and enriched evaluation outputs are inconsistent")

    _emit_reports(
        output_dir,
        raw_rows=raw_rows,
        summary_rows=raw_rows,
        enriched=enriched,
        fairness=fairness,
        hypotheses=hypotheses,
        ablation=ablation,
        consistency=consistency,
        safety=safety,
    )
    return {
        "status": "passed",
        "fairness": fairness,
        "hypotheses": hypotheses,
        "ablation": ablation,
        "consistency": consistency,
        "safety": safety,
        "summary": summary_payload,
        "source_experiment_dir": "experiment_suite",
    }
