"""Unit tests: workload/topology bias investigation (parameter fidelity + capacity)."""

from __future__ import annotations

import math

from src.analysis.paper_faithful_simulation_production import workload_topology_bias as wtb


def test_table_4_parameters_match_implementation():
    fid = wtb._parameter_fidelity_audit()
    assert fid["all_table_4_parameters_match"] is True
    assert fid["rate_constraint_RH_gt_RV"] is True
    # Every individual Table 4 check must pass.
    for name, detail in fid["table_4_parameter_checks"].items():
        assert detail["matches"] is True, name


def test_adjacency_is_recovered_degree_three_20_node():
    fid = wtb._parameter_fidelity_audit()
    adj = fid["adjacency_audit"]
    assert adj["implemented_nodes"] == 20
    assert adj["implemented_edges"] == 30
    assert adj["implemented_degree"] == 3
    assert adj["status"] == "recovered_assumption"


def test_capacity_predicts_local_best_pure_strategy():
    cap = wtb._capacity_feasibility_analysis()
    # Private pool saturates (~104%), cloud is worst (single 3 Gcycle/slot pool).
    pure = cap["pure_strategy_analysis"]
    assert pure["fixed_local"]["utilization"] > 1.0
    assert pure["fixed_vertical"]["utilization"] > pure["fixed_horizontal"]["utilization"]
    assert cap["predicted_best_pure_strategy"] == "fixed_local"
    # A mixed policy is feasible: the system is NOT fundamentally overloaded.
    assert cap["mixed_balanced_utilization"] < 1.0
    assert math.isclose(cap["capacity_gcycles_per_slot"]["cloud"], 3.0)


def test_run_verdict_is_genuine_not_artifact():
    report = wtb.run(emit_json=False)
    assert report["verdict"] == "local_dominance_is_genuine_paper_faithful_consequence"
    assert report["parameter_repair_needed"] is False
    assert report["local_dominance_expected"] is True
    assert report["recommended_next_step"] == "inspect_algorithm_fidelity_against_paper"
    assert report["claim_safety"]["algorithm_changed"] is False
    assert report["claim_safety"]["parameters_changed"] is False
