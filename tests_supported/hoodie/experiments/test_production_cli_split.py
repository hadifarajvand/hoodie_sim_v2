from __future__ import annotations

from pathlib import Path

from src.hoodie.experiments import cli


def test_run_command_uses_production_entrypoint(monkeypatch) -> None:
    called = {}

    def fake_production_campaign(*, campaign_id: str, output_dir: Path):
        called['campaign_id'] = campaign_id
        called['output_dir'] = output_dir
        return {'campaign_id': campaign_id, 'smoke': False, 'jobs': []}

    monkeypatch.setattr(cli, 'run_production_campaign', fake_production_campaign)
    assert 'run_smoke_campaign' not in cli.__dict__

    assert cli.main(['run', '--campaign-id', 'figures-8-11']) == 0
    assert called['campaign_id'] == 'figures-8-11'
    assert called['output_dir'] == Path('artifacts/hoodie/campaigns')
