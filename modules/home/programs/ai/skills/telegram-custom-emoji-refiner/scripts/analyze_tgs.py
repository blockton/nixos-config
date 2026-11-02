#!/usr/bin/env python3
"""Extract visual-evidence facts from TGS (gzipped Lottie) custom emoji assets.

Reports, per asset: timing (fps, duration), keyframed motion (which transform or
color properties animate and how many keyframes each has), staggered layer
timing, fill/stroke colors mapped to nearest color names, and shape-type counts.

This is asset evidence, not a visual review: use it to corroborate or challenge
what a preview shows — especially whether a manifest "animated" type actually
moves, and what display background will contrast with the artwork.

Usage:
    analyze_tgs.py <pack-dir>            # all .tgs under pack-dir/assets
    analyze_tgs.py <file.tgs> [more...]  # specific assets
"""

from __future__ import annotations

import glob
import gzip
import json
import sys

PROP_DESC = {
    "p": "position", "s": "scale", "r": "rotation", "o": "opacity",
    "a": "anchor", "c": "color", "tm": "trim", "sk": "skew",
    "so": "stroke-opacity", "eo": "fill-opacity",
}

NAMED_COLORS = {
    "white": (255, 255, 255), "black": (0, 0, 0), "gray": (128, 128, 128),
    "red": (227, 73, 73), "orange": (255, 167, 38), "amber": (255, 193, 7),
    "yellow": (255, 235, 59), "green": (67, 160, 71), "teal": (0, 137, 123),
    "cyan": (41, 208, 227), "sky blue": (66, 165, 245), "blue": (48, 105, 224),
    "navy": (26, 35, 126), "purple": (123, 61, 201), "violet": (149, 97, 226),
    "magenta": (216, 67, 231), "pink": (240, 98, 158), "brown": (121, 85, 72),
    "gold": (255, 214, 90),
}


def nearest_name(rgb):
    r, g, b = (value * 255 for value in rgb[:3])
    return min(NAMED_COLORS, key=lambda n: sum((
        (r - NAMED_COLORS[n][0]) ** 2,
        (g - NAMED_COLORS[n][1]) ** 2,
        (b - NAMED_COLORS[n][2]) ** 2,
    )))


def color_values(prop):
    """Static or keyframed color values from a fill/stroke color property."""
    if not isinstance(prop, dict):
        return []
    value = prop.get("k")
    if isinstance(value, list) and value and isinstance(value[0], list):
        return [c for c in value if isinstance(c, list) and len(c) >= 3]
    if isinstance(value, list) and len(value) >= 3 and not isinstance(value[0], dict):
        return [value]
    if isinstance(value, list):
        colors = []
        for keyframe in value:
            start = (keyframe or {}).get("s")
            if isinstance(start, list) and len(start) >= 3:
                colors.append(start)
        return colors
    return []


def analyze(data):
    frame_rate = data.get("fr", 0)
    duration = round((data.get("op", 0) - data.get("ip", 0)) / frame_rate, 2) if frame_rate else 0
    animated, fills, strokes, shape_types = {}, {}, {}, {}
    layers = []

    def walk(node, prop):
        if isinstance(node, dict):
            if node.get("a") == 1 and prop in PROP_DESC:
                keys = node.get("k")
                count = len(keys) if isinstance(keys, list) else 1
                animated[prop] = max(animated.get(prop, 0), count)
            if node.get("ty") == "fl":
                for color in color_values(node.get("c")):
                    name = nearest_name(color)
                    fills[name] = fills.get(name, 0) + 1
            elif node.get("ty") == "st":
                for color in color_values(node.get("c")):
                    name = nearest_name(color)
                    strokes[name] = strokes.get(name, 0) + 1
            elif isinstance(node.get("ty"), str):
                shape_types[node["ty"]] = shape_types.get(node["ty"], 0) + 1
            if all(key in node for key in ("ip", "op")) and "ks" in node:
                layers.append((node.get("ip", 0), node.get("op", 0)))
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    walk(value, key if key in PROP_DESC else prop)
        elif isinstance(node, list):
            for item in node:
                walk(item, prop)

    walk(data, None)
    total = data.get("op", 0)
    staggered = any(start > 0 or end < total for start, end in layers)
    return {
        "fps": frame_rate,
        "duration_s": duration,
        "keyframed_props": {PROP_DESC[name]: count for name, count in sorted(animated.items())},
        "moves": bool(animated) or staggered,
        "staggered_layers": staggered,
        "layer_count": len(layers),
        "fills": dict(sorted(fills.items(), key=lambda kv: -kv[1])),
        "strokes": dict(sorted(strokes.items(), key=lambda kv: -kv[1])),
        "shape_types": shape_types,
    }


def main() -> None:
    targets = []
    for argument in sys.argv[1:]:
        if argument.endswith(".tgs"):
            targets.extend(glob.glob(argument))
        else:
            targets.extend(glob.glob(f"{argument.rstrip('/')}/**/*.tgs", recursive=True))
    results = {}
    for path in sorted(targets):
        emoji_id = path.rsplit("/", 1)[-1][:-4]
        try:
            with open(path, "rb") as source:
                results[emoji_id] = analyze(json.loads(gzip.decompress(source.read())))
        except Exception as error:  # noqa: BLE001 - report and continue with other assets
            results[emoji_id] = {"error": f"{type(error).__name__}: {error}"[:120]}
    print(json.dumps(results, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
