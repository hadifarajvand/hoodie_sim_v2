"""RED phase: Test that HoodieGymEnvironment has _progress_shared_execution_queues.

This test should reveal any indentation/syntax issues in gym_adapter.py
by importing the class and verifying the method signature and behavior.
"""

import pytest


def test_import_hoodie_gym_environment():
    """Verify the module can be imported without SyntaxError."""
    from src.environment.gym_adapter import HoodieGymEnvironment

    assert HoodieGymEnvironment is not None


def test_class_has_shared_execution_queues_method():
    """Verify the _progress_shared_execution_queues method exists on the class."""
    from src.environment.gym_adapter import HoodieGymEnvironment

    assert hasattr(HoodieGymEnvironment, "_progress_shared_execution_queues")
    method = HoodieGymEnvironment._progress_shared_execution_queues
    assert callable(method)


def test_method_returns_list():
    """Verify the method signature indicates it returns list[Task]."""
    from src.environment.gym_adapter import HoodieGymEnvironment

    method = HoodieGymEnvironment._progress_shared_execution_queues
    # The method should exist and be callable — if the file had a syntax error
    # we wouldn't get this far.
    import inspect

    sig = inspect.signature(method)
    assert "self" in sig.parameters
    ret = sig.return_annotation
    # Return annotation should be list[Task] or similar list type
    assert "list" in str(ret).lower() or ret is inspect.Parameter.empty


def test_method_source_includes_class_indent():
    """Verify the method source starts with 4 spaces (class-level indent)."""
    from src.environment.gym_adapter import HoodieGymEnvironment
    import inspect

    try:
        source = inspect.getsource(HoodieGymEnvironment._progress_shared_execution_queues)
    except (TypeError, OSError) as exc:
        pytest.fail(f"Could not get source of method: {exc}")
    
    lines = source.splitlines()
    assert len(lines) >= 2, "Method should have at least a def line and a body line"

    # The first line (def) should have 4 spaces of indentation
    first_line = lines[0]
    leading_spaces = len(first_line) - len(first_line.lstrip())
    assert leading_spaces == 4, (
        f"Expected 4-space indent for class method, got {leading_spaces} spaces. "
        f"Line: {first_line!r}"
    )

    # The body lines should have at least 8 spaces of indentation
    for i, body_line in enumerate(lines[1:], start=2):
        if body_line.strip() and not body_line.strip().startswith("#"):
            body_spaces = len(body_line) - len(body_line.lstrip())
            assert body_spaces >= 8, (
                f"Expected >= 8-space indent for method body, got {body_spaces} spaces "
                f"on line {i}: {body_line!r}"
            )
