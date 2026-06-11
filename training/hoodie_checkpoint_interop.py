from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any, List


def detect_checkpoint_format(path: Path) -> Dict[str, Any]:
    """Detect the approximate checkpoint format for a path.

    Returns a dict with key "format" one of:
      - missing
      - directory
      - pytorch_model_file
      - pytorch_state_dict_file
      - trainer_json_checkpoint
      - unknown_file
      - unsupported
    """
    if not path.exists():
        return {"format": "missing"}
    if path.is_dir():
        return {"format": "directory"}
    name = path.name.lower()
    if name.endswith((".pth", ".pt")):
        # tentatively a PyTorch model file; more precise detection requires
        # attempting to inspect the file which may fail if torch isn't installed
        return {"format": "pytorch_model_file"}
    if name.endswith(".chkpt") or name.endswith(".json"):
        try:
            payload = json.loads(path.read_text())
            if isinstance(payload, dict) and any(
                k in payload for k in ("policy_weights", "policy_bias", "training_config", "algorithm")
            ):
                return {"format": "trainer_json_checkpoint"}
        except Exception:
            pass
        return {"format": "unknown_file"}
    return {"format": "unknown_file"}


def inspect_trainer_json_checkpoint(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not path.exists():
        return {"error": "missing"}
    try:
        payload = json.loads(path.read_text())
    except Exception as e:
        return {"error": f"json_load_error: {e}"}

    required = ["algorithm", "seed", "state_dim", "action_count"]
    out["fields_present"] = {k: (k in payload) for k in required}
    for k in ("algorithm", "seed", "state_dim", "action_count", "epochs_completed"):
        out[k] = payload.get(k)

    def shape_of(arr: Any):
        try:
            if isinstance(arr, list) and arr and isinstance(arr[0], list):
                return (len(arr), len(arr[0]))
            if isinstance(arr, list):
                return (len(arr),)
        except Exception:
            return None
        return None

    out["policy_weights_shape"] = shape_of(payload.get("policy_weights", []))
    out["target_weights_shape"] = shape_of(payload.get("target_weights", []))
    out["missing_required_fields"] = [k for k in required if k not in payload]
    return out


def inspect_runtime_torch_checkpoint(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "loadable": False,
        "object_type": None,
        "has_state_dict": False,
        "error": None,
        "warnings": [],
    }
    if not path.exists():
        out["error"] = "missing"
        return out
    try:
        import torch

        # load to CPU only; be defensive and catch any exception
        obj = torch.load(str(path), map_location="cpu")
        out["loadable"] = True
        out["object_type"] = type(obj).__name__
        if isinstance(obj, dict):
            # common pattern: saved dict contains 'state_dict' or tensor values
            out["has_state_dict"] = "state_dict" in obj or any(
                hasattr(v, "numpy") or isinstance(v, dict) for v in obj.values()
            )
    except Exception as e:
        out["error"] = str(e)
    return out


def assess_hoodie_checkpoint_dir(path: Path, expected_agent_count: int | None = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "agents_found": [],
        "issues": [],
        "pth_count": 0,
        "trainer_chkpt_count": 0,
        "suitable_for_official_validation": False,
    }
    if not path.exists() or not path.is_dir():
        out["issues"].append("missing_checkpoint_dir")
        return out
    files = list(path.iterdir())
    pth_files = [f for f in files if f.name.endswith((".pth", ".pt"))]
    chkpt_files = [f for f in files if f.name.endswith(".chkpt") or f.name.endswith(".json")]
    out["pth_count"] = len(pth_files)
    out["trainer_chkpt_count"] = len(chkpt_files)

    agents: List[str] = []
    for f in pth_files:
        if f.name.startswith("agent_"):
            agents.append(f.name)
    out["agents_found"] = sorted(agents)

    if expected_agent_count is not None:
        missing = []
        for i in range(expected_agent_count):
            name = f"agent_{i}.pth"
            if not (path / name).exists():
                missing.append(name)
        if missing:
            out["issues"].append("missing_agents")
            out["missing_agents"] = missing

    # detect trainer checkpoint present but no runtime pth files
    if chkpt_files and not pth_files:
        out["issues"].append("trainer_json_checkpoint_not_runtime_loadable")

    # detect missing metadata sidecars for each agent_N.pth
    missing_sidecars = []
    for f in pth_files:
        meta_name = f.name + ".meta.json"
        if not (path / meta_name).exists():
            missing_sidecars.append(meta_name)
    if missing_sidecars:
        out["issues"].append("missing_metadata_sidecar")
        out["missing_metadata_sidecar"] = missing_sidecars

    # suitability: require expected_agent_count present and sidecars present
    suitable = True
    if expected_agent_count is not None:
        if len(agents) < expected_agent_count:
            suitable = False
    if missing_sidecars:
        suitable = False
    out["suitable_for_official_validation"] = suitable
    return out


def write_checkpoint_metadata_sidecar(path: Path, metadata: Dict[str, Any]) -> Path:
    """Write a JSON-only sidecar for a model file path.

    Validates required fields and defaults `official_claim_allowed` to False.
    Does not write or modify model files.
    """
    meta_path = path.with_name(path.name + ".meta.json")
    required = [
        "policy_name",
        "checkpoint_format",
        "created_by",
        "seed",
        "state_dim",
        "action_count",
    ]
    # additional required paper/reference linkage
    if "paper_contract_ref" not in metadata and "config_ref" not in metadata:
        raise ValueError("missing metadata field: paper_contract_ref or config_ref")
    if "episode_count" not in metadata and "epoch_count" not in metadata:
        raise ValueError("missing metadata field: episode_count or epoch_count")

    for r in required:
        if r not in metadata:
            raise ValueError(f"missing metadata field: {r}")

    metadata.setdefault("official_claim_allowed", False)
    meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return meta_path
