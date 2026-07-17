from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

MATRIX_PATH = Path("artifacts/hoodie/implementation_run/campaign/expected_production_job_matrix.json")
SOURCE_CONTRACT_PATH = Path("artifacts/hoodie/source_contracts/figures_8_11_source_contract.json")
CONTRACT_DIR = Path("resources/papers/hoodie/contracts")
DEFAULT_SEED = 7
CANONICAL_CHECKPOINT_JOB_ID = "train-figure8a-lr-7e-07"


@dataclass(frozen=True, slots=True)
class ProductionJobRow:
    campaign_id: str
    panel_id: str
    scientific_unit_id: str
    job_id: str
    job_type: str
    independent_variable: str
    independent_value: object
    series_name: str | None
    policy: str
    variant: str | None
    seed: int | None
    topology_contract: dict[str, object]
    physical_contract: dict[str, object]
    workload_contract: dict[str, object]
    training_contract: dict[str, object]
    evaluation_contract: dict[str, object]
    trace_bank_id: str
    checkpoint_dependency: str | None
    config_hash: str
    source_contract_hash: str


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: object) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _source_contract_hash() -> str:
    return sha256(SOURCE_CONTRACT_PATH.read_bytes()).hexdigest()


def _contracts() -> dict[str, dict[str, Any]]:
    panels: dict[str, dict[str, Any]] = {}
    for filename in ("figure_8.json", "figure_9.json", "figure_10.json", "figure_11.json"):
        payload = json.loads((CONTRACT_DIR / filename).read_text(encoding="utf-8"))
        for panel in payload["panels"]:
            panels[str(panel["panel_id"])] = panel
    return panels


