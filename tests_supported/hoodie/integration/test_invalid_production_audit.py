from __future__ import annotations

import json
from pathlib import Path


def test_invalid_production_audit_records_quarantine() -> None:
    path = Path('artifacts/hoodie/implementation_run/campaign/invalid_production_audit.json')
    payload = json.loads(path.read_text(encoding='utf-8'))
    assert payload['quarantined_campaign_dir'].endswith('invalid-production-smoke-362cf20')
    assert payload['quarantined_release_dir'].endswith('invalid-production-smoke-362cf20')
    assert 'production CLI routes to smoke runner' in payload['verified_defects']
