from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Iterable

TERM_PATTERNS = {
    "echo": re.compile(r"\becho\b", re.IGNORECASE),
    "ert": re.compile(r"\bert\b", re.IGNORECASE),
    "event_smdp": re.compile(r"\bevent[_-]smdp\b", re.IGNORECASE),
    "deadline_mask": re.compile(r"\bdeadline[_ ]mask\b", re.IGNORECASE),
    "predicted_risk": re.compile(r"\bpredicted[_ ]risk\b", re.IGNORECASE),
    "normalized_lateness": re.compile(r"\bnormalized[_ ]lateness\b", re.IGNORECASE),
    "risk_penalty": re.compile(r"\brisk[_ ]penalty\b", re.IGNORECASE),
    "terminal_exposure": re.compile(r"\bterminal[_ ]exposure\b", re.IGNORECASE),
}

@dataclass(frozen=True, slots=True)
class SupportedSurfaceMatch:
    path: str
    line: int
    term: str
    context: str
    classification: str
    reason: str


def _supported_roots(manifest_path: Path | str = "artifacts/hoodie/implementation_run/supported_surface.json") -> tuple[Path, ...]:
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    roots = []
    for root in payload["supported_surface"]["source_roots"]:
        path = Path(root)
        if path.exists():
            roots.append(path)
    return tuple(roots)


def scan_supported_surface(*, manifest_path: Path | str = "artifacts/hoodie/implementation_run/supported_surface.json") -> list[SupportedSurfaceMatch]:
    matches: list[SupportedSurfaceMatch] = []
    for root in _supported_roots(manifest_path):
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.name == Path(__file__).name:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line_number, line in enumerate(lines, start=1):
                for term, pattern in TERM_PATTERNS.items():
                    if pattern.search(line):
                        lowered = line.lower()
                        classification = _classify(path, term, line)
                        reason = _reason(path, term, classification)
                        matches.append(SupportedSurfaceMatch(str(path), line_number, term, lowered.strip()[:240], classification, reason))
    return sorted(matches, key=lambda item: (item.path, item.line, item.term))


def validate_supported_surface(*, manifest_path: Path | str = "artifacts/hoodie/implementation_run/supported_surface.json") -> list[SupportedSurfaceMatch]:
    matches = scan_supported_surface(manifest_path=manifest_path)
    prohibited = [match for match in matches if match.classification.startswith("prohibited_")]
    if prohibited:
        raise RuntimeError(f"prohibited supported-surface references: {prohibited[:20]}")
    return matches


def _classify(path: Path, term: str, line: str) -> str:
    if path.parts and any(part in {"tests_historical", "historical", "archive"} for part in path.parts):
        return "historical_reference_outside_surface"
    if term == "ert":
        if re.search(r"\bvertical\b|\bquarter\b|\binsert\b|\bconcert\b|\bert\b", line, re.IGNORECASE):
            return "neutral_word_collision"
        return "prohibited_behavior"
    if term == "echo":
        return "prohibited_behavior"
    return "prohibited_behavior"


def _reason(path: Path, term: str, classification: str) -> str:
    if classification == "neutral_word_collision":
        return f"{term} appears as unrelated token in {path.name}"
    if classification == "historical_reference_outside_surface":
        return "historical path excluded from supported surface"
    return "canonical supported surface must not reference legacy ECHO concepts"
