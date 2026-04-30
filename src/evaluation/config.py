from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class EvaluationConfig:
    policy_name: str
    seed: int
    trace_id: str
    episode_count: int = 1
    episode_length: int = 4
    output_dir: Path | None = None
    trace_mode: str = "deterministic_seed"
    device: str = "cpu"
