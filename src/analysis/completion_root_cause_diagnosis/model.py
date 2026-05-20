from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Any

from .config import ROOT_CAUSE_CLASSES


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
SEVERITY_ORDER = {
    "runtime": 3,
    "formula": 3,
    "action_exposure": 2,
    "configuration_or_load": 2,
    "inconclusive": 1,
    "no_issue": 1,
}


@dataclass(frozen=True, slots=True)
class TaskLifecycleReconstruction:
    run_id: str
    strategy: str
    seed: int
    task_id: int
    arrival_slot: int | None
    absolute_deadline_slot: int | None
    size_mbits: float | None
    processing_density_gcycles_per_mbit: float | None
    cycles_required_gcycles: float | None
    generated_slot: int | None
    admitted_slot: int | None
    selected_action: str | None
    destination: str | None
    queue_type: str | None
    host_node_id: str | None
    transmission_started_at: int | None
    transmission_completed_at: int | None
    execution_started_at: int | None
    execution_progress_slots: list[int] = field(default_factory=list)
    execution_completed_at: int | None = None
    deadline_reached_at: int | None = None
    deadline_expired_at: int | None = None
    task_completed_at: int | None = None
    task_dropped_at: int | None = None
    pending_at_horizon_at: int | None = None
    reward_emitted_at: int | None = None
    terminal_outcome: str | None = None
    reward: float | None = None
    remaining_cycles_by_slot: dict[int, float] = field(default_factory=dict)
    task_age_by_slot: dict[int, int] = field(default_factory=dict)
    queue_wait_time_slots: int | None = None
    completed_before_deadline: bool | None = None
    deadline_or_drop_before_completion: bool | None = None
    reward_after_terminal_outcome: bool | None = None
    trace_event_types: list[str] = field(default_factory=list)
    trace_source_components: list[str] = field(default_factory=list)
    evidence_notes: list[str] = field(default_factory=list)
    source_event_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "strategy": self.strategy,
            "seed": self.seed,
            "task_id": self.task_id,
            "arrival_slot": self.arrival_slot,
            "absolute_deadline_slot": self.absolute_deadline_slot,
            "size_mbits": self.size_mbits,
            "processing_density_gcycles_per_mbit": self.processing_density_gcycles_per_mbit,
            "cycles_required_gcycles": self.cycles_required_gcycles,
            "generated_slot": self.generated_slot,
            "admitted_slot": self.admitted_slot,
            "selected_action": self.selected_action,
            "destination": self.destination,
            "queue_type": self.queue_type,
            "host_node_id": self.host_node_id,
            "transmission_started_at": self.transmission_started_at,
            "transmission_completed_at": self.transmission_completed_at,
            "execution_started_at": self.execution_started_at,
            "execution_progress_slots": list(self.execution_progress_slots),
            "execution_completed_at": self.execution_completed_at,
            "deadline_reached_at": self.deadline_reached_at,
            "deadline_expired_at": self.deadline_expired_at,
            "task_completed_at": self.task_completed_at,
            "task_dropped_at": self.task_dropped_at,
            "pending_at_horizon_at": self.pending_at_horizon_at,
            "reward_emitted_at": self.reward_emitted_at,
            "terminal_outcome": self.terminal_outcome,
            "reward": self.reward,
            "remaining_cycles_by_slot": {str(slot): value for slot, value in sorted(self.remaining_cycles_by_slot.items())},
            "task_age_by_slot": {str(slot): value for slot, value in sorted(self.task_age_by_slot.items())},
            "queue_wait_time_slots": self.queue_wait_time_slots,
            "completed_before_deadline": self.completed_before_deadline,
            "deadline_or_drop_before_completion": self.deadline_or_drop_before_completion,
            "reward_after_terminal_outcome": self.reward_after_terminal_outcome,
            "trace_event_types": list(self.trace_event_types),
            "trace_source_components": list(self.trace_source_components),
            "evidence_notes": list(self.evidence_notes),
            "source_event_count": self.source_event_count,
        }


