#!/usr/bin/env python3
"""Day 29 - Duplicate File Finder.

Find files with identical content in one or more folders. Fast because it
groups by size first, then compares a quick partial hash, and only then a
full SHA-256 hash. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

CHUNK = 1024 * 1024
PARTIAL = 64 * 1024


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1000
    return f"{n:.2f} TB"


def walk(roots, include_hidden, min_size, exts):
    seen = set()
    for root in roots:
        root = Path(root).expanduser()
        if root.is_file():
            candidates = [(str(root.parent), [], [root.name])]
        else:
            candidates = os.walk(root)
        for dirpath, dirnames, filenames in candidates:
            if not include_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                if not include_hidden and name.startswith("."):
                    continue
                if exts and Path(name).suffix.lower().lstrip(".") not in exts:
                    continue
                path = Path(dirpath) / name
                try:
                    st = path.lstat()
                except OSError:
                    continue
                if not path.is_file() or path.is_symlink():
                    continue
                key = (st.st_dev, st.st_ino)
                if key in seen:  # hard links to the same data are not dupes
                    continue
                seen.add(key)
                if st.st_size >= min_size:
                    yield path, st.st_size


def file_hash(path: Path, limit: int | None = None) -> str | None:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if limit:
                h.update(f.read(limit))
            else:
                for block in iter(lambda: f.read(CHUNK), b""):
                    h.update(block)
    except OSError:
        return None
    return h.hexdigest()


def regroup(groups, keyfn):
    out = []
    for files in groups:
        buckets = defaultdict(list)
        for path, size in files:
            k = keyfn(path, size)
            if k is not None:
                buckets[k].append((path, size))
        out.extend(b for b in buckets.values() if len(b) > 1)
    return out


def find_duplicates(roots, include_hidden=False, min_size=1, exts=None):
    by_size = defaultdict(list)
    scanned = 0
    for path, size in walk(roots, include_hidden, min_size, exts):
        by_size[size].append((path, size))
        scanned += 1
    groups = [g for g in by_size.values() if len(g) > 1]
    groups = regroup(groups, lambda p, s: file_hash(p, PARTIAL))
    # files up to PARTIAL bytes were fully hashed already; hash the rest fully
    final = [g if g[0][1] <= PARTIAL else None for g in groups]
    big = [g for g in groups if g[0][1] > PARTIAL]
    final = [g for g in final if g] + regroup(big, lambda p, s: file_hash(p))
    final.sort(key=lambda g: g[0][1] * (len(g) - 1), reverse=True)
    return scanned, [[(str(p), s) for p, s in sorted(g)] for g in final]


def pick_keeper(group, keep):
    if keep == "newest":
        return max(group, key=lambda x: os.path.getmtime(x[0]))
    if keep == "oldest":
        return min(group, key=lambda x: os.path.getmtime(x[0]))
    if keep == "shortest":
        return min(group, key=lambda x: (len(x[0]), x[0]))
    return group[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Find duplicate files by content.")
    ap.add_argument("paths", nargs="*", default=["."], help="folders to scan (default: .)")
    ap.add_argument("-a", "--all", action="store_true", help="include hidden files/folders")
    ap.add_argument("-m", "--min-size", type=int, default=1, help="ignore files smaller than N bytes (default 1)")
    ap.add_argument("-e", "--ext", action="append", help="only these extensions, e.g. -e jpg -e png")
    ap.add_argument("-k", "--keep", choices=["first", "newest", "oldest", "shortest"], default="first",
                    help="which copy to keep when deleting (default: first alphabetically)")
    ap.add_argument("--delete", action="store_true", help="delete the extra copies (asks first)")
    ap.add_argument("-y", "--yes", action="store_true", help="don't ask before deleting")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)

    for p in args.paths:
        if not Path(p).expanduser().exists():
            print(f"error: {p} does not exist", file=sys.stderr)
            return 2

    exts = {e.lower().lstrip(".") for e in args.ext} if args.ext else None
    scanned, groups = find_duplicates(args.paths, args.all, max(args.min_size, 0), exts)
    wasted = sum(g[0][1] * (len(g) - 1) for g in groups)

    if args.json:
        print(json.dumps({"scanned": scanned, "groups": [
            {"size": g[0][1], "files": [p for p, _ in g]} for g in groups],
            "wasted_bytes": wasted}, indent=2))
        return 0

    print(f"\n  Scanned {scanned:,} files")
    if not groups:
        print("  No duplicates found.\n")
        return 0
    extra = sum(len(g) - 1 for g in groups)
    print(f"  Found {len(groups)} duplicate groups ({extra} extra copies, {human(wasted)} wasted)\n")
    for i, g in enumerate(groups, 1):
        keeper = pick_keeper(g, args.keep)
        print(f"  [{i}] {human(g[0][1])} x {len(g)}")
        for path, _ in g:
            mark = "keep" if (path, _) == keeper else "dupe"
            print(f"      {mark}  {path}")
        print()

    if args.delete:
        victims = [p for g in groups for p, s in g if (p, s) != pick_keeper(g, args.keep)]
        if not args.yes:
            ans = input(f"  Delete {len(victims)} files and free {human(wasted)}? [y/N] ")
            if ans.strip().lower() not in ("y", "yes"):
                print("  Nothing deleted.")
                return 0
        freed = 0
        for p in victims:
            try:
                freed += os.path.getsize(p)
                os.remove(p)
            except OSError as exc:
                print(f"  could not delete {p}: {exc}", file=sys.stderr)
        print(f"  Deleted {len(victims)} files, freed {human(freed)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
