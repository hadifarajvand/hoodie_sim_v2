from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os
from tempfile import TemporaryDirectory


class StatusStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, job_id: str, payload: dict[str, Any]) -> Path:
        job_dir = self.root / job_id
        job_dir.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.root) as tempdir:
            temp = Path(tempdir)
            (temp / "status.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(temp, job_dir)
        return job_dir

    def read(self, job_id: str) -> dict[str, Any]:
        return json.loads((self.root / job_id / "status.json").read_text(encoding="utf-8"))
