from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PaperTable4Contract:
    source: str
    delta_sec: float
    action_slots: int
    drain_slots: int
    validation_episodes: int
    task_arrival_probability: float
    task_sizes_mbits: list[float]
    processing_density_gcycles_per_mbit: float
    private_cpu_ghz: float
    public_cpu_ghz: float
    cloud_cpu_ghz: float
    horizontal_rate_mbps: float
    vertical_rate_mbps: float
    number_of_eas: int
    timeout_slots: int
    timeout_sec: float
    learning_rate: float
    discount_factor: float
    replay_memory_size: int
    batch_size: int
    drop_penalty: float
    lstm_lookback_window: int
    training_episodes: int
    converted_runtime_units: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_paper_source() -> str:
    candidates = [
        ROOT / "resources/papers/hoodie/ocr/merged.tex",
        ROOT / "resources/papers/hoodie/ocr/merged.md",
        ROOT / "resources/papers/hoodie/ocr/merged.json",
    ]
    for path in candidates:
        if path.exists():
            return str(path.relative_to(ROOT))
    return "unavailable"


def build_paper_table4_contract() -> PaperTable4Contract:
    delta_sec = 0.1
    private_cpu_ghz = 5.0
    public_cpu_ghz = 5.0
    cloud_cpu_ghz = 30.0
    horizontal_rate_mbps = 30.0
    vertical_rate_mbps = 10.0
    converted_runtime_units = {
        "private_cpu_cycles_per_slot": private_cpu_ghz * 1e9 * delta_sec,
        "public_cpu_cycles_per_slot": public_cpu_ghz * 1e9 * delta_sec,
        "cloud_cpu_cycles_per_slot": cloud_cpu_ghz * 1e9 * delta_sec,
        "horizontal_mbits_per_slot": horizontal_rate_mbps * delta_sec,
        "vertical_mbits_per_slot": vertical_rate_mbps * delta_sec,
        "timeout_sec": 20 * delta_sec,
    }
    return PaperTable4Contract(
        source=_read_paper_source(),
        delta_sec=delta_sec,
        action_slots=100,
        drain_slots=10,
        validation_episodes=200,
        task_arrival_probability=0.5,
        task_sizes_mbits=[round(2 + 0.1 * i, 1) for i in range(31)],
        processing_density_gcycles_per_mbit=0.297,
        private_cpu_ghz=private_cpu_ghz,
        public_cpu_ghz=public_cpu_ghz,
        cloud_cpu_ghz=cloud_cpu_ghz,
        horizontal_rate_mbps=horizontal_rate_mbps,
        vertical_rate_mbps=vertical_rate_mbps,
        number_of_eas=20,
        timeout_slots=20,
        timeout_sec=2.0,
        learning_rate=7e-7,
        discount_factor=0.99,
        replay_memory_size=10000,
        batch_size=64,
        drop_penalty=40.0,
        lstm_lookback_window=10,
        training_episodes=5000,
        converted_runtime_units=converted_runtime_units,
    )


def write_paper_contract_json(output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_paper_table4_contract().to_dict(), indent=2, sort_keys=True))


def _load_hyperparameters() -> dict[str, Any]:
    hyper_path = ROOT / "hyperparameters" / "hyperparameters.json"
    return json.loads(hyper_path.read_text())


def validate_hyperparameters_against_contract() -> list[dict[str, Any]]:
    contract = build_paper_table4_contract()
    hp = _load_hyperparameters()
    diagnostics: list[dict[str, Any]] = []

    def add(name: str, paper_value: Any, runtime_value: Any, unit: str, formula: str, severity: str) -> None:
        diagnostics.append(
            {
                "parameter": name,
                "paper_value": paper_value,
                "runtime_value": runtime_value,
                "unit": unit,
                "conversion_formula": formula,
                "severity": severity,
            }
        )

    runtime_delta = hp.get("delta_sec", contract.delta_sec)
    if runtime_delta != contract.delta_sec:
        add("delta_sec", contract.delta_sec, runtime_delta, "sec", "slot_duration = delta_sec", "high")

    if hp.get("number_of_servers") != contract.number_of_eas:
        add("number_of_eas", contract.number_of_eas, hp.get("number_of_servers"), "count", "count", "high")

    if hp.get("cloud_computational_capacity") != contract.cloud_cpu_ghz:
        add("cloud_cpu_ghz", contract.cloud_cpu_ghz, hp.get("cloud_computational_capacity"), "GHz", "GHz -> cycles/sec", "high")

    if hp.get("task_arrive_probabilities", [None])[0] != contract.task_arrival_probability:
        add("task_arrival_probability", contract.task_arrival_probability, hp.get("task_arrive_probabilities", [None])[0], "probability", "direct", "medium")

    if hp.get("task_size_mins", [None])[0] != contract.task_sizes_mbits[0]:
        add("task_size_min", contract.task_sizes_mbits[0], hp.get("task_size_mins", [None])[0], "Mbits", "direct", "medium")

    if hp.get("task_size_maxs", [None])[0] != contract.task_sizes_mbits[-1]:
        add("task_size_max", contract.task_sizes_mbits[-1], hp.get("task_size_maxs", [None])[0], "Mbits", "direct", "medium")

    if hp.get("timeout_delay_mins", [None])[0] != contract.timeout_slots:
        add("timeout_slots", contract.timeout_slots, hp.get("timeout_delay_mins", [None])[0], "slots", "timeout_sec / delta_sec", "high")

    if hp.get("task_drop_penalty", hp.get("drop_penalty")) != contract.drop_penalty:
        add("drop_penalty", contract.drop_penalty, hp.get("task_drop_penalty", hp.get("drop_penalty")), "reward units", "direct", "medium")

    return diagnostics

