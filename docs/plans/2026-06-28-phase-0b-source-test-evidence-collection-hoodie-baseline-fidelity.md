# Phase 0B Source/Test Evidence Collection for HOODIE Baseline Fidelity

## Graphify Findings

### Affected Nodes/Files/Modules
Based on analysis of the graphify-out/graph.json and related specification files:

**Core Implementation Files:**
- `specs/068-paper-baseline-policy-fidelity-batch/` - Feature specification directory
  - `spec.md` - Feature specification
  - `plan.md` - Implementation plan
  - `research.md` - Research decisions
  - `data-model.md` - Data models
  - `plan-details.md` - Detailed planning
  - `quickstart.md` - Getting started guide
  - `tasks.md` - Implementation tasks
  - `tasks-repair-addendum.md` - Additional tasks
  - `checklists/requirements.md` - Requirements checklist
  - `paper-exact-baseline-repair.md` - Repair contract
  - `implementation-handoff.md` - Handoff notes

**Source Code Files:**
- `src/policies/` - Policy implementations:
  - `common.py` - Shared policy utilities
  - `flc.py` - First Come First Served policy
  - `vo.py` - Vehicle Offloading policy
  - `ho.py` - Hierarchical Offloading policy
  - `ro.py` - Random Offloading policy
  - `bco.py` - Binary Computation Offloading policy
  - `mleo.py` - Minimum Latency Expected Offloading policy
  - `policy_interface.py` - Policy interface definition

- `src/evaluation/policy_registry.py` - Policy registration and lookup

**Test Files:**
- `tests/unit/test_policy_registry.py` - Registry tests
- `tests/unit/test_baseline_policy_fidelity.py` - Baseline fidelity tests
- `tests/unit/test_mleo_policy.py` - MLEO policy tests
- `tests/integration/test_baseline_policy_fidelity_flow.py` - Integration tests

### Dependency Paths
Key dependency relationships identified:

1. **Policy Registry Dependencies:**
   - `src/evaluation/policy_registry.py` ← depends on all policy implementations in `src/policies/`
   - `tests/unit/test_policy_registry.py` ← depends on `src/evaluation/policy_registry.py`

2. **Policy Implementation Dependencies:**
   - All policy files (`*.py` in `src/policies/`) ← depend on `src/policies/policy_interface.py`
   - `src/policies/mleo.py` ← potentially depends on `src/policies/common.py` for DelayCandidate

3. **Test Dependencies:**
   - `tests/unit/test_baseline_policy_fidelity.py` ← depends on policy implementations
   - `tests/unit/test_mleo_policy.py` ← depends on `src/policies/mleo.py`
   - `tests/integration/test_baseline_policy_fidelity_flow.py` ← depends on policy registry and implementations

### Impact Radius
**High Impact Components:**
- Policy Registry (`src/evaluation/policy_registry.py`) - Central registry for all baselines
- MLEO Policy (`src/policies/mleo.py`) - Complex delay-ranking logic requiring significant changes
- Policy Interface (`src/policies/policy_interface.py`) - Contract that all policies must follow

**Medium Impact Components:**
- Individual policy implementations (FLC, VO, HO, RO, BCO) - Each requires mask compliance fixes
- Unit test files - Requires updates to test new behavior and maintain compatibility

**Low Impact Components:**
- Documentation files - Mostly informational
- Integration tests - Higher-level tests that should remain largely unchanged if contracts are maintained

### Risky Files Identified
1. **`src/policies/mleo.py`** - Highest risk due to complex delay ranking and fallback logic requirements
2. **`src/evaluation/policy_registry.py`** - Central component; errors affect all policy usage
3. **`src/policies/common.py`** (if modified) - Could affect multiple policies if shared functions are changed
4. **`tests/unit/test_mleo_policy.py`** - Complex test scenarios for ranking and fallback behavior

## Routing Result
Using `npx ruflo@latest hooks route --task "Phase 0B source/test evidence collection for HOODIE baseline fidelity using graphify-run-notes/GRAPHIFY_EVIDENCE_INDEX.md"`:

