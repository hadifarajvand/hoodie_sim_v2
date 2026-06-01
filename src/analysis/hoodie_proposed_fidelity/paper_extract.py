from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import BASE_PAPER_TARGET, REQUIRED_COMPONENT_IDS, SOURCE_OCR, SOURCE_PDF


@dataclass(frozen=True, slots=True)
class PaperComponentDefinition:
    component_id: str
    component_name: str
    paper_definition: str
    paper_source: str


def _definition(component_id: str, component_name: str, paper_definition: str, paper_source: str) -> PaperComponentDefinition:
    return PaperComponentDefinition(
        component_id=component_id,
        component_name=component_name,
        paper_definition=paper_definition,
        paper_source=f"{SOURCE_PDF}; {SOURCE_OCR} ({paper_source})",
    )


def extract_paper_components() -> tuple[PaperComponentDefinition, ...]:
    return (
        _definition(
            "system_model",
            "system_model",
            "Three-layer IoT-to-Edge-to-Cloud system with N edge agents and one cloud; tasks are non-divisible and each edge agent owns the tasks from its IoT area.",
            "pp. 5-7, system architecture and task model",
        ),
        _definition(
            "architecture",
            "architecture",
            "The architecture is a three-layer cloud-edge continuum with edge agents, edge controllers, and a cloud connected across the continuum.",
            "pp. 5-7, Fig. 1 and edge-controller description",
        ),
        _definition(
            "edge_agents",
            "edge_agents",
            "Each edge agent has dual behavior: it can process local tasks and host externally offloaded tasks while operating in a distributed DRL setup.",
            "pp. 6-7 and pp. 8-9, dual-role edge-agent discussion",
        ),
        _definition(
            "state_space",
            "state_space",
            "The state vector combines local task features with forecasted load values from previous load history via an LSTM forecast input.",
            "pp. 7-8, state table and LSTM load-history description",
        ),
        _definition(
            "action_space",
            "action_space",
            "The action space is hybrid: local processing or offloading, followed by a destination decision among horizontal edge and vertical cloud options.",
            "pp. 5-7, DM(1)/DM(2) action model and action-vector definition",
        ),
        _definition(
            "reward_cost",
            "reward_cost",
            "Reward is NaN when no task arrives, -Phi_n(t) on successful processing, and -C when the task is thrown; Phi_n splits into private and public/offloaded delay cost.",
            "pp. 7-8, reward equations (20), (24), (25)",
        ),
        _definition(
            "private_queue",
            "private_queue",
            "The private queue is FIFO; waiting time depends on the previous maximum completion slot and task completion is limited by the timeout.",
            "pp. 6-7, private queue model and waiting-time derivation",
        ),
        _definition(
            "offloading_queue",
            "offloading_queue",
            "The offloading queue is FIFO; horizontal and vertical transmission rates determine offloading completion, with task completion limited by timeout.",
            "pp. 6-7, offloading queue model and link-rate equations",
        ),
        _definition(
            "public_queue",
            "public_queue",
            "Each edge agent has public queues for external tasks and the cloud has public queues for tasks forwarded from edge agents.",
            "pp. 6-7, public queue and cloud queue descriptions",
        ),
        _definition(
            "dqn_training",
            "dqn_training",
            "Training uses distributed DQN-style learning with episodes, replay memory, target-network updates, and gradient-descent optimization.",
            "pp. 7-10, Algorithm 1, training section, Table 4",
        ),
        _definition(
            "double_dqn",
            "double_dqn",
            "Double-DQN is used to compute targets during training for better stability.",
            "pp. 7-8, training algorithm and Double DQL target update",
        ),
        _definition(
            "dueling_dqn",
            "dueling_dqn",
            "The Q-network includes an advantage/value decomposition consistent with dueling DQL.",
            "pp. 7-8, A&V layer and dueling DQL description",
        ),
        _definition(
            "lstm_forecast",
            "lstm_forecast",
            "An LSTM forecasts the next-slot load of each node from a W-step history.",
            "pp. 7-9, Fig. 5 and LSTM load forecast section",
        ),
        _definition(
            "replay_memory",
            "replay_memory",
            "Experience tuples are stored in replay memory and random batches are sampled during training.",
            "pp. 7-8, Algorithm 1 and replay-memory description",
        ),
        _definition(
            "inference",
            "inference",
            "Inference deploys the Q-model only, with epsilon forced to zero so the agent acts exploitatively.",
            "pp. 8-9, inference phase and epsilon-greedy discussion",
        ),
        _definition(
            "pubsub_recovery",
            "pubsub_recovery",
            "Inter-agent communication uses Pub-Sub brokers managed by edge controllers, and delayed messages can be recovered with previous LSTM outputs.",
            "pp. 9-10, Pub-Sub protocol and recovery mechanism",
        ),
        _definition(
            "baselines",
            "baselines",
            "The evaluation compares HOODIE against baselines such as FLC, VO, HO, RO, BCO, and MLEO.",
            "pp. 10-11, comparative evaluation section",
        ),
        _definition(
            "metrics",
            "metrics",
            "The paper reports average delay, drop ratio, cumulative reward, and related validation metrics across training and comparative experiments.",
            "pp. 10-11, evaluation metrics and figures 8-11",
        ),
        _definition(
            "simulation_parameters",
            "simulation_parameters",
            "The paper reports Table 4 simulation and training parameters, including rates, topology, timeouts, episodes, learning rate, gamma, replay memory, and batch size.",
            "pp. 10-11, Table 4 and simulation setup",
        ),
    )


def paper_component_ids() -> tuple[str, ...]:
    return tuple(definition.component_id for definition in extract_paper_components())


def validate_paper_extraction() -> tuple[str, ...]:
    extracted = paper_component_ids()
    if extracted != REQUIRED_COMPONENT_IDS:
        raise ValueError("paper extraction does not cover the required component set")
    return extracted
