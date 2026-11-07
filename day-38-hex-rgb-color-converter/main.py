#!/usr/bin/env python3
"""Day 38 - HEX/RGB Color Converter.

Convert colors between HEX, RGB and HSL from the command line.
Standard library only.

Usage:
  python main.py '#FF5733'
  python main.py rgb(255,87,51) --hsl
  python main.py '#FF5733' '#3498db' --contrast
  python main.py --random 3
"""

from __future__ import annotations

import argparse
import colorsys
import json
import random
import re
import sys

# A compact CSS named-color table for "closest name" hints.
NAMED: dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "lime": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "maroon": (128, 0, 0),
    "olive": (128, 128, 0),
    "green": (0, 128, 0),
    "purple": (128, 0, 128),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "coral": (255, 127, 80),
    "gold": (255, 215, 0),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238),
    "turquoise": (64, 224, 208),
    "crimson": (220, 20, 60),
    "tomato": (255, 99, 71),
    "salmon": (250, 128, 114),
    "khaki": (240, 230, 140),
    "lavender": (230, 230, 250),
    "beige": (245, 245, 220),
}


def clamp_byte(n: float) -> int:
    return max(0, min(255, int(round(n))))


def parse_hex(text: str) -> tuple[int, int, int]:
    s = text.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) == 8:  # drop alpha if present
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
    if not m:
        # bare "r,g,b" or "r g b"
        parts = re.split(r"[,\s]+", text.strip())
        if len(parts) != 3:
            raise ValueError(f"invalid rgb color: {text!r}")
        vals = parts
    else:
        vals = m.groups()

    out: list[int] = []
    for v in vals:
        if v.endswith("%"):
            out.append(clamp_byte(float(v[:-1]) * 2.55))
        else:
            n = float(v)
            if n < 0 or n > 255:
                raise ValueError(f"rgb channel out of range: {v}")
            out.append(clamp_byte(n))
    return out[0], out[1], out[2]


def parse_hsl(text: str) -> tuple[int, int, int]:
    m = re.fullmatch(
        r"hsla?\(\s*([0-9.]+)\s*,\s*([0-9.]+)%\s*,\s*([0-9.]+)%"
        r"(?:\s*,\s*[0-9.]+\s*)?\)",
        text.strip(),
        re.I,
    )
    if not m:
        raise ValueError(f"invalid hsl color: {text!r}")
    h, s, l = float(m.group(1)), float(m.group(2)), float(m.group(3))
    if not (0 <= s <= 100 and 0 <= l <= 100):
        raise ValueError("HSL S/L must be 0–100%")
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l / 100.0, s / 100.0)
    return clamp_byte(r * 255), clamp_byte(g * 255), clamp_byte(b * 255)


def parse_color(text: str) -> tuple[int, int, int]:
    raw = text.strip()
    low = raw.lower()
    if low in NAMED:
        return NAMED[low]
    if low.startswith("hsl"):
        return parse_hsl(raw)
    if low.startswith("rgb") or "," in raw:
        return parse_rgb(raw)
    if raw.startswith("#") or re.fullmatch(r"[0-9a-fA-F]{3,8}", raw):
        return parse_hex(raw)
    # last try: named-ish or hex without #
    try:
        return parse_hex(raw)
    except ValueError:
        raise ValueError(
            f"unrecognized color: {text!r} "
            "(try #RRGGBB, rgb(r,g,b), hsl(h,s%,l%), or a CSS name)"
        ) from None


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def to_rgb_str(rgb: tuple[int, int, int]) -> str:
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360.0, 1), round(s * 100.0, 1), round(l * 100.0, 1)


def to_hsl_str(rgb: tuple[int, int, int]) -> str:
    h, s, l = to_hsl(rgb)
    return f"hsl({h}, {s}%, {l}%)"


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    l1, l2 = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def closest_name(rgb: tuple[int, int, int]) -> tuple[str, int]:
    best, best_d = "black", 10**9
    for name, (nr, ng, nb) in NAMED.items():
        d = (rgb[0] - nr) ** 2 + (rgb[1] - ng) ** 2 + (rgb[2] - nb) ** 2
        if d < best_d:
            best, best_d = name, d
    return best, best_d


