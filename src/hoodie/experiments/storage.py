from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

@dataclass(slots=True)
class AtomicJobStorage:
    root: Path

    def write_job(self, job_id: str, payload: dict[str, object]) -> Path:
        job_dir = self.root / job_id
        job_dir.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.root) as tempdir:
            temp = Path(tempdir)
            (temp / "specification.json").write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
            (temp / "completion.marker").write_text("complete\n", encoding="utf-8")
            os.replace(temp, job_dir)
        return job_dir
