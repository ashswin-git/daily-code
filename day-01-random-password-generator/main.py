#!/usr/bin/env python3
"""Day 1 — Random Password Generator (CLI)."""

from __future__ import annotations

import argparse
import secrets
import string
import sys


LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"


def build_alphabet(
    *,
    use_lower: bool,
    use_upper: bool,
    use_digits: bool,
    use_symbols: bool,
) -> str:
    parts: list[str] = []
    if use_lower:
        parts.append(LOWER)
    if use_upper:
        parts.append(UPPER)
    if use_digits:
        parts.append(DIGITS)
    if use_symbols:
        parts.append(SYMBOLS)
    return "".join(parts)


def generate_password(length: int, alphabet: str) -> str:
    if length < 4:
        raise ValueError("Password length must be at least 4.")
    if not alphabet:
        raise ValueError("Select at least one character set.")

    # Guarantee at least one char from each selected set when possible.
    required: list[str] = []
    sets = []
    if any(c in alphabet for c in LOWER):
        sets.append(LOWER)
    if any(c in alphabet for c in UPPER):
        sets.append(UPPER)
    if any(c in alphabet for c in DIGITS):
        sets.append(DIGITS)
    if any(c in alphabet for c in SYMBOLS):
        sets.append(SYMBOLS)

    for charset in sets:
        required.append(secrets.choice(charset))

    remaining = length - len(required)
    body = [secrets.choice(alphabet) for _ in range(remaining)]
    chars = required + body
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate strong random passwords from the command line.",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=16,
        help="Password length (default: 16, minimum: 4).",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        help="How many passwords to generate (default: 1).",
    )
    parser.add_argument(
        "--no-lower",
        action="store_true",
        help="Exclude lowercase letters.",
    )
    parser.add_argument(
        "--no-upper",
        action="store_true",
        help="Exclude uppercase letters.",
    )
    parser.add_argument(
        "--no-digits",
        action="store_true",
        help="Exclude digits.",
    )
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Exclude symbols.",
    )
    parser.add_argument(
        "--symbols-only-safe",
        action="store_true",
        help="Use a smaller symbol set that is shell-friendly.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.count < 1:
        print("Error: --count must be at least 1.", file=sys.stderr)
        return 1

    alphabet = build_alphabet(
        use_lower=not args.no_lower,
        use_upper=not args.no_upper,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
    )

    if args.symbols_only_safe and not args.no_symbols:
        # Rebuild with a safer symbol subset.
        safe_symbols = "!@#$%^&*-_=+"
        alphabet = build_alphabet(
            use_lower=not args.no_lower,
            use_upper=not args.no_upper,
            use_digits=not args.no_digits,
            use_symbols=False,
        ) + ("" if args.no_symbols else safe_symbols)

    try:
        for _ in range(args.count):
            print(generate_password(args.length, alphabet))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
