from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _main_source() -> str:
    return (ROOT / "main.py").read_text()


def test_main_includes_guarded_export_flags():
    source = _main_source()
    for flag in [
        "--export_trained_checkpoints",
        "--checkpoint_export_dir",
        "--checkpoint_export_format",
        "--allow_training_checkpoint_export",
        "--checkpoint_export_manifest",
    ]:
        assert flag in source


def test_main_does_not_export_by_default():
    source = _main_source()
    assert "if args.export_trained_checkpoints" in source
    assert "export_training_checkpoints" in source
    assert "if not args.validate" in source


def test_main_export_path_is_guarded_and_validation_blocked():
    source = _main_source()
    assert "--allow_training_checkpoint_export" in source
    assert "checkpoint export is not allowed during validation runs" in source
    assert "repo checkpoint export dir refused" in source
    assert "repo checkpoint export manifest refused" in source


def test_main_uses_export_training_checkpoints():
    source = _main_source()
    assert "from training.hoodie_training_checkpoint_export import export_training_checkpoints" in source


def test_main_export_manifest_is_optional_and_external():
    source = _main_source()
    assert "--checkpoint_export_manifest" in source
    assert "checkpoint_export_manifest.parent.mkdir" in source


def test_main_fails_when_export_report_has_blockers():
    source = _main_source()
    assert "training checkpoint export failed" in source
    assert "export_report[\"blockers\"]" in source
    assert "all_checkpoints_written" in source
    assert "all_metadata_written" in source


def test_main_manifest_written_before_export_failure_check():
    source = _main_source()
    manifest_index = source.index("checkpoint_export_manifest.parent.mkdir")
    failure_index = source.index("training checkpoint export failed")
    assert manifest_index < failure_index
