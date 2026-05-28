from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PaperLSTMForecastInput:
    forecast_input_matrix: tuple[tuple[int, ...], ...]
    forecast_input_shape: tuple[int, int]
    forecast_input_source: str
    forecast_output_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "forecast_input_matrix": [list(row) for row in self.forecast_input_matrix],
            "forecast_input_shape": list(self.forecast_input_shape),
            "forecast_input_source": self.forecast_input_source,
            "forecast_output_status": self.forecast_output_status,
        }


def build_paper_lstm_forecast_input(active_queue_counts_by_node: dict[str, int], node_order: tuple[str, ...]) -> PaperLSTMForecastInput:
    row = tuple(int(active_queue_counts_by_node.get(node, 0)) for node in node_order)
    return PaperLSTMForecastInput(
        forecast_input_matrix=(row,),
        forecast_input_shape=(1, len(row)),
        forecast_input_source="active_queue_counts_by_node",
        forecast_output_status="contract_only_not_trained",
    )

