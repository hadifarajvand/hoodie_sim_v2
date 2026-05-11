from __future__ import annotations

from collections import OrderedDict
from typing import Any


def canonical_item_key(item: dict[str, Any]) -> str:
    return str(item.get("item_id") or item.get("title") or item.get("domain") or "").strip().lower().replace(" ", "_")


def deduplicate_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    for item in items:
        key = canonical_item_key(item)
        if key not in deduped:
            deduped[key] = item
    return list(deduped.values())


def normalize_inventory_item(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or item.get("item_id") or item.get("domain") or "unknown item")
    return {
        "item_id": str(item.get("item_id") or canonical_item_key(item) or title).strip() or canonical_item_key(item),
        "domain": str(item.get("domain") or "other"),
        "title": title,
        "description": str(item.get("description") or title),
        "runtime_approval_required": bool(item.get("runtime_approval_required", True)),
        "manual_visual_recovery": item.get("manual_visual_recovery"),
    }
