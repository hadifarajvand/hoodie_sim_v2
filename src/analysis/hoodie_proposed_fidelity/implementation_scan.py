from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import BASE_PAPER_TARGET


@dataclass(frozen=True, slots=True)
class ImplementationObservation:
    component_id: str
    current_implementation: str
    implementation_reference: str
    status: str
    gap: str
    required_repair: str

    def to_dict(self) -> dict[str, object]:
        return {
            "component_id": self.component_id,
            "current_implementation": self.current_implementation,
            "implementation_reference": self.implementation_reference,
            "status": self.status,
            "gap": self.gap,
            "required_repair": self.required_repair,
        }


_OBSERVATIONS: tuple[ImplementationObservation, ...] = (
    ImplementationObservation(
        component_id="system_model",
        current_implementation="Scenario profiles and campaign execution context capture the base-paper system only as deterministic fixtures, not as a full evolving simulator.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py::_scenario_action_profiles; src/analysis/campaign_execution_engine/report.py::_decorate_context",
        status="partial",
        gap="partial_runtime",
        required_repair="Build an explicit runtime system-state model that tracks arrivals, deadlines, and per-node resources over time slots.",
    ),
    ImplementationObservation(
        component_id="architecture",
        current_implementation="The codebase splits readiness, execution, and aggregation into separate analysis packages, but it does not expose a single HOODIE architecture model.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py; src/analysis/result_aggregation_statistical_summary/aggregator.py",
        status="partial",
        gap="missing_model_architecture",
        required_repair="Introduce a first-class architecture model for the IoT/EA/EC/Cloud topology and its message routes.",
    ),
    ImplementationObservation(
        component_id="edge_agents",
        current_implementation="Per-agent behavior exists as policy-facing context and action-bound execution, but the simulator lacks stateful distributed DRL agent objects.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py",
        status="partial",
        gap="partial_runtime",
        required_repair="Represent each edge agent as a stateful actor with local observation, action selection, and peer communication hooks.",
    ),
    ImplementationObservation(
        component_id="state_space",
        current_implementation="The implementation records local task features, load history, deadline slack, and queue/load evidence, but it does not build the full paper state vector.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py::_candidate_context; src/analysis/campaign_execution_engine/report.py::_decorate_context",
        status="partial",
        gap="partial_runtime",
        required_repair="Construct the full paper state vector from task features, load history, and forecasted next-slot load inputs.",
    ),
    ImplementationObservation(
        component_id="action_space",
        current_implementation="The active path exposes the paper action families local, horizontal, and vertical and binds selected actions to action-legality and terminal outcomes.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/model.py; src/analysis/proposed_method_integration_readiness/report.py; src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",
        status="implemented",
        gap="none",
        required_repair="No repair required at the action-family level; keep the paper action contract aligned if training is added later.",
    ),
    ImplementationObservation(
        component_id="reward_cost",
        current_implementation="Paper-like delay and drop penalties are surfaced through action-bound outcomes and runtime reports, but the full reward pipeline is not the paper's training loop.",
        implementation_reference="src/environment/paper_timeout.py; src/environment/reward_timing.py; src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py",
        status="partial",
        gap="partial_runtime",
        required_repair="Expose the exact reward helper end-to-end, including NaN omission for no-task slots and the paper's cost branches for success and drops.",
    ),
    ImplementationObservation(
        component_id="private_queue",
        current_implementation="Local processing is represented by action-bound completion logic, but the code does not simulate the paper's FIFO private queue semantics.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/environment/reward_timing.py",
        status="partial",
        gap="missing_queue_semantics",
        required_repair="Implement the FIFO private queue with waiting-time and completion-time formulas from the paper.",
    ),
    ImplementationObservation(
        component_id="offloading_queue",
        current_implementation="Horizontal and vertical choices are represented by action outcomes, but there is no explicit FIFO offloading queue simulation.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py",
        status="partial",
        gap="missing_queue_semantics",
        required_repair="Implement the FIFO offloading queue and compute transmission completion using the paper's horizontal and vertical rates.",
    ),
    ImplementationObservation(
        component_id="public_queue",
        current_implementation="Destination selection and public-queue references exist in helper context and execution provenance, but public queues are not modeled as explicit runtime queues.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py",
        status="partial",
        gap="missing_queue_semantics",
        required_repair="Represent destination public queues and cloud public queues as explicit runtime structures that receive offloaded tasks.",
    ),
    ImplementationObservation(
        component_id="dqn_training",
        current_implementation="No active HOODIE_PROPOSED training loop exists; the codebase only has adjacent training scaffolds in separate analysis packages.",
        implementation_reference="src/analysis/distributed_multi_agent_hoodie_training/*; src/analysis/paper_hoodie_network_implementation/network.py",
        status="missing",
        gap="missing_training",
        required_repair="Add a real multi-agent training loop that records experience tuples, trains Q-models, and follows the paper's episode structure.",
    ),
    ImplementationObservation(
        component_id="double_dqn",
        current_implementation="The active HOODIE_PROPOSED path does not implement Double-DQN target computation; only paper text and adjacent scaffolding refer to it.",
        implementation_reference="src/analysis/distributed_multi_agent_hoodie_training/*; resources/papers/hoodie/ocr/merged.txt",
        status="missing",
        gap="missing_training",
        required_repair="Wire Double-DQN target selection into the training loop and expose the same target-update path in the fidelity layer.",
    ),
    ImplementationObservation(
        component_id="dueling_dqn",
        current_implementation="The active HOODIE_PROPOSED path does not implement the dueling value/advantage network; only the paper and adjacent scaffolding mention it.",
        implementation_reference="src/analysis/paper_hoodie_network_implementation/network.py; src/analysis/distributed_multi_agent_hoodie_training/*",
        status="missing",
        gap="missing_training",
        required_repair="Add the advantage/value architecture and connect it to the agent network definition.",
    ),
    ImplementationObservation(
        component_id="lstm_forecast",
        current_implementation="The active HOODIE_PROPOSED path uses deterministic scenario readiness profiles, not an LSTM forecast model.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/distributed_multi_agent_hoodie_training/*",
        status="missing",
        gap="missing_model_architecture",
        required_repair="Add the LSTM load-forecast module and feed its predictions into the state vector construction.",
    ),
    ImplementationObservation(
        component_id="replay_memory",
        current_implementation="No replay-memory implementation exists in the active HOODIE_PROPOSED path; replay scaffolding appears only in adjacent training packages.",
        implementation_reference="src/analysis/distributed_multi_agent_hoodie_training/replay.py",
        status="missing",
        gap="missing_training",
        required_repair="Persist experience tuples and support random batch sampling for training updates.",
    ),
    ImplementationObservation(
        component_id="inference",
        current_implementation="Deployment behavior is represented by deterministic candidate selection and action-bound runtime execution rather than Q-model inference.",
        implementation_reference="src/analysis/proposed_method_integration_readiness/report.py; src/analysis/campaign_execution_engine/report.py",
        status="partial",
        gap="partial_runtime",
        required_repair="Replace heuristic candidate selection with actual Q-model inference and enforce epsilon=0 for deployment-mode behavior.",
    ),
    ImplementationObservation(
        component_id="pubsub_recovery",
        current_implementation="The active HOODIE_PROPOSED path does not implement Pub-Sub brokers or delayed-message recovery.",
        implementation_reference="src/analysis/distributed_multi_agent_hoodie_training/coordinator.py; resources/papers/hoodie/ocr/merged.txt",
        status="missing",
        gap="missing_communication",
        required_repair="Add brokered Pub-Sub communication and the LSTM-based delayed-message recovery path described in the paper.",
    ),
    ImplementationObservation(
        component_id="baselines",
        current_implementation="Baseline methods are present as comparative policies outside the proposed-method path, so they are evaluation context rather than HOODIE_PROPOSED internals.",
        implementation_reference="src/policies/*; src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",
        status="not_applicable",
        gap="not_applicable",
        required_repair="No repair inside HOODIE_PROPOSED; baselines belong to comparison layers, not the proposed method itself.",
    ),
    ImplementationObservation(
        component_id="metrics",
        current_implementation="Delay, drop, reward, and aggregate metrics are present in the readiness/execution/aggregation layers, but the paper's full metric set is not surfaced as a dedicated fidelity layer.",
        implementation_reference="src/analysis/campaign_execution_engine/report.py; src/analysis/result_aggregation_statistical_summary/aggregator.py; src/analysis/combined_baseline_proposed_comparative_readiness/report.py",
        status="partial",
        gap="partial_runtime",
        required_repair="Expose the paper metrics directly from the runtime layer and keep auxiliary summaries separate from the fidelity matrix.",
    ),
    ImplementationObservation(
        component_id="simulation_parameters",
        current_implementation="The simulator has campaign-level dimensions and deterministic seeds, but it does not encode the paper's Table 4 parameter set end-to-end.",
        implementation_reference="src/analysis/campaign_execution_engine/config.py; src/analysis/result_aggregation_statistical_summary/config.py; src/analysis/proposed_method_integration_readiness/report.py",
        status="partial",
        gap="partial_runtime",
        required_repair="Consolidate the paper's Table 4 parameters into a traceable runtime configuration for the proposed-method path.",
    ),
)


def scan_current_implementation() -> tuple[ImplementationObservation, ...]:
    return _OBSERVATIONS


def observation_by_component_id(component_id: str) -> ImplementationObservation:
    for observation in _OBSERVATIONS:
        if observation.component_id == component_id:
            return observation
    raise KeyError(component_id)
