#!/usr/bin/env python3
"""Day 39 - Color Palette Generator.

Build harmonious palettes from a seed color, or invent a random one.
Standard library only.

Usage:
  python main.py '#FF5733'
  python main.py '#3498db' --harmony triadic
  python main.py '#FF5733' --harmony shades --count 6
  python main.py --random --count 5
  python main.py '#FF5733' --css
"""

from __future__ import annotations

import argparse
import colorsys
import json
import random
import re
import sys

HARMONIES = (
    "analogous",
    "complementary",
    "split-complementary",
    "triadic",
    "tetradic",
    "monochromatic",
    "shades",
    "tints",
    "tones",
    "random",
)


def clamp_byte(n: float) -> int:
    return max(0, min(255, int(round(n))))


def parse_hex(text: str) -> tuple[int, int, int]:
    s = text.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) == 8:
        s = s[:6]
    if len(s) != 6 or any(c not in "0123456789abcdefABCDEF" for c in s):
        raise ValueError(f"invalid hex color: {text!r}")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def parse_rgb(text: str) -> tuple[int, int, int]:
    m = re.fullmatch(
        r"rgba?\(\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)"
        r"(?:\s*,\s*[0-9.]+\s*)?\)",
        text.strip(),
        re.I,
    )
    parts = m.groups() if m else re.split(r"[,\s]+", text.strip())
    if len(parts) != 3:
        raise ValueError(f"invalid rgb color: {text!r}")
    out: list[int] = []
    for v in parts:
        if str(v).endswith("%"):
            out.append(clamp_byte(float(v[:-1]) * 2.55))
        else:
            n = float(v)
            if n < 0 or n > 255:
                raise ValueError(f"rgb channel out of range: {v}")
            out.append(clamp_byte(n))
    return out[0], out[1], out[2]


def parse_color(text: str) -> tuple[int, int, int]:
    raw = text.strip()
    low = raw.lower()
    if low.startswith("rgb") or "," in raw:
        return parse_rgb(raw)
    if raw.startswith("#") or re.fullmatch(r"[0-9a-fA-F]{3,8}", raw):
        return parse_hex(raw)
    raise ValueError(
        f"unrecognized color: {text!r} (try #RRGGBB or rgb(r,g,b))"
    )


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0, s * 100.0, l * 100.0


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb((h % 360.0) / 360.0, l / 100.0, s / 100.0)
    return clamp_byte(r * 255), clamp_byte(g * 255), clamp_byte(b * 255)


def describe(rgb: tuple[int, int, int]) -> dict:
    h, s, l = rgb_to_hsl(rgb)
    return {
        "hex": to_hex(rgb),
        "rgb": list(rgb),
        "hsl": [round(h, 1), round(s, 1), round(l, 1)],
    }


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def sample_range(start: float, end: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    return [lerp(start, end, i / (count - 1)) for i in range(count)]


def rotate(h: float, deg: float) -> float:
    return (h + deg) % 360.0


def generate(
    seed: tuple[int, int, int], harmony: str, count: int
) -> list[tuple[int, int, int]]:
    h, s, l = rgb_to_hsl(seed)
    count = max(1, count)

    if harmony == "complementary":
        hues = [h, rotate(h, 180)]
    elif harmony == "split-complementary":
        hues = [h, rotate(h, 150), rotate(h, 210)]
    elif harmony == "triadic":
        hues = [h, rotate(h, 120), rotate(h, 240)]
    elif harmony == "tetradic":
        hues = [h, rotate(h, 90), rotate(h, 180), rotate(h, 270)]
    elif harmony == "analogous":
        step = 30.0
        start = -step * (count - 1) / 2.0
        hues = [rotate(h, start + i * step) for i in range(count)]
    elif harmony == "monochromatic":
        return [hsl_to_rgb(h, s, li) for li in sample_range(18.0, 82.0, count)]
    elif harmony == "shades":
        floor = min(l, max(8.0, l * 0.15))
        return [hsl_to_rgb(h, s, li) for li in sample_range(l, floor, count)]
    elif harmony == "tints":
        ceiling = min(92.0, l + (100.0 - l) * 0.9)
        return [hsl_to_rgb(h, s, li) for li in sample_range(l, ceiling, count)]
    elif harmony == "tones":
        return [hsl_to_rgb(h, si, l) for si in sample_range(s, 8.0, count)]
    elif harmony == "random":
        # Golden-angle walk keeps hues visually spaced; starts at the seed.
        return [hsl_to_rgb(h + i * 137.508, s, l) for i in range(count)]
    else:
        raise ValueError(f"unknown harmony: {harmony}")

    return [hsl_to_rgb(hi, s, l) for hi in hues]


def ansi_swatch(rgb: tuple[int, int, int], width: int = 4) -> str:
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m{' ' * width}\033[0m"


def format_human(colors: list[tuple[int, int, int]], *, swatch: bool) -> str:
    lines: list[str] = []
    for i, rgb in enumerate(colors, 1):
        info = describe(rgb)
        hh, ss, ll = info["hsl"]
        prefix = ansi_swatch(rgb) + "  " if swatch and sys.stdout.isatty() else ""
        lines.append(
            f"{prefix}{i:2}.  {info['hex']}  "
            f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})  "
            f"hsl({hh}, {ss}%, {ll}%)"
        )
    return "\n".join(lines)


def format_css(colors: list[tuple[int, int, int]]) -> str:
    rows = [f"  --color-{i}: {to_hex(c)};" for i, c in enumerate(colors, 1)]
    return ":root {\n" + "\n".join(rows) + "\n}"


def read_seed_text(arg_color: str | None) -> str:
    if arg_color:
        return arg_color.strip()
    if not sys.stdin.isatty():
        lines = [line.strip() for line in sys.stdin if line.strip()]
        if lines:
            return lines[0]
    return ""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate a color palette from a seed color or at random."
    )
    p.add_argument("color", nargs="?", help="seed color as #HEX or rgb(r,g,b)")
    p.add_argument(
        "--harmony",
        choices=HARMONIES,
        default="analogous",
        help="palette type (default: analogous)",
    )
    p.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="how many colors for scalable harmonies (default: 5)",
    )
    p.add_argument("--json", action="store_true", help="print machine-readable JSON")
    p.add_argument("--css", action="store_true", help="print CSS custom properties")
    p.add_argument("--no-swatch", action="store_true", help="disable ANSI preview")
    p.add_argument(
        "--random",
        action="store_true",
        help="generate a spaced random palette (seed is optional)",
    )
    args = p.parse_args()

    if args.count < 1:
        print("--count needs a positive number", file=sys.stderr)
        return 1

    harmony = "random" if args.random else args.harmony
    raw = read_seed_text(args.color)
    seed: tuple[int, int, int] | None = None

    if raw:
        try:
            seed = parse_color(raw)
        except ValueError as err:
            print(err, file=sys.stderr)
            return 2
    elif harmony != "random":
        p.print_help()
        return 1
    else:
        seed = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    colors = generate(seed, harmony, args.count)
    infos = [describe(c) for c in colors]
    payload = {
        "harmony": harmony,
        "seed": describe(seed) if raw else None,
        "count": len(colors),
        "colors": infos,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    if args.css:
        print(format_css(colors))
        return 0

    print(f"{harmony} palette  ({len(colors)} colors)")
    if payload["seed"]:
        print(f"seed  {payload['seed']['hex']}")
    print(format_human(colors, swatch=not args.no_swatch))
    return 0


if __name__ == "__main__":
    sys.exit(main())
