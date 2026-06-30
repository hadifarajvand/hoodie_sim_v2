from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig
from src.environment.link_rate_config import LinkRateConfig

FEATURE_ID = "041-full-training-reproduction-campaign"
TARGET_UPDATE_UNIT = "optimizer_step"
READINESS_MANUAL_APPROVAL_NOT_APPROVED = "not_approved"
READINESS_MANUAL_APPROVAL_PENDING = READINESS_MANUAL_APPROVAL_NOT_APPROVED
READINESS_MANUAL_APPROVAL_APPROVED = "approved"
READINESS_MANUAL_APPROVAL_REJECTED = "rejected"

CampaignStage = Literal["readiness_probe", "pilot_training", "full_training_candidate", "final_reproduction_campaign"]


@dataclass(slots=True)
class CampaignSeedBundle:
    readiness_probe_seed: int = 31
    training_trace_generation_seed: int = 41
    evaluation_trace_generation_seed: int = 43
    replay_sampling_seed: int = 47
    model_initialization_seed: int = 19
    action_exploration_seed: int = 53
    python_seed: int = 59
    torch_seed: int = 61

    def __post_init__(self) -> None:
        for field_name in (
            "readiness_probe_seed",
            "training_trace_generation_seed",
            "evaluation_trace_generation_seed",
            "replay_sampling_seed",
            "model_initialization_seed",
            "action_exploration_seed",
            "python_seed",
            "torch_seed",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise ValueError(f"{field_name} must be an integer.")

    @property
    def signature(self) -> str:
        return (
            f"probe={self.readiness_probe_seed}|train={self.training_trace_generation_seed}|"
            f"eval={self.evaluation_trace_generation_seed}|replay={self.replay_sampling_seed}|"
            f"model={self.model_initialization_seed}|explore={self.action_exploration_seed}|"
            f"python={self.python_seed}|torch={self.torch_seed}"
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "readiness_probe_seed": self.readiness_probe_seed,
            "training_trace_generation_seed": self.training_trace_generation_seed,
            "evaluation_trace_generation_seed": self.evaluation_trace_generation_seed,
            "replay_sampling_seed": self.replay_sampling_seed,
            "model_initialization_seed": self.model_initialization_seed,
            "action_exploration_seed": self.action_exploration_seed,
            "python_seed": self.python_seed,
            "torch_seed": self.torch_seed,
        }


@dataclass(slots=True)
class TargetUpdateContract:
    update_frequency: int = 2000
    target_update_unit: str = TARGET_UPDATE_UNIT
    approval_status: str = "user_approved_campaign_assumption"
    paper_evidence_status: str = "ambiguous_not_explicitly_defined"
    allowed_units: tuple[str, ...] = ("optimizer_step", "environment_step", "replay_insertion", "episode")

    def __post_init__(self) -> None:
        if self.update_frequency != 2000:
            raise ValueError("TargetUpdateContract.update_frequency must equal 2000.")
        if self.target_update_unit != TARGET_UPDATE_UNIT:
            raise ValueError("TargetUpdateContract.target_update_unit must equal optimizer_step.")
        if self.approval_status != "user_approved_campaign_assumption":
            raise ValueError("TargetUpdateContract.approval_status must reflect user-approved campaign assumption.")
        if self.paper_evidence_status != "ambiguous_not_explicitly_defined":
            raise ValueError("TargetUpdateContract.paper_evidence_status must remain ambiguous_not_explicitly_defined.")

    def should_sync(self, optimizer_step_count: int) -> bool:
        return optimizer_step_count > 0 and optimizer_step_count % self.update_frequency == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "update_frequency": self.update_frequency,
            "target_update_unit": self.target_update_unit,
            "approval_status": self.approval_status,
            "paper_evidence_status": self.paper_evidence_status,
            "allowed_units": list(self.allowed_units),
        }


@dataclass(slots=True)
class PilotBudget:
    primary_episodes: int = 10
    follow_up_episodes: int = 25

    def __post_init__(self) -> None:
        if self.primary_episodes != 10:
            raise ValueError("PilotBudget.primary_episodes must equal 10.")
        if self.follow_up_episodes != 25:
            raise ValueError("PilotBudget.follow_up_episodes must equal 25.")

    def to_dict(self) -> dict[str, int]:
        return {
            "primary_episodes": self.primary_episodes,
            "follow_up_episodes": self.follow_up_episodes,
        }


