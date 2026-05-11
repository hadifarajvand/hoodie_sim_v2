from __future__ import annotations

from pathlib import Path

from .audit import DifferentialEnvironmentAudit, build_default_toy_cases
from .report import build_instrumentation_summary


def run_differential_environment_audit(
    *,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    audit = DifferentialEnvironmentAudit(output_dir=output_dir)
    report = audit.run(build_default_toy_cases())
    return audit.output_dir / "differential-audit.json", audit.output_dir / "differential-audit.md"


def run_offload_lifecycle_instrumentation_summary(
    *,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    audit = DifferentialEnvironmentAudit(output_dir=output_dir)
    report = audit.run(build_default_toy_cases())
    summary = build_instrumentation_summary(report)
    summary_dir = Path("artifacts/analysis/offload-lifecycle-instrumentation")
    if output_dir is not None:
        summary_dir = Path(output_dir)
    return summary.write(summary_dir)

