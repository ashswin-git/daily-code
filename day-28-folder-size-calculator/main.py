#!/usr/bin/env python3
"""Day 28 - Folder Size Calculator.

Show how much space a folder uses, broken down by its subfolders (like a tiny
`du`), plus the biggest files and the file types eating the most space.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

DECIMAL = ["B", "KB", "MB", "GB", "TB", "PB"]
BINARY = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]


def human(n: int, binary: bool = False) -> str:
    base = 1024 if binary else 1000
    units = BINARY if binary else DECIMAL
    size = float(n)
    for unit in units:
        if size < base or unit == units[-1]:
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= base
    return f"{n} B"


def scan(root: Path, include_hidden: bool, follow_links: bool):
    """Walk root once. Return per-entry sizes, file list and totals."""
    top: Counter[str] = Counter()     # immediate child name -> bytes
    top_files: Counter[str] = Counter()
    exts: Counter[str] = Counter()
    files: list[tuple[int, str]] = []
    errors = 0
    n_files = n_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_links,
                                                onerror=lambda e: None):
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            filenames = [f for f in filenames if not f.startswith(".")]
        n_dirs += len(dirnames)
        rel = Path(dirpath).relative_to(root)
        child = rel.parts[0] if rel.parts else None
        for name in filenames:
            path = Path(dirpath) / name
            try:
                if path.is_symlink() and not follow_links:
                    continue
                size = path.stat().st_size
            except OSError:
                errors += 1
                continue
            n_files += 1
            key = child if child else name
            top[key] += size
            top_files[key] += 1
            ext = path.suffix.lower() or "(none)"
            exts[ext] += size
            files.append((size, str(path.relative_to(root))))
    return {
        "top": top, "top_files": top_files, "exts": exts, "files": files,
        "total": sum(top.values()), "n_files": n_files, "n_dirs": n_dirs,
        "errors": errors,
    }


def bar(share: float, width: int = 20) -> str:
    filled = round(share * width)
    return "#" * filled + "." * (width - filled)


def report(root: Path, data: dict, args) -> None:
    total = data["total"] or 1
    print(f"\n  {root.resolve()}")
    print(f"  Total: {human(data['total'], args.binary)}  "
          f"({data['total']:,} bytes) in {data['n_files']:,} files, "
          f"{data['n_dirs']:,} folders\n")

    print("  Contents (largest first)")
    for name, size in data["top"].most_common(args.top):
        is_dir = (root / name).is_dir()
        label = name + ("/" if is_dir else "")
        print(f"  {bar(size / total)} {size / total:6.1%}  "
              f"{human(size, args.binary):>11}  {label}")

    if args.files:
        print("\n  Biggest files")
        for size, path in sorted(data["files"], reverse=True)[:args.files]:
            print(f"  {human(size, args.binary):>11}  {path}")

    if args.types:
        print("\n  Space by file type")
        for ext, size in data["exts"].most_common(args.types):
            print(f"  {ext:>10}  {human(size, args.binary):>11}  "
                  f"{size / total:6.1%}")

    if data["errors"]:
        print(f"\n  Skipped {data['errors']} unreadable file(s).")
    print()


def to_json(root: Path, data: dict, args) -> str:
    return json.dumps({
        "path": str(root.resolve()),
        "total_bytes": data["total"],
        "total_human": human(data["total"], args.binary),
        "files": data["n_files"],
        "folders": data["n_dirs"],
        "contents": [{"name": n, "bytes": s, "files": data["top_files"][n]}
                     for n, s in data["top"].most_common(args.top)],
        "biggest_files": [{"path": p, "bytes": s} for s, p in
                          sorted(data["files"], reverse=True)[:args.files]],
        "types": [{"ext": e, "bytes": s}
                  for e, s in data["exts"].most_common(args.types)],
    }, indent=2)


def main() -> int:
    p = argparse.ArgumentParser(description="Show how much space a folder uses.")
    p.add_argument("path", nargs="*", default=["."], help="folder(s) to scan (default: .)")
    p.add_argument("-n", "--top", type=int, default=15, help="rows in the contents list (default 15)")
    p.add_argument("-f", "--files", type=int, default=5, help="show N biggest files (0 to hide)")
    p.add_argument("-t", "--types", type=int, default=5, help="show N biggest file types (0 to hide)")
    p.add_argument("-b", "--binary", action="store_true", help="use KiB/MiB/GiB units")
    p.add_argument("-a", "--all", action="store_true", help="include hidden files and folders")
    p.add_argument("-L", "--follow-links", action="store_true", help="follow symlinks")
    p.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = p.parse_args()

    status = 0
    for raw in args.path:
        root = Path(raw).expanduser()
        if not root.is_dir():
            print(f"error: not a folder: {raw}", file=sys.stderr)
            status = 1
            continue
        data = scan(root, args.all, args.follow_links)
        print(to_json(root, data, args) if args.json else "", end="")
        if args.json:
            print()
        else:
            report(root, data, args)
    return status


if __name__ == "__main__":
    sys.exit(main())
