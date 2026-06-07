from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
ARTIFACT_DIRNAME = "phase3_fidelity_audit"


@dataclass(frozen=True)
class GapRow:
    paper_variable: str
    paper_equation_or_source: str
    expected_meaning: str
    implementation_location: str
    implementation_status: str
    evidence: str
    gap_description: str
    recommended_next_step: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _read_text(path: Path) -> str:
    return path.read_text()


def _status_from_note(note: str) -> str:
    note = note.lower()
    if "paper-faithful" in note or "native" in note:
        return "PASS"
    if "collapsed" in note or "reconstructed" in note or "approx" in note:
        return "PARTIAL"
    if "missing" in note:
        return "MISSING"
    return "PARTIAL"


def _classify_state_contract() -> list[GapRow]:
    return [
        GapRow(
            paper_variable="eta_n(t)",
            paper_equation_or_source="Eq. (18)",
            expected_meaning="task size arriving at slot t",
            implementation_location="environment/task.py, environment/task_generator.py",
            implementation_status="PASS",
            evidence="Task exposes input_data_size/size and TaskGenerator generates size per task.",
            gap_description="The size field exists natively.",
            recommended_next_step="Keep size field explicit in runtime and traces.",
        ),
        GapRow(
            paper_variable="w_priv_n(t)",
            paper_equation_or_source="Eq. (18)",
            expected_meaning="private queue waiting time",
            implementation_location="environment/server.py, environment/queues.py",
            implementation_status="PARTIAL",
            evidence="Private waiting time is exposed by Server.get_features() and used in DQN observation vectors.",
            gap_description="It is present as a proxy waiting-time feature, but the current state vector collapses richer paper state into a small legacy observation.",
            recommended_next_step="Export a paper-native state object that preserves named fields.",
        ),
        GapRow(
            paper_variable="w_off_n(t)",
            paper_equation_or_source="Eq. (18)",
            expected_meaning="offloading queue waiting time",
            implementation_location="environment/server.py, environment/queues.py",
            implementation_status="PARTIAL",
            evidence="Offloading waiting time is exposed by Server.get_features() and fed into observations.",
            gap_description="Waiting time exists, but not as a first-class paper-state structure.",
            recommended_next_step="Separate paper-state export from legacy observation packing.",
        ),
        GapRow(
            paper_variable="l_pub_n(t-1)",
            paper_equation_or_source="Eq. (18)",
            expected_meaning="previous-slot public queue length vector",
            implementation_location="environment/environment.py, phase1_tracing.py",
            implementation_status="PARTIAL",
            evidence="Environment.pack_observation() appends public queue lengths to per-agent observations.",
            gap_description="The signal exists but is packed into a legacy observation array rather than an explicit paper state field.",
            recommended_next_step="Expose explicit l_pub_n(t-1) as a named state component.",
        ),
        GapRow(
            paper_variable="L(t)",
            paper_equation_or_source="Eq. (18), Section III.A.1",
            expected_meaning="historical load matrix W x (N+1)",
            implementation_location="environment/environment.py, training/trace_dataset.py",
            implementation_status="FAIL",
            evidence="The runtime does not maintain a native W x (N+1) load matrix; trace_dataset reconstructs proxy states from task lifecycle rows.",
            gap_description="Historical load is not stored natively and the current training pipeline reconstructs approximations from traces.",
            recommended_next_step="Introduce a paper-state history buffer before training consumes it.",
        ),
        GapRow(
            paper_variable="predicted next load",
            paper_equation_or_source="Figure 5 / Section IV.A",
            expected_meaning="LSTM forecast for all nodes",
            implementation_location="training/lstm_forecaster.py, decision_makers/agent.py",
            implementation_status="FAIL",
            evidence="LSTMForecaster is a standalone regressor on handcrafted rows; Agent uses an LSTM hidden history, not a node-wise load forecaster.",
            gap_description="The implemented LSTM is not the paper's W x (N+1) load predictor.",
            recommended_next_step="Replace the toy forecaster with the paper's load-history pipeline later.",
        ),
        GapRow(
            paper_variable="state_dim",
            paper_equation_or_source="Eq. (18), Eq. (25) input",
            expected_meaning="full paper-state dimensionality per agent",
            implementation_location="training/trace_dataset.py, decision_makers/agent.py",
            implementation_status="PARTIAL",
            evidence="TraceDataset summary reports state_dim from reconstructed transitions; DQN input_dim is this collapsed vector.",
            gap_description="The model trains on collapsed/reconstructed state vectors, not native paper-state tensors.",
            recommended_next_step="Decouple trace reconstruction from paper-state training inputs.",
        ),
    ]