def _slug(value: object) -> str:
    text = str(value).strip().lower()
    replacements = {" ": "-", ".": "p", "+": "", "/": "-", "_": "-"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _row(
    *,
    campaign_id: str,
    panel_id: str,
    job_id: str,
    job_type: str,
    independent_variable: str,
    independent_value: object,
    series_name: str | None,
    policy: str,
    variant: str | None,
    seed: int,
    topology_contract: dict[str, object],
    physical_contract: dict[str, object],
    workload_contract: dict[str, object],
    training_contract: dict[str, object],
    evaluation_contract: dict[str, object],
    trace_bank_id: str,
    checkpoint_dependency: str | None,
    source_contract_hash: str,
) -> ProductionJobRow:
    agent_count = None
    if isinstance(topology_contract, dict):
        counts = topology_contract.get("agent_counts")
        if isinstance(counts, (list, tuple)) and counts:
            agent_count = counts[0]
        elif counts is not None:
            agent_count = counts
    agent_count = None
    if isinstance(topology_contract, dict):
        counts = topology_contract.get("agent_counts")
        if isinstance(counts, (list, tuple)) and counts:
            agent_count = counts[0]
        elif counts is not None:
            agent_count = counts
    scientific_unit_id = f"{panel_id}:{independent_variable}:{independent_value}:{series_name}:{policy}:{variant}:{agent_count}:{seed}"
    payload = {
        "campaign_id": campaign_id,
        "panel_id": panel_id,
        "scientific_unit_id": scientific_unit_id,
        "job_id": job_id,
        "job_type": job_type,
        "independent_variable": independent_variable,
        "independent_value": independent_value,
        "series_name": series_name,
        "policy": policy,
        "variant": variant,
        "seed": seed,
        "topology_contract": topology_contract,
        "physical_contract": physical_contract,
        "workload_contract": workload_contract,
        "training_contract": training_contract,
        "evaluation_contract": evaluation_contract,
        "trace_bank_id": trace_bank_id,
        "checkpoint_dependency": checkpoint_dependency,
        "source_contract_hash": source_contract_hash,
    }
    return ProductionJobRow(config_hash=_hash(payload), **payload)


def _training_rows(
    campaign_id: str, panels: dict[str, dict[str, Any]], source_hash: str
) -> list[ProductionJobRow]:
    rows: list[ProductionJobRow] = []
    common = {
        "training_episodes": 5000,
        "slots_per_episode": 110,
        "decision_slots": 100,
        "drain_slots": 10,
        "batch_size": 64,
        "replay_capacity": 10_000,
        "target_copy_frequency": 2_000,
    }
    for learning_rate in panels["figure_8a"]["series"]:
        job_id = f"train-figure8a-lr-{learning_rate:.0e}"
        rows.append(
            _row(
                campaign_id=campaign_id,
                panel_id="figure_8a",
                job_id=job_id,
                job_type="training",
                independent_variable="learning_rate",
                independent_value=float(learning_rate),
                series_name=f"alpha={learning_rate:g}",
                policy="HOODIE",
                variant="hoodie_lstm",
                seed=DEFAULT_SEED,
                topology_contract={"agent_counts": [20], "fixed_topology": "Figure 7 adjacency matrix"},
                physical_contract={"backend": "cpu"},
                workload_contract={"task_arrival_probability": 0.5, **common},
                training_contract={**common, "learning_rate": float(learning_rate), "discount_factor": 0.99},
                evaluation_contract={},
                trace_bank_id=f"training-n20-seed-{DEFAULT_SEED}",
                checkpoint_dependency=None,
                source_contract_hash=source_hash,
            )
        )
    for gamma in panels["figure_8b"]["series"]:
        rows.append(
            _row(
                campaign_id=campaign_id,
                panel_id="figure_8b",
                job_id=f"train-figure8b-gamma-{_slug(gamma)}",
                job_type="training",
                independent_variable="discount_factor",
                independent_value=float(gamma),
                series_name=f"gamma={gamma:g}",
                policy="HOODIE",
                variant="hoodie_lstm",
                seed=DEFAULT_SEED,
                topology_contract={"agent_counts": [20], "fixed_topology": "Figure 7 adjacency matrix"},
                physical_contract={"backend": "cpu"},
                workload_contract={"task_arrival_probability": 0.5, **common},
                training_contract={**common, "learning_rate": 7e-7, "discount_factor": float(gamma)},
                evaluation_contract={},
                trace_bank_id=f"training-n20-seed-{DEFAULT_SEED}",
                checkpoint_dependency=None,
                source_contract_hash=source_hash,
            )
        )
    figure_11 = panels["figure_11"]
    for variant in figure_11["variants"]:
        rows.append(
            _row(
                campaign_id=campaign_id,
                panel_id="figure_11",
                job_id=f"train-figure11-{variant}",
                job_type="training",
                independent_variable="variant",
                independent_value=variant,
                series_name=variant,
                policy="HOODIE",
                variant=variant,
                seed=DEFAULT_SEED,
                topology_contract={"agent_counts": [20], "fixed_topology": "Figure 7 adjacency matrix"},
                physical_contract={"backend": "cpu"},
                workload_contract={
                    "task_arrival_probability": float(figure_11["task_arrival_probability"]),
                    "task_timeout_seconds": float(figure_11["task_timeout_seconds"]),
                    "slots_per_episode": 110,
                    "decision_slots": 100,
                    "drain_slots": 10,
                },
                training_contract={
                    "training_episodes": int(figure_11["training_episodes"]),
                    "slots_per_episode": 110,
                    "decision_slots": 100,
                    "drain_slots": 10,
                    "batch_size": 64,
                    "replay_capacity": 10_000,
                    "target_copy_frequency": 2_000,
                    "learning_rate": float(figure_11["learning_rate"]),
                    "discount_factor": float(figure_11["discount_factor"]),
                },
                evaluation_contract={},
                trace_bank_id=f"figure11-training-seed-{DEFAULT_SEED}",
                checkpoint_dependency=None,
                source_contract_hash=source_hash,
            )
        )
    return rows


def _evaluation_row(
    *,
    campaign_id: str,
    panel_id: str,
    independent_variable: str,
    independent_value: object,
    series_name: str,
    policy: str,
    agent_count: int,
    source_hash: str,
    workload: dict[str, object] | None = None,
    physical: dict[str, object] | None = None,
    suffix: str = "",
) -> ProductionJobRow:
    workload_contract = {
        "validation_episodes": 200,
        "slots_per_episode": 110,
        "decision_slots": 100,
        "drain_slots": 10,
        **(workload or {}),
    }
    physical_contract = {"backend": "cpu", **(physical or {})}
    job_id = "-".join(
        part
        for part in (
            "eval",
            panel_id,
            _slug(independent_value),
            _slug(series_name),
            _slug(policy),
            f"n{agent_count}",
            suffix,
        )
        if part
    )
    return _row(
        campaign_id=campaign_id,
        panel_id=panel_id,
        job_id=job_id,
        job_type="evaluation",
        independent_variable=independent_variable,
        independent_value=independent_value,
        series_name=series_name,
        policy=policy,
        variant="hoodie_lstm" if policy == "HOODIE" else None,
        seed=DEFAULT_SEED,
        topology_contract={"agent_counts": [agent_count], "fixed_topology": "Figure 7 adjacency matrix"},
        physical_contract=physical_contract,
        workload_contract=workload_contract,
        training_contract={},
        evaluation_contract={
            "validation_episodes": 200,
            "slots_per_episode": 110,
            "decision_slots": 100,
            "drain_slots": 10,
        },
        trace_bank_id=f"paired-{panel_id}-{_slug(independent_value)}-n{agent_count}-seed{DEFAULT_SEED}",
        checkpoint_dependency=CANONICAL_CHECKPOINT_JOB_ID if policy == "HOODIE" else None,
        source_contract_hash=source_hash,
    )


def _evaluation_rows(
    campaign_id: str, panels: dict[str, dict[str, Any]], source_hash: str
) -> list[ProductionJobRow]:
    rows: list[ProductionJobRow] = []
    for panel_id in ("figure_9a", "figure_9b"):
        panel = panels[panel_id]
        for probability in panel["independent_values"]:
            for agent_count in panel["agent_counts"]:
                rows.append(
                    _evaluation_row(
                        campaign_id=campaign_id,
                        panel_id=panel_id,
                        independent_variable="task_arrival_probability",
                        independent_value=float(probability),
                        series_name=f"N={agent_count}",
                        policy="HOODIE",
                        agent_count=int(agent_count),
                        workload={"task_arrival_probability": float(probability)},
                        source_hash=source_hash,
                    )
                )
    panel = panels["figure_9c"]
    for cpu in panel["independent_values"]:
        for agent_count in panel["agent_counts"]:
            rows.append(
                _evaluation_row(
                    campaign_id=campaign_id,
                    panel_id="figure_9c",
                    independent_variable="cpu_computation_capacity_ghz",
                    independent_value=float(cpu),
                    series_name=f"N={agent_count}",
                    policy="HOODIE",
                    agent_count=int(agent_count),
                    workload={"task_arrival_probability": 0.5},
                    source_hash=source_hash,
                )
            )
    panel = panels["figure_9d"]
    for agent_count in panel["independent_values"]:
        for scenario in panel["traffic_scenarios"]:
            resolved = {
                **scenario,
                "task_arrival_probability": float(scenario["arrival_probability"]),
            }
            rows.append(
                _evaluation_row(
                    campaign_id=campaign_id,
                    panel_id="figure_9d",
                    independent_variable="traffic_scenario",
                    independent_value=str(scenario["name"]),
                    series_name=str(scenario["name"]),
                    policy="HOODIE",
                    agent_count=int(agent_count),
                    workload={"traffic_scenario": resolved, **resolved},
                    source_hash=source_hash,
                )
            )
    panel = panels["figure_9e"]
    rate_scenarios = panel.get("offloading_rate_scenarios", panel.get("rate_scenarios", []))
    for agent_count in panel["independent_values"]:
        for scenario in rate_scenarios:
            rows.append(
                _evaluation_row(
                    campaign_id=campaign_id,
                    panel_id="figure_9e",
                    independent_variable="communication_rate_scenario",
                    independent_value=str(scenario["name"]),
                    series_name=str(scenario["name"]),
                    policy="HOODIE",
                    agent_count=int(agent_count),
                    workload={"task_arrival_probability": 0.5},
                    physical={"communication_rate_scenario": scenario, **scenario},
                    source_hash=source_hash,
                )
            )

    for panel_id in ("figure_10a", "figure_10b", "figure_10c", "figure_10d", "figure_10e", "figure_10f"):
        panel = panels[panel_id]
        for value in panel["independent_values"]:
            for policy in panel["compared_policies"]:
                workload: dict[str, object] = {}
                if "fixed_arrival_probability" in panel:
                    workload["task_arrival_probability"] = float(panel["fixed_arrival_probability"])
                if "fixed_timeout_seconds" in panel:
                    workload["task_timeout_seconds"] = float(panel["fixed_timeout_seconds"])
                if panel["independent_variable"] == "task_arrival_probability":
                    workload["task_arrival_probability"] = float(value)
                if panel["independent_variable"] == "task_timeout_seconds":
                    workload["task_timeout_seconds"] = float(value)
                rows.append(
                    _evaluation_row(
                        campaign_id=campaign_id,
                        panel_id=panel_id,
                        independent_variable=str(panel["independent_variable"]),
                        independent_value=value,
                        series_name=str(policy),
                        policy=str(policy),
                        agent_count=20,
                        workload=workload,
                        source_hash=source_hash,
                    )
                )
    return rows


def validate_production_job_matrix(rows: Iterable[ProductionJobRow]) -> dict[str, int]:
    materialized = list(rows)
    if not materialized:
        raise ValueError("production job matrix is empty")
    job_ids = [row.job_id for row in materialized]
    units = [row.scientific_unit_id for row in materialized]
    if len(job_ids) != len(set(job_ids)):
        raise ValueError("duplicate job_id in production matrix")
    if len(units) != len(set(units)):
        raise ValueError("duplicate scientific_unit_id in production matrix")
    training_ids = {row.job_id for row in materialized if row.job_type == "training"}
    dependencies = {row.checkpoint_dependency for row in materialized if row.checkpoint_dependency}
    missing = dependencies - training_ids
    if missing:
        raise ValueError(f"checkpoint dependencies are not training job IDs: {sorted(missing)}")
    expected_panels = {
        "figure_8a", "figure_8b", "figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e",
        "figure_10a", "figure_10b", "figure_10c", "figure_10d", "figure_10e", "figure_10f", "figure_11",
    }
    actual_panels = {row.panel_id for row in materialized}
    if actual_panels != expected_panels:
        raise ValueError(f"panel coverage mismatch: {sorted(expected_panels - actual_panels)}")
    if any(row.job_type == "training" and row.checkpoint_dependency for row in materialized):
        raise ValueError("training rows must not depend on checkpoints")
    if any(row.policy != "HOODIE" and row.checkpoint_dependency for row in materialized):
        raise ValueError("baseline evaluation rows must not depend on HOODIE checkpoints")
    return {
        "total": len(materialized),
        "training": sum(row.job_type == "training" for row in materialized),
        "evaluation": sum(row.job_type == "evaluation" for row in materialized),
    }


def build_production_job_matrix(campaign_id: str) -> list[ProductionJobRow]:
    panels = _contracts()
    source_hash = _source_contract_hash()
    rows = _training_rows(campaign_id, panels, source_hash) + _evaluation_rows(
        campaign_id, panels, source_hash
    )
    validate_production_job_matrix(rows)
    return rows


def write_production_job_matrix(path: str | Path, campaign_id: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = build_production_job_matrix(campaign_id)
    destination.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
