from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
src_analysis = Path(__file__).resolve().parent.parent / "src" / "analysis"
if src_analysis.exists():
    src_analysis_str = str(src_analysis)
    if src_analysis_str not in __path__:
        __path__.append(src_analysis_str)
