#!/usr/bin/env python3
"""Day 11 - Character Counter.

Break text down by character type: letters, digits, spaces,
punctuation and more. Shows totals, case split, and a mini
frequency chart. Reads a file, piped stdin, or inline text.
Standard library only.

Examples:
  python3 main.py notes.txt
  python3 main.py --text "Hello, World! 123"
  echo "abc XYZ 99!!" | python3 main.py --top 5
  python3 main.py a.txt b.txt --json
"""

from __future__ import annotations

import argparse
import json
import string
import sys
import unicodedata
from collections import Counter
from pathlib import Path

def analyze(text: str, top: int = 10) -> dict:
    letters = digits = spaces = punctuation = other = 0
    upper = lower = 0
    for ch in text:
        if ch.isalpha():
            letters += 1
            if ch.isupper():
                upper += 1
            elif ch.islower():
                lower += 1
        elif ch.isdigit():
            digits += 1
        elif ch.isspace():
            spaces += 1
        elif ch in string.punctuation:
            punctuation += 1
        else:
            other += 1

    no_spaces = sum(1 for ch in text if not ch.isspace())
    words = [w for w in text.split() if w]
    lines = text.splitlines() if text else []
    # visible frequency: skip whitespace for a cleaner chart
    visible = [ch for ch in text if not ch.isspace()]
    freq = Counter(visible).most_common(top)

    return {
        "characters": len(text),
        "characters_no_spaces": no_spaces,
        "letters": letters,
        "uppercase": upper,
        "lowercase": lower,
        "digits": digits,
        "spaces": spaces,
        "punctuation": punctuation,
        "other": other,
        "words": len(words),
        "lines": len(lines),
        "top_characters": [(ch, n) for ch, n in freq],
    }


def bar(n: int, biggest: int, width: int = 20) -> str:
    return "#" * max(1, round(width * n / biggest)) if biggest else ""


def show_char(ch: str) -> str:
    """Pretty-print a character for the frequency table."""
    if ch == "\t":
        return r"\t"
    if ch == "\n":
        return r"\n"
    if ch == "\r":
        return r"\r"
    if ch == " ":
        return "' '"
    name = unicodedata.name(ch, "")
    if not ch.isprintable():
        return f"U+{ord(ch):04X}"
    if name and not ch.isascii():
        return f"{ch} ({name.title()})"
    return ch


def print_report(name: str, s: dict) -> None:
    print(f"\n  {name}")
    print("  " + "-" * 38)
    rows = [
        ("Characters", s["characters"]),
        ("Chars (no spaces)", s["characters_no_spaces"]),
        ("Letters", s["letters"]),
        ("  Uppercase", s["uppercase"]),
        ("  Lowercase", s["lowercase"]),
        ("Digits", s["digits"]),
        ("Spaces", s["spaces"]),
        ("Punctuation", s["punctuation"]),
        ("Other", s["other"]),
        ("Words", s["words"]),
        ("Lines", s["lines"]),
    ]
    for label, value in rows:
        print(f"  {label:<18} {value}")

    if s["top_characters"]:
        print("\n  Top characters")
        biggest = s["top_characters"][0][1]
        shown = [(show_char(ch), n) for ch, n in s["top_characters"]]
        pad = max(len(label) for label, _ in shown)
        for label, n in shown:
            print(f"  {label:<{pad}}  {n:>4}  {bar(n, biggest)}")


def read_sources(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.text is not None:
        return [("inline text", args.text)]
    if args.files:
        out = []
        for f in args.files:
            path = Path(f)
            if not path.is_file():
                sys.exit(f"error: file not found: {f}")
            out.append((str(path), path.read_text(encoding="utf-8", errors="replace")))
        return out
    if not sys.stdin.isatty():
        return [("stdin", sys.stdin.read())]
    print("Type or paste text, then press Ctrl+D (Ctrl+Z then Enter on Windows):")
    return [("typed text", sys.stdin.read())]


def main() -> None:
    p = argparse.ArgumentParser(
        description="Count characters by type with a frequency chart."
    )
    p.add_argument("files", nargs="*", help="text files to analyze")
    p.add_argument("-t", "--text", help="analyze this text instead of a file")
    p.add_argument(
        "--top", type=int, default=10, help="how many top characters (default 10)"
    )
    p.add_argument("--json", action="store_true", help="print results as JSON")
    args = p.parse_args()

    sources = read_sources(args)
    results = {name: analyze(text, args.top) for name, text in sources}

    if len(results) > 1:
        results["TOTAL"] = analyze("\n".join(t for _, t in sources), args.top)

    if args.json:
        payload = results if len(results) > 1 else next(iter(results.values()))
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    for name, stats in results.items():
        print_report(name, stats)
    print()


if __name__ == "__main__":
    main()
