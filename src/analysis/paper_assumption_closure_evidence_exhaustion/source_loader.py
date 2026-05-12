from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LoadedSource:
    path: Path
    payload: Any


REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCE_GATE_PATHS = [
    REPO_ROOT / "resources/papers/hoodie/ocr/merged.tex",
    REPO_ROOT / "resources/papers/hoodie/ocr/merged.md",
    REPO_ROOT / "resources/papers/hoodie/ocr/merged.txt",
    REPO_ROOT / "resources/papers/hoodie/ocr/merged.json",
    REPO_ROOT / "resources/papers/hoodie/HOODIE_paper.pdf",
    REPO_ROOT / "resources/papers/hoodie/recovered/topology-g.json",
    REPO_ROOT / "resources/papers/hoodie/recovered/paper-parameter-registry.json",
    REPO_ROOT / "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json",
    REPO_ROOT / "artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json",
    REPO_ROOT / "artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json",
    REPO_ROOT / "artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json",
]


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_sources(paths: list[Path]) -> dict[Path, LoadedSource]:
    loaded: dict[Path, LoadedSource] = {}
    for path in paths:
        if path.suffix == ".json":
            payload = load_json(path)
        else:
            payload = load_text(path)
        loaded[path] = LoadedSource(path=path, payload=payload)
    return loaded