def _classify_action_contract() -> list[GapRow]:
    return [
        GapRow(
            paper_variable="d_n^(1)(t)",
            paper_equation_or_source="Eq. (19)",
            expected_meaning="local vs offload first-stage decision",
            implementation_location="environment/action_model.py, environment/matchmaker.py, phase1_tracing.py",
            implementation_status="PASS",
            evidence="TwoStageAction.first_stage_decision and d_n_1 represent local/offload explicitly; traces carry first_stage_decision.",
            gap_description="No gap in the first-stage decision representation.",
            recommended_next_step="Keep the explicit contract and preserve trace fields.",
        ),
        GapRow(
            paper_variable="D_n(t)",
            paper_equation_or_source="Eq. (19), Algorithm 1",
            expected_meaning="destination choice for offloaded task",
            implementation_location="environment/action_model.py, environment/matchmaker.py",
            implementation_status="PASS",
            evidence="TwoStageAction.d_nk_2 stores the chosen destination sparsely; local actions use an empty destination map.",
            gap_description="The destination route is explicit, although the runtime still uses a legacy target-node compatibility mapping.",
            recommended_next_step="Keep the sparse route encoding and preserve compatibility mapping only as a bridge.",
        ),
        GapRow(
            paper_variable="local/horizontal/vertical distinction",
            paper_equation_or_source="Section III.A.2, Eq. (19)",
            expected_meaning="three route families",
            implementation_location="environment/action_model.py",
            implementation_status="PASS",
            evidence="destination_type distinguishes local, horizontal_edge, and vertical_cloud.",
            gap_description="No gap in route family labeling.",
            recommended_next_step="Keep labels in traces and audit reports.",
        ),
        GapRow(
            paper_variable="one route per task",
            paper_equation_or_source="Section III.A.2",
            expected_meaning="exactly one destination or local route",
            implementation_location="environment/action_model.py",
            implementation_status="PASS",
            evidence="validate_explicit_choice() rejects missing/multiple destinations and self-offload.",
            gap_description="No gap in the legality check itself.",
            recommended_next_step="Preserve rejection behavior and trace invalid reasons.",
        ),
        GapRow(
            paper_variable="self-offload / non-neighbor rejection",
            paper_equation_or_source="Section III.A.2 / Figure 7",
            expected_meaning="horizontal offload only to legal neighbors",
            implementation_location="environment/action_model.py, environment/matchmaker.py",
            implementation_status="PASS",
            evidence="TopologyAdapter checks adjacency and rejects self-offload/non-neighbor choices.",
            gap_description="No gap in legality, but the topology provenance is still user-approved/manual rather than paper-verified.",
            recommended_next_step="Separate legality from topology-fidelity claims.",
        ),
        GapRow(
            paper_variable="action trace semantics",
            paper_equation_or_source="Algorithm 1 / trace plumbing",
            expected_meaning="trace raw action plus paper semantics",
            implementation_location="phase1_tracing.py, main.py",
            implementation_status="PASS",
            evidence="Action traces now include raw_action_id, first_stage_decision, destination_node_id, destination_type, validity, and d_n_1/d_nk_2.",
            gap_description="No gap in trace field availability.",
            recommended_next_step="Keep trace schema stable for downstream training audits.",
        ),
        GapRow(
            paper_variable="replay-training readiness",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="sufficient action semantics for replay training",
            implementation_location="training/trace_dataset.py, decision_makers/agent.py",
            implementation_status="PARTIAL",
            evidence="Trace schema is richer, but replay training still consumes reconstructed state vectors and legacy action integers.",
            gap_description="Training readiness is improved but not yet paper-complete.",
            recommended_next_step="Bridge replay buffer to paper-state and delayed reward tuples later.",
        ),
    ]


