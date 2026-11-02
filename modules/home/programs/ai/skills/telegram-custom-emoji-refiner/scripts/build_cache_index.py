#!/usr/bin/env python3
"""Build a fingerprinted, visually annotated catalog for an emoji-cache directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest_file(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.digest()


def pack_fingerprint(pack_dir: Path, manifest: dict) -> str:
    digest = hashlib.sha256()
    manifest_path = pack_dir / "manifest.json"
    digest.update(b"manifest\0")
    digest.update(digest_file(manifest_path))
    for entry in manifest.get("emoji", []):
        for field in ("preview", "asset"):
            relative_path = entry.get(field)
            if not relative_path:
                continue
            media_path = pack_dir / relative_path
            digest.update(field.encode() + b"\0" + str(relative_path).encode() + b"\0")
            if media_path.is_file():
                digest.update(digest_file(media_path))
            else:
                digest.update(b"missing")
    return f"sha256:{digest.hexdigest()}"


def entry_fingerprint(pack_dir: Path, entry: dict) -> str:
    """Fingerprint only the media that a single visual review relies on."""
    digest = hashlib.sha256()
    digest.update(b"id\0" + str(entry["id"]).encode() + b"\0")
    for field in ("preview", "asset"):
        relative_path = entry.get(field)
        digest.update(field.encode() + b"\0" + str(relative_path).encode() + b"\0")
        if not relative_path:
            digest.update(b"missing")
            continue
        media_path = pack_dir / relative_path
        if media_path.is_file():
            digest.update(digest_file(media_path))
        else:
            digest.update(b"missing")
    return f"sha256:{digest.hexdigest()}"


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


REVIEW_FIELDS = {
    "visual_description": str,
    "semantic_tags": list,
    "tone": list,
    "dominant_colors": list,
    "animation": str,
    "good_for": list,
    "avoid_for": list,
    "confidence": str,
}


def reviewed_entry(data: dict) -> dict:
    """Validate a human/agent visual review before making it durable."""
    if not isinstance(data, dict):
        raise ValueError("each emoji review must be an object")
    for field, expected_type in REVIEW_FIELDS.items():
        value = data.get(field)
        if not isinstance(value, expected_type) or not value:
            raise ValueError(f"review field {field!r} must be a non-empty {expected_type.__name__}")
        if expected_type is list and not all(isinstance(item, str) and item.strip() for item in value):
            raise ValueError(f"review field {field!r} must contain non-empty strings")
    if data["confidence"] not in {"high", "medium", "low"}:
        raise ValueError("confidence must be high, medium, or low")
    return {
        "status": "reviewed",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        **{field: data[field] for field in REVIEW_FIELDS},
    }


def entry_review(
    previous_entry: dict | None,
    source_fingerprint: str,
    pack_unchanged: bool,
) -> dict:
    if previous_entry:
        review = previous_entry.get("visual_review")
        matching_entry = previous_entry.get("source_fingerprint") == source_fingerprint
        legacy_pack_match = pack_unchanged and "source_fingerprint" not in previous_entry
        if isinstance(review, dict) and (matching_entry or legacy_pack_match):
            return review
    return {"status": "needs_review"}


def catalog_entry(
    pack_dir: Path,
    entry: dict,
    previous_entry: dict | None,
    pack_unchanged: bool,
) -> dict:
    preview = entry.get("preview")
    asset = entry.get("asset")
    source_fingerprint = entry_fingerprint(pack_dir, entry)
    return {
        "id": entry["id"],
        "unicode_hint": entry.get("emoji"),
        "type": entry.get("type"),
        "source_fingerprint": source_fingerprint,
        "preview_path": f"{pack_dir.name}/{preview}" if preview else None,
        "asset_path": f"{pack_dir.name}/{asset}" if asset else None,
        "media": {
            "preview_available": bool(preview and (pack_dir / preview).is_file()),
            "asset_available": bool(asset and (pack_dir / asset).is_file()),
        },
        "visual_review": entry_review(previous_entry, source_fingerprint, pack_unchanged),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache_dir", type=Path)
    parser.add_argument("--pack", help="Build only one manifest pack by name.")
    parser.add_argument("--style", action="append", default=[])
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument(
        "--reviews",
        type=Path,
        help="JSON file containing visually verified English reviews for one pack.",
    )
    arguments = parser.parse_args()
    if arguments.reviews and not arguments.pack:
        raise SystemExit("--reviews requires --pack so annotations cannot be applied to another pack")

    cache_dir = arguments.cache_dir.resolve()
    intelligence_dir = cache_dir / ".emoji-intelligence"
    packs_dir = intelligence_dir / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)
    supplied_reviews = load_json(arguments.reviews) if arguments.reviews else {}
    if arguments.reviews and not supplied_reviews:
        raise SystemExit("--reviews must contain a valid JSON object")
    if supplied_reviews and not isinstance(supplied_reviews.get("emoji", {}), dict):
        raise SystemExit("--reviews.emoji must map emoji IDs to review objects")

    index_packs = []
    index_entries = []
    for manifest_path in sorted(cache_dir.glob("*/manifest.json")):
        pack_dir = manifest_path.parent
        manifest = load_json(manifest_path)
        if not manifest or not isinstance(manifest.get("emoji"), list):
            continue
        pack = manifest.get("pack") or pack_dir.name
        if arguments.pack and pack != arguments.pack:
            continue
        if supplied_reviews and supplied_reviews.get("pack") not in {None, pack}:
            raise SystemExit(f"--reviews is for {supplied_reviews['pack']!r}, not {pack!r}")
        fingerprint = pack_fingerprint(pack_dir, manifest)
        summary_path = packs_dir / f"{pack}.json"
        previous = load_json(summary_path)
        unchanged = previous and previous.get("source", {}).get("fingerprint") == fingerprint
        previous_entries = {
            entry.get("id"): entry
            for entry in (previous or {}).get("emoji", [])
            if entry.get("id")
        }
        entries = [
            catalog_entry(pack_dir, entry, previous_entries.get(entry["id"]), bool(unchanged))
            for entry in manifest["emoji"]
        ]
        supplied_by_id = supplied_reviews.get("emoji", {})
        entry_ids = {entry["id"] for entry in entries}
        unknown_ids = set(supplied_by_id) - entry_ids
        if unknown_ids:
            raise SystemExit(f"--reviews has unknown emoji IDs: {', '.join(sorted(unknown_ids))}")
        for entry in entries:
            if entry["id"] in supplied_by_id:
                entry["visual_review"] = reviewed_entry(supplied_by_id[entry["id"]])
        all_entries_reviewed = bool(entries) and all(
            entry["visual_review"].get("status") == "reviewed" for entry in entries
        )
        existing_pack_review = previous.get("visual_review", {}) if previous else {}
        review_status = "reviewed" if all_entries_reviewed else "needs_review"
        if arguments.style or arguments.note:
            review = {
                "status": review_status,
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "style_summary": arguments.style or existing_pack_review.get("style_summary", []),
                "notes": arguments.note or existing_pack_review.get("notes", []),
            }
        elif supplied_reviews:
            review = {
                "status": review_status,
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "style_summary": supplied_reviews.get(
                    "style_summary", existing_pack_review.get("style_summary", [])
                ),
                "notes": supplied_reviews.get("notes", existing_pack_review.get("notes", [])),
            }
        elif existing_pack_review:
            review = {**existing_pack_review, "status": review_status}
        else:
            review = {"status": review_status}
        summary = {
            "schema_version": 3,
            "pack": pack,
            "source": {
                "manifest_path": f"{pack_dir.name}/manifest.json",
                "fingerprint": fingerprint,
            },
            "visual_review": review,
            "emoji": entries,
        }
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index_packs.append({"pack": pack, **summary["source"], "visual_review": review})
        index_entries.extend({"pack": pack, **entry} for entry in summary["emoji"])

    processed_packs = {entry["pack"] for entry in index_packs}
    current_packs = {
        (load_json(path) or {}).get("pack") or path.parent.name
        for path in cache_dir.glob("*/manifest.json")
    }
    for summary_path in sorted(packs_dir.glob("*.json")):
        summary = load_json(summary_path)
        if not summary or summary.get("pack") not in current_packs or summary["pack"] in processed_packs:
            continue
        index_packs.append({"pack": summary["pack"], **summary["source"], "visual_review": summary["visual_review"]})
        index_entries.extend({"pack": summary["pack"], **entry} for entry in summary["emoji"])

    index = {
        "schema_version": 3,
        "packs": sorted(index_packs, key=lambda entry: entry["pack"]),
        "emoji": sorted(index_entries, key=lambda entry: (entry["pack"], entry["id"])),
    }
    (intelligence_dir / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
