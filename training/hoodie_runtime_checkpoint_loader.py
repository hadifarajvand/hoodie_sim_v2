from __future__ import annotations

from pathlib import Path
from typing import Any


def _torch():
    import torch

    return torch


def _load_torch_object(path: Path, map_location: str = "cpu") -> tuple[Any | None, str | None]:
    torch = _torch()
    try:
        return torch.load(str(path), map_location=map_location, weights_only=False), None
    except Exception as exc:  # pragma: no cover - exercised through tests
        return None, str(exc)


def _looks_like_trainer_json(path: Path) -> bool:
    try:
        text = path.read_text()
    except Exception:
        return False
    return all(key in text for key in ("algorithm", "policy_weights"))


def load_deepqnetwork_checkpoint(path: Path, *, map_location: str = "cpu") -> tuple[Any | None, dict[str, Any]]:
    from decision_makers.agent import DeepQNetwork

    report: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "format": None,
        "model_class": None,
        "loadable": False,
        "blockers": [],
        "warnings": [],
    }
    if not path.exists():
        report["blockers"].append("checkpoint_missing")
        report["blockers"].append("checkpoint_not_loadable")
        return None, report
    if path.is_dir():
        report["blockers"].append("checkpoint_is_directory")
        report["blockers"].append("checkpoint_not_loadable")
        return None, report
    if _looks_like_trainer_json(path):
        report["blockers"].append("trainer_json_checkpoint_not_runtime_loadable")
        report["blockers"].append("checkpoint_not_loadable")
        report["format"] = "trainer_json_checkpoint"
        return None, report

    payload, error = _load_torch_object(path, map_location=map_location)
    if error is not None:
        report["blockers"].append("checkpoint_load_failed")
        report["blockers"].append("checkpoint_not_loadable")
        report["error"] = error
        return None, report

    torch = _torch()
    if isinstance(payload, torch.nn.Module):
        report["format"] = "pytorch_model_file"
        report["model_class"] = type(payload).__name__
        if not hasattr(payload, "forward") or not callable(getattr(payload, "forward")):
            report["blockers"].append("unsupported_checkpoint_object_type")
            report["blockers"].append("checkpoint_not_loadable")
            return None, report
        report["loadable"] = True
        return payload, report

    if not isinstance(payload, dict):
        report["blockers"].append("unsupported_checkpoint_object_type")
        report["blockers"].append("checkpoint_not_loadable")
        report["error"] = f"object_type={type(payload).__name__}"
        return None, report

    required = [
        "state_dict",
        "model_class",
        "state_dim",
        "lstm_input_shape",
        "lstm_output_shape",
        "number_of_actions",
        "hidden_layers",
        "lstm_layers",
        "dueling",
        "dropout_rate",
    ]
    missing = [field for field in required if field not in payload]
    if missing:
        for field in missing:
            report["blockers"].append(f"missing_architecture_field:{field}")
        if "state_dict" not in payload:
            report["blockers"].append("missing_state_dict")
        report["blockers"].append("checkpoint_not_loadable")
        report["error"] = f"missing_fields={missing}"
        return None, report

    if payload.get("model_class") != "DeepQNetwork":
        report["blockers"].append("unsupported_model_class")
        report["blockers"].append("checkpoint_not_loadable")
        report["model_class"] = payload.get("model_class")
        return None, report

    try:
        model = DeepQNetwork(
            state_dimensions=int(payload["state_dim"]),
            lstm_input_shape=int(payload["lstm_input_shape"]),
            lstm_output_shape=int(payload["lstm_output_shape"]),
            number_of_actions=int(payload["number_of_actions"]),
            hidden_layers=list(payload["hidden_layers"]),
            lstm_layers=int(payload["lstm_layers"]),
            dueling=bool(payload["dueling"]),
            dropout_rate=float(payload["dropout_rate"]),
        ).to(map_location)
        model.load_state_dict(payload["state_dict"])
        model.eval()
        report["format"] = "pytorch_state_dict_payload"
        report["model_class"] = "DeepQNetwork"
        report["loadable"] = True
        return model, report
    except Exception as exc:
        report["blockers"].append("state_dict_load_failed")
        report["blockers"].append("checkpoint_not_loadable")
        report["error"] = str(exc)
        return None, report


def validate_hoodie_checkpoint_metadata(meta_path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "exists": meta_path.exists(),
        "policy_name": None,
        "checkpoint_format": None,
        "official_claim_allowed": None,
        "runtime_fixture_checkpoint": None,
        "trained_checkpoint": None,
        "blockers": [],
    }
    if not meta_path.exists():
        report["blockers"].append("metadata_missing")
        return report
    try:
        payload = meta_path.read_text()
        import json

        metadata = json.loads(payload)
    except Exception:
        report["blockers"].append("metadata_json_load_failed")
        return report

    report["policy_name"] = metadata.get("policy_name")
    report["checkpoint_format"] = metadata.get("checkpoint_format")
    report["official_claim_allowed"] = metadata.get("official_claim_allowed")
    report["runtime_fixture_checkpoint"] = metadata.get("runtime_fixture_checkpoint")
    report["trained_checkpoint"] = metadata.get("trained_checkpoint")

    if metadata.get("policy_name") != "HOODIE":
        report["blockers"].append("metadata_policy_name_invalid")
    if metadata.get("official_claim_allowed") is True:
        report["blockers"].append("metadata_official_claim_allowed_true")
    if metadata.get("checkpoint_format") not in {
        "pytorch_model_file",
        "pytorch_state_dict_file",
        "pytorch_state_dict_payload",
    }:
        report["blockers"].append("metadata_checkpoint_format_invalid")
    if metadata.get("checkpoint_format") == "trainer_json_checkpoint":
        report["blockers"].append("trainer_json_checkpoint_not_runtime_loadable")
    return report


def load_hoodie_checkpoint_with_metadata(path: Path, *, map_location: str = "cpu") -> tuple[Any | None, dict[str, Any]]:
    model, checkpoint_report = load_deepqnetwork_checkpoint(path, map_location=map_location)
    metadata_report = validate_hoodie_checkpoint_metadata(path.with_name(path.name + ".meta.json"))
    blockers = list(dict.fromkeys([*checkpoint_report.get("blockers", []), *metadata_report.get("blockers", [])]))
    runtime_loadable = bool(checkpoint_report.get("loadable")) and not metadata_report.get("blockers")
    return model, {
        "checkpoint_path": str(path),
        "metadata_path": str(path.with_name(path.name + ".meta.json")),
        "checkpoint_report": checkpoint_report,
        "metadata_report": metadata_report,
        "loadable": bool(checkpoint_report.get("loadable")) and not metadata_report.get("blockers"),
        "runtime_loadable": runtime_loadable,
        "official_claim_allowed": False,
        "blockers": blockers,
    }
