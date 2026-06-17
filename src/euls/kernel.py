from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

if False:  # pragma: no cover
    from environment.environment import Environment


@dataclass(frozen=True)
class _ActionShim:
    action: Any


class EULSKernel:
    """Explicit EULS boundary for deterministic execution.

    Phase 1 is a non-semantic wrapper around `environment.environment.Environment`.
    """

    def __init__(self, environment: Any) -> None:
        self.environment = environment

    def reset(self, seed: int | None = None):
        if seed is not None:
            np.random.seed(int(seed))
        return self.environment.reset()

    def observe(self):
        return self.environment.pack_observation()

    def observe_flat(self, task=None):
        observations, active_queues = self.observe()
        if task is None:
            return observations, active_queues
        return observations, active_queues, task

    def legal_action_mask(self, task=None):
        if task is None:
            return [1] * 2
        return [1] * int(self.environment.matchmakers[0].get_number_of_actions())

    def step(self, action: str | None):
        if action is None:
            action = "0"
        if isinstance(action, str):
            action = int(action)
        actions = [int(action) for _ in range(self.environment.number_of_servers)]
        observation, reward, terminated, info = self.environment.step(actions)
        truncated = False
        return observation, reward, terminated, truncated, info

    @property
    def current_task(self):
        return self.environment.tasks

    @property
    def current_slot(self):
        return self.environment.current_time

    @property
    def queue_load(self):
        private = sum(server.processing_queue.get_queue_length() for server in self.environment.servers)
        offloading = sum(server.offloading_queue.get_queue_length() for server in self.environment.servers)
        public = sum(sum(server.public_queue_manager.get_queue_lengths()) for server in self.environment.servers)
        cloud_public = sum(self.environment.cloud.public_queue_manager.get_queue_lengths())
        return {
            "private": private,
            "offloading": offloading,
            "public": public,
            "cloud_public": cloud_public,
        }