def _classify_reward_contract() -> list[GapRow]:
    return [
        GapRow(
            paper_variable="reward timing",
            paper_equation_or_source="Eq. (20), Algorithm 1",
            expected_meaning="reward collected later at completion/drop time",
            implementation_location="environment/environment.py, phase1_tracing.py, phase2_mechanisms.py",
            implementation_status="FAIL",
            evidence="Runtime returns step rewards immediately from queue stepping; trace code reconstructs delayed reward post hoc from lifecycle rows.",
            gap_description="Reward is not natively delayed per completed task in the runtime.",
            recommended_next_step="Move to task-completion-delayed reward collection in a later phase.",
        ),
        GapRow(
            paper_variable="Phi_n(t)",
            paper_equation_or_source="Eq. (21)",
            expected_meaning="local/private or public completion cost",
            implementation_location="phase2_mechanisms.py, environment/queues.py",
            implementation_status="PARTIAL",
            evidence="Delayed reward reconstruction distinguishes completed vs dropped tasks and can label local/private vs offloaded completion by traces.",
            gap_description="The paper cost is reconstructable, not computed natively in runtime.",
            recommended_next_step="Attach Phi_n(t) to native lifecycle events.",
        ),
        GapRow(
            paper_variable="Phi_priv_n(t)",
            paper_equation_or_source="Eq. (22)",
            expected_meaning="private completion delay",
            implementation_location="environment/task.py, phase2_mechanisms.py",
            implementation_status="PARTIAL",
            evidence="Completion delay can be inferred from arrival and completion timestamps in traces.",
            gap_description="Available only as reconstructed delay, not as a native paper variable at runtime.",
            recommended_next_step="Store paper completion delay directly in the lifecycle trace.",
        ),
        GapRow(
            paper_variable="Phi_pub_n(t)",
            paper_equation_or_source="Eq. (23)",
            expected_meaning="public/offloaded completion delay",
            implementation_location="environment/task.py, phase2_mechanisms.py",
            implementation_status="PARTIAL",
            evidence="Offloaded task delay can be reconstructed from task lifecycle traces, but public queue timing is not exported as the paper formula.",
            gap_description="The paper summation is not directly computed by the runtime.",
            recommended_next_step="Emit public queue timing required by Eq. (23).",
        ),
        GapRow(
            paper_variable="drop penalty C",
            paper_equation_or_source="Eq. (20)",
            expected_meaning="constant penalty for dropped tasks",
            implementation_location="phase2_mechanisms.py, environment/task.py",
            implementation_status="PARTIAL",
            evidence="Drop penalty is available and reconstructed as -40.0 in trace-based reporting.",
            gap_description="Penalty exists, but not as a native delayed reward event in the runtime loop.",
            recommended_next_step="Bind drop penalty to native lifecycle events.",
        ),
        GapRow(
            paper_variable="task-traceable replay tuple",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="(s_n(t'), a_n(t'), r_n(t'), s_n(t'+1)) stored after completion",
            implementation_location="decision_makers/agent.py, training/replay_buffer.py, training/trace_dataset.py",
            implementation_status="FAIL",
            evidence="ReplayBuffer stores immediate transitions and DQNTrainer.push() receives dataset rows, not completion-delayed tuples keyed by task completion.",
            gap_description="Algorithm 1 delayed replay semantics are not implemented.",
            recommended_next_step="Introduce completion-keyed experience buffering.",
        ),
    ]


