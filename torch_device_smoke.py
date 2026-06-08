from __future__ import annotations

import argparse
import json
import os
import resource
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import torch

from main import select_torch_device


@dataclass
class DeviceRunResult:
    device: str
    available: bool
    wall_time_sec: float | None
    cpu_user_sec: float | None
    cpu_system_sec: float | None
    rss_kb_before: int | None
    rss_kb_after: int | None
    rss_kb_delta: int | None
    mps_allocated_before: int | None
    mps_allocated_after: int | None
    mps_allocated_delta: int | None
    mps_driver_allocated_before: int | None
    mps_driver_allocated_after: int | None
    mps_driver_allocated_delta: int | None
    checksum: float | None
    iterations: int | None
    note: str | None = None


def _rss_kb() -> int | None:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    if hasattr(usage, "ru_maxrss"):
        return int(usage.ru_maxrss)
    return None


def _mps_mem() -> tuple[int | None, int | None]:
    if not hasattr(torch, "mps") and not hasattr(torch.backends, "mps"):
        return None, None
    if not hasattr(torch.backends, "mps") or not torch.backends.mps.is_available():
        return None, None
    allocated = None
    driver = None
    try:
        allocated = int(torch.mps.current_allocated_memory())
    except Exception:
        allocated = None
    try:
        driver = int(torch.mps.driver_allocated_memory())
    except Exception:
        driver = None
    return allocated, driver


def _sync(device: str) -> None:
    if device == "cuda" and torch.cuda.is_available():
        torch.cuda.synchronize()
    elif device == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        try:
            torch.mps.synchronize()
        except Exception:
            pass


def _device_available(device: str) -> bool:
    if device == "cpu":
        return True
    if device == "cuda":
        return torch.cuda.is_available()
    if device == "mps":
        return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    return False


def _run_workload(device: str, size: int, duration_sec: float) -> DeviceRunResult:
    available = _device_available(device)
    if not available:
        return DeviceRunResult(
            device=device,
            available=False,
            wall_time_sec=None,
            cpu_user_sec=None,
            cpu_system_sec=None,
            rss_kb_before=None,
            rss_kb_after=None,
            rss_kb_delta=None,
            mps_allocated_before=None,
            mps_allocated_after=None,
            mps_allocated_delta=None,
            mps_driver_allocated_before=None,
            mps_driver_allocated_after=None,
            mps_driver_allocated_delta=None,
            checksum=None,
            iterations=None,
            note="device unavailable",
        )

    torch_device = torch.device(device)
    rss_before = _rss_kb()
    mps_alloc_before, mps_driver_before = _mps_mem()
    cpu_before = resource.getrusage(resource.RUSAGE_SELF)
    start = time.perf_counter()

    x = torch.randn(size, size, device=torch_device)
    y = torch.randn(size, size, device=torch_device)
    result = None
    iterations = 0
    while True:
        result = x @ y
        result = torch.relu(result)
        x = result + 0.01
        y = y * 0.99 + 0.01
        iterations += 1

        _sync(device)
        if (time.perf_counter() - start) >= duration_sec:
            break

    checksum = float(result.mean().detach().cpu().item()) if result is not None else None
    end = time.perf_counter()
    cpu_after = resource.getrusage(resource.RUSAGE_SELF)
    rss_after = _rss_kb()
    mps_alloc_after, mps_driver_after = _mps_mem()

    return DeviceRunResult(
        device=device,
        available=True,
        wall_time_sec=end - start,
        cpu_user_sec=cpu_after.ru_utime - cpu_before.ru_utime,
        cpu_system_sec=cpu_after.ru_stime - cpu_before.ru_stime,
        rss_kb_before=rss_before,
        rss_kb_after=rss_after,
        rss_kb_delta=(rss_after - rss_before) if rss_before is not None and rss_after is not None else None,
        mps_allocated_before=mps_alloc_before,
        mps_allocated_after=mps_alloc_after,
        mps_allocated_delta=(mps_alloc_after - mps_alloc_before) if mps_alloc_before is not None and mps_alloc_after is not None else None,
        mps_driver_allocated_before=mps_driver_before,
        mps_driver_allocated_after=mps_driver_after,
        mps_driver_allocated_delta=(mps_driver_after - mps_driver_before) if mps_driver_before is not None and mps_driver_after is not None else None,
        checksum=checksum,
        iterations=iterations,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--json-output", type=str, default=None)
    args = parser.parse_args()

    main_device = select_torch_device()
    results = [_run_workload(main_device, args.size, args.duration)]
    if main_device != "cpu":
        results.append(_run_workload("cpu", args.size, args.duration))
    payload = {
        "host": os.uname().sysname if hasattr(os, "uname") else "unknown",
        "results": [asdict(result) for result in results],
    }

    for result in results:
        print(f"device: {result.device}")
        print(f"  available: {result.available}")
        print(f"  wall_time_sec: {result.wall_time_sec}")
        print(f"  cpu_user_sec: {result.cpu_user_sec}")
        print(f"  cpu_system_sec: {result.cpu_system_sec}")
        print(f"  rss_kb_delta: {result.rss_kb_delta}")
        print(f"  mps_allocated_delta: {result.mps_allocated_delta}")
        print(f"  mps_driver_allocated_delta: {result.mps_driver_allocated_delta}")
        print(f"  iterations: {result.iterations}")
        print(f"  checksum: {result.checksum}")
        if result.note:
            print(f"  note: {result.note}")

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
