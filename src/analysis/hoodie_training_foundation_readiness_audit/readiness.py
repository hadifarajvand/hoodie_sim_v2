from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


READINESS_DIMENSION_NAMES: tuple[str, ...] = (
    "state_representation",
    "action_space_legality",
    "delayed_reward_timing",
    "episode_protocol",
    "replay_log_artifacts",
    "dqn_mechanism_gap",
    "double_dqn_mechanism_gap",
    "dueling_dqn_mechanism_gap",
    "lstm_mechanism_gap",
    "training_evaluation_separation",
    "reproducibility",
    "pre_training_blockers",
)

MECHANISM_FAMILY_NAMES: tuple[str, ...] = ("DQN", "Double-DQN", "Dueling-DQN", "LSTM")


@dataclass(slots=True)
class ReadinessDimension:
    name: str
    supported: bool
    evidence_source: str
    blocker_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "supported": self.supported,
            "evidence_source": self.evidence_source,
            "blocker_notes": list(self.blocker_notes),
        }


@dataclass(slots=True)
class MechanismGap:
    family: str
    gap_type: str
    severity: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "family": self.family,
            "gap_type": self.gap_type,
            "severity": self.severity,
            "evidence": list(self.evidence),
        }


@dataclass(slots=True)
class ReadinessAudit:
    dimensions: list[ReadinessDimension]
    mechanism_gaps: list[MechanismGap]
    blockers: list[str]
    verdict: str
    limitations: list[str]
    source_summary: dict[str, Any]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "dimensions": [item.to_dict() for item in self.dimensions],
            "mechanism_gaps": [item.to_dict() for item in self.mechanism_gaps],
            "blockers": list(self.blockers),
            "verdict": self.verdict,
            "limitations": list(self.limitations),
            "source_summary": dict(self.source_summary),
            "notes": list(self.notes),
        }


def _has_any(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in phrases)


def _ocr_text(payload: dict[str, Any]) -> str:
    checks = payload.get("checks", [])
    paper_check = next((item for item in checks if item.get("artifact") == "paper_ocr"), {})
    details = paper_check.get("details", [])
    if isinstance(details, list):
        return " ".join(str(item) for item in details)
    return str(details)


def classify_readiness(source_gate_status: dict[str, Any], source_artifact_payloads: dict[str, Any]) -> ReadinessAudit:
    paper_text = str(source_artifact_payloads.get("paper_ocr_text", "")).lower()
    ocr_supported = source_gate_status.get("passed") and bool(paper_text)

    dimensions = [
        ReadinessDimension("state_representation", _has_any(paper_text, ("state input", "task features", "local task characteristics")), "paper_ocr", [] if _has_any(paper_text, ("state input", "task features")) else ["OCR only describes inputs, not implementable state handling"]),
        ReadinessDimension("action_space_legality", False, "no training artifact", ["No training loop or policy controller exists to prove legal-action handling"]),
        ReadinessDimension("delayed_reward_timing", _has_any(paper_text, ("delay", "drop", "reward")), "paper_ocr", [] if _has_any(paper_text, ("delay", "drop")) else ["Reward timing is only paper-described, not implemented"]),
        ReadinessDimension("episode_protocol", False, "no training artifact", ["No training/evaluation episode protocol exists in the repository"]),
        ReadinessDimension("replay_log_artifacts", False, "artifact inventory", ["No replay buffer or training-log artifact contract is present"]),
        ReadinessDimension("dqn_mechanism_gap", _has_any(paper_text, ("dqn",)), "paper_ocr", [] if _has_any(paper_text, ("dqn",)) else ["Paper mechanisms are not recoverable"]),
        ReadinessDimension("double_dqn_mechanism_gap", _has_any(paper_text, ("double-dqn", "double q-learning")), "paper_ocr", [] if _has_any(paper_text, ("double-dqn", "double q-learning")) else ["Double-DQN evidence is not recoverable"]),
        ReadinessDimension("dueling_dqn_mechanism_gap", _has_any(paper_text, ("dueling", "dueling dqn")), "paper_ocr", [] if _has_any(paper_text, ("dueling",)) else ["Dueling-DQN evidence is not recoverable"]),
        ReadinessDimension("lstm_mechanism_gap", _has_any(paper_text, ("lstm",)), "paper_ocr", [] if _has_any(paper_text, ("lstm",)) else ["LSTM evidence is not recoverable"]),
        ReadinessDimension("training_evaluation_separation", False, "repository audit", ["No training/evaluation split or training runner exists yet"]),
        ReadinessDimension("reproducibility", False, "artifact inventory", ["No training/evaluation seeds or run logs exist for future DRL training"]),
        ReadinessDimension("pre_training_blockers", False, "all diagnostics", ["The project is still missing training foundation work and explicit training contracts"]),
    ]

    mechanism_gaps = [
        MechanismGap("DQN", "paper_mechanism_ready", "blocking" if not dimensions[5].supported else "informational", ["Supported only as OCR evidence, not as executable training infrastructure"]),
        MechanismGap("Double-DQN", "paper_mechanism_ready", "blocking" if not dimensions[6].supported else "informational", ["Supported only as OCR evidence, not as executable training infrastructure"]),
        MechanismGap("Dueling-DQN", "paper_mechanism_ready", "blocking" if not dimensions[7].supported else "informational", ["Supported only as OCR evidence, not as executable training infrastructure"]),
        MechanismGap("LSTM", "paper_mechanism_ready", "blocking" if not dimensions[8].supported else "informational", ["Supported only as OCR evidence, not as executable training infrastructure"]),
    ]

    blockers: list[str] = []
    for dimension in dimensions:
        if not dimension.supported:
            blockers.extend(dimension.blocker_notes or [f"{dimension.name} is not ready"])
    if not ocr_supported:
        blockers.append("Source gate is incomplete or OCR evidence is insufficient")

    verdict = "ready" if ocr_supported and all(dimension.supported for dimension in dimensions) else "blocked_readiness"
    limitations = [
        "Diagnostic only.",
        "This audit does not implement training, DRL, or neural-network code.",
        "Partial OCR evidence is preserved as evidence, not promoted to readiness.",
    ]
    return ReadinessAudit(
        dimensions=dimensions,
        mechanism_gaps=mechanism_gaps,
        blockers=blockers,
        verdict=verdict,
        limitations=limitations,
        source_summary={
            "source_gate_passed": bool(source_gate_status.get("passed")),
            "paper_ocr_supported": ocr_supported,
            "mechanism_families": list(MECHANISM_FAMILY_NAMES),
        },
    )