def _classify_lstm_contract() -> list[GapRow]:
    return [
        GapRow(
            paper_variable="L(t)",
            paper_equation_or_source="Section III.A.1, Figure 5",
            expected_meaning="W x (N+1) historical load matrix",
            implementation_location="decision_makers/agent.py, training/lstm_forecaster.py",
            implementation_status="FAIL",
            evidence="No native W x (N+1) load history matrix is maintained; the forecaster is a standalone regressor on simplified rows.",
            gap_description="This is not the paper's load-history pipeline.",
            recommended_next_step="Implement explicit load matrix history storage.",
        ),
        GapRow(
            paper_variable="W",
            paper_equation_or_source="Figure 5 / Section IV.A",
            expected_meaning="lookback window for load prediction",
            implementation_location="training/lstm_forecaster.py, decision_makers/agent.py",
            implementation_status="PARTIAL",
            evidence="Agent maintains an LSTM history deque and LSTMForecaster uses a sequence_length parameter.",
            gap_description="A window exists, but it is not the paper's node-wise EC load matrix window.",
            recommended_next_step="Rewire the lookback window around explicit node load vectors.",
        ),
        GapRow(
            paper_variable="predicted next-slot load",
            paper_equation_or_source="Figure 5",
            expected_meaning="forecast for all N+1 nodes",
            implementation_location="training/lstm_forecaster.py",
            implementation_status="FAIL",
            evidence="LSTMForecaster predicts a single scalar target from handcrafted features, not all node loads.",
            gap_description="Forecast output shape is not paper-faithful.",
            recommended_next_step="Replace scalar target prediction with multi-node load prediction.",
        ),
        GapRow(
            paper_variable="LSTM integrated into HOODIE state",
            paper_equation_or_source="Section IV.A / Eq. (25)",
            expected_meaning="predicted load feeds DQN input",
            implementation_location="decision_makers/agent.py",
            implementation_status="PARTIAL",
            evidence="Agent concatenates an LSTM hidden-history tensor with the state before the Q-network, but that is not the paper's explicit load forecast input.",
            gap_description="There is LSTM usage, but it is an opaque history channel rather than the paper's forecast state.",
            recommended_next_step="Separate forecast output from policy memory.",
        ),
        GapRow(
            paper_variable="EC message delay recovery",
            paper_equation_or_source="Section IV.A / algorithm narrative",
            expected_meaning="fallback when EC load messages are delayed",
            implementation_location="decision_makers/agent.py, training/lstm_forecaster.py",
            implementation_status="MISSING",
            evidence="No explicit message-delay recovery path is implemented.",
            gap_description="The paper's delayed-message recovery behavior is not present.",
            recommended_next_step="Document and implement recovery later.",
        ),
    ]


