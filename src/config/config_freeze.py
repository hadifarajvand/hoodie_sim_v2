from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
from typing import Any


class FrozenConfigError(RuntimeError):
    pass


class FrozenConfig:
    def __init__(self, config: Any) -> None:
        object.__setattr__(self, "_config", config)
        snapshot = self._serialize(config)
        object.__setattr__(self, "_snapshot", snapshot)
        object.__setattr__(self, "_hash", hashlib.sha256(snapshot.encode("utf-8")).hexdigest())
        object.__setattr__(self, "_locked", True)

    @staticmethod
    def _serialize(config: Any) -> str:
        if is_dataclass(config):
            payload = asdict(config)
        elif hasattr(config, "to_dict"):
            payload = config.to_dict()
        else:
            payload = dict(config)
        return json.dumps(payload, sort_keys=True, default=str)

    @property
    def snapshot(self) -> str:
        return self._snapshot

    @property
    def hash(self) -> str:
        return self._hash

    def ensure_unchanged(self) -> None:
        current = self._serialize(self._config)
        if current != self._snapshot:
            raise FrozenConfigError("Configuration mutated after validation freeze")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._config, name)