- **Primary Recommendation**: `tester` agent (95.0% confidence)
- **Reason**: Task contains keywords matching tester specialization
- **Alternative**: `reviewer` agent (85.0% confidence)
- **Estimated Duration**: 30-60 minutes
- **Complexity**: MEDIUM
- **Success Probability**: 95.0%

## Memory Findings
Searched RuFlo memory for:
- **Decisions**: No specific decisions found related to this task
- **Patterns**: No specific patterns found
- **Failures**: No failure patterns found
- **Project Rules**: No project-specific rules found in memory

Note: RuFlo memory appears to be empty or not populated with relevant historical data for this specific task.

## Selected Built-in RuFlo Agents
Based on the routing results and task requirements:

1. **Primary Agent**: `tester` 
   - Responsible for identifying test requirements, gaps, and validation strategies
   - Will focus on test evidence collection and verification approaches

2. **Supporting Agent**: `reviewer`
   - Will assist in reviewing findings and ensuring completeness
   - Will help validate that all necessary artifacts and dependencies are identified

## Implementation Order
1. **Initial Analysis** (Completed)
   - Review feature specifications and plans
   - Analyze graph dependencies
   - Identify affected files and risk areas

2. **Evidence Collection**
   - Document current state of all identified files
   - Extract relevant specification requirements
   - Identify gaps between current implementation and requirements

3. **Test Mapping**
   - Map existing tests to requirements
   - Identify missing test coverage
   - Document test requirements for each user story

4. **Risk Assessment**
   - Document potential failure points
   - Identify breaking change risks
   - Outline mitigation strategies

## Validation Gates
1. **Specification Compliance**
   - All requirements from `spec.md` must be traceable to implementation or test plans
   - No implementation should contradict stated constraints

2. **Test Coverage**
   - Each user story (US1-US4) must have corresponding test evidence
   - Edge cases and error conditions must be covered

3. **Dependency Integrity**
   - No forbidden paths modified (per plan.md sections 19-20, 131-135)
   - Dependency files remain unchanged
   - Generated artifacts not affected

4. **Backward Compatibility**
   - Existing Feature 068 guarantees must be preserved (plan.md lines 15-25)
   - No breaking changes to public interfaces should not pass by deleting, weakening, or replacing prior tests (plan.md line 30)

## Security/Production Risks
1. **Policy Bypass Risk**
   - Incorrect implementation of action-mask compliance could allow invalid actions
   - Must ensure legal-action mask remains the final authority (spec.md line 25, plan.md line 31)

2. **Fallback Handling Risk**
   - Improper MLEO fallback behavior could lead to undefined behavior
   - Must ensure fallback is explicit and documented (spec.md line 22, plan.md line 28)

3. **Performance Regression Risk**
   - Inefficient delay ranking algorithms in MLEO could impact simulation performance
   - Must maintain acceptable time complexity for candidate ranking

4. **Test Contamination Risk**
   - Tests that modify shared state could produce false positives/negatives
   - Must ensure proper test isolation and cleanup

## Acceptance Criteria
1. **Documentation Complete**
   - All files in `specs/068-paper-baseline-policy-fidelity-batch/` reviewed and understood
   - Dependency mapping completed for all identified files
   - Risk assessment documented for high-risk components

2. **Traceability Established**
   - Each requirement in `spec.md` mapped to implementation locations or test plans
   - Each user story in `plan.md` has corresponding test evidence identified
   - All "Decision" sections in `research.md` have implementation implications noted

3. **Test Coverage Mapped**
   - Existing test files inventoried and their coverage documented
   - Gaps in test coverage identified for each user story
   - Test requirements documented for new functionality

4. **Review Complete**
   - Findings reviewed with secondary validator (per routing recommendation)
   - All constraining factors from specification acknowledged
   - No forbidden modification areas identified in planned work

## Next Command
Based on the completed analysis, the next logical step would be to:

```bash
npx ruflo@latest task create --description "Detailed evidence collection for HOODIE baseline fidelity implementation" --type research --assignee tester --priority high
```

This would create a detailed research task to gather specific evidence from each identified file area, ensuring comprehensive coverage before proceeding to implementation planning.

