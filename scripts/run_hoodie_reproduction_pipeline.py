from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.pipeline import DeterministicSimulator, PipelineConfig, write_artifacts, write_plots


def _load_config(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def _build_report(output_dir: Path, config: PipelineConfig, result: dict[str, object], artifacts: dict[str, str], plots: dict[str, str]) -> dict[str, object]:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    return {
        "branch": branch,
        "commit": commit,
        "runtime_mode": config.mode,
        "phase": config.phase,
        "paper_faithful": config.mode == "paper_faithful",
        "config_hash": _config_hash(config.to_dict()),
        "seed": config.seed,
        "num_edge_nodes": config.num_edge_nodes,
        "arrival_probability": config.arrival_probability,
        "task_count": config.task_count,
        "artifacts": {**artifacts, **plots},
        "event_hash": result["event_hash"],
        "policy": "FIFO or deterministic heuristic",
        "notes": [
            "This pipeline is baseline/heuristic only.",
            "No RL, DRL, LSTM, or learning-based policy is used.",
        ],
    }


def _config_hash(payload: dict) -> str:
    import hashlib

    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    cfg = PipelineConfig(**_load_config(args.config))
    simulator = DeterministicSimulator(cfg)
    result = simulator.run()
    output_dir = Path(args.output_dir)
    artifacts = write_artifacts(output_dir, result)
    plots = write_plots(output_dir, result)
    report = _build_report(output_dir, cfg, result, artifacts, plots)
    (output_dir / "final_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    (output_dir / "final_report.md").write_text(
        "\n".join(
            [
                "# HOODIE Reproduction Pipeline Report",
                "",
                f"branch: {report['branch']}",
                f"runtime_mode: {report['runtime_mode']}",
                f"phase: {report['phase']}",
                f"config_hash: {report['config_hash']}",
                f"seed: {report['seed']}",
                f"event_hash: {report['event_hash']}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
