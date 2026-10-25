import json
import os
from pathlib import Path

SIDECAR = ".vidcurator.json"
DEFAULT_BUCKETS = [
    {"id": "accepted", "label": "Accepted", "folder": "accepted"},
    {"id": "declined", "label": "Declined", "folder": "declined"},
]


def _valid_bucket(b):
    return (
        isinstance(b, dict)
        and all(isinstance(b.get(k), str) and b[k] for k in ("id", "label", "folder"))
        and b["folder"] not in (".", "..")
        and not any(c in b["folder"] for c in "/\\")
    )


def load(folder):
    data = {
        "buckets": [dict(b) for b in DEFAULT_BUCKETS],
        "marks": {},
        "ignored": [],
        "recursive": False,
    }
    try:
        raw = json.loads((Path(folder) / SIDECAR).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return data
    if not isinstance(raw, dict) or raw.get("version") != 1:
        return data
    buckets = [b for b in raw.get("buckets") or [] if _valid_bucket(b)]
    if buckets:
        data["buckets"] = [
            {"id": b["id"], "label": b["label"], "folder": b["folder"]} for b in buckets
        ]
    ids = {b["id"] for b in data["buckets"]}
    data["marks"] = {
        k: v
        for k, v in (raw.get("marks") or {}).items()
        if isinstance(k, str) and isinstance(v, str) and v in ids
    }
    data["ignored"] = [
        x
        for x in (raw.get("ignored") or [])
        if isinstance(x, str) and x and not any(c in x for c in "/\\")
    ]
    data["recursive"] = bool(raw.get("recursive"))
    return data


def save(folder, data):
    path = Path(folder) / SIDECAR
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps({"version": 1, **data}, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
