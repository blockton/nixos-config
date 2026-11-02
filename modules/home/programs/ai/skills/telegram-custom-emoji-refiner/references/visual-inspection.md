# Visual Inspection Protocol

Read this before writing any visual review or proposing any placement. The rules below come from real runs; each one exists because skipping it produced wrong or fabricated data.

## Establish a working visual channel first

Before promising any review, prove you can actually see an emoji. Test the channel on one or two previews; if you cannot describe them with confidence, stop and report that visual verification is unavailable in this environment — never fall back to describing emojis from hints or filenames.

Channels, in order of preference:

1. Direct file reads, if the harness renders image pixels to you.
2. A vision-model MCP or tool that accepts an image URL. Test it on a known-good public image first: some vision endpoints are simply broken and reject everything.
3. A browser screenshot of the image plus channel 2 for the screenshot.

Hosting tip: serve the cache directory over localhost HTTP (`python3 -m http.server`) when a URL-consuming tool needs access; browsers cannot navigate to `file:` URLs in most automation setups.

## Single-icon inspection is the only reliable per-emoji evidence

Contact sheets and grids are position-unreliable in practice: the same grid produced contradictory per-tile descriptions across calls, with only the first row stable. Treat any multi-tile image as orientation at most, never as per-emoji evidence.

For per-emoji evidence, inspect one emoji per image: upscaled (300–400 px), on a contrasting background, with its index or ID as a visible label. Focused questions ("is there a handle?", "is it filled or outline?") resolve ambiguity; a second differently-phrased pass settles disputes.

## Vision output is often truncated

Accept a reading only if it covers the full requested range — check that the last requested index actually appears in the result. If it is cut off, re-ask only the missing range. Request short, line-based outputs to stay under the truncation budget.

## Process discipline

- One vision call at a time. Never pre-write expected outputs before the result arrives; if you can no longer prove which descriptions came from tool results, discard the whole batch and redo it. A fabricated review poisons the index for every later run.
- Append each verified result to a scratch file on disk immediately.
- Cross-check surprising reads programmatically: `magick <preview> -trim -format '%wx%h+%X+%Y' info:` reveals content bounding boxes (detects cropped previews; a "cut off" vision claim with a padded bbox is a model artifact, not real cropping).

## Media pitfalls

- Previews may be WebP bytes under a `.jpg` name. Verify with `file` and convert to real PNG before browser display; a wrong `Content-Type` renders as blank tiles that look like empty emojis.
- White glyphs on transparency vanish on light backgrounds. Pick the display background to contrast with the artwork — `scripts/analyze_tgs.py` reports fill/stroke colors so you know which contrast to choose.
- Telegram preview thumbnails can crop or differ from the asset. When a preview is ambiguous, inspect the asset as well.

## Scale reality: hundreds of icons

Reliable single-icon inspection costs one vision call per emoji. A 500-icon pack is hundreds of calls — often infeasible in one session. In that case fall back to placement-first mode (see SKILL.md): verify every final placement candidate individually, merge those reviews, and leave the pack `needs_review` with a note stating method and coverage. Offer to complete the full index as follow-up work.
