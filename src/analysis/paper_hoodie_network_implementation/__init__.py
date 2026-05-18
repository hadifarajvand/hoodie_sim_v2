from __future__ import annotations

from .report import (
    DuelingHeads,
    LstmEncoder,
    OnlineTargetNetworkPair,
    PaperHoodieNetworkConfig,
    QNetworkBody,
    ShapeValidationReport,
    build_network_implementation_report,
    write_network_implementation_report,
)


def build_online_network(*args, **kwargs):
    from .network import build_online_network as _build_online_network

    return _build_online_network(*args, **kwargs)


def build_target_network(*args, **kwargs):
    from .network import build_target_network as _build_target_network

    return _build_target_network(*args, **kwargs)


try:  # pragma: no cover - only used when torch is available
    from .network import PaperHoodieDuelingNetwork
except ModuleNotFoundError:  # pragma: no cover - dependency-blocked path
    PaperHoodieDuelingNetwork = None  # type: ignore[assignment]

__all__ = [
    "DuelingHeads",
    "LstmEncoder",
    "OnlineTargetNetworkPair",
    "PaperHoodieNetworkConfig",
    "QNetworkBody",
    "PaperHoodieDuelingNetwork",
    "ShapeValidationReport",
    "build_online_network",
    "build_target_network",
    "build_network_implementation_report",
    "write_network_implementation_report",
]
