from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path

MATRIX_PATH = Path("artifacts/hoodie/implementation_run/campaign/expected_production_job_matrix.json")


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


def build_production_job_matrix(campaign_id: str) -> list[ProductionJobRow]:
    if not MATRIX_PATH.exists():
        raise FileNotFoundError(f"missing frozen matrix: {MATRIX_PATH}")
    source_contract_hash = sha256(Path("artifacts/hoodie/source_contracts/figures_8_11_source_contract.json").read_bytes()).hexdigest()
    rows = [
        ProductionJobRow(
            **{
                **row,
                "campaign_id": campaign_id,
                "config_hash": sha256(json.dumps({k: row[k] for k in ("panel_id", "scientific_unit_id", "job_id", "job_type", "independent_variable", "independent_value", "series_name", "policy", "variant", "seed")}, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
                "source_contract_hash": source_contract_hash,
            }
        )
        for row in json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    ]
    if rows and any(row.campaign_id != campaign_id for row in rows):
        rows = [
            ProductionJobRow(
                **{**asdict(row), "campaign_id": campaign_id}
            )
            for row in rows
        ]
    return rows


def write_production_job_matrix(path: str | Path, campaign_id: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(row) for row in build_production_job_matrix(campaign_id)]
    destination.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
