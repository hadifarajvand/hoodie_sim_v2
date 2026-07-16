from __future__ import annotations

import os

PORTABLE_BACKENDS = {"auto", "portable", "worker-selected"}
SUPPORTED_DEVICE_PREFIXES = {"cpu", "cuda", "mps"}


def _validate_device_name(device: str) -> str:
    value = str(device).strip().lower()
    if not value:
        raise ValueError("execution device cannot be empty")
    prefix = value.split(":", 1)[0]
    if prefix not in SUPPORTED_DEVICE_PREFIXES:
        raise ValueError(
            f"unsupported HOODIE execution device {device!r}; expected cpu, cuda[:index], or mps"
        )
    return value


def resolve_execution_device(contract_backend: object) -> str:
    """Resolve the worker's tensor backend without changing scientific inputs.

    The simulation's CPU capacities are model parameters and are unrelated to the
    tensor execution device. Corrected matrix rows therefore use a portable backend
    contract. Workers may select one device through ``HOODIE_DEVICE``. When it is
    omitted, CPU is used deterministically.
    """

    contract = str(contract_backend or "worker-selected").strip().lower()
    requested = os.environ.get("HOODIE_DEVICE")
    if contract in PORTABLE_BACKENDS:
        return _validate_device_name(requested or "cpu")
    fixed = _validate_device_name(contract)
    if requested is not None and _validate_device_name(requested) != fixed:
        raise ValueError(
            f"HOODIE_DEVICE={requested!r} conflicts with fixed matrix backend {fixed!r}"
        )
    return fixed


def backend_family(device: str) -> str:
    return _validate_device_name(device).split(":", 1)[0]