@dataclass(frozen=True, slots=True)
class RootCauseEvaluation:
    root_cause_class: str
    evaluated: bool
    detected: bool
    evidence_count: int
    supporting_event_types: list[str]
    representative_task_ids: list[str]
    explanation: str
    confidence: str
    required_next_action: str

    def __post_init__(self) -> None:
        if self.root_cause_class not in ROOT_CAUSE_CLASSES:
            raise ValueError(f"Unsupported root cause class: {self.root_cause_class}")
        if self.confidence not in CONFIDENCE_ORDER:
            raise ValueError("confidence must be low, medium, or high")

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_cause_class": self.root_cause_class,
            "evaluated": self.evaluated,
            "detected": self.detected,
            "evidence_count": self.evidence_count,
            "supporting_event_types": list(self.supporting_event_types),
            "representative_task_ids": list(self.representative_task_ids),
            "explanation": self.explanation,
            "confidence": self.confidence,
            "required_next_action": self.required_next_action,
        }


class TaskLifecycleReconstructor:
    @staticmethod
    def reconstruct(run_id: str, strategy: str, seed: int, events: list[dict[str, Any]]) -> list[TaskLifecycleReconstruction]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            task_id = event.get("task_id")
            if task_id is None:
                continue
            grouped.setdefault(str(task_id), []).append(event)
        reconstructions: list[TaskLifecycleReconstruction] = []
        for task_id, task_events in grouped.items():
            enumerated = list(enumerate(task_events))
            enumerated.sort(key=lambda item: (int(item[1].get("slot", 0)), item[0]))
            task_events = [item[1] for item in enumerated]
            reconstructions.append(TaskLifecycleReconstructor._from_task_events(run_id, strategy, seed, int(task_id), task_events))
        reconstructions.sort(key=lambda item: (item.generated_slot if item.generated_slot is not None else 10**9, item.task_id))
        return reconstructions

    @staticmethod
    def _from_task_events(run_id: str, strategy: str, seed: int, task_id: int, events: list[dict[str, Any]]) -> TaskLifecycleReconstruction:
        first = events[0] if events else {}
        generated_slot = None
        admitted_slot = None
        selected_action = None
        destination = None
        queue_type = None
        host_node_id = None
        transmission_started_at = None
        transmission_completed_at = None
        execution_started_at = None
        execution_completed_at = None
        deadline_reached_at = None
        deadline_expired_at = None
        task_completed_at = None
        task_dropped_at = None
        pending_at_horizon_at = None
        reward_emitted_at = None
        terminal_outcome = None
        reward = None
        execution_progress_slots: list[int] = []
        remaining_cycles_by_slot: dict[int, float] = {}
        task_age_by_slot: dict[int, int] = {}
        trace_event_types: list[str] = []
        trace_source_components: list[str] = []
        evidence_notes: list[str] = []
        for event in events:
            event_type = str(event.get("event_type", ""))
            slot = int(event.get("slot", 0))
            trace_event_types.append(event_type)
            component = str(event.get("trace_source_component", ""))
            if component:
                trace_source_components.append(component)
            task_age = event.get("task_age_slots")
            if isinstance(task_age, int):
                task_age_by_slot[slot] = task_age
            cycles_after = event.get("cycles_after_gcycles")
            if isinstance(cycles_after, (int, float)):
                remaining_cycles_by_slot[slot] = float(cycles_after)
            if event_type == "task_generated":
                generated_slot = slot
                selected_action = selected_action or event.get("selected_action")
                destination = destination or event.get("destination")
                queue_type = queue_type or event.get("queue_type")
                host_node_id = host_node_id or event.get("host_node_id")
            elif event_type == "task_admitted":
                admitted_slot = slot
                selected_action = selected_action or event.get("selected_action")
                destination = destination or event.get("destination")
                queue_type = queue_type or event.get("queue_type")
                host_node_id = host_node_id or event.get("host_node_id")
            elif event_type == "transmission_started":
                transmission_started_at = transmission_started_at or slot
            elif event_type == "transmission_completed":
                transmission_completed_at = transmission_completed_at or slot
            elif event_type == "execution_started":
                execution_started_at = execution_started_at or slot
            elif event_type == "execution_progress":
                execution_progress_slots.append(slot)
                execution_started_at = execution_started_at or slot
            elif event_type == "execution_completed":
                execution_completed_at = execution_completed_at or slot
                terminal_outcome = terminal_outcome or event.get("terminal_outcome")
            elif event_type == "deadline_reached":
                deadline_reached_at = deadline_reached_at or slot
                terminal_outcome = terminal_outcome or event.get("terminal_outcome")
            elif event_type == "deadline_expired":
                deadline_expired_at = deadline_expired_at or slot
                terminal_outcome = terminal_outcome or event.get("terminal_outcome")
            elif event_type == "task_completed":
                task_completed_at = task_completed_at or slot
                terminal_outcome = terminal_outcome or event.get("terminal_outcome")
                reward = reward if reward is not None else event.get("reward")
            elif event_type == "task_dropped":
                task_dropped_at = task_dropped_at or slot
                terminal_outcome = terminal_outcome or event.get("terminal_outcome")
                reward = reward if reward is not None else event.get("reward")
            elif event_type == "pending_at_horizon":
                pending_at_horizon_at = pending_at_horizon_at or slot
            elif event_type == "reward_emitted":
                reward_emitted_at = reward_emitted_at or slot
                reward = reward if reward is not None else event.get("reward")
            if event_type in {"task_dropped", "task_completed"}:
                evidence_notes.append(f"terminal:{event_type}@{slot}")
        completed_before_deadline = None
        if task_completed_at is not None and first.get("absolute_deadline_slot") is not None:
            completed_before_deadline = task_completed_at <= int(first["absolute_deadline_slot"])
        deadline_or_drop_before_completion = None
        if task_dropped_at is not None and task_completed_at is not None:
            deadline_or_drop_before_completion = task_dropped_at <= task_completed_at
        elif task_dropped_at is not None:
            deadline_or_drop_before_completion = True
        reward_after_terminal_outcome = None
        if reward_emitted_at is not None and (task_completed_at is not None or task_dropped_at is not None):
            terminal_slot = task_completed_at if task_completed_at is not None else task_dropped_at
            reward_after_terminal_outcome = reward_emitted_at >= int(terminal_slot or reward_emitted_at)
        queue_wait_time_slots = None
        if generated_slot is not None and admitted_slot is not None:
            queue_wait_time_slots = max(0, admitted_slot - generated_slot)
        return TaskLifecycleReconstruction(
            run_id=run_id,
            strategy=strategy,
            seed=seed,
            task_id=task_id,
            arrival_slot=int(first.get("arrival_slot")) if first.get("arrival_slot") is not None else None,
            absolute_deadline_slot=int(first.get("absolute_deadline_slot")) if first.get("absolute_deadline_slot") is not None else None,
            size_mbits=float(first.get("size_mbits")) if first.get("size_mbits") is not None else None,
            processing_density_gcycles_per_mbit=float(first.get("processing_density_gcycles_per_mbit")) if first.get("processing_density_gcycles_per_mbit") is not None else None,
            cycles_required_gcycles=float(first.get("cycles_required_gcycles")) if first.get("cycles_required_gcycles") is not None else None,
            generated_slot=generated_slot,
            admitted_slot=admitted_slot,
            selected_action=selected_action,
            destination=destination,
            queue_type=queue_type,
            host_node_id=host_node_id,
            transmission_started_at=transmission_started_at,
            transmission_completed_at=transmission_completed_at,
            execution_started_at=execution_started_at,
            execution_progress_slots=execution_progress_slots,
            execution_completed_at=execution_completed_at,
            deadline_reached_at=deadline_reached_at,
            deadline_expired_at=deadline_expired_at,
            task_completed_at=task_completed_at,
            task_dropped_at=task_dropped_at,
            pending_at_horizon_at=pending_at_horizon_at,
            reward_emitted_at=reward_emitted_at,
            terminal_outcome=terminal_outcome,
            reward=float(reward) if reward is not None else None,
            remaining_cycles_by_slot=remaining_cycles_by_slot,
            task_age_by_slot=task_age_by_slot,
            queue_wait_time_slots=queue_wait_time_slots,
            completed_before_deadline=completed_before_deadline,
            deadline_or_drop_before_completion=deadline_or_drop_before_completion,
            reward_after_terminal_outcome=reward_after_terminal_outcome,
            trace_event_types=trace_event_types,
            trace_source_components=trace_source_components,
            evidence_notes=evidence_notes,
            source_event_count=len(events),
        )


