#!/usr/bin/env python3
"""Day 12 - Text Case Converter.

Convert text between common cases: upper, lower, title, sentence,
camelCase, PascalCase, snake_case, kebab-case, CONSTANT_CASE and more.
Reads inline text, a file, or piped stdin. Standard library only.

Examples:
  python3 main.py --text "hello world" --to snake
  python3 main.py --text "user_profile_id" --to camel
  echo "make this a title" | python3 main.py --to title
  python3 main.py notes.txt --to upper
  python3 main.py --text "Hello World" --all
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def split_words(text: str) -> list[str]:
    """Split on spaces/_/-, and on camelCase boundaries (HTTPServer -> HTTP, Server)."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return [w for w in re.split(r"[^0-9A-Za-z\u00C0-\uFFFF]+", text) if w]


def to_sentence(text: str) -> str:
    out, cap = [], True
    for ch in text.lower():
        if cap and ch.isalpha():
            out.append(ch.upper())
            cap = False
        else:
            out.append(ch)
        if ch in ".!?\n":
            cap = True
    return "".join(out)


def to_alternating(text: str) -> str:
    out, flip = [], False
    for ch in text:
        if ch.isalpha():
            out.append(ch.upper() if flip else ch.lower())
            flip = not flip
        else:
            out.append(ch)
    return "".join(out)


CONVERTERS = {
    "upper": lambda t: t.upper(),
    "lower": lambda t: t.lower(),
    "title": lambda t: t.title(),
    "sentence": to_sentence,
    "swap": lambda t: t.swapcase(),
    "alternating": to_alternating,
    "camel": lambda t: (lambda w: w[0].lower() + "".join(x.capitalize() for x in w[1:]) if w else "")(split_words(t)),
    "pascal": lambda t: "".join(w.capitalize() for w in split_words(t)),
    "snake": lambda t: "_".join(w.lower() for w in split_words(t)),
    "kebab": lambda t: "-".join(w.lower() for w in split_words(t)),
    "constant": lambda t: "_".join(w.upper() for w in split_words(t)),
    "dot": lambda t: ".".join(w.lower() for w in split_words(t)),
}


def convert(text: str, style: str) -> str:
    if style not in CONVERTERS:
        raise ValueError(f"unknown style '{style}' (choose from: {', '.join(CONVERTERS)})")
    return CONVERTERS[style](text)


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.exit("No input: pass --text, a file, or pipe text in. See --help.")


def main() -> None:
    p = argparse.ArgumentParser(description="Convert text between different cases.")
    p.add_argument("file", nargs="?", help="text file to convert")
    p.add_argument("--text", "-t", help="inline text to convert")
    p.add_argument("--to", "-c", choices=list(CONVERTERS), help="target case")
    p.add_argument("--all", "-a", action="store_true", help="show every case")
    p.add_argument("--list", "-l", action="store_true", help="list available cases")
    args = p.parse_args()

    if args.list:
        print("Available cases: " + ", ".join(CONVERTERS))
        return
    if not args.to and not args.all:
        p.error("choose a target with --to CASE, or use --all")

    text = read_input(args)
    if args.all:
        width = max(len(k) for k in CONVERTERS)
        for name in CONVERTERS:
            print(f"{name:<{width}}  {convert(text.rstrip(chr(10)), name)}")
    else:
        sys.stdout.write(convert(text, args.to))
        if not text.endswith("\n"):
            print()


if __name__ == "__main__":
    main()
