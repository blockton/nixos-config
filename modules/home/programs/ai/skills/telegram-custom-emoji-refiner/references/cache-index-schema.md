# Cache Intelligence Schema

Store generated analysis inside the supplied cache directory:

```text
emoji-cache/
├── <pack>/manifest.json
└── .emoji-intelligence/
    ├── index.json
    └── packs/<pack>.json
```

All generated prose, tags, and values in these files are English. This directory is local cache data, not source control input.

## Refresh rule

For each pack, persist a content fingerprint for `manifest.json` and every existing referenced `preview` or `asset`. Each emoji also has a fingerprint of its ID and referenced media. A rebuild reuses an individual review whenever that emoji fingerprint matches, even if the manifest's cache timestamp, entry order, or another emoji changed. Missing media is recorded per entry; it must not be silently treated as visual evidence.

## Pack summary

`packs/<pack>.json` contains the source fingerprint, a durable pack-level visual review, and a complete English visual review for every manifest emoji. Keep the source fields necessary to resolve the media locally. Never derive an individual review only from a Unicode hint, filename, or pack name: inspect the preview, and the asset when needed to understand animation or an ambiguous subject.

```json
{
  "schema_version": 3,
  "pack": "example-pack",
  "source": {
    "manifest_path": "example-pack/manifest.json",
    "fingerprint": "sha256:..."
  },
  "visual_review": {
    "status": "reviewed",
    "reviewed_at": "2026-11-02T12:00:00Z",
    "style_summary": ["playful", "rounded", "bright"],
    "notes": ["Use direct visual verification before any final placement."]
  },
  "emoji": [
    {
      "id": "1234567890123456789",
      "unicode_hint": "💎",
      "type": "static",
      "source_fingerprint": "sha256:...",
      "preview_path": "example-pack/previews/123.jpg",
      "asset_path": "example-pack/assets/123.webp",
      "media": {"preview_available": true, "asset_available": true},
      "visual_review": {
        "status": "reviewed",
        "reviewed_at": "2026-11-02T12:00:00Z",
        "visual_description": "Glossy blue faceted gem with a bright cyan highlight.",
        "semantic_tags": ["premium", "value", "reward", "highlight"],
        "tone": ["premium", "playful"],
        "dominant_colors": ["blue", "cyan"],
        "animation": "static",
        "good_for": ["feature title", "reward", "paid status"],
        "avoid_for": ["warning", "delete", "error"],
        "confidence": "high"
      }
    }
  ]
}
```

All descriptions, tags, tones, colors, usage guidance, and notes are English. `animation` states the observed behavior (for example `static`, `subtle pulse`, or `looping rotation`); it must not be inferred from the manifest type alone. Verify motion with `scripts/analyze_tgs.py`: an `animated` manifest entry whose asset has no keyframed properties and no staggered layers is visually still, and the review should say so explicitly. `confidence` is `high`, `medium`, or `low`. An unavailable or unreadable asset is explicitly recorded and cannot receive a `reviewed` status without sufficient visual evidence.

The pack-level review summarizes the shared visible style, contrast, animation character, and suitable UI families. Its `status` is `reviewed` only when every emoji entry has a complete `reviewed` visual review; otherwise it is `needs_review`. The final per-placement review always opens the exact selected preview or asset.

## Writing reviews

After visual inspection, give `scripts/build_cache_index.py` a temporary English JSON review file with `--reviews`. It has the pack name, optional English `style_summary` and `notes`, and an `emoji` object keyed by ID. Each value contains every field shown in `visual_review` above except `status` and `reviewed_at`; the script validates it, timestamps it, and merges it into the durable summary. Partial review files are allowed, but the pack remains `needs_review` until every emoji is complete.

## Script behavior notes

- Partial merges are the intended way to record a placement-first run: verified candidate reviews persist, and a pack note should state the method and coverage (for example, "9/515 verified via single-icon inspection").
- Plain rebuilds preserve prior entry reviews and pack-level notes for matching media. A changed or newly added emoji alone becomes `needs_review`; it does not erase reviews for unchanged entries. Existing schema-2 indexes seed the per-emoji fingerprints on the first unchanged rebuild.
- To record a user-directed skip: `build_cache_index.py <cache> --pack <name> --note "Skipped per user instruction (<date>): <reason>"`. The pack stays `needs_review` and its entries stay unreviewed, which is the honest state for an unreviewed pack.

## Aggregate index

`index.json` is the unified cross-pack lookup table. It lists each current pack summary and fingerprint, and duplicates every entry's factual fields plus its complete individual visual review so searches can use English descriptions, tags, tones, colors, and usage guidance across all packs. The pack summary remains authoritative.

When selecting an emoji, use the aggregate index first, then open the exact `preview_path` or `asset_path` for a final visual check. The index does not waive final inspection.
