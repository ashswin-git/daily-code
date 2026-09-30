#!/usr/bin/env python3
"""Day 2 — Username Generator (CLI)."""

from __future__ import annotations

import argparse
import random
import secrets
import string
import sys

ADJECTIVES = [
    "swift",
    "calm",
    "bright",
    "quiet",
    "bold",
    "lucky",
    "clever",
    "cosmic",
    "neon",
    "silent",
    "fuzzy",
    "rapid",
    "sunny",
    "misty",
    "mighty",
    "gentle",
    "pixel",
    "lunar",
    "amber",
    "coral",
    "frost",
    "vivid",
    "noble",
    "wild",
]

NOUNS = [
    "otter",
    "falcon",
    "panda",
    "nexus",
    "comet",
    "river",
    "maple",
    "ember",
    "nova",
    "pixel",
    "wave",
    "stone",
    "cloud",
    "tiger",
    "spark",
    "orbit",
    "cedar",
    "lotus",
    "hawk",
    "drift",
    "quark",
    "bloom",
    "cinder",
    "aurora",
]


def random_digits(n: int) -> str:
    if n <= 0:
        return ""
    return "".join(secrets.choice(string.digits) for _ in range(n))


def generate_username(
    *,
    style: str,
    separator: str,
    digits: int,
    capitalize: bool,
) -> str:
    adj = secrets.choice(ADJECTIVES)
    noun = secrets.choice(NOUNS)

    if capitalize:
        adj = adj.capitalize()
        noun = noun.capitalize()

    if style == "adj-noun":
        base = f"{adj}{separator}{noun}"
    elif style == "noun-adj":
        base = f"{noun}{separator}{adj}"
    elif style == "adjnoun":
        base = f"{adj}{noun}"
    else:  # word-number only uses one word + digits
        base = secrets.choice(ADJECTIVES + NOUNS)
        if capitalize:
            base = base.capitalize()

    return f"{base}{random_digits(digits)}"


def unique_batch(
    count: int,
    *,
    style: str,
    separator: str,
    digits: int,
    capitalize: bool,
) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    attempts = 0
    max_attempts = count * 50

    while len(names) < count and attempts < max_attempts:
        attempts += 1
        name = generate_username(
            style=style,
            separator=separator,
            digits=digits,
            capitalize=capitalize,
        )
        if name not in seen:
            seen.add(name)
            names.append(name)

    if len(names) < count:
        raise RuntimeError(
            "Could not generate enough unique usernames. "
            "Try more digits or a different style."
        )
    return names


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fun, readable usernames from the command line.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        help="How many usernames to generate (default: 5).",
    )
    parser.add_argument(
        "-s",
        "--style",
        choices=["adj-noun", "noun-adj", "adjnoun", "word"],
        default="adj-noun",
        help="Username pattern (default: adj-noun).",
    )
    parser.add_argument(
        "--separator",
        default="_",
        help="Separator between words (default: _). Use '' for none.",
    )
    parser.add_argument(
        "-d",
        "--digits",
        type=int,
        default=2,
        help="Trailing digits to append (default: 2, use 0 for none).",
    )
    parser.add_argument(
        "--capitalize",
        action="store_true",
        help="Capitalize each word (CamelCase-friendly).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for reproducible demos (not for uniqueness).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.count < 1:
        print("Error: --count must be at least 1.", file=sys.stderr)
        return 1
    if args.digits < 0:
        print("Error: --digits cannot be negative.", file=sys.stderr)
        return 1

    if args.seed is not None:
        # Only affects list shuffle demos; generation still uses secrets.
        random.seed(args.seed)

    try:
        names = unique_batch(
            args.count,
            style=args.style,
            separator=args.separator,
            digits=args.digits,
            capitalize=args.capitalize,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for name in names:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
