#!/usr/bin/env python3
"""Day 32 - Text File Search Tool.

A tiny grep-like search for text files: find a word, phrase or regex across a
file or a whole folder, with line numbers, context lines and colored matches.
Standard library only.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".mypy_cache"}
RED, CYAN, GREEN, DIM, RESET = "\033[31;1m", "\033[36m", "\033[32m", "\033[2m", "\033[0m"


def build_pattern(args: argparse.Namespace) -> re.Pattern:
    text = args.pattern if args.regex else re.escape(args.pattern)
    if args.word:
        text = rf"\b{text}\b"
    flags = re.IGNORECASE if args.ignore_case else 0
    try:
        return re.compile(text, flags)
    except re.error as exc:
        sys.exit(f"Invalid regex: {exc}")


def looks_binary(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return b"\0" in fh.read(2048)
    except OSError:
        return True


def iter_files(paths: list[str], include: list[str], exclude: list[str], hidden: bool, max_mb: float):
    limit = max_mb * 1024 * 1024
    for raw in paths:
        root = Path(raw)
        if root.is_file():
            candidates = [root]
        elif root.is_dir():
            candidates = []
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = sorted(
                    d for d in dirnames if d not in SKIP_DIRS and (hidden or not d.startswith("."))
                )
                for name in sorted(filenames):
                    if hidden or not name.startswith("."):
                        candidates.append(Path(dirpath) / name)
        else:
            print(f"warning: {raw} not found", file=sys.stderr)
            continue
        for path in candidates:
            if include and not any(fnmatch.fnmatch(path.name, g) for g in include):
                continue
            if any(fnmatch.fnmatch(path.name, g) for g in exclude):
                continue
            try:
                if path.stat().st_size > limit:
                    continue
            except OSError:
                continue
            if not looks_binary(path):
                yield path


def highlight(line: str, pattern: re.Pattern, color: bool) -> str:
    return pattern.sub(lambda m: f"{RED}{m.group(0)}{RESET}", line) if color else line


def search_file(path: Path, pattern: re.Pattern, args: argparse.Namespace, color: bool) -> int:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
        return 0

    hits = [i for i, line in enumerate(lines) if bool(pattern.search(line)) != args.invert]
    if args.max_count:
        hits = hits[: args.max_count]
    if not hits:
        return 0

    name = f"{GREEN}{path}{RESET}" if color else str(path)
    if args.files_only:
        print(name)
        return len(hits)
    if args.count:
        print(f"{name}: {len(hits)}")
        return len(hits)

    print(name)
    ctx = args.context
    shown: set[int] = set()
    last = -2
    for i in hits:
        for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
            if j in shown:
                continue
            if ctx and last >= 0 and j > last + 1:
                print(f"  {DIM}--{RESET}" if color else "  --")
            num = f"{j + 1:>5}"
            if j == i or (j in hits and not args.invert):
                body = highlight(lines[j], pattern, color and not args.invert)
                print(f"  {CYAN}{num}{RESET}: {body}" if color else f"  {num}: {body}")
            else:
                print(f"  {DIM}{num}- {lines[j]}{RESET}" if color else f"  {num}- {lines[j]}")
            shown.add(j)
            last = j
    print()
    return len(hits)


def main() -> None:
    p = argparse.ArgumentParser(description="Search text files for a word, phrase or regex.")
    p.add_argument("pattern", help="text (or regex with -r) to find")
    p.add_argument("paths", nargs="*", default=["."], help="files or folders (default: current folder)")
    p.add_argument("-i", "--ignore-case", action="store_true", help="case-insensitive match")
    p.add_argument("-r", "--regex", action="store_true", help="treat pattern as a regular expression")
    p.add_argument("-w", "--word", action="store_true", help="match whole words only")
    p.add_argument("-v", "--invert", action="store_true", help="show lines that do NOT match")
    p.add_argument("-C", "--context", type=int, default=0, metavar="N", help="show N lines around each hit")
    p.add_argument("-c", "--count", action="store_true", help="only print match counts per file")
    p.add_argument("-l", "--files-only", action="store_true", help="only print names of matching files")
    p.add_argument("-m", "--max-count", type=int, default=0, metavar="N", help="stop after N hits per file")
    p.add_argument("--include", action="append", default=[], metavar="GLOB", help="only files like *.py (repeatable)")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="skip files like *.log (repeatable)")
    p.add_argument("--hidden", action="store_true", help="also search hidden files and folders")
    p.add_argument("--max-size", type=float, default=10, metavar="MB", help="skip files bigger than this (default 10)")
    p.add_argument("--no-color", action="store_true", help="disable colored output")
    args = p.parse_args()

    color = sys.stdout.isatty() and not args.no_color and not os.environ.get("NO_COLOR")
    pattern = build_pattern(args)

    files_searched = files_matched = total = 0
    for path in iter_files(args.paths, args.include, args.exclude, args.hidden, args.max_size):
        files_searched += 1
        n = search_file(path, pattern, args, color)
        if n:
            files_matched += 1
            total += n

    if not args.files_only:
        summary = f"{total} matching line(s) in {files_matched} of {files_searched} file(s) searched"
        print(f"{DIM}{summary}{RESET}" if color else summary)
    sys.exit(0 if total else 1)


if __name__ == "__main__":
    main()
