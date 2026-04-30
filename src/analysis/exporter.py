from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

from .plot_builder import PlotBuilder
from .report_builder import ReportBuilder


@dataclass(slots=True)
class AnalysisExporter:
    report_builder: ReportBuilder
    plot_builder: PlotBuilder
    timestamp: str | None = None

    def export(self, output_dir: Path, *, deterministic: bool = False, timestamp: str | None = None) -> dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        export_timestamp = timestamp if timestamp is not None else self.timestamp
        if export_timestamp is None and not deterministic:
            export_timestamp = datetime.now(timezone.utc).isoformat()
        report_path = output_dir / "analysis_report.json"
        plot_path = output_dir / "analysis_plots.json"
        report_path.write_text(
            json.dumps(
                {
                    "timestamp": export_timestamp,
                    "report": self.report_builder.to_dict(),
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        plot_path.write_text(
            json.dumps(
                {
                    "timestamp": export_timestamp,
                    "plots": self.plot_builder.build_payload(),
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        result = {"report_path": str(report_path), "plot_path": str(plot_path)}
        if export_timestamp is not None:
            result["timestamp"] = export_timestamp
        return result
