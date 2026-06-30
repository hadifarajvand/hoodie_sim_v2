from __future__ import annotations

from typing import Any, Dict, List, Optional


class TraceCollector:
    """
    Optional trace collector for recording events during training/rollout.
    Disabled by default; when enabled, records events without affecting behavior.
    """

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
        self._events: List[Dict[str, Any]] = []

    def record(self, episode_id: int, slot: int, event_type: str, **metadata: Any) -> None:
        """
        Record an event if tracing is enabled.
        """
        if not self.enabled:
            return
        self._events.append(
            {
                "episode_id": episode_id,
                "slot": slot,
                "event_type": event_type,
                **metadata,
            }
        )

    def get_events(self) -> List[Dict[str, Any]]:
        """
        Return a copy of the recorded events.
        """
        return list(self._events)

    def clear(self) -> None:
        """
        Clear recorded events.
        """
        self._events.clear()

    def count_events_by_type(self) -> Dict[str, int]:
        """
        Return a dictionary mapping event type to count.
        """
        counts: Dict[str, int] = {}
        for event in self._events:
            etype = event["event_type"]
            counts[etype] = counts.get(etype, 0) + 1
        return counts


def make_disabled_trace_collector() -> TraceCollector:
    """
    Factory for a disabled trace collector.
    """
    return TraceCollector(enabled=False)


def make_enabled_trace_collector() -> TraceCollector:
    """
    Factory for an enabled trace collector.
    """
    return TraceCollector(enabled=True)
