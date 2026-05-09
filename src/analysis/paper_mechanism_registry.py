from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _stable_relpath(base: Path, path: Path) -> str:
    return path.relative_to(base).as_posix()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _snippet(text: str, start: int, end: int) -> str:
    return _normalize(text[max(start, 0) : min(end, len(text))])


def _first_match(text: str, patterns: list[str], *, flags: int = re.IGNORECASE) -> tuple[int, int] | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.start(), match.end()
    return None


@dataclass(slots=True)
class MechanismEvidence:
    source_path: str
    section_or_context: str
    equation_or_table_reference: str | None
    figure_reference: str | None
    char_offset: int
    snippet_index: int
    ocr_snippet: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "section_or_context": self.section_or_context,
            "equation_or_table_reference": self.equation_or_table_reference,
            "figure_reference": self.figure_reference,
            "char_offset": self.char_offset,
            "snippet_index": self.snippet_index,
            "ocr_snippet": self.ocr_snippet,
        }


@dataclass(slots=True)
class MechanismEntry:
    mechanism_id: str
    mechanism_name: str
    category: str
    paper_status: str
    implementation_status: str
    assumption_risk: str
    paper_evidence: list[MechanismEvidence]
    expected_mechanism_behavior: str
    current_project_mapping: dict[str, object]
    missing_details: list[str]
    implementation_gaps: list[str]
    validation_implications: list[str]
    next_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mechanism_id": self.mechanism_id,
            "mechanism_name": self.mechanism_name,
            "category": self.category,
            "paper_status": self.paper_status,
            "implementation_status": self.implementation_status,
            "assumption_risk": self.assumption_risk,
            "paper_evidence": [evidence.to_dict() for evidence in self.paper_evidence],
            "expected_mechanism_behavior": self.expected_mechanism_behavior,
            "current_project_mapping": dict(self.current_project_mapping),
            "missing_details": list(self.missing_details),
            "implementation_gaps": list(self.implementation_gaps),
            "validation_implications": list(self.validation_implications),
            "next_action": self.next_action,
        }


@dataclass(slots=True)
class MechanismRegistryReport:
    input_sources: dict[str, object]
    registry_version: str
    read_only: bool
    behavior_changes: bool
    mechanism_entries: list[MechanismEntry]
    blocking_gaps: list[dict[str, object]]
    high_risk_assumptions: list[dict[str, object]]
    implementation_gap_summary: dict[str, object]
    next_recommended_feature: str
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "input_sources": dict(self.input_sources),
            "registry_version": self.registry_version,
            "read_only": self.read_only,
            "behavior_changes": self.behavior_changes,
            "mechanism_entries": [entry.to_dict() for entry in self.mechanism_entries],
            "blocking_gaps": list(self.blocking_gaps),
            "high_risk_assumptions": list(self.high_risk_assumptions),
            "implementation_gap_summary": dict(self.implementation_gap_summary),
            "next_recommended_feature": self.next_recommended_feature,
            "passed": self.passed,
        }


@dataclass(slots=True)
class _MechanismSpec:
    mechanism_id: str
    mechanism_name: str
    category: str
    paper_status: str
    implementation_status: str
    assumption_risk: str
    patterns: list[str]
    expected_mechanism_behavior: str
    current_project_mapping: dict[str, object]
    missing_details: list[str]
    implementation_gaps: list[str]
    validation_implications: list[str]
    next_action: str
    figure_reference: str | None = None
    equation_or_table_reference: str | None = None
    fallback_context: str = ""


