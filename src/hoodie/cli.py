from __future__ import annotations

import argparse
import json
from pathlib import Path

from .kernel import HoodieKernel, NeutralSlotKernel
from .models import Action, Identifier, Task, Time, Trace, Unit
from .topology import Topology


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hoodie-smoke")
    parser.add_argument("--topology", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    topology = Topology.load(args.topology)
    kernel = HoodieKernel(topology=topology)
    task = Task(
        task_id=Identifier("task-1"),
        source_id=Identifier(topology.node_ids[0]),
        arrival=Time(0),
        size=Unit(10.0, "mbit"),
        density=Unit(2.0, "gcycles/mbit"),
        timeout_slots=5,
    )
    action = Action("local")
    service = kernel.service_time(task, action)
    neutral = NeutralSlotKernel().step(task, action, current_slot=0)
    print(json.dumps({"service_slots": service.service_slots, "outcome": neutral.name}, sort_keys=True))
    return 0
