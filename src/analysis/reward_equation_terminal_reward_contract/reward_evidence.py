from __future__ import annotations

from dataclasses import dataclass


FEATURE_ID = "029-reward-equation-terminal-reward-contract"


@dataclass(frozen=True, slots=True)
class EquationEvidence:
    equation_id: str
    source_path: str
    source_location_or_char_offset: str
    raw_ocr_text: str
    normalized_formula: str
    confidence: str
    recovery_status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "equation_id": self.equation_id,
            "source_path": self.source_path,
            "source_location_or_char_offset": self.source_location_or_char_offset,
            "raw_ocr_text": self.raw_ocr_text,
            "normalized_formula": self.normalized_formula,
            "confidence": self.confidence,
            "recovery_status": self.recovery_status,
        }


def build_recovered_equations() -> list[EquationEvidence]:
    source_path = "resources/papers/hoodie/ocr/merged.tex"
    return [
        EquationEvidence(
            equation_id="20",
            source_path=source_path,
            source_location_or_char_offset="char_offset=134900..135300",
            raw_ocr_text=(
                "r_n(t+1)=begin{cases}{NaN,} if x_n(t)=0 (no task arrived) "
                "{-Phi_n(t),} if psi_n^priv(t)<t+phi_n-1 or psi_n,k^pub(t')<t+phi_n-1 "
                "(task successfully processed) {-C,} otherwise (task thrown) end{cases}"
            ),
            normalized_formula=(
                "r_n(t+1) = NaN if x_n(t)=0; "
                "r_n(t+1) = -Phi_n(t) if successfully processed before timeout; "
                "r_n(t+1) = -C otherwise (task thrown)"
            ),
            confidence="high",
            recovery_status="paper_backed",
        ),
        EquationEvidence(
            equation_id="21",
            source_path=source_path,
            source_location_or_char_offset="char_offset=135300..135900",
            raw_ocr_text=(
                "Phi_n(t)=begin{cases}{Phi_n^priv(t),} if d_n^(1)=1 (local processing) "
                "{Phi_n^pub(t),} if d_n^(1)=0 (offloading) end{cases}"
            ),
            normalized_formula=(
                "Phi_n(t) = Phi_n^priv(t) if d_n^(1)=1; "
                "Phi_n(t) = Phi_n^pub(t) if d_n^(1)=0"
            ),
            confidence="high",
            recovery_status="paper_backed",
        ),
        EquationEvidence(
            equation_id="22",
            source_path=source_path,
            source_location_or_char_offset="char_offset=135900..136300",
            raw_ocr_text="Phi_n^priv(t)=psi_n^priv(t)-t+1",
            normalized_formula="Phi_n^priv(t) = psi_n^priv(t) - t + 1",
            confidence="high",
            recovery_status="paper_backed",
        ),
        EquationEvidence(
            equation_id="23",
            source_path=source_path,
            source_location_or_char_offset="char_offset=136300..136900",
            raw_ocr_text=(
                "Phi_n^pub(t)=sum_{k in N-{n}} sum_{t'=t}^T d_n,k^(2)(t) "
                "(psi_n,k^pub(t')-t+1) [OCR noisy]"
            ),
            normalized_formula=(
                "Phi_n^pub(t) = sum over k in N \\ {n} of sum over t' = t..T "
                "d_n,k^(2)(t) * (psi_n,k^pub(t') - t + 1)"
            ),
            confidence="medium",
            recovery_status="paper_backed_with_ocr_noise_caveat",
        ),
        EquationEvidence(
            equation_id="24",
            source_path=source_path,
            source_location_or_char_offset="char_offset=136900..137350",
            raw_ocr_text=(
                "pi_n* = arg max over pi_n E[sum_{t in T} gamma^(t-1) * r_n(t) | pi_n]"
            ),
            normalized_formula=(
                "pi_n* = arg max over pi_n E[ sum_{t in T} gamma^(t-1) * r_n(t) | pi_n ]"
            ),
            confidence="high",
            recovery_status="paper_backed",
        ),
    ]


def build_reward_evidence_summary() -> dict[str, object]:
    return {
        "feature_id": FEATURE_ID,
        "equations": [item.to_dict() for item in build_recovered_equations()],
        "c_value": {
            "value": 40,
            "source_path": "resources/papers/hoodie/recovered/paper-parameter-registry.json",
            "source_location_or_char_offset": "Table 4 / recovery registry",
            "recovery_status": "paper_backed",
            "artifact_backed": True,
        },
        "aggregation_evidence": {
            "cumulative_reward": True,
            "training_episodes": 5000,
            "validation_episodes": 200,
            "averaged_across_distributed_agents": True,
            "exact_reduction_order": "assumption_backed",
            "source_path": "resources/papers/hoodie/ocr/merged.tex",
        },
        "no_task_behavior": {
            "paper_status": "paper_backed",
            "runtime_policy": "omit_or_nan_not_numeric_zero",
        },
    }