@dataclass(slots=True)
class CampaignConfig:
    feature_id: str = FEATURE_ID
    state_dim: int = 3
    action_count: int = 3
    lookback_w: int = 10
    q_network_hidden_layers: list[int] = field(default_factory=lambda: [1024, 1024, 1024])
    lstm_num_layers: int = 1
    lstm_hidden_size: int = 20
    model_initialization_seed: int = 19
    learning_rate: float = 7e-7
    gamma: float = 0.99
    batch_size: int = 64
    replay_memory_capacity: int = 10_000
    readiness_probe_episode_count: int = 3
    readiness_probe_episode_length: int = 20
    pilot_episode_length: int = 20
    evaluation_episode_length: int = 110
    full_campaign_episode_length: int = 110
    full_campaign_budget: int = 5_000
    full_campaign_enabled: bool = False
    readiness_manual_approval_required: bool = True
    readiness_manual_approval_status: str = READINESS_MANUAL_APPROVAL_NOT_APPROVED
    readiness_manual_approval_reference: str = ""
    target_update_contract: TargetUpdateContract = field(default_factory=TargetUpdateContract)
    pilot_budget: PilotBudget = field(default_factory=PilotBudget)
    seed_bundle: CampaignSeedBundle = field(default_factory=CampaignSeedBundle)
    training_trace_bank_id: str = "full-training-train-bank"
    evaluation_trace_bank_id: str = "full-training-eval-bank"
    baseline_reference_set: tuple[str, ...] = (
        "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.json",
        "artifacts/analysis/baseline-revalidation-after-runtime-repair/baseline-revalidation-report.md",
    )
    horizontal_data_rate_mbps: float = 30.0
    vertical_data_rate_mbps: float = 10.0
    full_campaign_flag_name: str = "--enable-full-campaign"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("CampaignConfig.feature_id must equal 041-full-training-reproduction-campaign.")
        if self.state_dim <= 0:
            raise ValueError("CampaignConfig.state_dim must be positive.")
        if self.action_count <= 0:
            raise ValueError("CampaignConfig.action_count must be positive.")
        if self.lookback_w != 10:
            raise ValueError("CampaignConfig.lookback_w must equal 10.")
        if not isinstance(self.q_network_hidden_layers, list):
            raise ValueError("CampaignConfig.q_network_hidden_layers must be a list.")
        if list(self.q_network_hidden_layers) != [1024, 1024, 1024]:
            raise ValueError("CampaignConfig.q_network_hidden_layers must equal [1024, 1024, 1024].")
        if self.lstm_num_layers != 1:
            raise ValueError("CampaignConfig.lstm_num_layers must equal 1.")
        if self.lstm_hidden_size != 20:
            raise ValueError("CampaignConfig.lstm_hidden_size must equal 20.")
        if self.model_initialization_seed != 19:
            raise ValueError("CampaignConfig.model_initialization_seed must equal 19.")
        if self.learning_rate != 7e-7:
            raise ValueError("CampaignConfig.learning_rate must equal 7e-7.")
        if self.gamma != 0.99:
            raise ValueError("CampaignConfig.gamma must equal 0.99.")
        if self.batch_size != 64:
            raise ValueError("CampaignConfig.batch_size must equal 64.")
        if self.replay_memory_capacity != 10_000:
            raise ValueError("CampaignConfig.replay_memory_capacity must equal 10000.")
        if self.readiness_probe_episode_count <= 0:
            raise ValueError("CampaignConfig.readiness_probe_episode_count must be positive.")
        if self.readiness_probe_episode_length <= 0:
            raise ValueError("CampaignConfig.readiness_probe_episode_length must be positive.")
        if self.pilot_episode_length <= 0:
            raise ValueError("CampaignConfig.pilot_episode_length must be positive.")
        if self.evaluation_episode_length <= 0:
            raise ValueError("CampaignConfig.evaluation_episode_length must be positive.")
        if self.full_campaign_episode_length != 110:
            raise ValueError("CampaignConfig.full_campaign_episode_length must equal 110.")
        if self.full_campaign_budget != 5_000:
            raise ValueError("CampaignConfig.full_campaign_budget must equal 5000.")
        if self.readiness_manual_approval_required is not True:
            raise ValueError("CampaignConfig.readiness_manual_approval_required must remain true.")
        if self.readiness_manual_approval_status not in {
            READINESS_MANUAL_APPROVAL_NOT_APPROVED,
            READINESS_MANUAL_APPROVAL_PENDING,
            READINESS_MANUAL_APPROVAL_APPROVED,
            READINESS_MANUAL_APPROVAL_REJECTED,
        }:
            raise ValueError("CampaignConfig.readiness_manual_approval_status has an invalid value.")
        if self.readiness_manual_approval_status == READINESS_MANUAL_APPROVAL_APPROVED and not self.readiness_manual_approval_reference.strip():
            raise ValueError("CampaignConfig.readiness_manual_approval_status cannot be approved without readiness_manual_approval_reference.")
        if not isinstance(self.seed_bundle, CampaignSeedBundle):
            raise ValueError("seed_bundle must be a CampaignSeedBundle.")
        self.horizontal_data_rate_mbps = float(self.horizontal_data_rate_mbps)
        self.vertical_data_rate_mbps = float(self.vertical_data_rate_mbps)
        if self.horizontal_data_rate_mbps <= 0:
            raise ValueError("CampaignConfig.horizontal_data_rate_mbps must be positive.")
        if self.vertical_data_rate_mbps <= 0:
            raise ValueError("CampaignConfig.vertical_data_rate_mbps must be positive.")

    def build_network_config(self) -> PaperHoodieNetworkConfig:
        return PaperHoodieNetworkConfig.standard(
            state_dim=self.state_dim,
            action_count=self.action_count,
            model_initialization_seed=self.model_initialization_seed,
        )

    def build_link_rate_config(self) -> LinkRateConfig:
        return LinkRateConfig(
            horizontal_data_rate_mbps=self.horizontal_data_rate_mbps,
            vertical_data_rate_mbps=self.vertical_data_rate_mbps,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "state_dim": self.state_dim,
            "action_count": self.action_count,
            "lookback_w": self.lookback_w,
            "q_network_hidden_layers": list(self.q_network_hidden_layers),
            "lstm_num_layers": self.lstm_num_layers,
            "lstm_hidden_size": self.lstm_hidden_size,
            "model_initialization_seed": self.model_initialization_seed,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "batch_size": self.batch_size,
            "replay_memory_capacity": self.replay_memory_capacity,
            "readiness_probe_episode_count": self.readiness_probe_episode_count,
            "readiness_probe_episode_length": self.readiness_probe_episode_length,
            "pilot_episode_length": self.pilot_episode_length,
            "evaluation_episode_length": self.evaluation_episode_length,
            "full_campaign_episode_length": self.full_campaign_episode_length,
            "full_campaign_budget": self.full_campaign_budget,
            "full_campaign_enabled": self.full_campaign_enabled,
            "readiness_manual_approval_required": self.readiness_manual_approval_required,
            "readiness_manual_approval_status": self.readiness_manual_approval_status,
            "readiness_manual_approval_reference": self.readiness_manual_approval_reference,
            "target_update_contract": self.target_update_contract.to_dict(),
            "pilot_budget": self.pilot_budget.to_dict(),
            "seed_bundle": self.seed_bundle.to_dict(),
            "training_trace_bank_id": self.training_trace_bank_id,
            "evaluation_trace_bank_id": self.evaluation_trace_bank_id,
            "horizontal_data_rate_mbps": self.horizontal_data_rate_mbps,
            "vertical_data_rate_mbps": self.vertical_data_rate_mbps,
            "baseline_reference_set": list(self.baseline_reference_set),
            "full_campaign_flag_name": self.full_campaign_flag_name,
        }

    @staticmethod
    def paper_default() -> CampaignConfig:
        return CampaignConfig(
            feature_id="041-full-training-reproduction-campaign",
            state_dim=74,
            action_count=22,
            lookback_w=10,
            q_network_hidden_layers=[1024, 1024, 1024],
            lstm_num_layers=1,
            lstm_hidden_size=20,
            model_initialization_seed=19,
            learning_rate=7e-7,
            gamma=0.99,
            batch_size=64,
            replay_memory_capacity=10_000,
            readiness_probe_episode_count=3,
            readiness_probe_episode_length=50,
            pilot_episode_length=50,
            evaluation_episode_length=50,
            full_campaign_episode_length=110,
            full_campaign_budget=5_000,
            full_campaign_enabled=False,
            readiness_manual_approval_required=True,
            readiness_manual_approval_status="approved",
            readiness_manual_approval_reference="paper-default-smoke-campaign-approved",
            horizontal_data_rate_mbps=30.0,
            vertical_data_rate_mbps=10.0,
        )
