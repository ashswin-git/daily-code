#!/usr/bin/env python3
"""Day 26 - File Extension Finder.

Scan a folder and see which file extensions it contains: counts, total size,
and a category for each (image, video, code, document...). Or list every file
with a given extension. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

CATEGORIES = {
    "image": "jpg jpeg png gif bmp webp svg ico tiff heic",
    "video": "mp4 mkv mov avi webm flv wmv m4v",
    "audio": "mp3 wav flac aac ogg m4a opus",
    "document": "pdf doc docx odt rtf txt md xls xlsx csv ppt pptx",
    "code": "py js ts jsx tsx java c cpp h hpp cs go rs rb php swift kt sh html css scss sql",
    "data": "json yaml yml xml toml ini cfg env lock",
    "archive": "zip tar gz tgz bz2 xz 7z rar",
    "font": "ttf otf woff woff2",
    "executable": "exe msi dmg apk deb rpm bin appimage",
}
EXT_TO_CAT = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts.split()}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def extension_of(path: Path) -> str:
    """Return the lowercase extension without dot ('' if none). Handles .tar.gz."""
    name = path.name.lower()
    if name.endswith(".tar.gz"):
        return "tar.gz"
    if name.startswith(".") and name.count(".") == 1:
        return ""  # dotfile like .bashrc
    return path.suffix.lower().lstrip(".")


def category_of(ext: str) -> str:
    if not ext:
        return "no extension"
    return EXT_TO_CAT.get(ext.split(".")[-1], "other")


def human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def walk_files(root: Path, recursive: bool, hidden: bool):
    if not recursive:
        for p in root.iterdir():
            if p.is_file() and (hidden or not p.name.startswith(".")):
                yield p
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and (hidden or not d.startswith("."))]
        for f in filenames:
            if hidden or not f.startswith("."):
                yield Path(dirpath) / f


def scan(root: Path, recursive: bool, hidden: bool) -> dict:
    stats = defaultdict(lambda: {"count": 0, "size": 0})
    for p in walk_files(root, recursive, hidden):
        try:
            size = p.stat().st_size
        except OSError:
            continue
        s = stats[extension_of(p)]
        s["count"] += 1
        s["size"] += size
    return stats


def print_summary(stats: dict, sort_by: str, top: int | None) -> None:
    rows = sorted(stats.items(), key=lambda kv: (-kv[1][sort_by], kv[0]))
    if top:
        rows = rows[:top]
    total_files = sum(s["count"] for s in stats.values())
    total_size = sum(s["size"] for s in stats.values())
    print(f"  {'EXTENSION':<12} {'CATEGORY':<13} {'FILES':>6} {'SIZE':>10} {'SHARE':>6}")
    for ext, s in rows:
        share = s["count"] / total_files * 100 if total_files else 0
        label = f".{ext}" if ext else "(none)"
        print(f"  {label:<12} {category_of(ext):<13} {s['count']:>6} "
              f"{human_size(s['size']):>10} {share:>5.1f}%")
    print(f"\n  {total_files} files, {len(stats)} extensions, {human_size(total_size)} total")


def find_ext(root: Path, ext: str, recursive: bool, hidden: bool) -> list[Path]:
    ext = ext.lower().lstrip(".")
    return sorted(p for p in walk_files(root, recursive, hidden) if extension_of(p) == ext)


def main() -> int:
    ap = argparse.ArgumentParser(description="Find and summarize file extensions in a folder.")
    ap.add_argument("folder", nargs="?", default=".", help="folder to scan (default: .)")
    ap.add_argument("-e", "--ext", help="list files with this extension, e.g. py or .jpg")
    ap.add_argument("-n", "--no-recursive", action="store_true", help="only scan the top folder")
    ap.add_argument("-a", "--all", action="store_true", help="include hidden files/folders")
    ap.add_argument("-s", "--sort", choices=("count", "size"), default="count")
    ap.add_argument("-t", "--top", type=int, help="show only the top N extensions")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    root = Path(args.folder).expanduser()
    if not root.is_dir():
        print(f"error: not a folder: {root}", file=sys.stderr)
        return 2
    recursive = not args.no_recursive

    if args.ext:
        files = find_ext(root, args.ext, recursive, args.all)
        if args.json:
            print(json.dumps([str(f) for f in files], indent=2))
        else:
            for f in files:
                print(f"  {f}  ({human_size(f.stat().st_size)})")
            print(f"\n  {len(files)} file(s) with .{args.ext.lower().lstrip('.')}")
        return 0 if files else 1

    stats = scan(root, recursive, args.all)
    if args.json:
        out = {(e or "(none)"): {**s, "category": category_of(e)} for e, s in stats.items()}
        print(json.dumps(out, indent=2, sort_keys=True))
    elif not stats:
        print("  No files found.")
    else:
        print_summary(stats, args.sort, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
