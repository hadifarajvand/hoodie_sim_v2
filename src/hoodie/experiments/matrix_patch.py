from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from . import job_matrix as matrix

_INSTALLED = False
_ORIGINAL_BUILD = matrix.build_production_job_matrix


def reference_checkpoint_job_id(agent_count: int) -> str:
    return (
        matrix.CANONICAL_CHECKPOINT_JOB_ID
        if agent_count == 20
        else f"train-reference-n{agent_count}"
    )


def _resolved_row(row: matrix.ProductionJobRow, *, checkpoint_dependency: str | None) -> matrix.ProductionJobRow:
    return matrix._row(
        campaign_id=row.campaign_id,
        panel_id=row.panel_id,
        job_id=row.job_id,
        job_type=row.job_type,
        independent_variable=row.independent_variable,
        independent_value=row.independent_value,
        series_name=row.series_name,
        policy=row.policy,
        variant=row.variant,
        seed=int(row.seed or 0),
        topology_contract=dict(row.topology_contract),
        physical_contract=dict(row.physical_contract),
        workload_contract=dict(row.workload_contract),
        training_contract=dict(row.training_contract),
        evaluation_contract=dict(row.evaluation_contract),
        trace_bank_id=row.trace_bank_id,
        checkpoint_dependency=checkpoint_dependency,
        source_contract_hash=row.source_contract_hash,
    )


def build_production_job_matrix(campaign_id: str) -> list[matrix.ProductionJobRow]:
    rows = _ORIGINAL_BUILD(campaign_id)
    canonical = next(row for row in rows if row.job_id == matrix.CANONICAL_CHECKPOINT_JOB_ID)
    for agent_count in (10, 15, 25, 30):
        job_id = reference_checkpoint_job_id(agent_count)
        rows.append(
            matrix._row(
                campaign_id=campaign_id,
                panel_id="figure_8a",
                job_id=job_id,
                job_type="training",
                independent_variable="learning_rate",
                independent_value=7e-7,
                series_name=f"reference-only-N={agent_count}",
                policy="HOODIE",
                variant="hoodie_lstm",
                seed=matrix.DEFAULT_SEED,
                topology_contract={
                    "agent_counts": [agent_count],
                    "fixed_topology": "Figure 7 modular family",
                },
                physical_contract=dict(canonical.physical_contract),
                workload_contract=dict(canonical.workload_contract),
                training_contract={**canonical.training_contract, "reference_only": True},
                evaluation_contract={},
                trace_bank_id=f"reference-training-n{agent_count}-seed-{matrix.DEFAULT_SEED}",
                checkpoint_dependency=None,
                source_contract_hash=canonical.source_contract_hash,
            )
        )
    resolved: list[matrix.ProductionJobRow] = []
    for row in rows:
        if row.job_type == "evaluation" and row.policy == "HOODIE":
            counts = row.topology_contract.get("agent_counts", [20])
            agent_count = int(counts[0] if isinstance(counts, (list, tuple)) else counts)
            row = _resolved_row(
                row,
                checkpoint_dependency=reference_checkpoint_job_id(agent_count),
            )
        resolved.append(row)
    matrix.validate_production_job_matrix(resolved)
    return resolved


def write_production_job_matrix(path: str | Path, campaign_id: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            [asdict(row) for row in build_production_job_matrix(campaign_id)],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


def install_matrix_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    matrix.build_production_job_matrix = build_production_job_matrix
    matrix.write_production_job_matrix = write_production_job_matrix
    _INSTALLED = True
