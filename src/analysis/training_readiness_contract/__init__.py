from __future__ import annotations

from .config import FEATURE_ID, TrainingReadinessContractConfig
from .model import ALLOWED_FINAL_VERDICTS, BehaviorEquivalenceSummary, TrainingReadinessContractReport
from .report import write_training_readiness_contract_report
from .runner import build_training_readiness_contract_report, main, run_training_readiness_contract

__all__ = [
    "ALLOWED_FINAL_VERDICTS",
    "BehaviorEquivalenceSummary",
    "FEATURE_ID",
    "TrainingReadinessContractConfig",
    "TrainingReadinessContractReport",
    "build_training_readiness_contract_report",
    "main",
    "run_training_readiness_contract",
    "write_training_readiness_contract_report",
]
