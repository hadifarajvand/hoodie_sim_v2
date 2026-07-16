from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path

import torch

from src.hoodie.experiments.checkpoint_registry_patch import (
    register_training_checkpoint,
)


@dataclass
class Row:
    job_id: str = "train"
    policy: str = "HOODIE"
    variant: str = "hoodie_lstm"
    seed: int = 7
    source_contract_hash: str = "source"
    topology_contract: dict[str, object] = field(
        default_factory=lambda: {"agent_counts": [1]}
    )


def test_registry_hash_is_checkpoint_file_sha256(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    job = campaign / "jobs" / "train"
    checkpoint_id = "selected"
    checkpoint_dir = job / "internal_checkpoints" / checkpoint_id
    checkpoint_dir.mkdir(parents=True)
    checkpoint = checkpoint_dir / "checkpoint.pt"
    torch.save(
        {
            "schema_version": 3,
            "backend_type": "cpu",
            "device_string": "cpu",
            "resume_capable": False,
            "policy_state": {"agents": {}},
        },
        checkpoint,
    )
    digest = sha256(checkpoint.read_bytes()).hexdigest()
    (checkpoint_dir / "metadata.json").write_text(
        json.dumps({"checkpoint_sha256": digest}), encoding="utf-8"
    )

    record = register_training_checkpoint(
        job,
        Row(),
        source_commit="commit",
        checkpoint_id=checkpoint_id,
    )
    assert record["checkpoint_hash"] == digest
    registry = json.loads(
        (campaign / "checkpoint_registry.json").read_text(encoding="utf-8")
    )
    assert registry["checkpoints"][0]["checkpoint_hash"] == digest
    selected = json.loads(
        (job / "selected_checkpoint.json").read_text(encoding="utf-8")
    )
    assert selected["checkpoint_hash"] == digest
