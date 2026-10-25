#!/usr/bin/env python3
"""Day 27 - File Size Calculator.

Show the size of one or more files in every common unit, total them up,
estimate download time, or convert a raw size like "1.5GB" to other units.
Standard library only.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

BINARY = [("B", 1), ("KiB", 1024), ("MiB", 1024**2), ("GiB", 1024**3), ("TiB", 1024**4)]
DECIMAL = [("B", 1), ("KB", 1000), ("MB", 1000**2), ("GB", 1000**3), ("TB", 1000**4)]

UNIT_FACTORS = {u.lower(): f for u, f in BINARY + DECIMAL}
UNIT_FACTORS.update({"k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4, "bytes": 1})

SPEED_UNITS = {"kbps": 1000 / 8, "mbps": 1000**2 / 8, "gbps": 1000**3 / 8,
               "kb/s": 1000, "mb/s": 1000**2, "gb/s": 1000**3}


def human(n: float, binary: bool = False) -> str:
    """Format a byte count with the best-fitting unit."""
    units = BINARY if binary else DECIMAL
    for name, factor in reversed(units):
        if n >= factor:
            value = n / factor
            return f"{n:,.0f} B" if factor == 1 else f"{value:,.2f} {name}"
    return "0 B"


def parse_size(text: str) -> int:
    """Turn '1.5GB', '700 MiB' or '2048' into bytes."""
    m = re.fullmatch(r"\s*([\d.]+)\s*([a-zA-Z]*)\s*", text)
    if not m:
        raise ValueError(f"can't read size: {text!r}")
    number, unit = float(m.group(1)), m.group(2).lower() or "b"
    if unit not in UNIT_FACTORS:
        raise ValueError(f"unknown unit {m.group(2)!r} (try B, KB, MB, GB, KiB, MiB...)")
    return int(number * UNIT_FACTORS[unit])


def parse_speed(text: str) -> float:
    """Turn '50Mbps' or '10MB/s' into bytes per second."""
    m = re.fullmatch(r"\s*([\d.]+)\s*([a-zA-Z/]+)\s*", text)
    if not m or m.group(2).lower() not in SPEED_UNITS:
        raise ValueError(f"can't read speed: {text!r} (try 50Mbps or 10MB/s)")
    return float(m.group(1)) * SPEED_UNITS[m.group(2).lower()]


def fmt_time(seconds: float) -> str:
    if seconds < 1:
        return "under 1s"
    h, rem = divmod(int(round(seconds)), 3600)
    mins, s = divmod(rem, 60)
    parts = [f"{h}h" if h else "", f"{mins}m" if mins else "", f"{s}s" if s or not (h or mins) else ""]
    return " ".join(p for p in parts if p)


def all_units(n: int) -> dict:
    return {name: round(n / f, 4) for name, f in DECIMAL + BINARY[1:]}


def collect(patterns: list[str]) -> tuple[list[Path], list[str]]:
    files, missing = [], []
    for pat in patterns:
        matches = [Path(p) for p in glob.glob(pat)] or [Path(pat)]
        for p in matches:
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                missing.append(f"{p} is a folder (this tool sizes files)")
            else:
                missing.append(f"{p} not found")
    return files, missing


def main() -> int:
    ap = argparse.ArgumentParser(description="File size calculator: sizes, totals, unit conversion, download time.")
    ap.add_argument("files", nargs="*", help="files or glob patterns, e.g. *.mp4")
    ap.add_argument("-c", "--convert", metavar="SIZE", help="convert a size like 1.5GB instead of reading files")
    ap.add_argument("-b", "--binary", action="store_true", help="use KiB/MiB (1024) instead of KB/MB (1000)")
    ap.add_argument("-s", "--speed", metavar="SPEED", help="estimate download time, e.g. 50Mbps or 10MB/s")
    ap.add_argument("--sort", action="store_true", help="largest files first")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    try:
        speed = parse_speed(args.speed) if args.speed else None
        if args.convert:
            n = parse_size(args.convert)
            if args.json:
                print(json.dumps({"bytes": n, "units": all_units(n)}, indent=2))
                return 0
            print(f"  {args.convert.strip()} = {n:,} bytes")
            for name, f in DECIMAL[1:] + BINARY[1:]:
                print(f"  {name:>4}  {n / f:,.4f}")
            if speed:
                print(f"\n  Download at {args.speed}: {fmt_time(n / speed)}")
            return 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if not args.files:
        ap.print_help()
        return 1

    files, problems = collect(args.files)
    for msg in problems:
        print(f"warning: {msg}", file=sys.stderr)
    if not files:
        return 1

    rows = [(p, p.stat().st_size) for p in dict.fromkeys(files)]
    if args.sort:
        rows.sort(key=lambda r: r[1], reverse=True)
    total = sum(size for _, size in rows)

    if args.json:
        out = {"files": [{"path": str(p), "bytes": s, "human": human(s, args.binary)} for p, s in rows],
               "total_bytes": total, "total_human": human(total, args.binary)}
        if speed:
            out["download_seconds"] = round(total / speed, 2)
        print(json.dumps(out, indent=2))
        return 0

    width = min(max(len(str(p)) for p, _ in rows), 50)
    print(f"  {'FILE':<{width}}  {'SIZE':>12}  {'BYTES':>14}  SHARE")
    for p, s in rows:
        name = str(p) if len(str(p)) <= width else "..." + str(p)[-(width - 3):]
        share = s / total * 100 if total else 0
        print(f"  {name:<{width}}  {human(s, args.binary):>12}  {s:>14,}  {share:5.1f}%")
    print(f"\n  {len(rows)} file(s), {human(total, args.binary)} total")
    if speed:
        print(f"  Download at {args.speed}: {fmt_time(total / speed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
