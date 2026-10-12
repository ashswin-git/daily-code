#!/usr/bin/env python3
"""JSON Minifier: strip whitespace from JSON and show how many bytes you saved."""

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


def minify(data, sort_keys=False, ascii_only=False):
    """Dump JSON with the tightest separators possible."""
    return json.dumps(data, separators=(",", ":"), sort_keys=sort_keys, ensure_ascii=ascii_only)


def main():
    p = argparse.ArgumentParser(description="Minify JSON and report the size savings.")
    p.add_argument("file", nargs="?", help="JSON file to minify (or use --text / stdin)")
    p.add_argument("-t", "--text", help="JSON string to minify")
    p.add_argument("-s", "--sort-keys", action="store_true", help="sort object keys alphabetically")
    p.add_argument("-a", "--ascii", action="store_true", help="escape non-ASCII characters")
    p.add_argument("-o", "--output", help="write the result to this file")
    p.add_argument("-q", "--quiet", action="store_true", help="don't print the size summary")
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

    out = minify(data, args.sort_keys, args.ascii)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"Saved to {args.output}")
    else:
        print(out)

    if not args.quiet:
        before = len(raw.encode("utf-8"))
        after = len(out.encode("utf-8"))
        saved = before - after
        pct = (saved / before * 100) if before else 0
        print(f"{before} -> {after} bytes (saved {saved}, {pct:.1f}%)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
