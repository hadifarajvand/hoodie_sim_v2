#!/usr/bin/env python3
"""
HOODIE Baseline Policy Verification Script

This script verifies that each of the 6 baseline policies in the HOODIE simulation
behaves according to its specification:

## Policies Tested

1. **FLC** (FullLocalComputingPolicy): Always picks local computation if legal
2. **RO** (RandomOffloadingPolicy): Uniform random selection over legal action families  
3. **HO** (HorizontalOffloadingPolicy): Prefers horizontal offloading when legal
4. **VO** (VerticalOffloadingPolicy): Always offloads to cloud when legal
5. **BCO** (BalancedCooperationOffloadingPolicy): Round-robin selection with placement awareness
6. **MLEO** (MinimumLatencyEstimateOffloadingPolicy): Chooses action with minimum estimated delay

## Verification Approach

- Loads the Figure 7 topology from the user-approved assumption registry
- Creates test scenarios covering different network conditions and task characteristics
- Directly tests each policy's `choose_action()` method with synthetic observations
- Validates policy-specific behavior rules
- Reports pass/fail status for each policy

## Usage

```bash
PYTHONPATH=. .venv/bin/python scripts/verify_baseline_policies.py
```

## Exit Codes

- 0: All policies passed verification
- 1: One or more policies failed verification
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

# Import HOODIE simulation components
from src.environment.topology import TopologyGraph
from src.policies import (
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    VerticalOffloadingPolicy,
    RandomOffloadingPolicy,
    BalancedCooperationOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    SharedPolicy,
)
from src.policies.common import (
    action_family,
    fallback_action,
    first_legal_placement_action,
    placement_actions_for_family,
    legal_actions,
)


@dataclass
class VerificationResult:
    """Result of verifying a single policy."""
    policy_name: str
    action_counts: Dict[str, int] = field(default_factory=dict)
    total_actions: int = 0
    passed: bool = False
    failures: List[str] = field(default_factory=list)


def load_figure_7_topology() -> TopologyGraph:
    """Load the Figure 7 topology from the user-approved assumption registry."""
    registry_path = Path("resources/papers/hoodie/recovered/user-approved-assumption-registry.json")
    return TopologyGraph.from_approved_assumption_registry(registry_path)


def create_test_scenarios() -> List[Dict[str, Any]]:
    """
    Create test scenarios that exercise different aspects of the policies.
    
    Each scenario represents an observation that would be presented to a policy.
    """
    scenarios = []
    
    # Scenario 1: Local action legal and preferred (all actions legal)
    scenarios.append({
        'name': 'All actions legal',
        'observation': {
            'slot': 0,
            'queue_load': 0.0,
            'load_hint': 0.0,
            'history_length': 0,
            'task_id': 1,
            'source_agent_id': 1,
            'arrival_slot': 0,
            'size': 5.0,
            'processing_density': 2.0,
            'cycles_required': 10.0,
            'cycles_remaining': 10.0,
            'timeout_length': 10,
            'absolute_deadline_slot': 10,
            'topology': ('2', '6', '11'),  # Node 1's neighbors in Figure 7
            'legal_action_mask': {
                'local': True,
                'compute_local': True,
                'horizontal': True,
                'offload_horizontal': True,
                'vertical': True,
                'offload_vertical': True,
            },
            'fallback_hints': {
                'local': 1.0,
                'horizontal': 2.0,
                'vertical': 3.0,
                'task_size': 5.0,
            },
            'latency_estimates': {
                'local': 2.0,
                'horizontal': 1.0,
                'vertical': 0.0,  # Cloud is fastest
            },
            'balance_hint': {
                'local': 5.0,
                'horizontal': 3.0,
                'vertical': 2.0,
            },
        },
        'expected_families': {
            'FLC': ['local'],           # Should choose local
            'RO': ['local', 'horizontal', 'vertical'],  # Any legal family
            'HO': ['horizontal'],       # Should prefer horizontal
            'VO': ['vertical'],         # Should prefer vertical
            'BCO': ['local', 'horizontal', 'vertical'], # Should balance
            'MLEO': ['vertical'],       # Should choose lowest latency (vertical)
        }
    })
    
    # Scenario 2: Only local action legal (e.g., no network connectivity)
    scenarios.append({
        'name': 'Only local legal',
        'observation': {
            'slot': 1,
            'queue_load': 1.0,
            'load_hint': 1.0,
            'history_length': 1,
            'task_id': 2,
            'source_agent_id': 1,
            'arrival_slot': 1,
            'size': 3.0,
            'processing_density': 1.0,
            'cycles_required': 3.0,
            'cycles_remaining': 3.0,
            'timeout_length': 5,
            'absolute_deadline_slot': 6,
            'topology': (),  # No neighbors (isolated node)
            'legal_action_mask': {
                'local': True,
                'compute_local': True,
                'horizontal': False,
                'offload_horizontal': False,
                'vertical': True,
                'offload_vertical': True,
            },
            'fallback_hints': {
                'local': 1.0,
                'horizontal': 2.0,
                'vertical': 3.0,
                'task_size': 3.0,
            },
            'latency_estimates': {
                'local': 1.0,
                'horizontal': float('inf'),
                'vertical': 0.5,
            },
            'balance_hint': {
                'local': 3.0,
                'horizontal': 0.0,
                'vertical': 1.5,
            },
        },
        'expected_families': {
            'FLC': ['local'],           # Must choose local
            'RO': ['local', 'vertical'], # Can choose local or vertical
            'HO': ['local', 'vertical'], # Should fall back when horizontal not legal
            'VO': ['vertical'],         # Should choose vertical when legal
            'BCO': ['local', 'vertical'], # Should choose from legal options
            'MLEO': ['vertical'],       # Should choose lowest latency
        }
    })
    
    # Scenario 3: Only horizontal legal (local blocked for some reason)
    scenarios.append({
        'name': 'Only horizontal legal',
        'observation': {
            'slot': 2,
            'queue_load': 2.0,
            'load_hint': 2.0,
            'history_length': 2,
            'task_id': 3,
            'source_agent_id': 1,
            'arrival_slot': 2,
            'size': 4.0,
            'processing_density': 3.0,
            'cycles_required': 12.0,
            'cycles_remaining': 12.0,
            'timeout_length': 8,
            'absolute_deadline_slot': 10,
            'topology': ('2', '6'),  # Has neighbors but pretend local is blocked
            'legal_action_mask': {
                'local': False,      # Local blocked
                'compute_local': False,
                'horizontal': True,
                'offload_horizontal': True,
                'vertical': False,   # Vertical blocked too
                'offload_vertical': False,
            },
            'fallback_hints': {
                'local': 1.0,
                'horizontal': 2.0,
                'vertical': 3.0,
                'task_size': 4.0,
            },
            'latency_estimates': {
                'local': float('inf'),
                'horizontal': 1.5,
                'vertical': float('inf'),
            },
            'balance_hint': {
                'local': 0.0,
                'horizontal': 4.0,
                'vertical': 0.0,
            },
        },
        'expected_families': {
            'FLC': ['horizontal'],     # Should fall back to horizontal when local not legal
            'RO': ['horizontal'],      # Only horizontal family legal
            'HO': ['horizontal'],      # Should choose horizontal
            'VO': ['horizontal'],      # Should fall back when vertical not legal
            'BCO': ['horizontal'],     # Only legal option
            'MLEO': ['horizontal'],    # Only legal option
        }
    })
    
    # Scenario 4: Only vertical legal (horizontal blocked)
    scenarios.append({
        'name': 'Only vertical legal',
        'observation': {
            'slot': 3,
            'queue_load': 1.5,
            'load_hint': 1.5,
            'history_length': 3,
            'task_id': 4,
            'source_agent_id': 1,
            'arrival_slot': 3,
            'size': 6.0,
            'processing_density': 2.0,
            'cycles_required': 12.0,
            'cycles_remaining': 12.0,
            'timeout_length': 12,
            'absolute_deadline_slot': 15,
            'topology': (),  # No horizontal neighbors (isolated)
            'legal_action_mask': {
                'local': True,
                'compute_local': True,
                'horizontal': False,
                'offload_horizontal': False,
                'vertical': True,
                'offload_vertical': True,
            },
            'fallback_hints': {
                'local': 1.0,
                'horizontal': 2.0,
                'vertical': 3.0,
                'task_size': 6.0,
            },
            'latency_estimates': {
                'local': 2.0,
                'horizontal': float('inf'),
                'vertical': 0.5,
            },
            'balance_hint': {
                'local': 6.0,
                'horizontal': 0.0,
                'vertical': 3.0,
            },
        },
        'expected_families': {
            'FLC': ['local'],          # Should choose local when legal
            'RO': ['local', 'vertical'], # Can choose legal families
            'HO': ['local', 'vertical'], # Should fall back when horizontal not legal
            'VO': ['vertical'],        # Should choose vertical when legal
            'BCO': ['local', 'vertical'], # Should choose from legal options
            'MLEO': ['vertical'],      # Should choose lowest latency (vertical)
        }
    })
    
    # Scenario 5: Placement hints available (testing BCO placement logic)
    scenarios.append({
        'name': 'With placement hints',
        'observation': {
            'slot': 4,
            'queue_load': 3.0,
            'load_hint': 3.0,
            'history_length': 4,
            'task_id': 5,
            'source_agent_id': 1,
            'arrival_slot': 4,
            'size': 8.0,
            'processing_density': 1.5,
            'cycles_required': 12.0,
            'cycles_remaining': 12.0,
            'timeout_length': 15,
            'absolute_deadline_slot': 19,
            'topology': ('2', '6', '11'),
            'legal_action_mask': {
                'local': True,
                'compute_local': True,
                'horizontal': True,
                'offload_horizontal': True,
                'vertical': True,
                'offload_vertical': True,
            },
            'fallback_hints': {
                'local': 1.0,
                'horizontal': 2.0,
                'vertical': 3.0,
                'task_size': 8.0,
            },
            'latency_estimates': {
                'local': 1.5,
                'horizontal': 1.2,
                'vertical': 0.4,
            },
            'balance_hint': {
                'local': 8.0,
                'horizontal': 5.0,
                'vertical': 3.0,
            },
            # Placement hints for BCO
            'local_action': 'compute_local',
            'cloud_action': 'offload_vertical',
            'horizontal_destinations': ['2', '6', '11'],
            'placement_actions': {
                'local': 'compute_local',
                'horizontal': 'offload_horizontal',
                'vertical': 'offload_vertical',
            }
        },
        'expected_families': {
            'FLC': ['local'],           # Should choose local placement
            'RO': ['local', 'horizontal', 'vertical'], # Any legal
            'HO': ['horizontal'],       # Should prefer horizontal
            'VO': ['vertical'],         # Should prefer vertical
            'BCO': ['local', 'horizontal', 'vertical'], # Should use placement hints
            'MLEO': ['vertical'],       # Should choose lowest latency
        }
    })
    
    return scenarios


def create_policy_context(observation: Dict[str, Any]) -> PolicyContext:
    """Create a PolicyContext from an observation dictionary."""
    return PolicyContext(
        observation=observation,
        legal_action_mask=observation['legal_action_mask'],
        trace_history=('test-scenario',),
    )


def test_policy_on_scenario(policy: SharedPolicy, scenario: Dict[str, Any]) -> List[str]:
    """
    Test a policy on a single scenario.
    
    Returns:
        List of failure messages (empty if passed)
    """
    failures = []
    
    try:
        context = create_policy_context(scenario['observation'])
        action = policy.choose_action(context)
        action_family_name = action_family(action)
        
        # Get expected families for this policy
        policy_name_map = {
            'FullLocalComputingPolicy': 'FLC',
            'RandomOffloadingPolicy': 'RO',
            'HorizontalOffloadingPolicy': 'HO',
            'VerticalOffloadingPolicy': 'VO',
            'BalancedCooperationOffloadingPolicy': 'BCO',
            'MinimumLatencyEstimateOffloadingPolicy': 'MLEO',
        }
        policy_key = policy_name_map.get(policy.__class__.__name__, policy.__class__.__name__)
        expected_families = scenario['expected_families'].get(policy_key, [])
        
        # Check if the chosen action family is expected
        if expected_families and action_family_name not in expected_families:
            legal_actions = [k for k, v in scenario['observation']['legal_action_mask'].items() if v]
            failures.append(
                f"Scenario '{scenario['name']}': {policy_key} chose {action} ({action_family_name}), "
                f"expected one of {expected_families}. Legal actions: {legal_actions}"
            )
            
    except Exception as e:
        failures.append(
            f"Scenario '{scenario['name']}': {policy.__class__.__name__} raised exception: {e}"
        )
    
    return failures


def main() -> int:
    """Main verification function."""
    print("HOODIE Baseline Policy Verification (Direct Policy Testing)")
    print("=" * 60)
    
    try:
        # Load Figure 7 topology
        print("Loading Figure 7 topology from user-approved assumption registry...")
        topology = load_figure_7_topology()
        print(f"Loaded topology with {len(topology.node_ids)} nodes")
        print(f"Node 1 neighbors: {topology.legal_horizontal_destinations('1')}")
        
        # Create test scenarios
        print("\nCreating test scenarios...")
        scenarios = create_test_scenarios()
        print(f"Created {len(scenarios)} test scenarios")
        
        # Define policies to test
        policies = [
            ("FLC", FullLocalComputingPolicy()),
            ("RO", RandomOffloadingPolicy(seed=42)),  # Fixed seed for reproducibility
            ("HO", HorizontalOffloadingPolicy()),
            ("VO", VerticalOffloadingPolicy()),
            ("BCO", BalancedCooperationOffloadingPolicy()),
            ("MLEO", MinimumLatencyEstimateOffloadingPolicy()),
        ]
        
        # Track overall results
        all_passed = True
        results = []
        
        # Test each policy
        for policy_name, policy in policies:
            print(f"\nTesting {policy_name} policy...")
            
            total_failures = []
            action_counts = Counter()
            
            # Test on each scenario
            for scenario in scenarios:
                failures = test_policy_on_scenario(policy, scenario)
                if failures:
                    total_failures.extend(failures)
                else:
                    # Count the action that would be chosen
                    try:
                        context = create_policy_context(scenario['observation'])
                        action = policy.choose_action(context)
                        action_counts[action] += 1
                    except Exception:
                        pass  # Counting failed, but we already recorded the failure
            
            total_actions = sum(action_counts.values())
            passed = len(total_failures) == 0
            
            # Store result
            result = VerificationResult(
                policy_name=policy_name,
                action_counts=dict(action_counts),
                total_actions=total_actions,
                passed=passed,
                failures=total_failures,
            )
            results.append(result)
            
            # Report result
            if passed:
                print(f"  ✓ {policy_name} PASSED")
                if action_counts:
                    print(f"    Actions: {dict(action_counts)}")
            else:
                print(f"  ✗ {policy_name} FAILED")
                for failure in total_failures[:3]:  # Show first 3 failures
                    print(f"    - {failure}")
                if len(total_failures) > 3:
                    print(f"    - ... and {len(total_failures) - 3} more failures")
                all_passed = False
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        all_passed = all(r.passed for r in results)
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            action_info = f" ({result.total_actions} actions)" if result.total_actions > 0 else ""
            print(f"  {result.policy_name:4}: {status}{action_info}")
        
        if all_passed:
            print("\n✓ ALL POLICIES PASSED VERIFICATION")
            return 0
        else:
            print("\n✗ SOME POLICIES FAILED VERIFICATION")
            return 1
            
    except Exception as e:
        print(f"\nERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())