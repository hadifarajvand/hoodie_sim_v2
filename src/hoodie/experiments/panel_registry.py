from __future__ import annotations

from dataclasses import dataclass

from .specification import PanelSpec

@dataclass(frozen=True, slots=True)
class PanelContract:
    spec: PanelSpec
    source_contract: str | None = None

PANEL_REGISTRY: dict[str, PanelContract] = {
    "figure_8a": PanelContract(PanelSpec("figure_8a", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "reward"), output_filenames=("figure_8a.svg",))),
    "figure_8b": PanelContract(PanelSpec("figure_8b", "seed", {}, ("HOODIE",), variants=("hoodie_lstm", "hoodie_no_lstm"), expected_columns=("seed", "reward"), output_filenames=("figure_8b.svg",))),
    "figure_9a": PanelContract(PanelSpec("figure_9a", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "completion_ratio"), output_filenames=("figure_9a.svg",))),
    "figure_9b": PanelContract(PanelSpec("figure_9b", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "drop_ratio"), output_filenames=("figure_9b.svg",))),
    "figure_9c": PanelContract(PanelSpec("figure_9c", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "delay"), output_filenames=("figure_9c.svg",))),
    "figure_9d": PanelContract(PanelSpec("figure_9d", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "reward"), output_filenames=("figure_9d.svg",))),
    "figure_9e": PanelContract(PanelSpec("figure_9e", "policy", {}, ("FLC", "RO", "HO", "VO", "BCO", "MLEO"), expected_columns=("policy", "provenance"), output_filenames=("figure_9e.svg",))),
    "figure_10a": PanelContract(PanelSpec("figure_10a", "seed", {}, ("HOODIE",), expected_columns=("seed", "loss"), output_filenames=("figure_10a.svg",))),
    "figure_10b": PanelContract(PanelSpec("figure_10b", "seed", {}, ("HOODIE",), expected_columns=("seed", "epsilon"), output_filenames=("figure_10b.svg",))),
    "figure_10c": PanelContract(PanelSpec("figure_10c", "seed", {}, ("HOODIE",), expected_columns=("seed", "checkpoint"), output_filenames=("figure_10c.svg",))),
    "figure_10d": PanelContract(PanelSpec("figure_10d", "seed", {}, ("HOODIE",), expected_columns=("seed", "trace"), output_filenames=("figure_10d.svg",))),
    "figure_10e": PanelContract(PanelSpec("figure_10e", "seed", {}, ("HOODIE",), expected_columns=("seed", "dataset"), output_filenames=("figure_10e.svg",))),
    "figure_10f": PanelContract(PanelSpec("figure_10f", "seed", {}, ("HOODIE",), expected_columns=("seed", "provenance"), output_filenames=("figure_10f.svg",))),
    "figure_11": PanelContract(PanelSpec("figure_11", "variant", {}, ("HOODIE",), variants=("hoodie_lstm", "hoodie_no_lstm"), expected_columns=("variant", "reward"), output_filenames=("figure_11.svg",))),
}
