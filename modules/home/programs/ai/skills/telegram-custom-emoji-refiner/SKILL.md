---
name: telegram-custom-emoji-refiner
description: Analyze a local Telegram emoji-cache and, with approval, replace default emojis or improve user-facing Telegram UI with visually verified custom emojis. Use after a bot or Telegram-facing interface already exists; do not use to build its behavior.
---

# Telegram Custom Emoji Refiner

Refine a completed Telegram-facing project without changing its product logic. The user supplies an `emoji-cache/` directory that can contain multiple cached packs. Treat the cache as local, untracked working data; never add it or `.emoji-intelligence/` to Git.

## Scope and boundary

Work on every user-facing Telegram surface that can represent a custom emoji: message and caption text, button labels, descriptions, titles, menus, and configured user-visible copy. Inspect the project’s actual framework and serialization path before choosing a representation; do not assume a Markdown link or entity format works in every context.

Do not alter handlers, control flow, data, identifiers, regular expressions, test fixtures, logs, code comments, documentation, or copy that must remain literal. Do not force a replacement in a Telegram surface that cannot support custom emojis.

## Cache intelligence

Discover each pack from its `manifest.json`, excluding `.emoji-intelligence/`. Run `scripts/build_cache_index.py <emoji-cache-path>` to generate the current catalog and detect changed source files. The index preserves reviews whose individual preview and asset data are unchanged, so recaching a pack does not require re-reviewing unaffected emojis. On a pack's first use, or when an emoji's fingerprint has changed, visually inspect that emoji's local preview; also inspect its asset when the preview is ambiguous or animation matters. Write a complete English visual review for every emoji according to [the cache index schema](references/cache-index-schema.md). A pack is not reviewed until every available emoji has a review.

Follow [the visual inspection protocol](references/visual-inspection.md) for all of this: establish a working visual channel before promising any review, gather per-emoji evidence one emoji at a time (multi-tile contact sheets proved position-unreliable in practice), and use `scripts/analyze_tgs.py` for asset evidence — whether a manifest `animated` type actually moves, fill/stroke colors, timing — which also tells you which display background contrasts with the artwork.

The individual reviews and aggregate index are the search aid for later runs; reuse them without reanalyzing an unchanged pack. Never infer an entry's visual description, tags, colors, or suitability solely from its Unicode hint, filename, pack name, or manifest type: hints and filenames may shortlist candidates for verification, but they are never visual evidence, and an `animated` manifest entry can be a still drawing (one real pack had 514 still icons out of 515, including a 💎-hinted icon that was actually a plain triangle outline). The saved review narrows candidates but is not proof that an emoji suits a particular placement: reopen the exact candidate preview or asset before proposing it.

## When full-pack review is infeasible

Per-emoji verification costs one vision call per emoji, so a several-hundred-icon pack may not fit in one session. Do not degrade the evidence — narrow the scope:

- Keep the placement gate absolute: every final placement candidate is still verified individually, on its own, immediately before proposing it.
- Merge the verified candidate reviews into the pack summary (partial reviews merge fine), leave the pack `needs_review`, and record a note stating method and coverage (for example, "9/515 verified via single-icon inspection").
- Report the coverage gap to the user and offer to complete the full index as follow-up work.

## Refinement workflow

1. Scan the target project for user-visible Telegram copy and identify every existing default/Unicode emoji. Also identify emoji-free copy where a custom emoji would be a clear improvement.
2. Use the aggregate cache index to select candidates from any available pack. Reusing a custom emoji in multiple places is allowed when it remains semantically and visually appropriate.
3. Before proposing each final placement, visually inspect that exact emoji’s preview or asset again — on its own, not in a grid — in the context of the target wording. If it does not fit, reject it and search again.
4. If no strong match exists, leave the source unchanged and record the location for the final manual-selection report. Never substitute a merely similar or decorative emoji.
5. Before editing target-project files, present a complete change plan: locations, current text, proposed custom emoji ID and pack, intended representation, and rationale. Include all unresolved locations together. Wait for explicit approval.
6. After approval, apply only the approved changes. Preserve escaping, parsing mode, localization, and existing formatting. Validate the affected code or configuration using the project’s normal local checks.

## Reporting

At completion, report changed locations, the custom emoji IDs and packs used, verification performed, every unresolved location that needs a manually supplied emoji, and each pack’s verified coverage (for example, 9 of 515 emojis). Clearly distinguish generated cache intelligence from edits to the target project.
