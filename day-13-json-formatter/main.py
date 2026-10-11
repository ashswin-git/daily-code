#!/usr/bin/env python3
"""JSON Formatter: pretty-print, validate and tidy JSON from text, files or stdin."""

import argparse
import json
import sys


def load(args):
    """Return raw JSON text from --text, a file, or stdin."""
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            return fh.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def explain_error(err, raw):
    """Build a friendly message that points at the broken spot."""
    lines = raw.splitlines() or [""]
    line = lines[min(err.lineno, len(lines)) - 1]
    pointer = " " * (err.colno - 1) + "^"
    return f"Invalid JSON: {err.msg} (line {err.lineno}, column {err.colno})\n  {line}\n  {pointer}"


def main():
    p = argparse.ArgumentParser(description="Pretty-print and validate JSON.")
    p.add_argument("file", nargs="?", help="JSON file to format (or use --text / stdin)")
    p.add_argument("-t", "--text", help="JSON string to format")
    p.add_argument("-i", "--indent", type=int, default=2, help="spaces per indent level (default 2)")
    p.add_argument("-s", "--sort-keys", action="store_true", help="sort object keys alphabetically")
    p.add_argument("-a", "--ascii", action="store_true", help="escape non-ASCII characters")
    p.add_argument("-c", "--check", action="store_true", help="only validate, print nothing else")
    p.add_argument("-o", "--output", help="write the result to this file")
    args = p.parse_args()

    raw = load(args)
    if raw is None:
        p.print_help()
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as err:
        print(explain_error(err, raw), file=sys.stderr)
        return 2

    if args.check:
        print("Valid JSON")
        return 0

    out = json.dumps(data, indent=args.indent, sort_keys=args.sort_keys, ensure_ascii=args.ascii)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"Saved to {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
