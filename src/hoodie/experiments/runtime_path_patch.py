from __future__ import annotations


_INSTALLED = False


def install_runtime_path_patch() -> None:
    """Point every active pipeline module at the central runtime root."""

    global _INSTALLED
    if _INSTALLED:
        return

    from .runtime_paths import campaign_root, distributed_root, release_root
    from . import distributed_v2, production_campaign, scientific_pipeline

    campaigns = campaign_root()
    releases = release_root()
    distributed = distributed_root()

    production_campaign._CAMPAIGNS_ROOT = campaigns
    production_campaign._RELEASES_ROOT = releases
    scientific_pipeline.CAMPAIGN_ROOT = campaigns
    scientific_pipeline.RELEASE_ROOT = releases
    distributed_v2.CAMPAIGN_ROOT = campaigns
    distributed_v2.DISTRIBUTED_ROOT = distributed

    _INSTALLED = True