class RootCauseClassifier:
    @staticmethod
    def _confidence(count: int, total: int, *, strong_threshold: float = 0.25, medium_threshold: float = 0.1) -> str:
        if total <= 0 or count <= 0:
            return "low"
        ratio = count / float(total)
        if ratio >= strong_threshold:
            return "high"
        if ratio >= medium_threshold:
            return "medium"
        return "low"

    @staticmethod
    def _evaluation(
        *,
        root_cause_class: str,
        detected: bool,
        evidence_count: int,
        supporting_event_types: list[str],
        representative_task_ids: list[str],
        explanation: str,
        confidence: str,
        required_next_action: str,
    ) -> RootCauseEvaluation:
        return RootCauseEvaluation(
            root_cause_class=root_cause_class,
            evaluated=True,
            detected=detected,
            evidence_count=evidence_count,
            supporting_event_types=supporting_event_types,
            representative_task_ids=representative_task_ids,
            explanation=explanation,
            confidence=confidence,
            required_next_action=required_next_action,
        )

    @staticmethod
    def classify_queue_pressure(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [str(task.task_id) for task in lifecycles if task.queue_wait_time_slots is not None and task.queue_wait_time_slots >= 1 and task.terminal_outcome == "dropped"]
        detected = len(candidate_ids) >= max(1, summary["dropped_count"] // 4)
        return RootCauseClassifier._evaluation(
            root_cause_class="queue_pressure",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_admitted", "execution_progress", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation="Dropped tasks spend measurable time waiting in private or shared queues before reaching terminal state.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="audit queue pressure and load balancing before considering runtime repair",
        )

    @staticmethod
    def classify_task_generation_admission_overload(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [str(task.task_id) for task in lifecycles if task.pending_at_horizon_at is not None or (task.queue_wait_time_slots is not None and task.queue_wait_time_slots >= 2)]
        detected = summary["pending_at_horizon_count"] > 0 and summary["dropped_count"] > summary["completed_count"]
        return RootCauseClassifier._evaluation(
            root_cause_class="task_generation_admission_overload",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_generated", "task_admitted", "pending_at_horizon"],
            representative_task_ids=candidate_ids[:5],
            explanation="Generation and admission progress faster than the system can retire work within the paper-default horizon.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="audit arrival/load configuration and admission pressure",
        )

    @staticmethod
    def classify_action_exposure_bias(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        action_counts = summary["action_counts"]
        total_actions = sum(action_counts.values())
        if total_actions <= 0:
            return RootCauseClassifier._evaluation(
                root_cause_class="action_exposure_bias",
                detected=False,
                evidence_count=0,
                supporting_event_types=["task_admitted"],
                representative_task_ids=[],
                explanation="No action data were collected.",
                confidence="low",
                required_next_action="collect action exposure evidence",
            )
        dominant_action, dominant_count = max(action_counts.items(), key=lambda item: item[1])
        share = dominant_count / float(total_actions)
        detected = share >= 0.6 and len({task.selected_action for task in lifecycles if task.selected_action}) > 1
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.selected_action == dominant_action and task.terminal_outcome == "dropped"]
        return RootCauseClassifier._evaluation(
            root_cause_class="action_exposure_bias",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_admitted", "execution_progress", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation=f"Action usage is dominated by {dominant_action!r} but this alone does not explain the completion pattern unless completion rates diverge materially.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), total_actions),
            required_next_action="adjust observation vectors or exploration if action exposure appears to suppress viable paths",
        )

    @staticmethod
    def classify_local_private_queue_blockage(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.queue_type == "private" and task.terminal_outcome == "dropped" and (task.queue_wait_time_slots or 0) >= 1]
        detected = len(candidate_ids) >= max(1, summary["dropped_count"] // 6)
        return RootCauseClassifier._evaluation(
            root_cause_class="local_private_queue_blockage",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_admitted", "execution_started", "execution_progress", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation="Local/private tasks pile up long enough to expire before completion on a meaningful subset of runs.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="audit local/private queue pressure and service rate assumptions",
        )

    @staticmethod
    def classify_public_cloud_queue_blockage(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.queue_type in {"public", "cloud"} and task.terminal_outcome == "dropped" and (task.queue_wait_time_slots or 0) >= 1]
        detected = len(candidate_ids) >= max(1, summary["dropped_count"] // 6)
        return RootCauseClassifier._evaluation(
            root_cause_class="public_cloud_queue_blockage",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["transmission_started", "transmission_completed", "execution_progress", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation="Offloaded work accumulates in public/cloud queues long enough to miss the useful completion window.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="audit public/cloud queue sharing and service rates",
        )

    @staticmethod
    def classify_transmission_delay_admission_mismatch(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [
            f"{task.run_id}:{task.task_id}"
            for task in lifecycles
            if task.queue_type in {"offloading", "public", "cloud"}
            and task.transmission_completed_at is not None
            and task.execution_started_at is not None
            and task.task_dropped_at is not None
            and (task.transmission_completed_at >= task.deadline_expired_at if task.deadline_expired_at is not None else False)
        ]
        detected = len(candidate_ids) > 0 and summary["dropped_count"] > summary["completed_count"]
        return RootCauseClassifier._evaluation(
            root_cause_class="transmission_delay_admission_mismatch",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["transmission_started", "transmission_completed", "execution_started", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation="Transmission plus queue admission consumes the useful budget for a non-trivial subset of offloaded tasks.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="audit transmission-delay and admission timing assumptions",
        )

    @staticmethod
    def classify_execution_progress_deadline_expires_first(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.execution_progress_slots and task.task_dropped_at is not None and not task.completed_before_deadline]
        detected = len(candidate_ids) > 0
        return RootCauseClassifier._evaluation(
            root_cause_class="execution_progress_deadline_expires_first",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["execution_progress", "deadline_reached", "deadline_expired", "task_dropped"],
            representative_task_ids=candidate_ids[:5],
            explanation="Some tasks make measurable execution progress but the deadline drops them before completion can finish.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="consider runtime repair only if progress is lost despite adequate budget",
        )

    @staticmethod
    def classify_completion_emitted_but_reward_or_counter_path_wrong(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.task_completed_at is not None and (task.reward_emitted_at is None or task.reward_after_terminal_outcome is False)]
        detected = len(candidate_ids) > 0
        return RootCauseClassifier._evaluation(
            root_cause_class="completion_emitted_but_reward_or_counter_path_wrong",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_completed", "reward_emitted"],
            representative_task_ids=candidate_ids[:5],
            explanation="Completion exists but the reward/counter path fails to reflect it correctly.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="repair the runtime reward/counter path if this appears in the evidence",
        )

    @staticmethod
    def classify_completion_reward_counter_mismatch(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        return RootCauseClassifier.classify_completion_emitted_but_reward_or_counter_path_wrong(lifecycles, summary)

    @staticmethod
    def classify_deadline_drop_ordering_issue(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.task_dropped_at is not None and task.deadline_expired_at is not None and task.deadline_expired_at > task.task_dropped_at]
        detected = len(candidate_ids) > 0
        return RootCauseClassifier._evaluation(
            root_cause_class="deadline_drop_ordering_issue",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["deadline_reached", "deadline_expired", "task_dropped", "reward_emitted"],
            representative_task_ids=candidate_ids[:5],
            explanation="Deadline/drop/reward ordering violates the expected passive trace sequence.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="repair deadline/drop ordering in the runtime only if the ordering is actually violated",
        )

    @staticmethod
    def classify_formula_unit_mismatch(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        mismatch_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.cycles_required_gcycles is not None and task.size_mbits is not None and round(task.size_mbits * task.processing_density_gcycles_per_mbit, 6) != round(task.cycles_required_gcycles, 6)]
        detected = len(mismatch_ids) > 0 or not summary["formula_consistency_ok"]
        return RootCauseClassifier._evaluation(
            root_cause_class="formula_unit_mismatch",
            detected=detected,
            evidence_count=len(mismatch_ids),
            supporting_event_types=["task_generated", "execution_progress"],
            representative_task_ids=mismatch_ids[:5],
            explanation="No evidence indicates that the unit conversion or cycles formula is drifting from the paper-default contract.",
            confidence="low",
            required_next_action="audit the formula contract only if future evidence shows a mismatch",
        )

    @staticmethod
    def classify_no_completion_problem_detected(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        detected = summary["completed_count"] > 0 and summary["dropped_count"] > 0 and not summary["runtime_bug_detected"]
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if task.task_completed_at is not None]
        return RootCauseClassifier._evaluation(
            root_cause_class="no_completion_problem_detected",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_completed", "reward_emitted"],
            representative_task_ids=candidate_ids[:5],
            explanation="Completions do occur under paper-default traces; the problem is weakness, not total absence.",
            confidence=RootCauseClassifier._confidence(len(candidate_ids), len(lifecycles)),
            required_next_action="no runtime repair needed for absence alone; continue with load/configuration review",
        )

    @staticmethod
    def classify_inconclusive_trace_evidence(lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> RootCauseEvaluation:
        detected = not summary["trace_depth_ok"]
        candidate_ids = [f"{task.run_id}:{task.task_id}" for task in lifecycles if not task.trace_event_types]
        return RootCauseClassifier._evaluation(
            root_cause_class="inconclusive_trace_evidence",
            detected=detected,
            evidence_count=len(candidate_ids),
            supporting_event_types=["task_generated", "task_admitted"],
            representative_task_ids=candidate_ids[:5],
            explanation="Trace depth is sufficient to distinguish terminal ordering, so inconclusive evidence is not the dominant explanation.",
            confidence="low",
            required_next_action="increase trace depth only if future data lose lifecycle ordering evidence",
        )

    @classmethod
    def evaluate_all(cls, lifecycles: list[TaskLifecycleReconstruction], summary: dict[str, Any]) -> list[RootCauseEvaluation]:
        evaluations = [
            cls.classify_queue_pressure(lifecycles, summary),
            cls.classify_task_generation_admission_overload(lifecycles, summary),
            cls.classify_action_exposure_bias(lifecycles, summary),
            cls.classify_local_private_queue_blockage(lifecycles, summary),
            cls.classify_public_cloud_queue_blockage(lifecycles, summary),
            cls.classify_transmission_delay_admission_mismatch(lifecycles, summary),
            cls.classify_execution_progress_deadline_expires_first(lifecycles, summary),
            cls.classify_completion_emitted_but_reward_or_counter_path_wrong(lifecycles, summary),
            cls.classify_deadline_drop_ordering_issue(lifecycles, summary),
            cls.classify_formula_unit_mismatch(lifecycles, summary),
            cls.classify_no_completion_problem_detected(lifecycles, summary),
            cls.classify_inconclusive_trace_evidence(lifecycles, summary),
        ]
        return evaluations

    @staticmethod
    def rank(evaluations: list[RootCauseEvaluation]) -> list[RootCauseEvaluation]:
        return sorted(
            [evaluation for evaluation in evaluations if evaluation.detected],
            key=lambda evaluation: (
                evaluation.evidence_count,
                CONFIDENCE_ORDER[evaluation.confidence],
                SEVERITY_ORDER.get(_severity_bucket_for_class(evaluation.root_cause_class), 1),
            ),
            reverse=True,
        )


def _severity_bucket_for_class(root_cause_class: str) -> str:
    if root_cause_class in {"completion_emitted_but_reward_or_counter_path_wrong", "deadline_drop_ordering_issue", "formula_unit_mismatch"}:
        return "runtime"
    if root_cause_class in {"queue_pressure", "task_generation_admission_overload", "local_private_queue_blockage", "public_cloud_queue_blockage", "transmission_delay_admission_mismatch"}:
        return "configuration_or_load"
    if root_cause_class == "action_exposure_bias":
        return "action_exposure"
    if root_cause_class == "inconclusive_trace_evidence":
        return "inconclusive"
    return "no_issue"
