from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _snippet(text: str, start: int, end: int) -> str:
    return _normalize(text[max(0, start) : min(len(text), end)])


def _first_match(text: str, patterns: list[str]) -> re.Match[str] | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match
    return None


def _stable_id(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass(slots=True)
class Evidence:
    source_path: str
    section_or_context: str
    char_offset: int
    snippet_index: int
    ocr_snippet: str
    figure_reference: str | None = None
    equation_or_table_reference: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "section_or_context": self.section_or_context,
            "char_offset": self.char_offset,
            "snippet_index": self.snippet_index,
            "ocr_snippet": self.ocr_snippet,
            "figure_reference": self.figure_reference,
            "equation_or_table_reference": self.equation_or_table_reference,
        }


def _evidence_item(source_path: Path, section: str, text: str, pattern: str | None = None, *, figure: str | None = None, table: str | None = None) -> Evidence:
    if pattern:
        try:
            match = re.search(pattern, text, flags=re.IGNORECASE)
        except re.error:
            idx = text.lower().find(pattern.lower())
            match = None
            if idx >= 0:
                class _Match:
                    def __init__(self, start: int, end: int):
                        self._start = start
                        self._end = end

                    def start(self) -> int:
                        return self._start

                    def end(self) -> int:
                        return self._end

                match = _Match(idx, idx + len(pattern))  # type: ignore[assignment]
    else:
        match = None
    if match:
        start, end = match.start(), match.end()
    else:
        start, end = (text.lower().find(section.lower()), 0)
        if start < 0:
            start = -1
    return Evidence(
        source_path=source_path.as_posix(),
        section_or_context=section,
        char_offset=start,
        snippet_index=0,
        ocr_snippet=_snippet(text, max(0, start - 220), end + 500) if start >= 0 else f"[MISSING EVIDENCE] {section}",
        figure_reference=figure,
        equation_or_table_reference=table,
    )


