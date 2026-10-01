#!/usr/bin/env python3
"""Day 3 — QR Code Generator (CLI)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import segno
except ImportError:  # pragma: no cover
    print(
        "Missing dependency: segno\n"
        "Install with: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate QR codes from text or URLs (terminal, SVG, or PNG).",
    )
    parser.add_argument(
        "data",
        nargs="?",
        help="Text or URL to encode. Omit to read from --file or stdin.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Read payload from a text file instead of the data argument.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path (.svg, .png, .eps, .pdf, or .txt for ASCII art).",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=8,
        help="Module scale for raster/SVG export (default: 8).",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=2,
        help="Quiet-zone border modules (default: 2).",
    )
    parser.add_argument(
        "--error",
        choices=["L", "M", "Q", "H"],
        default="M",
        help="Error-correction level (default: M).",
    )
    parser.add_argument(
        "--dark",
        default="black",
        help="Dark module color for SVG/PNG (default: black).",
    )
    parser.add_argument(
        "--light",
        default="white",
        help="Light module color for SVG/PNG (default: white).",
    )
    parser.add_argument(
        "--no-terminal",
        action="store_true",
        help="Do not print an ASCII QR code to the terminal.",
    )
    return parser.parse_args(argv)


def load_payload(args: argparse.Namespace) -> str:
    if args.file is not None:
        text = args.file.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"File is empty: {args.file}")
        return text

    if args.data is not None:
        text = args.data.strip()
        if not text:
            raise ValueError("Data argument is empty.")
        return text

    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if not text:
            raise ValueError("Stdin is empty.")
        return text

    raise ValueError("Provide data, --file, or pipe text on stdin.")


def save_output(qr: segno.QRCode, path: Path, args: argparse.Namespace) -> None:
    suffix = path.suffix.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".txt":
        with path.open("w", encoding="utf-8") as handle:
            qr.terminal(out=handle, border=args.border, compact=True)
            handle.write("\n")
        return

    if suffix == ".svg":
        qr.save(
            str(path),
            kind="svg",
            scale=args.scale,
            border=args.border,
            dark=args.dark,
            light=args.light,
        )
        return

    if suffix in {".png", ".eps", ".pdf"}:
        kind = suffix.lstrip(".")
        qr.save(
            str(path),
            kind=kind,
            scale=args.scale,
            border=args.border,
            dark=args.dark,
            light=args.light,
        )
        return

    raise ValueError(
        f"Unsupported output type '{suffix}'. Use .svg, .png, .eps, .pdf, or .txt."
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.scale < 1:
        print("Error: --scale must be at least 1.", file=sys.stderr)
        return 1
    if args.border < 0:
        print("Error: --border cannot be negative.", file=sys.stderr)
        return 1

    try:
        payload = load_payload(args)
        qr = segno.make(payload, error=args.error)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # segno may raise for oversized payloads
        print(f"Error: could not build QR code ({exc})", file=sys.stderr)
        return 1

    if args.output is not None:
        try:
            save_output(qr, args.output, args)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"Error: failed to write {args.output} ({exc})", file=sys.stderr)
            return 1
        print(f"Saved: {args.output.resolve()}")

    if not args.no_terminal:
        # Compact ASCII art works in most terminals without color support.
        qr.terminal(border=args.border, compact=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
