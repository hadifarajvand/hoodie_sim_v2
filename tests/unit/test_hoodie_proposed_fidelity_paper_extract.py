from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_fidelity.config import BASE_PAPER_TARGET, REQUIRED_COMPONENT_IDS
from src.analysis.hoodie_proposed_fidelity.paper_extract import extract_paper_components, paper_component_ids


class HoodieProposedFidelityPaperExtractTests(unittest.TestCase):
    def test_all_required_component_ids_are_present(self) -> None:
        self.assertEqual(paper_component_ids(), REQUIRED_COMPONENT_IDS)

    def test_each_component_has_paper_definition_and_source(self) -> None:
        components = extract_paper_components()
        self.assertEqual(len(components), 19)
        for component in components:
            self.assertTrue(component.paper_definition)
            self.assertTrue(component.paper_source)

    def test_base_paper_target_is_recorded(self) -> None:
        self.assertEqual(BASE_PAPER_TARGET, "HOODIE_PROPOSED")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
