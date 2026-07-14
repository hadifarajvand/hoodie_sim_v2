from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.trace_protocol import EvaluationTrace

from .gym_adapter import HoodieGymEnvironment


@dataclass(slots=True)
class EvaluationHoodieGymEnvironment(HoodieGymEnvironment):
    """Gym environment variant that executes an already materialized trace.

    The base environment remains the single owner of queue and service
    semantics.  This adapter changes only the reset-time trace source so every
    compared policy consumes the exact same task blueprints, including the
    decision/drain split encoded by the trace protocol.
    """

    supplied_trace: EvaluationTrace | None = None

    def reset(self, seed: int | None = None):
        # Let the base class reset every queue, ledger, metric, and runtime
        # object.  Its internally generated trace is then replaced before the
        # first policy decision, so physical execution semantics are unchanged.
        super().reset(seed=seed)
        if self.supplied_trace is None:
            return self.observe(), self._build_info()

        self.trace = self.supplied_trace
        self._pending_arrivals.clear()
        for blueprint in sorted(self.trace.tasks, key=self._trace_sort_key):
            self._pending_arrivals[blueprint.arrival_slot].append(blueprint)
        for blueprints in self._pending_arrivals.values():
            blueprints.sort(key=self._trace_sort_key)

        self._current_task = self._load_current_task()
        return self.observe(), self._build_info()