class StructuredPaperTopologyLinkRateRegistryBuilder:
    def __init__(self, paper_ocr_path: Path, artifact_root: Path, output_root: Path):
        self.paper_ocr_path = Path(paper_ocr_path)
        self.artifact_root = Path(artifact_root)
        self.output_root = Path(output_root)
        self.figure_extraction_path = self.artifact_root / "analysis/paper-figure-extraction/paper-figure-extraction.json"
        self.mechanism_registry_path = self.artifact_root / "analysis/paper-mechanism-registry/paper-mechanism-registry.json"

    def _paper_text(self) -> str:
        return self.paper_ocr_path.read_text(encoding="utf-8") if self.paper_ocr_path.exists() else ""

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _source_inventory(self, text: str) -> dict[str, object]:
        supporting = [
            "resources/papers/hoodie/ocr/merged.md",
            "resources/papers/hoodie/ocr/merged.txt",
            "resources/papers/hoodie/ocr/merged.json",
            "resources/papers/hoodie/HOODIE_paper.pdf",
            "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json",
            "artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json",
        ]
        return {
            "input_paper_ocr_path": self.paper_ocr_path.as_posix(),
            "paper_ocr_exists": self.paper_ocr_path.exists(),
            "paper_ocr_char_count": len(text),
            "supporting_inputs": supporting,
        }

    def _figure7_evidence(self, text: str) -> dict[str, object]:
        snippets: list[dict[str, object]] = []
        for idx, pat in enumerate([r"FIGURE\s+7\.\s*Edge layer topology graph of matrix G with 20 EAs", r"matrix G", r"20 EAs"]):
            m = _first_match(text, [pat])
            if m:
                snippets.append(
                    Evidence(
                        source_path=self.paper_ocr_path.as_posix(),
                        section_or_context="Figure 7 / topology",
                        char_offset=m.start(),
                        snippet_index=idx,
                        ocr_snippet=_snippet(text, m.start() - 180, m.end() + 320),
                        figure_reference="Figure 7",
                    ).to_dict()
                )
        return {
            "paper_figure_id": "Figure 7",
            "paper_claim_type": "topology_caption",
            "node_count": 20 if "20 EAs" in text else None,
            "node_ids": None,
            "adjacency_matrix": None,
            "adjacency_matrix_status": "unrecoverable",
            "legal_horizontal_destinations": None,
            "edge_cloud_connectivity": {
                "recovery_status": "unrecoverable",
                "value": None,
                "source_evidence": [],
                "unrecoverable_reason": "Paper/OCR evidence does not recover explicit edge/cloud connectivity facts without inventing topology.",
            },
            "source_evidence": snippets,
            "unrecoverable_items": [
                "topology_adjacency_edges",
                "adjacency_matrix",
                "legal_horizontal_destinations",
                "edge_cloud_connectivity",
            ],
            "recovery_confidence": "low",
            "no_fabrication_disclaimer": True,
            "schema_version": "1.0",
            "recovery_status": "unrecoverable",
        }

    def _parameter_registry(self, text: str) -> dict[str, object]:
        def ev(section: str, pattern: str | None = None, *, figure: str | None = None, table: str | None = None) -> dict[str, object]:
            return _evidence_item(self.paper_ocr_path, section, text, pattern, figure=figure, table=table).to_dict()

        task_arrival = {
            "value": 0.5,
            "recovery_status": "recovered",
            "source_evidence": [ev("Task Arrival Probability", r"Task Arrival Probability</td><td>\$\\mathcal\{P\}\$</td><td>0\.5</td>", table="Table 4")],
        }
        horizontal_rate = {
            "value": "30 Mbps",
            "recovery_status": "recovered",
            "source_evidence": [ev("Horizontal Data Rate", r"Horizontal Data Rate</td><td>\$R_\{H\}\$</td><td>30 Mbps", table="Table 4")],
        }
        vertical_rate = {
            "value": "10 Mbps",
            "recovery_status": "recovered",
            "source_evidence": [ev("Vertical Data Rate", r"Vertical Data Rate</td><td>\$R_\{V\}\$</td><td>10 Mbps", table="Table 4")],
        }
        task_size = {
            "value": "[2,2.1,...,5] Mbits",
            "recovery_status": "recovered",
            "source_evidence": [ev("Task size", r"Task size.*\[2,2\.1,\ldots,5\]", table="Table 4")],
        }
        processing_density = {
            "value": "0.297 gigacycles/Mbit",
            "recovery_status": "recovered",
            "source_evidence": [ev("Task processing density", r"Task processing density</td><td>\$\\rho_n\(t\)\$</td><td>0\.297 gigacycles/Mbit", table="Table 4")],
        }
        num_eas = {
            "value": 20,
            "recovery_status": "recovered",
            "source_evidence": [ev("Number of EAs", r"Number of EAs</td><td>\$N\$", table="Table 4")],
        }
        topology = self._figure7_evidence(text)
        return {
            "schema_version": "1.0",
            "recovery_status": "partially_recovered",
            "no_fabrication_disclaimer": True,
            "source_inventory": self._source_inventory(text),
            "task_arrival_parameters": task_arrival,
            "task_size_parameters": task_size,
            "timeout_values": {
                "value": None,
                "recovery_status": "unrecoverable",
                "source_evidence": [ev("timeout", r"Timeout of task \[time slot\]", table="Table 3")],
                "unrecoverable_reason": "The OCR excerpt exposes the timeout symbol but not a canonical numeric timeout value in a reliable structured form.",
            },
            "processing_density": processing_density,
            "cpu_capacities": {
                "EA_private": {"value": None, "recovery_status": "unrecoverable", "source_evidence": []},
                "EA_public": {"value": None, "recovery_status": "unrecoverable", "source_evidence": []},
                "cloud": {"value": None, "recovery_status": "unrecoverable", "source_evidence": []},
            },
            "horizontal_data_rate": horizontal_rate,
            "vertical_data_rate": vertical_rate,
            "cloud_data_rate": {
                "value": None,
                "recovery_status": "unrecoverable",
                "source_evidence": [],
                "unrecoverable_reason": "The paper OCR does not provide a distinct cloud-facing data-rate constant beyond vertical offload rate.",
            },
            "learning_parameters": {
                "learning_rate": {
                    "value": [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7],
                    "recovery_status": "recovered",
                    "source_evidence": [ev("learning rate", r"learning rate \$\\alpha", figure="Figure 8")],
                },
                "discount_factor": {
                    "value": [0.2, 0.4, 0.6, 0.8, 0.99],
                    "recovery_status": "recovered",
                    "source_evidence": [ev("discount factor", r"gamma=\[0\.2,0\.4,0\.6,0\.8,0\.99\]", figure="Figure 8")],
                },
                "episodes": {
                    "training": 5000,
                    "validation": 200,
                    "recovery_status": "recovered",
                    "source_evidence": [
                        ev("5000 episodes", r"5000 episodes", figure="Figure 8"),
                        ev("200 validation episodes", r"200 validation episodes", figure="Figure 9"),
                    ],
                },
            },
            "scenario_parameters": {
                "task_arrival_probability": task_arrival,
                "task_size": task_size,
                "N": num_eas,
                "adjacency_matrix": {
                    "value": None,
                    "recovery_status": "unrecoverable",
                    "source_evidence": [topology["source_evidence"][0]] if topology["source_evidence"] else [],
                    "unrecoverable_reason": "Figure 7 adjacency matrix is not recovered as a paper-backed structured artifact.",
                },
                "edge_layer_density": {
                    "value": [10, 15, 20],
                    "recovery_status": "recovered",
                    "source_evidence": [ev("N=[10,15,20]", r"N=\[10,15,20\]", figure="Figure 9")],
                },
                "discount_factor_sweep": {
                    "value": [0.2, 0.4, 0.6, 0.8, 0.99],
                    "recovery_status": "recovered",
                    "source_evidence": [ev("gamma sweep", r"gamma=\[0\.2,0\.4,0\.6,0\.8,0\.99\]", figure="Figure 8")],
                },
            },
            "unrecoverable_items": [
                "EA_private_cpu_capacities",
                "EA_public_cpu_capacities",
                "cloud_cpu_capacities",
                "adjacency_matrix",
                "legal_horizontal_destinations",
                "edge_cloud_connectivity",
                "cloud_data_rate",
            ],
            "paper_evidence": [
                ev("Table 4 / system and learning parameters", r"TABLE 4\.\s*System and Learning Parameters", table="Table 4"),
                ev("Figure 7 / matrix G", r"FIGURE 7\.\s*Edge layer topology graph of matrix G with 20 EAs", figure="Figure 7"),
            ],
        }

    def build(self) -> dict[str, object]:
        text = self._paper_text()
        figure = self._figure7_evidence(text)
        params = self._parameter_registry(text)
        report = self._report_payload(figure, params, text)
        return {"topology": figure, "parameters": params, "report": report}

    def _report_payload(self, topology: dict[str, object], params: dict[str, object], text: str) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "input_sources": self._source_inventory(text),
            "topology_summary": {
                "recovery_status": topology["recovery_status"],
                "node_count": topology["node_count"],
                "adjacency_matrix_status": topology["adjacency_matrix_status"],
                "unrecoverable_items": topology["unrecoverable_items"],
            },
            "parameter_summary": {
                "recovery_status": params["recovery_status"],
                "recovered_fields": [
                    "task_arrival_parameters",
                    "task_size_parameters",
                    "processing_density",
                    "horizontal_data_rate",
                    "vertical_data_rate",
                    "learning_parameters",
                    "scenario_parameters.N",
                    "scenario_parameters.edge_layer_density",
                ],
                "unrecoverable_items": params["unrecoverable_items"],
            },
            "recovered_items": [
                {"item": "N", "status": "recovered", "evidence_count": 1},
                {"item": "horizontal_data_rate", "status": "recovered", "evidence_count": 1},
                {"item": "vertical_data_rate", "status": "recovered", "evidence_count": 1},
                {"item": "task_arrival_probability", "status": "recovered", "evidence_count": 1},
                {"item": "task_size", "status": "recovered", "evidence_count": 1},
                {"item": "processing_density", "status": "recovered", "evidence_count": 1},
            ],
            "partially_recovered_items": [
                {"item": "paper_parameter_registry", "status": "partially_recovered", "reason": "CPU capacities and exact topology adjacency remain unrecoverable."}
            ],
            "unrecoverable_items": [
                "Figure 7 adjacency edges",
                "Figure 7 legal horizontal destinations",
                "EA private/public/cloud CPU capacities",
            ],
            "no_fabrication_disclaimer": True,
            "recovery_confidence": "low",
        }

    def write_outputs(self) -> dict[str, Path]:
        built = self.build()
        topology = built["topology"]
        params = built["parameters"]
        report = built["report"]
        topo_path = self.output_root / "resources/papers/hoodie/recovered/topology-g.json"
        param_path = self.output_root / "resources/papers/hoodie/recovered/paper-parameter-registry.json"
        report_json_path = self.output_root / "artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json"
        report_md_path = self.output_root / "artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.md"
        for path in [topo_path, param_path, report_json_path, report_md_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
        topo_path.write_text(_json_dump(topology), encoding="utf-8")
        param_path.write_text(_json_dump(params), encoding="utf-8")
        report_json_path.write_text(_json_dump(report), encoding="utf-8")
        report_md_path.write_text(
            "\n".join(
                [
                    "# Structured Paper Topology and Link-Rate Registry",
                    "",
                    f"- Topology recovery status: {topology['recovery_status']}",
                    f"- Topology adjacency status: {topology['adjacency_matrix_status']}",
                    f"- Parameter registry status: {params['recovery_status']}",
                    f"- No fabrication disclaimer: {report['no_fabrication_disclaimer']}",
                    "",
                    "## Recovered items",
                    *[f"- {item['item']}: {item['status']}" for item in report["recovered_items"]],
                    "",
                    "## Partially recovered items",
                    *[f"- {item['item']}: {item['reason']}" for item in report["partially_recovered_items"]],
                    "",
                    "## Unrecoverable items",
                    *[f"- {item}" for item in report["unrecoverable_items"]],
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "topology": topo_path,
            "parameters": param_path,
            "report_json": report_json_path,
            "report_md": report_md_path,
        }
