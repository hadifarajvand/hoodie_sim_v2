from __future__ import annotations

from typing import Any

_INSTALLED = False


def install_runtime_fixes() -> None:
    """Install narrowly scoped runtime fixes required by the CLI execution path."""
    global _INSTALLED
    if _INSTALLED:
        return

    from src.environment.evaluation_gym_adapter import (
        EvaluationHoodieGymEnvironment,
    )
    from src.environment.gym_adapter import HoodieGymEnvironment

    def reset(
        self: EvaluationHoodieGymEnvironment, seed: int | None = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        # dataclass(slots=True) may replace the class object, which makes a
        # zero-argument super() captured in the pre-decoration function fail at
        # runtime. Call the known base implementation explicitly.
        HoodieGymEnvironment.reset(self, seed=seed)
        self._active_transmission_task_ids.clear()
        if self.supplied_trace is None:
            return self.observe(), self._build_info()

        self.trace = self.supplied_trace
        self._pending_arrivals.clear()
        self._active_tasks.clear()
        self._current_task = None
        for blueprint in sorted(self.trace.tasks, key=self._trace_sort_key):
            self._pending_arrivals[blueprint.arrival_slot].append(blueprint)
        for blueprints in self._pending_arrivals.values():
            blueprints.sort(key=self._trace_sort_key)

        self._current_task = self._load_current_task()
        return self.observe(), self._build_info()

    EvaluationHoodieGymEnvironment.reset = reset
    _INSTALLED = True
