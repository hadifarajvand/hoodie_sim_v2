from __future__ import annotations

import unittest

from src.analysis.controlled_mechanistic_sweeps.classify import classify_monotonic
from src.analysis.controlled_mechanistic_sweeps.report import render_markdown
from src.analysis.controlled_mechanistic_sweeps.sweeps import (
    ControlledMechanisticSweepReport,
    FixedInput,
    MonotonicCheck,
    SweepDefinition,
    SweepObservation,
    build_controlled_mechanistic_sweep_definitions,
)


class ControlledMechanisticSweepDefinitionTests(unittest.TestCase):
    def test_required_sweep_families_and_tiny_value_sets_are_defined(self) -> None:
        definitions = build_controlled_mechanistic_sweep_definitions()

        self.assertEqual(
            [definition.name for definition in definitions],
            [
                "arrival_probability",
                "timeout",
                "cpu_capacity",
                "link_rate",
                "topology_density",
            ],
        )
        self.assertEqual(definitions[0].values, (0.2, 0.5, 0.8))
        self.assertEqual(definitions[1].values, (1, 2, 3))
        self.assertEqual(definitions[2].values, (1.0, 2.0, 4.0))
        self.assertEqual(definitions[3].values, ("low", "medium", "high"))
        self.assertEqual(definitions[4].values, ("sparse", "default", "dense"))
        self.assertEqual(definitions[3].control_source, "unsupported")
        self.assertFalse(definitions[3].control_available)

    def test_monotonic_classification_supports_all_required_statuses(self) -> None:
        passing_definition = SweepDefinition(
            name="arrival_probability",
            parameter="arrival_probability",
            values=(0.2, 0.5, 0.8),
            fixed_seeds=(7,),
            expected_direction="nondecreasing",
            control_source="TrafficConfig.arrival_probability",
        )
        passing_observations = [
            SweepObservation("arrival_probability", 7, 0.2, 0.1, "low", True),
            SweepObservation("arrival_probability", 7, 0.5, 0.4, "medium", True),
            SweepObservation("arrival_probability", 7, 0.8, 0.9, "high", True),
        ]
        self.assertEqual(classify_monotonic(passing_definition, passing_observations).status, "pass")

        warned_observations = [
            SweepObservation("arrival_probability", 7, 0.2, 0.5, "flat", True),
            SweepObservation("arrival_probability", 7, 0.5, 0.5, "flat", True),
            SweepObservation("arrival_probability", 7, 0.8, 0.5, "flat", True),
        ]
        self.assertEqual(classify_monotonic(passing_definition, warned_observations).status, "warn")

        inconclusive_observations = [
            SweepObservation("arrival_probability", 7, 0.2, 0.2, "low", True),
            SweepObservation("arrival_probability", 7, 0.5, 0.1, "dip", True),
            SweepObservation("arrival_probability", 7, 0.8, 0.3, "rise", True),
        ]
        self.assertEqual(classify_monotonic(passing_definition, inconclusive_observations).status, "inconclusive")

        instrumentation_gap_definition = SweepDefinition(
            name="link_rate",
            parameter="link_rate",
            values=("low", "medium", "high"),
            fixed_seeds=(7,),
            expected_direction="nondecreasing",
            control_source="unsupported",
            control_available=False,
        )
        instrumentation_gap_observations = [
            SweepObservation("link_rate", 7, "low", None, "unsupported", False),
            SweepObservation("link_rate", 7, "medium", None, "unsupported", False),
            SweepObservation("link_rate", 7, "high", None, "unsupported", False),
        ]
        self.assertEqual(classify_monotonic(instrumentation_gap_definition, instrumentation_gap_observations).status, "instrumentation_gap")

    def test_report_schema_is_deterministic_and_includes_disclaimers(self) -> None:
        report = ControlledMechanisticSweepReport(
            metadata={
                "feature_id": "020-controlled-mechanistic-sweeps",
                "generated_by": "controlled_mechanistic_sweeps",
                "deterministic": True,
                "source_refs": ["specs/020-controlled-mechanistic-sweeps/spec.md"],
            },
            sweep_definitions=build_controlled_mechanistic_sweep_definitions()[:1],
            fixed_inputs=[FixedInput("arrival_probability", 7, 0.2, "paper_default-7", "controlled")],
            observations=[SweepObservation("arrival_probability", 7, 0.2, 0.1, "arrivals=1", True)],
            monotonic_checks=[MonotonicCheck("arrival_probability", "pass", "full", "monotonic")],
            warnings=[],
            instrumentation_gaps=[],
            limitations=["Diagnostic only."],
            no_campaign_rerun_disclaimer="No baseline campaigns were rerun to generate this report.",
            no_paper_validity_disclaimer="This report is not a paper-validity or reproduction-completeness claim.",
            reproducibility={
                "approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
                "fixed_seeds": [7],
            },
            overall_status="pass",
        )

        payload = report.to_dict()
        self.assertEqual(
            set(payload),
            {
                "metadata",
                "sweep_definitions",
                "fixed_inputs",
                "observations",
                "monotonic_checks",
                "warnings",
                "instrumentation_gaps",
                "limitations",
                "no_campaign_rerun_disclaimer",
                "no_paper_validity_disclaimer",
                "reproducibility",
                "overall_status",
            },
        )
        markdown = render_markdown(report)
        self.assertIn("No Campaign Rerun Disclaimer", markdown)
        self.assertIn("No Paper Validity Disclaimer", markdown)
        self.assertIn("This report is not a paper-validity or reproduction-completeness claim.", markdown)


if __name__ == "__main__":
    unittest.main()
