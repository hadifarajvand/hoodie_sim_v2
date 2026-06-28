from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.environment.topology import TopologyGraph


class TopologyConfigTests(unittest.TestCase):
    """Test that configuration files use correct topology."""
    
    def _load_config(self, config_path: str) -> dict:
        """Load JSON config file."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _extract_topology(self, config: dict) -> dict | None:
        """Extract topology configuration from config dict."""
        # Check validation section first (most common)
        if "validation" in config and "topology" in config["validation"]:
            return config["validation"]["topology"]
        # Check if topology is at root level
        if "topology" in config:
            return config["topology"]
        return None
    
    def test_smoke_validation_flc_hoodie_uses_20_node_topology(self) -> None:
        """Smoke config should use 20-node Figure 7 topology as default."""
        config = self._load_config("configs/smoke/smoke_validation_flc_hoodie.json")
        topology_config = self._extract_topology(config)
        
        # For now, this test will fail because the config still uses the old 3-node topology
        # After we implement the fix, it should pass
        self.assertIsNotNone(topology_config)
        
        if topology_config is not None:
            # Should have 20 node IDs (1-20)
            node_ids = topology_config.get("node_ids", [])
            self.assertEqual(len(node_ids), 20, f"Expected 20 nodes, got {len(node_ids)}")
            
            # Should have nodes labeled "1" through "20"
            expected_nodes = [str(i) for i in range(1, 21)]
            self.assertEqual(sorted(node_ids), sorted(expected_nodes))
            
            # Each node should have exactly 3 connections (degree 3)
            legal_adjacency = topology_config.get("legal_adjacency", {})
            for node_id in node_ids:
                connections = legal_adjacency.get(node_id, [])
                self.assertEqual(
                    len(connections), 3,
                    f"Node {node_id} should have 3 connections, got {len(connections)}: {connections}"
                )
                
            # Should be symmetric (if A connects to B, then B connects to A)
            for node_id, connections in legal_adjacency.items():
                for connected_node in connections:
                    reverse_connections = legal_adjacency.get(connected_node, [])
                    self.assertIn(
                        node_id, reverse_connections,
                        f"Connection should be symmetric: {node_id} -> {connected_node} "
                        f"but {connected_node} does not connect back to {node_id}"
                    )
    
    def test_all_config_should_use_20_node_topology_after_fix(self) -> None:
        """All config files should eventually use 20-node topology."""
        # This test documents the requirement - after implementing the fix,
        # we would check all config files
        config_files = [
            "configs/smoke/smoke_validation_flc_hoodie.json",
            "configs/smoke/smoke_validation_all_baselines.json", 
            "configs/experiments/exp_small_deterministic.json"
        ]
        
        for config_file in config_files:
            with self.subTest(config_file=config_file):
                config = self._load_config(config_file)
                topology_config = self._extract_topology(config)
                self.assertIsNotNone(
                    topology_config, 
                    f"No topology found in {config_file}"
                )
                
                if topology_config is not None:
                    node_ids = topology_config.get("node_ids", [])
                    self.assertEqual(
                        len(node_ids), 20,
                        f"{config_file} should have 20 nodes, got {len(node_ids)}"
                    )


if __name__ == "__main__":
    unittest.main()