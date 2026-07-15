from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CheckpointContract:
    checkpoint_id: str
    policy: str
    model_variant: str
    training_job_id: str
    training_seed: int
    step: int
    selection_metric: str
    selection_rule: str
    online_network_hash: str
    target_network_hash: str
    lstm_hash: str | None
    optimizer_state_hash: str
    replay_state_hash: str
    configuration_hash: str
    source_hash: str

@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    contract: CheckpointContract
    valid: bool = True

    def validate_for_experiment(self, policy: str, model_variant: str) -> None:
        if self.contract.policy != policy or self.contract.model_variant != model_variant:
            raise ValueError("checkpoint contract mismatch")
        if model_variant == "hoodie_no_lstm" and self.contract.lstm_hash is not None:
            raise ValueError("no-LSTM checkpoint must not carry LSTM state")