def ansi_swatch(rgb: tuple[int, int, int], width: int = 4) -> str:
    r, g, b = rgb
    block = " " * width
    return f"\033[48;2;{r};{g};{b}m{block}\033[0m"


def describe(rgb: tuple[int, int, int], *, show_hsl: bool, show_name: bool) -> dict:
    info: dict = {
        "hex": to_hex(rgb),
        "rgb": list(rgb),
        "rgb_str": to_rgb_str(rgb),
    }
    h, s, l = to_hsl(rgb)
    info["hsl"] = [h, s, l]
    info["hsl_str"] = to_hsl_str(rgb)
    if show_name:
        name, dist = closest_name(rgb)
        info["closest_name"] = name
        info["name_distance"] = dist
    return info


def format_human(info: dict, rgb: tuple[int, int, int], *, swatch: bool, show_hsl: bool, show_name: bool) -> str:
    parts: list[str] = []
    if swatch and sys.stdout.isatty():
        parts.append(ansi_swatch(rgb))
    parts.append(info["hex"])
    parts.append(info["rgb_str"])
    if show_hsl:
        parts.append(info["hsl_str"])
    if show_name and "closest_name" in info:
        parts.append(f"~{info['closest_name']}")
    return "  ".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Convert colors between HEX, RGB and HSL."
    )
    p.add_argument(
        "colors",
        nargs="*",
        help="colors as #HEX, rgb(r,g,b), hsl(h,s%,l%), or a CSS name",
    )
    p.add_argument(
        "--hsl",
        action="store_true",
        help="always include HSL in the output",
    )
    p.add_argument(
        "--name",
        action="store_true",
        help="show the closest CSS named color",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable JSON",
    )
    p.add_argument(
        "--no-swatch",
        action="store_true",
        help="disable ANSI truecolor preview",
    )
    p.add_argument(
        "--contrast",
        action="store_true",
        help="with two colors, print WCAG contrast ratio",
    )
    p.add_argument(
        "--random",
        type=int,
        metavar="N",
        help="generate N random colors instead of parsing args",
    )
    args = p.parse_args()

    if args.random is not None:
        if args.random < 1:
            print("--random needs a positive count", file=sys.stderr)
            return 1
        colors = [
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for _ in range(args.random)
        ]
    else:
        raw_list = list(args.colors)
        if not raw_list and not sys.stdin.isatty():
            raw_list = [line.strip() for line in sys.stdin if line.strip()]
        if not raw_list:
            p.print_help()
            return 1
        colors = []
        for raw in raw_list:
            try:
                colors.append(parse_color(raw))
            except ValueError as err:
                print(err, file=sys.stderr)
                return 2

    infos = [
        describe(c, show_hsl=True, show_name=args.name or True)
        for c in colors
    ]
    # always compute name for json richness when --name; for human, only if asked
    if not args.name:
        for info in infos:
            info.pop("closest_name", None)
            info.pop("name_distance", None)

    if args.contrast:
        if len(colors) != 2:
            print("--contrast needs exactly two colors", file=sys.stderr)
            return 1
        ratio = contrast_ratio(colors[0], colors[1])
        if args.json:
            print(
                json.dumps(
                    {
                        "a": infos[0],
                        "b": infos[1],
                        "contrast": ratio,
                        "aa_normal": ratio >= 4.5,
                        "aaa_normal": ratio >= 7.0,
                        "aa_large": ratio >= 3.0,
                    },
                    indent=2,
                )
            )
        else:
            for c, info in zip(colors, infos):
                print(
                    format_human(
                        info,
                        c,
                        swatch=not args.no_swatch,
                        show_hsl=args.hsl or True,
                        show_name=args.name,
                    )
                )
            level = (
                "AAA"
                if ratio >= 7.0
                else "AA"
                if ratio >= 4.5
                else "AA large"
                if ratio >= 3.0
                else "fail"
            )
            print(f"contrast {ratio}:1  ({level})")
        return 0

    if args.json:
        payload = infos[0] if len(infos) == 1 else infos
        print(json.dumps(payload, indent=2))
        return 0

    for c, info in zip(colors, infos):
        print(
            format_human(
                info,
                c,
                swatch=not args.no_swatch,
                show_hsl=args.hsl or True,
                show_name=args.name,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
