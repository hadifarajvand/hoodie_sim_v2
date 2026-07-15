from __future__ import annotations

import json
from pathlib import Path

from hoodie.cli import main
from hoodie.kernel import HoodieKernel, NeutralSlotKernel, FIFOQueue
from hoodie.models import Action, Identifier, Task, Time, Trace, Unit
from hoodie.topology import Topology


def make_task() -> Task:
    return Task(
        task_id=Identifier("t1"),
        source_id=Identifier("n1"),
        arrival=Time(0),
        size=Unit(12.0, "mbit"),
        density=Unit(3.0, "gcycles/mbit"),
        timeout_slots=4,
    )


def test_fifo_queue_order():
    q = FIFOQueue()
    task = make_task()
    q.push(task)
    assert q.pop() == task


def test_service_and_kernel():
    topology = Topology(node_ids=("n1", "n2"), legal_actions={"n1": ("local", "horizontal")})
    kernel = HoodieKernel(topology=topology, local_capacity=4.0, horizontal_capacity=6.0, vertical_capacity=8.0)
    task = make_task()
    result = kernel.service_time(task, Action("local"))
    assert result.service_slots == 3
    assert kernel.legal_actions("n1") == ("local", "horizontal")


def test_neutral_kernel_timeout_and_completion():
    task = make_task()
    kernel = NeutralSlotKernel()
    assert kernel.step(task, Action("local"), current_slot=0).name == "completed"
    assert kernel.step(task, Action("local"), current_slot=5).name == "dropped"


def test_trace_hash_stable():
    trace = Trace(events=({"slot": 0, "action": "local"}, {"slot": 1, "action": "done"}))
    assert trace.hash() == Trace(events=({"slot": 0, "action": "local"}, {"slot": 1, "action": "done"})).hash()


def test_smoke_cli(tmp_path: Path, capsys):
    topology_path = tmp_path / "topology.json"
    topology_path.write_text(json.dumps({"node_ids": ["n1"], "legal_actions": {"n1": ["local"]}}), encoding="utf-8")
    assert main(["--topology", str(topology_path)]) == 0
    out = capsys.readouterr().out.strip()
    assert "service_slots" in out
