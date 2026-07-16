from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import subprocess
from typing import Any


_OWNED_CHILDREN: dict[int, tuple[int, str]] = {}


@dataclass(frozen=True, slots=True)
class ProcessMetadata:
    pid: int
    ppid: int
    pgid: int
    sid: int
    start_time: str
    command: str


def record_owned_child_pid(pid: int, start_time: str, command: str) -> None:
    _OWNED_CHILDREN[pid] = (int(os.getpid()), json.dumps({"start_time": start_time, "command": command}, sort_keys=True))


def clear_owned_child_registry() -> None:
    _OWNED_CHILDREN.clear()


def _ancestor_pids() -> set[int]:
    pids = {os.getpid(), os.getppid()}
    parent = os.getppid()
    while parent > 1:
        try:
            with open(f"/proc/{parent}/stat", "r", encoding="utf-8") as handle:
                fields = handle.read().split()
            parent = int(fields[3])
        except Exception:
            break
        if parent in pids:
            break
        pids.add(parent)
    return pids


def _process_metadata(pid: int) -> ProcessMetadata:
    output = subprocess.run(
        ["ps", "-p", str(pid), "-o", "pid=,ppid=,pgid=,sid=,lstart=,command="],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not output:
        raise ProcessLookupError(pid)
    left, command = output.rsplit(None, 1)
    fields = left.split()
    if len(fields) < 7:
        raise ValueError("unexpected ps output")
    return ProcessMetadata(
        pid=int(fields[0]),
        ppid=int(fields[1]),
        pgid=int(fields[2]),
        sid=int(fields[3]),
        start_time=" ".join(fields[4:]),
        command=command,
    )


def assert_safe_owned_child_pid(pid: int, expected_command_fragment: str) -> None:
    if pid <= 1:
        raise ValueError("unsafe pid")
    if pid in _ancestor_pids():
        raise ValueError("unsafe ancestor pid")
    if pid not in _OWNED_CHILDREN:
        raise ValueError("pid not recorded as owned child")
    metadata = _process_metadata(pid)
    if metadata.pid in {os.getpid(), os.getppid(), 1}:
        raise ValueError("unsafe pid")
    if metadata.pid in {metadata.pgid, metadata.sid}:
        raise ValueError("unsafe leader pid")
    if any(token in metadata.command.lower() for token in ("codex", "claude", "agent")):
        raise ValueError("unsafe command")
    if expected_command_fragment not in metadata.command:
        raise ValueError("command mismatch")
    recorded_parent, recorded_payload = _OWNED_CHILDREN[pid]
    if recorded_parent != os.getpid():
        raise ValueError("reused pid metadata")
    payload = json.loads(recorded_payload)
    if payload.get("command") != metadata.command or payload.get("start_time") != metadata.start_time:
        raise ValueError("reused pid metadata")

