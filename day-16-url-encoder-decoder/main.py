#!/usr/bin/env python3
"""URL Encoder/Decoder: percent-encode or decode text, and break URLs into parts."""

import argparse
import sys
from urllib.parse import parse_qsl, quote, quote_plus, unquote, unquote_plus, urlsplit


def read_input(args):
    """Return text from --text, a file, or stdin."""
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            return fh.read().rstrip("\n")
    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")
    return None


def encode(text, plus=False, safe=""):
    """Percent-encode text. With plus=True, spaces become '+' (form style)."""
    return quote_plus(text, safe=safe) if plus else quote(text, safe=safe)


def decode(text, plus=False, rounds=1):
    """Decode percent-escapes, repeating for double-encoded input."""
    fn = unquote_plus if plus else unquote
    for _ in range(max(1, rounds)):
        new = fn(text)
        if new == text:
            break
        text = new
    return text


def inspect(url):
    """Split a URL into its parts and decoded query parameters."""
    parts = urlsplit(url)
    lines = [
        f"scheme:   {parts.scheme or '-'}",
        f"host:     {parts.hostname or '-'}",
        f"port:     {parts.port or '-'}",
        f"path:     {unquote(parts.path) or '-'}",
        f"fragment: {unquote(parts.fragment) or '-'}",
    ]
    params = parse_qsl(parts.query, keep_blank_values=True)
    lines.append(f"query:    {len(params)} param(s)")
    width = max((len(k) for k, _ in params), default=0)
    lines += [f"  {k.ljust(width)} = {v}" for k, v in params]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Percent-encode, decode, or inspect URLs.")
    p.add_argument("mode", choices=["encode", "decode", "inspect", "e", "d", "i"],
                   help="encode, decode, or inspect (e / d / i)")
    p.add_argument("file", nargs="?", help="input file (or use --text / stdin)")
    p.add_argument("-t", "--text", help="text or URL to process")
    p.add_argument("-p", "--plus", action="store_true", help="form style: spaces as '+'")
    p.add_argument("-s", "--safe", default="", help="characters to leave unencoded (e.g. '/:')")
    p.add_argument("-r", "--rounds", type=int, default=1,
                   help="decode up to N times for double-encoded text")
    args = p.parse_args()

    text = read_input(args)
    if text is None:
        p.print_help()
        return 1

    if args.mode in ("encode", "e"):
        out = encode(text, args.plus, args.safe)
    elif args.mode in ("decode", "d"):
        out = decode(text, args.plus, args.rounds)
    else:
        out = inspect(text.strip())
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
