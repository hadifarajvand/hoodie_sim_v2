from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass(frozen=True)
class TempGitRepo:
    root: Path
    _tempdir: TemporaryDirectory[str]

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True)

    def output(self, *args: str) -> str:
        return self.git(*args).stdout.strip()

    def commit_file(self, relative_path: str, content: str, message: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.git("add", relative_path)
        self.git("commit", "-m", message)

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def cleanup(self) -> None:
        self._tempdir.cleanup()



def make_temp_git_repo() -> TempGitRepo:
    tempdir = TemporaryDirectory()
    root = Path(tempdir.name)
    subprocess.run(["git", "init", "-b", "main", str(root)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "HOODIE Test"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "hoodie-test@example.invalid"], check=True, capture_output=True, text=True)
    return TempGitRepo(root=root, _tempdir=tempdir)