class PaperMechanismRegistryBuilder:
    def __init__(self, paper_path: Path, artifact_root: Path, output_dir: Path):
        self.paper_path = Path(paper_path)
        self.artifact_root = Path(artifact_root)
        self.output_dir = Path(output_dir)
        self.figure_extraction_path = self.artifact_root / "analysis/paper-figure-extraction/paper-figure-extraction.json"
        self.audit_report_path = self.artifact_root / "campaigns/paper-baseline-reproduction/audit/audit-report.json"
        self.sensitivity_report_path = self.artifact_root / "campaigns/paper-baseline-reproduction/sensitivity/sensitivity-report.json"

    def _load_text(self) -> str:
        return self.paper_path.read_text(encoding="utf-8") if self.paper_path.exists() else ""

    def _load_optional_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _evidence(self, text: str, spec: _MechanismSpec) -> list[MechanismEvidence]:
        evidence: list[MechanismEvidence] = []
        match = _first_match(text, spec.patterns)
        if match is None:
            evidence.append(
                MechanismEvidence(
                    source_path=self.paper_path.as_posix(),
                    section_or_context="missing",
                    equation_or_table_reference=spec.equation_or_table_reference,
                    figure_reference=spec.figure_reference,
                    char_offset=-1,
                    snippet_index=0,
                    ocr_snippet=f"[MISSING EVIDENCE] No explicit OCR evidence located for {spec.mechanism_name}.",
                )
            )
            return evidence
        start, end = match
        evidence.append(
            MechanismEvidence(
                source_path=self.paper_path.as_posix(),
                section_or_context=spec.fallback_context or spec.category,
                equation_or_table_reference=spec.equation_or_table_reference,
                figure_reference=spec.figure_reference,
                char_offset=start,
                snippet_index=0,
                ocr_snippet=_snippet(text, start - 220, end + 420),
            )
        )
        return evidence

    def _source_inventory(self, text: str) -> dict[str, object]:
        supporting_sources = [
            Path("resources/papers/hoodie/ocr/merged.md"),
            Path("resources/papers/hoodie/ocr/merged.txt"),
            Path("resources/papers/hoodie/ocr/merged.json"),
            Path("resources/papers/hoodie/HOODIE_paper.pdf"),
            Path("artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json"),
            Path("artifacts/analysis/paper-figure-extraction/paper-figure-extraction.md"),
        ]
        return {
            "paper_ocr_path": self.paper_path.as_posix(),
            "paper_ocr_exists": self.paper_path.exists(),
            "paper_ocr_char_count": len(text),
            "supporting_inputs": [path.as_posix() for path in supporting_sources],
        }

    def _artifact_inventory(self) -> dict[str, object]:
        campaign_root = self.artifact_root / "campaigns/paper-baseline-reproduction"
        required = [
            "campaign/campaign-summary.json",
            "campaign/policy-summary.json",
            "campaign/scenario-summary.json",
            "campaign/determinism-check.json",
            "matrix/matrix-summary.csv",
            "matrix/traces",
        ]
        return {
            "analysis_output_root": self.output_dir.as_posix(),
            "campaign_root": campaign_root.as_posix(),
            "campaign_root_exists": campaign_root.exists(),
            "required_inputs": required,
            "present_campaign_artifacts": sorted(
                _stable_relpath(campaign_root, path)
                for path in campaign_root.rglob("*")
                if path.is_file()
            )
            if campaign_root.exists()
            else [],
        }

    def _load_figure_context(self) -> dict[str, Any]:
        return self._load_optional_json(self.figure_extraction_path, {})

    def _audit_context(self) -> dict[str, Any]:
        return self._load_optional_json(self.audit_report_path, {})

    def _sensitivity_context(self) -> dict[str, Any]:
        return self._load_optional_json(self.sensitivity_report_path, {})

    def _mechanism_specs(self) -> list[_MechanismSpec]:
        return [
            _MechanismSpec(
                mechanism_id="M001",
                mechanism_name="System Topology",
                category="system_topology",
                paper_status="partially_documented",
                implementation_status="partially_implemented",
                assumption_risk="blocking",
                patterns=[
                    r"multi-server topology graph",
                    r"Adjacent matrix",
                    r"Edge topology graph",
                    r"plotting the adjacent matrix G",
                ],
                expected_mechanism_behavior="A multi-server edge topology is defined with an adjacency matrix G over edge agents and cloud connectivity.",
                current_project_mapping={"module_paths": ["src/environment/topology.py", "src/environment/slot_engine.py"], "mapping_confidence": "high", "notes": "Topology representation is implemented in the environment layer."},
                missing_details=["Topology adjacency matrix G is not present as a structured artifact."],
                implementation_gaps=["Structured adjacency artifact is absent from the repository.", "Topology evidence is conceptual rather than encoded as a reusable registry artifact."],
                validation_implications=["A reference kernel or topology artifact is needed before topology assertions can be made beyond the OCR text."],
                next_action="requires_reference_kernel",
                figure_reference="Figure 7",
                equation_or_table_reference="Table 4",
                fallback_context="Section V.A / Table 4",
            ),
            _MechanismSpec(
                mechanism_id="M002",
                mechanism_name="Edge Agents and Cloud",
                category="edge_agents_and_cloud",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="low",
                patterns=[r"Set of EAs and Cloud", r"Edge Agents", r"Cloud entity maintains", r"Cloud processing capacity"],
                expected_mechanism_behavior="Each edge agent and the cloud are part of the cloud-edge continuum and participate in hybrid offloading decisions.",
                current_project_mapping={"module_paths": ["src/environment/environment.py", "src/environment/runtime_model.py"], "mapping_confidence": "high", "notes": "System entities are modeled in the runtime layer."},
                missing_details=["Precise boundary semantics between EC and EA roles are not fully formalized in the OCR text."],
                implementation_gaps=["Project mapping is clear, but the OCR is more descriptive than operational for controller relationships."],
                validation_implications=["The registry should not infer controller behavior beyond the paper's set definitions."],
                next_action="keep",
                figure_reference=None,
                equation_or_table_reference="Table 3",
                fallback_context="Table 3 / system model symbols",
            ),
            _MechanismSpec(
                mechanism_id="M003",
                mechanism_name="Action Space",
                category="action_space",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="high",
                patterns=[r"local computing", r"horizontal offloading", r"vertical offloading", r"single-step offloading decisions", r"available actions"],
                expected_mechanism_behavior="Agents choose among local processing, horizontal offload, and vertical offload, with single-step action semantics.",
                current_project_mapping={"module_paths": ["src/policies/action_masking.py", "src/policies/policy_interface.py"], "mapping_confidence": "high", "notes": "Action masking and policy interfaces define the action space."},
                missing_details=["Multi-hop action semantics are intentionally excluded by the paper's single-step constraint, but the exact legality matrix is not fully exposed."],
                implementation_gaps=["Need explicit reference kernel if action legality must be validated independently of current policy code."],
                validation_implications=["Action legality must be tested against topology and queue semantics."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M004",
                mechanism_name="Local Computation",
                category="local_computation",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"local task processor", r"private Processing Capacity of EA", r"processed locally", r"local computing"],
                expected_mechanism_behavior="Tasks may be processed locally by an EA using its private compute capacity.",
                current_project_mapping={"module_paths": ["src/environment/private_queue.py", "src/environment/execution_helper.py"], "mapping_confidence": "high", "notes": "Local execution and private queue behavior are modeled in the environment layer."},
                missing_details=["Exact local-computation timing formula is not fully restated in the OCR snippets we rely on."],
                implementation_gaps=["Need a reference kernel to verify local-compute timing from paper semantics alone."],
                validation_implications=["Local-compute duration and completion order should be covered by environment-level tests."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M005",
                mechanism_name="Horizontal Offloading",
                category="horizontal_offloading",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="high",
                patterns=[r"horizontal offloading", r"offload to another edge node", r"horizontal data rate", r"public queue"],
                expected_mechanism_behavior="Tasks can be offloaded from one EA to a neighboring EA through the horizontal link and processed via a public queue.",
                current_project_mapping={"module_paths": ["src/environment/offloading_queue.py", "src/environment/public_queue.py", "src/policies/ho.py"], "mapping_confidence": "high", "notes": "Horizontal offload and public queue behavior are present in the environment and policy layers."},
                missing_details=["Neighbor legality depends on topology adjacency, which is not recovered as structured data."],
                implementation_gaps=["Need adjacency-backed validation before horizontal routing can be treated as fully proven."],
                validation_implications=["Offload routing must be checked against topology and queue behavior."],
                next_action="requires_reference_kernel",
            ),
            _MechanismSpec(
                mechanism_id="M006",
                mechanism_name="Vertical Offloading",
                category="vertical_offloading",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"vertical offloading", r"offload to the cloud", r"vertical data rate", r"Cloud processing capacity"],
                expected_mechanism_behavior="Tasks can be offloaded from an EA to the cloud for processing through the vertical link.",
                current_project_mapping={"module_paths": ["src/environment/offloading_queue.py", "src/policies/vo.py"], "mapping_confidence": "high", "notes": "Vertical offload behavior is reflected in policy and environment modules."},
                missing_details=["Cloud queue semantics are not fully spelled out in the OCR text."],
                implementation_gaps=["A reference kernel is needed to validate cloud-handling semantics independently."],
                validation_implications=["Cloud offloading must be checked under deadline pressure and queueing behavior."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M007",
                mechanism_name="Private Queue",
                category="private_queue",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"private queue", r"waiting time of private task", r"completion time slot of private task", r"private Processing Capacity"],
                expected_mechanism_behavior="Each EA maintains a private queue for locally processed tasks with waiting and completion timing.",
                current_project_mapping={"module_paths": ["src/environment/private_queue.py"], "mapping_confidence": "high", "notes": "Private queue behavior is implemented in the environment layer."},
                missing_details=["Service discipline is only implicitly described by the OCR excerpts."],
                implementation_gaps=["Need explicit lifecycle tracing if queue order needs formal auditing."],
                validation_implications=["Private queue timing should be exercised by environment tests."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M008",
                mechanism_name="Public Queue",
                category="public_queue",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"public queue", r"FIFO public queue", r"active public queues", r"public processing capacity"],
                expected_mechanism_behavior="Offloaded tasks are inserted into FIFO public queues and processed under the destination node's public capacity.",
                current_project_mapping={"module_paths": ["src/environment/public_queue.py", "src/environment/offloading_queue.py"], "mapping_confidence": "high", "notes": "Public queue semantics are represented in the environment code."},
                missing_details=["The scheduling rules among multiple public queues are not fully explicit in the OCR excerpts."],
                implementation_gaps=["Need a reference kernel for queue-accounting checks if public queue rules are ambiguous."],
                validation_implications=["Public queue behavior must be compared with trace accounting."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M009",
                mechanism_name="Task Arrival Process",
                category="task_arrival_process",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="high",
                patterns=[r"stochastic traffic", r"Task Arrival Probability", r"arrival binary index", r"task arrived in EA", r"number of tasks arrived"],
                expected_mechanism_behavior="Tasks arrive stochastically with a Bernoulli arrival probability per EA and slot.",
                current_project_mapping={"module_paths": ["src/environment/traffic_generator.py", "src/environment/traffic_config.py"], "mapping_confidence": "high", "notes": "Traffic generation and configuration modules encode arrival behavior."},
                missing_details=["The exact randomization boundaries outside the OCR table are not fully recovered here."],
                implementation_gaps=["Need to compare trace arrivals against the paper traffic assumptions."],
                validation_implications=["Arrival process correctness influences all later sensitivity and fairness analysis."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M010",
                mechanism_name="Task Size Distribution",
                category="task_size_distribution",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"values of task size are drawn from the discrete set", r"Task size", r"\[2,2\.1", r"size of task"],
                expected_mechanism_behavior="Task sizes are drawn from a discrete set of values recovered from the OCR table.",
                current_project_mapping={"module_paths": ["src/environment/traffic_generator.py", "src/environment/task.py"], "mapping_confidence": "high", "notes": "Task size distribution is part of traffic generation and task modeling."},
                missing_details=["The OCR recovery of the size set is incomplete in places, so the discrete range should be treated as best-effort evidence."],
                implementation_gaps=["Need to compare the recovered size set against committed traces if finer validation is required."],
                validation_implications=["Task size variation drives delay and drop behavior."],
                next_action="recover_from_paper",
                equation_or_table_reference="Table 4",
            ),
            _MechanismSpec(
                mechanism_id="M011",
                mechanism_name="Processing Density",
                category="processing_density",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"processing density", r"gigacycles/Mbit", r"CPU cycles/bit"],
                expected_mechanism_behavior="Task processing density expresses how many CPU cycles per bit are required.",
                current_project_mapping={"module_paths": ["src/environment/task.py", "src/environment/compute_config.py"], "mapping_confidence": "high", "notes": "Processing density is modeled in the task and compute configuration layers."},
                missing_details=["OCR provides a value, but some surrounding unit annotations are noisy."],
                implementation_gaps=["Unit normalization must be checked against the paper text before assuming exact scale conversion."],
                validation_implications=["Processing density affects both local computation and offloading delay calculations."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M012",
                mechanism_name="CPU Capacity",
                category="cpu_capacity",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="high",
                patterns=[r"Private Processing Capacity of EA", r"Public processing capacity", r"Cloud processing capacity", r"CPU frequency in private queues"],
                expected_mechanism_behavior="Private, public, and cloud compute capacities determine whether tasks can be executed locally or offloaded.",
                current_project_mapping={"module_paths": ["src/environment/compute_config.py", "src/environment/runtime_model.py"], "mapping_confidence": "high", "notes": "Compute-capacity values are captured by the environment configuration layer."},
                missing_details=["Evaluation sweeps over CPU capacity exist in the paper, but the registry only captures the documented values, not a new sweep."],
                implementation_gaps=["Exact boundary handling across private, public, and cloud capacities remains a paper-to-code comparison point."],
                validation_implications=["CPU capacity is central to delay and drop behavior under load."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M013",
                mechanism_name="Link Data Rates",
                category="link_data_rates",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="high",
                patterns=[r"Horizontal Data Rate", r"Vertical Data Rate", r"Data rate between EA n and node k", r"Mbps"],
                expected_mechanism_behavior="Horizontal and vertical links use distinct data rates that influence offloading delay.",
                current_project_mapping={"module_paths": ["src/environment/compute_config.py", "src/environment/traffic_config.py"], "mapping_confidence": "high", "notes": "Network rate parameters are modeled in the environment configuration layer."},
                missing_details=["Exact topology-specific rate mapping is not fully explicit in the OCR excerpts."],
                implementation_gaps=["Need adjacency-backed validation to connect data rates to specific link pairs."],
                validation_implications=["Link-rate assumptions can materially alter horizontal and vertical offload latency."],
                next_action="requires_reference_kernel",
            ),
            _MechanismSpec(
                mechanism_id="M014",
                mechanism_name="Transmission Delay",
                category="transmission_delay",
                paper_status="partially_documented",
                implementation_status="assumption_backed",
                assumption_risk="medium",
                patterns=[r"offloading delay", r"data rate between EA n and node k", r"vertical offloading", r"horizontal offloading"],
                expected_mechanism_behavior="Transmission delay arises from moving tasks across horizontal or vertical links and should depend on task size and link rate.",
                current_project_mapping={"module_paths": ["src/environment/runtime_model.py", "src/environment/reward_timing.py"], "mapping_confidence": "medium", "notes": "Transmission timing is represented indirectly through runtime and reward timing modules."},
                missing_details=["The exact closed-form transmission-delay equation is not recovered here.", "Link-specific formulas are only partially exposed in OCR."],
                implementation_gaps=["Need explicit formula recovery before a strict paper-faithful check can be made."],
                validation_implications=["Transmission delay is a major source of paper-to-code drift if units are misread."],
                next_action="recover_from_paper",
            ),
            _MechanismSpec(
                mechanism_id="M015",
                mechanism_name="Computation Delay",
                category="computation_delay",
                paper_status="partially_documented",
                implementation_status="assumption_backed",
                assumption_risk="medium",
                patterns=[r"average task processing delays", r"task completion delay", r"completion time slot", r"processing density"],
                expected_mechanism_behavior="Computation delay reflects processing time for local, public, and cloud execution paths.",
                current_project_mapping={"module_paths": ["src/environment/execution_helper.py", "src/environment/reward_timing.py"], "mapping_confidence": "medium", "notes": "Execution and timing modules reflect computation-delay mechanics."},
                missing_details=["The precise delay decomposition is not fully restated in the OCR snippets.", "Unit normalization is incomplete in the OCR extraction."],
                implementation_gaps=["Need formula-level tracing before asserting exact paper-faithful delay math."],
                validation_implications=["Delay-sensitive behavior drives all comparison metrics and reward shaping."],
                next_action="recover_from_paper",
            ),
            _MechanismSpec(
                mechanism_id="M016",
                mechanism_name="Timeout and Drop",
                category="timeout_and_drop",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="blocking",
                patterns=[r"task timeout", r"dropped entirely when deadlines are missed", r"drop ratio", r"deadline violations"],
                expected_mechanism_behavior="Tasks that miss their deadlines are dropped, and timeout values constrain how long they may remain in the system.",
                current_project_mapping={"module_paths": ["src/environment/deadline_rules.py", "src/environment/reward_timing.py"], "mapping_confidence": "high", "notes": "Deadline and reward timing modules represent timeout and drop behavior."},
                missing_details=["The OCR exposes timeout values, but the exact terminal accounting path should be verified against the runtime kernel."],
                implementation_gaps=["Need careful validation against traces because timeout/drop strongly affects audit findings and fairness."],
                validation_implications=["Any mismatch here changes reported drop ratio and the validity of baseline comparisons."],
                next_action="requires_reference_kernel",
            ),
            _MechanismSpec(
                mechanism_id="M017",
                mechanism_name="Reward Definition",
                category="reward_definition",
                paper_status="documented",
                implementation_status="assumption_backed",
                assumption_risk="blocking",
                patterns=[r"cumulative reward, as defined in \(20\) and \(24\)", r"task delay is considered a negative metric", r"Task Drop Penalty", r"reward curves are negative"],
                expected_mechanism_behavior="Reward combines delayed-task completion value and drop penalties, and is only emitted on terminal outcomes.",
                current_project_mapping={"module_paths": ["src/environment/reward_timing.py", "src/evaluation/metric_formulas.py"], "mapping_confidence": "high", "notes": "Reward timing and metric-formula modules implement the reward path."},
                missing_details=["The exact equation text is not reconstructed here, only the paper references and convention are preserved."],
                implementation_gaps=["Reward formula validation should be tied back to the OCR equations before any repair work is attempted."],
                validation_implications=["Reward integrity is a high-risk point because it shapes all training and evaluation behavior."],
                next_action="requires_reference_kernel",
                equation_or_table_reference="(20), (24)",
            ),
            _MechanismSpec(
                mechanism_id="M018",
                mechanism_name="State Representation",
                category="state_representation",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="medium",
                patterns=[r"local task features and forecasts about the upcoming load", r"Historical load matrix", r"Public queues length", r"state input"],
                expected_mechanism_behavior="The state combines local task features with load-history and forecast information from the CEC environment.",
                current_project_mapping={"module_paths": ["src/environment/traffic_observer.py", "src/environment/runtime_model.py"], "mapping_confidence": "high", "notes": "Observation and runtime model modules hold state information."},
                missing_details=["Exact vector ordering is not fully described in the OCR snippets."],
                implementation_gaps=["Need a reference kernel to check that the state layout matches the paper semantics."],
                validation_implications=["State drift can alter policy behavior and invalidate learned comparisons."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M019",
                mechanism_name="Load Forecasting or LSTM Input",
                category="load_forecasting_or_lstm_input",
                paper_status="documented",
                implementation_status="assumption_backed",
                assumption_risk="high",
                patterns=[r"forecasts about the upcoming load", r"Historical load matrix", r"LSTM lookback window", r"load history"],
                expected_mechanism_behavior="The DRL agents consume load-history information and LSTM-based forecasts to anticipate upcoming demand.",
                current_project_mapping={"module_paths": ["src/agents/history_builder.py", "src/training/training_loop.py"], "mapping_confidence": "medium", "notes": "Load history and training loops are the closest project-side mappings."},
                missing_details=["Sequence length semantics and exact forecast encoding are not fully recoverable here."],
                implementation_gaps=["No committed proof here that the forecast pipeline matches the paper's intended input shape."],
                validation_implications=["Forecast input drift directly affects training stability and any LSTM claim."],
                next_action="requires_reference_kernel",
                equation_or_table_reference="Table 3 / Table 4",
            ),
            _MechanismSpec(
                mechanism_id="M020",
                mechanism_name="DQN Double Dueling LSTM Training",
                category="dqn_double_dueling_lstm_training",
                paper_status="documented",
                implementation_status="unknown",
                assumption_risk="high",
                patterns=[r"Double and Dueling DRL techniques", r"Long Short-term Memory", r"Replay Memory size", r"Q-network hidden layers", r"Learning rate", r"Discount factor"],
                expected_mechanism_behavior="The training stack uses DQN-style learning with double and dueling techniques, plus LSTM for enhanced stability and forecasting.",
                current_project_mapping={"module_paths": ["src/agents/double_dqn.py", "src/agents/dueling_dqn.py", "src/agents/torchrl_hoodie_learner.py", "src/training/training_loop.py"], "mapping_confidence": "medium", "notes": "Training and agent modules exist, but the paper-to-code fidelity is not yet proven by this registry."},
                missing_details=["Exact network topology and training hyperparameters are only partially visible in OCR.", "Committed artifacts do not prove the learned HOODIE stack itself."],
                implementation_gaps=["Training mechanics remain a future reference-kernel or repair topic, not something this registry can prove."],
                validation_implications=["Training claims must not be overinterpreted as validated implementation behavior."],
                next_action="requires_reference_kernel",
            ),
            _MechanismSpec(
                mechanism_id="M021",
                mechanism_name="Training Episode Protocol",
                category="training_episode_protocol",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="medium",
                patterns=[r"5000 episodes", r"number of time slots per episode", r"first 100 slots", r"last 10 slots", r"training phase"],
                expected_mechanism_behavior="Training runs over 5000 episodes with a fixed episode horizon and queue-emptying tail slots.",
                current_project_mapping={"module_paths": ["src/training/training_loop.py", "src/training/training_logging.py"], "mapping_confidence": "high", "notes": "Training loop and logging modules are the natural project-side mapping."},
                missing_details=["Exploration schedule and seed handling are not fully recovered from OCR here."],
                implementation_gaps=["Need validation against training logs if episode protocol fidelity becomes relevant."],
                validation_implications=["Episode protocol affects reward curves and any Fig. 8 / Fig. 11 reproduction claim."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M022",
                mechanism_name="Validation Episode Protocol",
                category="validation_episode_protocol",
                paper_status="documented",
                implementation_status="partially_implemented",
                assumption_risk="medium",
                patterns=[r"200 validation episodes", r"exploitative actions", r"validation episodes"],
                expected_mechanism_behavior="Validation uses trained Q-models over 200 episodes with exploitative actions.",
                current_project_mapping={"module_paths": ["src/evaluation/validation_runner.py", "src/evaluation/matrix_runner.py"], "mapping_confidence": "high", "notes": "Validation and matrix runners are the project-side mapping."},
                missing_details=["Exact trace reuse and pairing details are not fully spelled out in the OCR snippets."],
                implementation_gaps=["Validation protocol should be checked against audit and sensitivity outputs if needed."],
                validation_implications=["Validation semantics determine reported performance comparisons."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M023",
                mechanism_name="Baseline Policy Definitions",
                category="baseline_policy_definitions",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="low",
                patterns=[r"RO", r"FLC", r"VO", r"HO", r"BCO", r"MLEO", r"baseline methods", r"offloading schemes"],
                expected_mechanism_behavior="The paper compares HOODIE against named baselines such as RO, FLC, VO, HO, BCO, and MLEO.",
                current_project_mapping={"module_paths": ["src/policies/ro.py", "src/policies/flc.py", "src/policies/vo.py", "src/policies/ho.py", "src/policies/bco.py", "src/policies/mleo.py"], "mapping_confidence": "high", "notes": "Baseline policy modules are present in the repository."},
                missing_details=["Exact tie-breaking and all paper-side heuristics for the baselines are not fully enumerated in the OCR excerpts."],
                implementation_gaps=["Policy-by-policy fidelity should be checked in later fairness and differential features."],
                validation_implications=["Baselines are central to all comparison claims and fairness checks."],
                next_action="keep",
            ),
            _MechanismSpec(
                mechanism_id="M024",
                mechanism_name="Evaluation Metrics",
                category="evaluation_metrics",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="medium",
                patterns=[r"average delay", r"drop ratio", r"throughput", r"negative metric", r"reward values are negative", r"calculated over 200 validation episodes"],
                expected_mechanism_behavior="Evaluation reports average delay, drop ratio, throughput, and related reward behavior with paper-specific sign conventions.",
                current_project_mapping={"module_paths": ["src/evaluation/metrics.py", "src/evaluation/aggregate_metrics.py", "src/evaluation/per_trace_metrics.py"], "mapping_confidence": "high", "notes": "Metric calculation and aggregation are centralized in the evaluation layer."},
                missing_details=["The paper's negative-delay convention must remain a caveat because repository outputs may preserve positive stored values."],
                implementation_gaps=["Exact aggregation formulas should be checked against the paper equations if metric repair is ever attempted."],
                validation_implications=["Any metric drift would invalidate comparison and audit outputs."],
                next_action="inspect_source",
            ),
            _MechanismSpec(
                mechanism_id="M025",
                mechanism_name="Figure Result Requirements",
                category="figure_result_requirements",
                paper_status="documented",
                implementation_status="implemented",
                assumption_risk="low",
                patterns=[r"FIGURE 7", r"FIGURE 8", r"FIGURE 9", r"FIGURE 10", r"FIGURE 11"],
                expected_mechanism_behavior="The paper requires specific evaluation outputs across figures 7 through 11 and associated narrative claims.",
                current_project_mapping={"module_paths": ["src/analysis/paper_figure_extraction.py", "artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json"], "mapping_confidence": "high", "notes": "Figure extraction outputs already exist as analysis artifacts."},
                missing_details=["Figure numbers alone do not prove reproducibility of the underlying mechanisms."],
                implementation_gaps=["Figure requirements are only comparison scaffolding until mechanism fidelity is proven elsewhere."],
                validation_implications=["The registry must not confuse figure support with full paper validation."],
                next_action="keep",
            ),
        ]

    def _build_entries(self, text: str) -> list[MechanismEntry]:
        entries: list[MechanismEntry] = []
        for spec in self._mechanism_specs():
            evidence = self._evidence(text, spec)
            entries.append(
                MechanismEntry(
                    mechanism_id=spec.mechanism_id,
                    mechanism_name=spec.mechanism_name,
                    category=spec.category,
                    paper_status=spec.paper_status,
                    implementation_status=spec.implementation_status,
                    assumption_risk=spec.assumption_risk,
                    paper_evidence=evidence,
                    expected_mechanism_behavior=spec.expected_mechanism_behavior,
                    current_project_mapping=spec.current_project_mapping,
                    missing_details=spec.missing_details,
                    implementation_gaps=spec.implementation_gaps,
                    validation_implications=spec.validation_implications,
                    next_action=spec.next_action,
                )
            )
        return entries

    def _blocking_gaps(self, entries: list[MechanismEntry]) -> list[dict[str, object]]:
        gaps: list[dict[str, object]] = []
        for entry in entries:
            if entry.category == "system_topology":
                gaps.append(
                    {
                        "category": entry.category,
                        "severity": "blocking",
                        "description": "Topology adjacency is not present as a structured artifact.",
                    }
                )
            if entry.category in {"reward_definition", "timeout_and_drop"}:
                gaps.append(
                    {
                        "category": entry.category,
                        "severity": "high",
                        "description": f"{entry.mechanism_name} requires paper-faithful validation before any repair feature.",
                    }
                )
        return gaps

    def _high_risk_assumptions(self, entries: list[MechanismEntry]) -> list[dict[str, object]]:
        assumptions: list[dict[str, object]] = []
        for entry in entries:
            if entry.category in {"cpu_capacity", "link_data_rates", "transmission_delay", "computation_delay", "timeout_and_drop", "reward_definition", "dqn_double_dueling_lstm_training"}:
                assumptions.append(
                    {
                        "category": entry.category,
                        "assumption_risk": entry.assumption_risk,
                        "description": entry.missing_details[0] if entry.missing_details else entry.expected_mechanism_behavior,
                    }
                )
        return assumptions

    def _gap_summary(self, entries: list[MechanismEntry]) -> dict[str, object]:
        mapped_in_project = sum(1 for entry in entries if entry.current_project_mapping.get("module_paths"))
        paper_validated = 0
        mapped_but_unvalidated = mapped_in_project - paper_validated
        return {
            "documented": sum(1 for entry in entries if entry.paper_status == "documented"),
            "partially_documented": sum(1 for entry in entries if entry.paper_status == "partially_documented"),
            "ambiguous": sum(1 for entry in entries if entry.paper_status == "ambiguous"),
            "missing": sum(1 for entry in entries if entry.paper_status == "missing"),
            "implemented": sum(1 for entry in entries if entry.implementation_status == "implemented"),
            "partially_implemented": sum(1 for entry in entries if entry.implementation_status == "partially_implemented"),
            "assumption_backed": sum(1 for entry in entries if entry.implementation_status == "assumption_backed"),
            "unknown": sum(1 for entry in entries if entry.implementation_status == "unknown"),
            "not_implemented": sum(1 for entry in entries if entry.implementation_status == "not_implemented"),
            "mapped_in_project": mapped_in_project,
            "mapped_but_unvalidated": mapped_but_unvalidated,
            "paper_validated": paper_validated,
            "total_entries": len(entries),
        }

    def _passed(self, entries: list[MechanismEntry]) -> bool:
        required_categories = {
            "system_topology",
            "edge_agents_and_cloud",
            "action_space",
            "local_computation",
            "horizontal_offloading",
            "vertical_offloading",
            "private_queue",
            "public_queue",
            "task_arrival_process",
            "task_size_distribution",
            "processing_density",
            "cpu_capacity",
            "link_data_rates",
            "transmission_delay",
            "computation_delay",
            "timeout_and_drop",
            "reward_definition",
            "state_representation",
            "load_forecasting_or_lstm_input",
            "dqn_double_dueling_lstm_training",
            "training_episode_protocol",
            "validation_episode_protocol",
            "baseline_policy_definitions",
            "evaluation_metrics",
            "figure_result_requirements",
        }
        return required_categories == {entry.category for entry in entries} and bool(entries)

    def build_report(self) -> MechanismRegistryReport:
        text = self._load_text()
        entries = self._build_entries(text)
        report = MechanismRegistryReport(
            input_sources={
                "paper_ocr": self.paper_path.as_posix(),
                "secondary_sources": [
                    "resources/papers/hoodie/ocr/merged.md",
                    "resources/papers/hoodie/ocr/merged.txt",
                    "resources/papers/hoodie/ocr/merged.json",
                    "resources/papers/hoodie/HOODIE_paper.pdf",
                    "artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json",
                    "artifacts/analysis/paper-figure-extraction/paper-figure-extraction.md",
                    "artifacts/campaigns/paper-baseline-reproduction/audit/audit-report.json",
                    "artifacts/campaigns/paper-baseline-reproduction/sensitivity/sensitivity-report.json",
                ],
            },
            registry_version="016",
            read_only=True,
            behavior_changes=False,
            mechanism_entries=entries,
            blocking_gaps=self._blocking_gaps(entries),
            high_risk_assumptions=self._high_risk_assumptions(entries),
            implementation_gap_summary=self._gap_summary(entries),
            next_recommended_feature="reference_task_lifecycle_kernel",
            passed=self._passed(entries),
        )
        return report

    def render_markdown(self, report: MechanismRegistryReport) -> str:
        lines: list[str] = []
        lines.append("# Paper Mechanism Registry")
        lines.append("")
        lines.append("Read-only warning: this registry is analysis-only and does not change simulator behavior.")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        lines.append(f"| Registry Version | {report.registry_version} |")
        lines.append(f"| Read Only | {str(report.read_only).lower()} |")
        lines.append(f"| Behavior Changes | {str(report.behavior_changes).lower()} |")
        lines.append(f"| Passed | {str(report.passed).lower()} |")
        lines.append("")
        lines.append("## Blocking Gaps")
        for gap in report.blocking_gaps:
            lines.append(f"- {gap['category']}: {gap['description']} ({gap['severity']})")
        lines.append("")
        lines.append("## High-Risk Assumptions")
        for assumption in report.high_risk_assumptions:
            lines.append(f"- {assumption['category']}: {assumption['description']} ({assumption['assumption_risk']})")
        lines.append("")
        lines.append("## Mechanism Entries")
        for entry in report.mechanism_entries:
            lines.append(f"### {entry.mechanism_id} - {entry.mechanism_name}")
            lines.append(f"- Category: `{entry.category}`")
            lines.append(f"- Paper Status: `{entry.paper_status}`")
            lines.append(f"- Implementation Status: `{entry.implementation_status}`")
            lines.append(f"- Assumption Risk: `{entry.assumption_risk}`")
            lines.append(f"- Next Action: `{entry.next_action}`")
            lines.append(f"- Expected Behavior: {entry.expected_mechanism_behavior}")
            lines.append(f"- Missing Details: {', '.join(entry.missing_details) if entry.missing_details else 'None'}")
            lines.append(f"- Implementation Gaps: {', '.join(entry.implementation_gaps) if entry.implementation_gaps else 'None'}")
            lines.append(f"- Validation Implications: {', '.join(entry.validation_implications) if entry.validation_implications else 'None'}")
            lines.append("- Evidence:")
            for evidence in entry.paper_evidence:
                lines.append(f"  - [{evidence.section_or_context}] {evidence.ocr_snippet}")
        lines.append("")
        lines.append("## Implementation Gap Summary")
        for key, value in report.implementation_gap_summary.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
        lines.append(f"Recommended next feature: `{report.next_recommended_feature}`")
        lines.append("")
        lines.append("No runtime changes statement: this registry is read-only and does not validate paper reproduction.")
        return "\n".join(lines) + "\n"

    def write_outputs(self, report: MechanismRegistryReport) -> tuple[Path, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "paper-mechanism-registry.json"
        md_path = self.output_dir / "paper-mechanism-registry.md"
        json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
        md_path.write_text(self.render_markdown(report), encoding="utf-8")
        return json_path, md_path

    def run(self) -> MechanismRegistryReport:
        report = self.build_report()
        self.write_outputs(report)
        return report
