#!/usr/bin/env python3
"""Base64 Encoder/Decoder: encode or decode text and files from the command line."""

import argparse
import base64
import binascii
import sys


def read_input(args):
    """Return raw bytes from --text, a file, or stdin."""
    if args.text is not None:
        return args.text.encode("utf-8")
    if args.file:
        with open(args.file, "rb") as fh:
            return fh.read()
    if not sys.stdin.isatty():
        return sys.stdin.buffer.read()
    return None


def encode(data, url_safe=False, wrap=0):
    """Encode bytes to Base64 text, optionally URL-safe and wrapped."""
    out = (base64.urlsafe_b64encode if url_safe else base64.b64encode)(data).decode("ascii")
    if wrap > 0:
        out = "\n".join(out[i:i + wrap] for i in range(0, len(out), wrap))
    return out


def decode(text, url_safe=False):
    """Decode Base64 text to bytes. Tolerates whitespace and missing padding."""
    cleaned = "".join(text.split())
    if not url_safe and ("-" in cleaned or "_" in cleaned):
        url_safe = True  # auto-detect the URL-safe alphabet
    cleaned += "=" * (-len(cleaned) % 4)
    altchars = b"-_" if url_safe else None
    return base64.b64decode(cleaned, altchars=altchars, validate=True)


def show_bytes(data):
    """Print decoded bytes as text when possible, otherwise as a hex preview."""
    try:
        return data.decode("utf-8"), True
    except UnicodeDecodeError:
        preview = data[:32].hex(" ")
        more = " ..." if len(data) > 32 else ""
        return f"<binary, {len(data)} bytes> {preview}{more}", False


def main():
    p = argparse.ArgumentParser(description="Encode or decode Base64 text and files.")
    p.add_argument("mode", choices=["encode", "decode", "e", "d"], help="encode or decode (e / d)")
    p.add_argument("file", nargs="?", help="input file (or use --text / stdin)")
    p.add_argument("-t", "--text", help="text to encode or decode")
    p.add_argument("-u", "--url-safe", action="store_true", help="use the URL-safe alphabet (- and _)")
    p.add_argument("-w", "--wrap", type=int, default=0, help="wrap encoded output every N chars (e.g. 76)")
    p.add_argument("-o", "--output", help="write the result to this file (raw bytes when decoding)")
    p.add_argument("-q", "--quiet", action="store_true", help="don't print the size summary")
    args = p.parse_args()

    raw = read_input(args)
    if raw is None:
        p.print_help()
        return 1

    if args.mode in ("encode", "e"):
        result = encode(raw, args.url_safe, args.wrap)
        if args.output:
            with open(args.output, "w", encoding="ascii") as fh:
                fh.write(result + "\n")
            print(f"Saved to {args.output}")
        else:
            print(result)
        if not args.quiet:
            print(f"{len(raw)} bytes -> {len(result.replace(chr(10), ''))} Base64 chars", file=sys.stderr)
        return 0

    try:
        data = decode(raw.decode("ascii", errors="strict"), args.url_safe)
    except (binascii.Error, UnicodeDecodeError, ValueError) as err:
        print(f"Invalid Base64: {err}", file=sys.stderr)
        return 2

    if args.output:
        with open(args.output, "wb") as fh:
            fh.write(data)
        print(f"Saved {len(data)} bytes to {args.output}")
    else:
        text, _ = show_bytes(data)
        print(text)
    if not args.quiet:
        print(f"{len(''.join(raw.decode('ascii').split()))} Base64 chars -> {len(data)} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
