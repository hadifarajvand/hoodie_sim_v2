from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any


@dataclass(frozen=True)
class StatisticalSummary:
    mean: float | None
    variance: float | None
    stddev: float | None

    def to_dict(self) -> dict[str, Any]:
        return {"mean": self.mean, "variance": self.variance, "stddev": self.stddev}


def compute_mean_std(data: list[float]) -> StatisticalSummary:
    if not data:
        return StatisticalSummary(None, None, None)
    if len(data) == 1:
        return StatisticalSummary(float(data[0]), 0.0, 0.0)
    return StatisticalSummary(float(mean(data)), float(pstdev(data) ** 2), float(pstdev(data)))


def compute_confidence_interval_95(data: list[float]) -> tuple[float | None, float | None]:
    if not data:
        return None, None
    mu = float(mean(data))
    if len(data) == 1:
        return mu, mu
    sd = float(math.sqrt(sum((x - mu) ** 2 for x in data) / len(data)))
    half = 1.96 * sd / math.sqrt(len(data))
    return mu - half, mu + half


def t_test_independent(sample_a: list[float], sample_b: list[float]) -> dict[str, Any]:
    if not sample_a or not sample_b:
        return {"t_stat": None, "df": None, "p_value": None}
    mean_a = mean(sample_a)
    mean_b = mean(sample_b)
    var_a = pstdev(sample_a) ** 2 if len(sample_a) > 1 else 0.0
    var_b = pstdev(sample_b) ** 2 if len(sample_b) > 1 else 0.0
    se = math.sqrt(var_a / max(1, len(sample_a)) + var_b / max(1, len(sample_b)))
    t_stat = (mean_a - mean_b) / se if se > 0 else 0.0
    return {"t_stat": float(t_stat), "df": len(sample_a) + len(sample_b) - 2, "p_value": None}


def cohens_d(sample_a: list[float], sample_b: list[float]) -> float | None:
    if not sample_a or not sample_b:
        return None
    mean_a = mean(sample_a)
    mean_b = mean(sample_b)
    var_a = pstdev(sample_a) ** 2 if len(sample_a) > 1 else 0.0
    var_b = pstdev(sample_b) ** 2 if len(sample_b) > 1 else 0.0
    pooled = math.sqrt(((len(sample_a) - 1) * var_a + (len(sample_b) - 1) * var_b) / max(1, len(sample_a) + len(sample_b) - 2))
    return float((mean_a - mean_b) / pooled) if pooled > 0 else 0.0


def one_way_anova(samples_dict: dict[str, list[float]]) -> dict[str, Any]:
    groups = [values for values in samples_dict.values() if values]
    if len(groups) < 2:
        return {"f_stat": None, "df_between": None, "df_within": None, "p_value": None}
    all_values = [x for group in groups for x in group]
    grand_mean = mean(all_values)
    ss_between = sum(len(group) * (mean(group) - grand_mean) ** 2 for group in groups)
    ss_within = sum(sum((x - mean(group)) ** 2 for x in group) for group in groups)
    df_between = len(groups) - 1
    df_within = len(all_values) - len(groups)
    ms_between = ss_between / df_between if df_between else 0.0
    ms_within = ss_within / df_within if df_within else 0.0
    f_stat = ms_between / ms_within if ms_within else 0.0
    return {"f_stat": float(f_stat), "df_between": df_between, "df_within": df_within, "p_value": None}
