from __future__ import annotations

import json
from pathlib import Path


def test_supported_surface_has_no_echo_terms() -> None:
    manifest = json.loads(Path('artifacts/hoodie/implementation_run/supported_surface.json').read_text(encoding='utf-8'))
    roots = [Path(root) for root in manifest['supported_surface']['source_roots']]
    banned = ('echo', 'event_smdp', 'event-smdp', 'deadline mask', 'predicted risk', 'normalized lateness', 'risk penalty', 'terminal exposure')
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts or path.name == 'test_supported_surface_has_no_echo.py':
                continue
            text = path.read_text(encoding='utf-8', errors='ignore').lower()
            for term in banned:
                if term in text:
                    hits.append(f'{path}:{term}')
    assert not hits, f'prohibited references: {hits[:20]}'
