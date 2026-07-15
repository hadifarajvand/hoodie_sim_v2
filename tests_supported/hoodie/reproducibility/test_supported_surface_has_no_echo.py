from __future__ import annotations

import ast
import json
from pathlib import Path

from src.hoodie.reproducibility.supported_surface_scan import validate_supported_surface


def test_supported_surface_has_no_echo_terms() -> None:
    matches = validate_supported_surface()
    assert matches == []


def test_supported_surface_excludes_historical_paths_explicitly() -> None:
    manifest = json.loads(Path('artifacts/hoodie/implementation_run/supported_surface.json').read_text(encoding='utf-8'))
    excluded = manifest['supported_surface']['excluded_historical_areas']
    assert any('historical' in entry.lower() or 'legacy' in entry.lower() for entry in excluded)


def test_supported_surface_has_no_transitive_echo_imports() -> None:
    roots = [Path(root) for root in json.loads(Path('artifacts/hoodie/implementation_run/supported_surface.json').read_text())['supported_surface']['source_roots']]
    banned_modules = {'src.echo_action_space', 'src.echo_ert'}
    imported: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*.py'):
            if '__pycache__' in path.parts or path.name == Path(__file__).name:
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
    assert not (imported & banned_modules)
