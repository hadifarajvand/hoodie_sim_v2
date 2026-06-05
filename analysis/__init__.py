from __future__ import annotations

from pathlib import Path

_SRC_ANALYSIS = Path(__file__).resolve().parent.parent / "src" / "analysis"
if _SRC_ANALYSIS.exists():
    __path__.append(str(_SRC_ANALYSIS))  # type: ignore[name-defined]

