from __future__ import annotations

from dataclasses import asdict, dataclass, field

from src.config.training_config import TrainingConfig
from .seed_management import SeedManagement


@dataclass(slots=True)
class TrainingLogEntry:
    episode_index: int
    loss: float | None
    replay_buffer_size: int


@dataclass(slots=True)
class TrainingLogger:
    entries: list[TrainingLogEntry] = field(default_factory=list)
    last_context: dict[str, object] = field(default_factory=dict, init=False, repr=False)

    def log_episode(
        self,
        *,
        config: TrainingConfig,
        seeds: SeedManagement,
        episode_index: int,
        loss: float | None,
        replay_buffer_size: int,
    ) -> TrainingLogEntry:
        entry = TrainingLogEntry(
            episode_index=episode_index,
            loss=loss,
            replay_buffer_size=replay_buffer_size,
        )
        self.entries.append(entry)
        self.last_context = {
            "config": config.to_dict(),
            "seeds": asdict(seeds),
            "episode_index": episode_index,
        }
        return entry

    def snapshot(self) -> dict[str, object]:
        return {
            "entries": [asdict(entry) for entry in self.entries],
            "context": self.last_context,
        }