def _classify_training_loop_contract() -> list[GapRow]:
    return [
        GapRow(
            paper_variable="per-agent replay memory",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="N_R experience buffer per agent",
            implementation_location="decision_makers/agent.py, training/replay_buffer.py",
            implementation_status="PARTIAL",
            evidence="Agent maintains numpy replay arrays and DQNTrainer uses ReplayBuffer(capacity=10000).",
            gap_description="Replay memory exists, but the training harness is not the paper's per-agent delayed replay pipeline.",
            recommended_next_step="Bridge replay storage to completion-delayed paper tuples.",
        ),
        GapRow(
            paper_variable="Q / target-Q pair",
            paper_equation_or_source="Algorithm 1 / Eq. (25)",
            expected_meaning="online network plus target network",
            implementation_location="decision_makers/agent.py, training/train_phase3.py, training/trainers.py",
            implementation_status="PASS",
            evidence="Agent has Q_eval_network and Q_target_network; DQNTrainer has policy_net and target_net.",
            gap_description="Model pair exists.",
            recommended_next_step="Keep target-network separation explicit.",
        ),
        GapRow(
            paper_variable="epsilon-greedy",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="epsilon-greedy action selection",
            implementation_location="decision_makers/agent.py, training/trainers.py",
            implementation_status="PASS",
            evidence="Agent.choose_action() and DQNTrainer.select_action() both implement epsilon-greedy selection.",
            gap_description="No gap in exploration policy.",
            recommended_next_step="Keep epsilon schedule transparent in reports.",
        ),
        GapRow(
            paper_variable="Double-DQN target",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="target uses online argmax with target evaluation",
            implementation_location="training/trainers.py",
            implementation_status="PASS",
            evidence="DQNTrainer.train_step() uses next_policy_q argmax with next_target_q for ddqn.",
            gap_description="Double-DQN is explicitly supported.",
            recommended_next_step="Keep algorithm labeling accurate in outputs.",
        ),
        GapRow(
            paper_variable="dueling DQN",
            paper_equation_or_source="Eq. (25) / Figure 4",
            expected_meaning="value + advantage decomposition",
            implementation_location="decision_makers/agent.py",
            implementation_status="PASS",
            evidence="DeepQNetwork optionally builds value_layer and advantage_layer with dueling aggregation.",
            gap_description="Architecture exists, but paper-grade training results are not claimed.",
            recommended_next_step="Keep the dueling flag auditable.",
        ),
        GapRow(
            paper_variable="MSE loss",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="mean squared TD error",
            implementation_location="decision_makers/agent.py, training/trainers.py",
            implementation_status="PASS",
            evidence="Agent uses loss_function() and DQNTrainer uses np.mean(td_error ** 2) with MSELoss in the scaffold.",
            gap_description="Loss choice is aligned.",
            recommended_next_step="Preserve in training metadata.",
        ),
        GapRow(
            paper_variable="target network copy every Ncopy",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="periodic target update",
            implementation_location="decision_makers/agent.py, training/trainers.py",
            implementation_status="PASS",
            evidence="Agent uses replace_target_iter and trainer uses target_update_interval.",
            gap_description="Update cadence is present.",
            recommended_next_step="Record the actual interval in run metadata.",
        ),
        GapRow(
            paper_variable="store experience after completion",
            paper_equation_or_source="Algorithm 1",
            expected_meaning="collect D_n(t) and then store transition",
            implementation_location="main.py, decision_makers/agent.py, training/trainers.py",
            implementation_status="FAIL",
            evidence="main.py stores transitions immediately from each step; no completion-keyed delay buffer exists.",
            gap_description="The runtime does not wait for task completion before pushing the replay tuple.",
            recommended_next_step="Introduce a completion-aware replay staging layer.",
        ),
        GapRow(
            paper_variable="paper-state vs trace approximation",
            paper_equation_or_source="Algorithm 1 / Section IV",
            expected_meaning="train on paper-native state, not collapsed proxies",
            implementation_location="training/trace_dataset.py, training/train_phase3.py",
            implementation_status="FAIL",
            evidence="TraceDataset reconstructs state from lifecycle rows when direct RL state is unavailable.",
            gap_description="Training uses approximations rather than the native paper state pipeline.",
            recommended_next_step="Separate paper-state export from approximation-based reconstruction.",
        ),
        GapRow(
            paper_variable="checkpoint/reporting",
            paper_equation_or_source="Training algorithm / project scaffold",
            expected_meaning="save checkpoints and reports without paper-performance claims",
            implementation_location="training/train_phase3.py",
            implementation_status="PASS",
            evidence="Training emits checkpoints and reports with paper_claims_made false in the scaffold.",
            gap_description="No paper-performance claim is being made.",
            recommended_next_step="Keep smoke-training and paper-grade results segregated.",
        ),
    ]


