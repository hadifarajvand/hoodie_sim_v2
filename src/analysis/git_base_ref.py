from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Iterable


@dataclass(frozen=True, slots=True)
class GitBaseRefResolutionError(RuntimeError):
    repo_path: str
    explicit_base_ref: str | None
    configured_base_ref: str | None
    candidates: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class GitBaseRefResolution:
    base_ref: str
    triple_dot_range: str


def _git(repo_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo_path), *args], check=False, capture_output=True, text=True)


def _verify_commit(repo_path: Path, ref: str) -> bool:
    return _git(repo_path, "rev-parse", "--verify", f"{ref}^{{commit}}").returncode == 0


def _resolve_origin_head(repo_path: Path) -> str | None:
    symbolic = _git(repo_path, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if symbolic.returncode != 0:
        return None
    ref = symbolic.stdout.strip()
    return ref if ref and _verify_commit(repo_path, ref) else None


def resolve_base_ref(
    repo_path: str | Path = ".",
    *,
    explicit_base: str | None = None,
    configured_base: str | None = None,
) -> str:
    repo = Path(repo_path)
    candidates: list[str] = []
    if explicit_base:
        candidates.append(explicit_base)
    elif configured_base:
        candidates.append(configured_base)
    else:
        for candidate in ("origin/main", "main", "origin/HEAD"):
            if candidate not in candidates:
                candidates.append(candidate)
    for candidate in candidates:
        if candidate == "origin/HEAD":
            resolved = _resolve_origin_head(repo)
            if resolved:
                return resolved
            continue
        if _verify_commit(repo, candidate):
            return candidate
    if explicit_base or configured_base:
        raise GitBaseRefResolutionError(str(repo), explicit_base, configured_base, tuple(candidates), "explicit or configured base ref is invalid")
    raise GitBaseRefResolutionError(str(repo), explicit_base, configured_base, tuple(candidates), "unable to resolve valid base ref")


def comparison_range(repo_path: str | Path = ".", *, explicit_base: str | None = None, configured_base: str | None = None) -> str:
    return f"{resolve_base_ref(repo_path, explicit_base=explicit_base, configured_base=configured_base)}...HEAD"


def committed_changed_files(repo_path: str | Path = ".", base_ref: str | None = None) -> list[str]:
    repo = Path(repo_path)
    if base_ref is None:
        base_ref = resolve_base_ref(repo)
    diff = _git(repo, "diff", "--name-only", f"{base_ref}...HEAD")
    if diff.returncode != 0:
        raise GitBaseRefResolutionError(str(repo), base_ref, None, (base_ref,), diff.stderr.strip() or "unable to list changed files")
    return [line.strip() for line in diff.stdout.splitlines() if line.strip()]


def is_worktree_dirty(repo_path: str | Path = ".") -> bool:
    status = _git(Path(repo_path), "status", "--porcelain")
    if status.returncode != 0:
        raise GitBaseRefResolutionError(str(repo_path), None, None, (), status.stderr.strip() or "unable to inspect worktree")
    return bool(status.stdout.strip())


def repository_head(repo_path: str | Path = ".") -> str:
    head = _git(Path(repo_path), "rev-parse", "HEAD")
    if head.returncode != 0:
        raise GitBaseRefResolutionError(str(repo_path), None, None, (), head.stderr.strip() or "unable to resolve HEAD")
    return head.stdout.strip()




def resolve_git_base_ref(
    repo_path: str | Path = ".",
    *,
    explicit_base_ref: str | None = None,
    configured_base_ref: str | None = None,
) -> GitBaseRefResolution:
    base_ref = resolve_base_ref(repo_path, explicit_base=explicit_base_ref, configured_base=configured_base_ref)
    return GitBaseRefResolution(base_ref=base_ref, triple_dot_range=f"{base_ref}...HEAD")

def git_triple_dot_range(repo_path: str | Path = ".", *, explicit_base_ref: str | None = None, configured_base_ref: str | None = None) -> str:
    return comparison_range(repo_path, explicit_base=explicit_base_ref, configured_base=configured_base_ref)
