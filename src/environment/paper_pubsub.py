from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PubSubLoadSnapshot:
    publisher_agent_id: str
    controller_id: str
    published_slot: int
    received_slot: int | None
    load_snapshot: dict[str, Any] | None
    message_status: str
    dissemination_policy: str
    pubsub_version: str = "paper_pubsub_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "publisher_agent_id": self.publisher_agent_id,
            "controller_id": self.controller_id,
            "published_slot": self.published_slot,
            "received_slot": self.received_slot,
            "load_snapshot": self.load_snapshot,
            "message_status": self.message_status,
            "dissemination_policy": self.dissemination_policy,
            "pubsub_version": self.pubsub_version,
        }


@dataclass(slots=True)
class PubSubController:
    controller_id: str
    last_known_by_agent: dict[str, dict[str, Any]]

    def publish(self, snapshot: PubSubLoadSnapshot) -> None:
        if snapshot.load_snapshot is not None:
            self.last_known_by_agent[snapshot.publisher_agent_id] = dict(snapshot.load_snapshot)

    def disseminate(self, publisher_agent_id: str, receive_slot: int | None) -> PubSubLoadSnapshot:
        load_snapshot = self.last_known_by_agent.get(publisher_agent_id)
        status = "delayed" if receive_slot is None else "delivered"
        return PubSubLoadSnapshot(
            publisher_agent_id=publisher_agent_id,
            controller_id=self.controller_id,
            published_slot=max(receive_slot or 0, 0),
            received_slot=receive_slot,
            load_snapshot=load_snapshot,
            message_status=status,
            dissemination_policy="load-sharing_snapshot",
        )