def _write_csv(path: Path, rows: list[GapRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _make_summary(rows: list[GapRow]) -> dict[str, Any]:
    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "MISSING": 0}
    for row in rows:
        counts[row.implementation_status] += 1
    if counts["FAIL"]:
        overall = "FAIL"
    elif counts["MISSING"]:
        overall = "MISSING"
    elif counts["PARTIAL"]:
        overall = "PARTIAL"
    else:
        overall = "PASS"
    return {"overall_status": overall, "counts": counts}


def run_audit(output_dir: str | Path) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files_inspected = [
        "main.py",
        "environment/environment.py",
        "environment/server.py",
        "environment/cloud.py",
        "environment/queues.py",
        "environment/task.py",
        "environment/task_generator.py",
        "environment/action_model.py",
        "environment/matchmaker.py",
        "phase1_tracing.py",
        "phase2_mechanisms.py",
        "training/trace_dataset.py",
        "training/replay_buffer.py",
        "training/lstm_forecaster.py",
        "training/trainers.py",
        "training/train_phase3.py",
        "decision_makers/agent.py",
        "decision_makers/dummies.py",
        "hyperparameters/hyperparameters.json",
        "specs/100-hoodie-paper-faithful-baseline/contracts/paper-runtime-contract.md",
        "specs/100-hoodie-paper-faithful-baseline/contracts/paper-state-reward-contract.md",
        "specs/100-hoodie-paper-faithful-baseline/contracts/paper-lstm-training-contract.md",
        "specs/100-hoodie-paper-faithful-baseline/contracts/paper-topology-action-contract.md",
        "specs/100-hoodie-paper-faithful-baseline/contracts/paper-evaluation-figures-contract.md",
        "specs/100-hoodie-paper-faithful-baseline/checklists/system-model-ocr-122-747/system-model-checklist.md",
        "resources/papers/hoodie/ocr/merged.tex",
    ]

    state_rows = _classify_state_contract()
    action_rows = _classify_action_contract()
    reward_rows = _classify_reward_contract()
    lstm_rows = _classify_lstm_contract()
    training_rows = _classify_training_loop_contract()

    for name, rows in [
        ("state_contract_gap_matrix.csv", state_rows),
        ("action_contract_gap_matrix.csv", action_rows),
        ("reward_contract_gap_matrix.csv", reward_rows),
        ("lstm_contract_gap_matrix.csv", lstm_rows),
        ("training_loop_gap_matrix.csv", training_rows),
    ]:
        _write_csv(output_dir / name, rows)

    report = {
        "branch": "100-hoodie-paper-base",
        "audit_phase": "Phase 3.0",
        "runtime_behavior_changed": False,
        "paper_performance_claims_made": False,
        "files_inspected": files_inspected,
        "audit_status_by_dimension": {
            "state": _make_summary(state_rows),
            "action": _make_summary(action_rows),
            "reward": _make_summary(reward_rows),
            "lstm": _make_summary(lstm_rows),
            "training_loop": _make_summary(training_rows),
        },
        "blocker_gaps": [
            "Native paper-state vector is not produced at runtime.",
            "Reward is not collected as delayed task-completion tuples.",
            "LSTM does not implement W x (N+1) load forecasting.",
            "Training does not consume paper-native delayed replay tuples.",
        ],
        "non_blocker_gaps": [
            "Phase 2 action legality and trace semantics are already explicit.",
            "Checkpointing and smoke training exist, but they are not paper-grade proof.",
            "Trace reconstruction can support audit, but it remains an approximation.",
        ],
        "recommended_next_phase": "Phase 3.1 paper-state and delayed-reward runtime contract repair",
        "artifact_paths": {
            "report_json": str((output_dir / "phase3_fidelity_report.json").resolve()),
            "report_md": str((output_dir / "phase3_fidelity_report.md").resolve()),
            "state_contract_gap_matrix": str((output_dir / "state_contract_gap_matrix.csv").resolve()),
            "action_contract_gap_matrix": str((output_dir / "action_contract_gap_matrix.csv").resolve()),
            "reward_contract_gap_matrix": str((output_dir / "reward_contract_gap_matrix.csv").resolve()),
            "lstm_contract_gap_matrix": str((output_dir / "lstm_contract_gap_matrix.csv").resolve()),
            "training_loop_gap_matrix": str((output_dir / "training_loop_gap_matrix.csv").resolve()),
        },
        "assumptions": [
            "Current topology/action legality work from Phase 2 is accepted as the runtime baseline.",
            "The only usable Figure 7 reference is the user-approved manual extraction registry, not a paper-recovered matrix.",
            "No long simulations were run for this audit.",
            "Runtime behavior was not modified by this audit script.",
            "No paper-performance claim is being made.",
        ],
    }

    (output_dir / "phase3_fidelity_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))

    md_lines = [
        "# Phase 3.0 DRL/LSTM Fidelity Audit",
        "",
        "## Scope",
        "",
        "- Audit-only comparison of the current implementation against HOODIE DRL/LSTM contracts.",
        "- Runtime behavior unchanged.",
        "- No paper-performance claim made.",
        "",
        "## Files Inspected",
        "",
    ]
    md_lines.extend(f"- `{path}`" for path in files_inspected)
    md_lines.extend(
        [
            "",
            "## Paper Contracts Used",
            "",
            "- Section III.A.1 state space, Eq. (18)",
            "- Section III.A.2 action space, Eq. (19)",
            "- Section III.A.3 reward/cost, Eq. (20)–(23)",
            "- Section III.B problem formulation, Eq. (24)",
            "- Section IV.A HOODIE model",
            "- Figure 4 HOODIE neural network structure",
            "- Figure 5 LSTM load prediction model",
            "- Algorithm 1 HOODIE training",
            "- Eq. (25) dueling DQN",
            "- Double-DQN target update in Algorithm 1",
            "- Replay memory behavior in Algorithm 1",
            "- Delayed reward collection using D_n(t), Eq. (27)",
        ]
    )

    def _render_section(title: str, rows: list[GapRow]) -> None:
        md_lines.extend(["", f"## {title}", "", "| paper_variable | paper_equation_or_source | expected_meaning | implementation_location | implementation_status | evidence | gap_description | recommended_next_step |", "|---|---|---|---|---|---|---|---|"])
        for row in rows:
            md_lines.append(
                f"| {row.paper_variable} | {row.paper_equation_or_source} | {row.expected_meaning} | {row.implementation_location} | {row.implementation_status} | {row.evidence} | {row.gap_description} | {row.recommended_next_step} |"
            )

    _render_section("State Contract Audit Summary", state_rows)
    _render_section("Action Contract Audit Summary", action_rows)
    _render_section("Reward Contract Audit Summary", reward_rows)
    _render_section("LSTM Contract Audit Summary", lstm_rows)
    _render_section("Training-Loop Contract Audit Summary", training_rows)
    md_lines.extend(
        [
            "",
            "## Critical Blockers Before Phase 3.1",
            "",
        ]
    )
    for gap in report["blocker_gaps"]:
        md_lines.append(f"- {gap}")
    md_lines.extend(
        [
            "",
            "## Non-Blocking Limitations",
            "",
        ]
    )
    for gap in report["non_blocker_gaps"]:
        md_lines.append(f"- {gap}")
    md_lines.extend(
        [
            "",
            f"## Exact Next Recommended Sub-Phase",
            "",
            report["recommended_next_phase"],
            "",
            "Runtime behavior was unchanged.",
            "No paper-performance claim is made.",
        ]
    )
    (output_dir / "phase3_fidelity_report.md").write_text("\n".join(md_lines) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    run_audit(args.output_dir)


if __name__ == "__main__":
    main()
