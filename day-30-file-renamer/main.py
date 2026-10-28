#!/usr/bin/env python3
"""Day 30 - File Renamer.

Bulk-rename files in a folder with find/replace, regex, case changes,
prefix/suffix, numbering and date stamps. Shows a preview first (dry run)
and only renames with --apply. Every applied batch is logged so it can be
undone with --undo. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

UNDO_FILE = ".renamer-undo.json"


def change_case(stem: str, mode: str) -> str:
    words = re.split(r"[\s_\-.]+", stem.strip())
    words = [w for w in words if w]
    if mode == "lower":
        return stem.lower()
    if mode == "upper":
        return stem.upper()
    if mode == "title":
        return " ".join(w.capitalize() for w in words)
    if mode == "snake":
        return "_".join(w.lower() for w in words)
    if mode == "kebab":
        return "-".join(w.lower() for w in words)
    if mode == "camel":
        return words[0].lower() + "".join(w.capitalize() for w in words[1:]) if words else stem
    return stem


def build_name(path: Path, index: int, args: argparse.Namespace) -> str:
    stem, ext = path.stem, path.suffix
    if args.find is not None:
        stem = stem.replace(args.find, args.replace)
    if args.regex is not None:
        stem = re.sub(args.regex, args.replace, stem)
    if args.case:
        stem = change_case(stem, args.case)
    if args.strip:
        stem = stem.strip(" _-.")
    if args.number:
        num = str(args.start + index).zfill(args.pad)
        stem = f"{num}{args.sep}{stem}" if args.number == "prefix" else f"{stem}{args.sep}{num}"
    if args.date:
        stamp = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        stem = f"{stamp}{args.sep}{stem}"
    stem = f"{args.prefix}{stem}{args.suffix}"
    if args.ext is not None:
        ext = "." + args.ext.lstrip(".") if args.ext else ""
    elif args.lower_ext:
        ext = ext.lower()
    return stem + ext


def collect(folder: Path, args: argparse.Namespace) -> list[Path]:
    exts = {"." + e.lower().lstrip(".") for e in args.only} if args.only else None
    files = []
    for p in folder.iterdir():
        if not p.is_file() or p.is_symlink() or p.name == UNDO_FILE:
            continue
        if not args.all and p.name.startswith("."):
            continue
        if exts and p.suffix.lower() not in exts:
            continue
        if args.match and not re.search(args.match, p.name):
            continue
        files.append(p)
    key = {"name": lambda p: p.name.lower(), "mtime": lambda p: p.stat().st_mtime,
           "size": lambda p: p.stat().st_size}[args.sort]
    return sorted(files, key=key)


def plan(files: list[Path], args: argparse.Namespace) -> tuple[list[tuple[Path, Path]], list[str]]:
    moves, problems = [], []
    proposed = {p.name: build_name(p, i, args) for i, p in enumerate(files)}
    # Names that will be freed up because their current file is renamed away.
    leaving = {old for old, new in proposed.items() if new != old}
    targets: set[str] = set()
    for p in files:
        new = proposed[p.name]
        if not new or new in (".", "..") or "/" in new or "\\" in new:
            problems.append(f"{p.name}: invalid new name {new!r}")
            continue
        if new == p.name:
            continue
        if new in targets:
            problems.append(f"{p.name}: would collide with another file named {new!r}")
            continue
        if (p.parent / new).exists() and new not in leaving:
            problems.append(f"{p.name}: {new!r} already exists")
            continue
        targets.add(new)
        moves.append((p, p.parent / new))
    return moves, problems


def apply(moves: list[tuple[Path, Path]], folder: Path) -> None:
    # Two-phase rename so swaps like a->b, b->a never clobber each other.
    temps = []
    for i, (src, dst) in enumerate(moves):
        tmp = src.with_name(f".renamer-tmp-{i}-{src.name}")
        src.rename(tmp)
        temps.append((tmp, dst))
    for tmp, dst in temps:
        tmp.rename(dst)
    log = [{"from": s.name, "to": d.name} for s, d in moves]
    (folder / UNDO_FILE).write_text(json.dumps(log, indent=2), encoding="utf-8")


def undo(folder: Path) -> int:
    log_path = folder / UNDO_FILE
    if not log_path.exists():
        print("  Nothing to undo here.")
        return 1
    log = json.loads(log_path.read_text(encoding="utf-8"))
    moves = [(folder / e["to"], folder / e["from"]) for e in log if (folder / e["to"]).exists()]
    apply(moves, folder)
    log_path.unlink()
    print(f"  Undid {len(moves)} rename(s).")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Bulk file renamer with preview and undo.")
    ap.add_argument("folder", nargs="?", default=".", help="folder to work in (default: .)")
    g = ap.add_argument_group("what to change")
    g.add_argument("-f", "--find", help="plain text to find in the name")
    g.add_argument("-x", "--regex", help="regex to find in the name")
    g.add_argument("-r", "--replace", default="", help="replacement for --find/--regex")
    g.add_argument("-c", "--case", choices=["lower", "upper", "title", "snake", "kebab", "camel"])
    g.add_argument("--prefix", default="", help="text to add before the name")
    g.add_argument("--suffix", default="", help="text to add after the name (before extension)")
    g.add_argument("-n", "--number", choices=["prefix", "suffix"], help="add a running number")
    g.add_argument("--start", type=int, default=1, help="first number (default 1)")
    g.add_argument("--pad", type=int, default=3, help="zero-pad numbers to this width (default 3)")
    g.add_argument("--sep", default="_", help="separator for numbers/dates (default _)")
    g.add_argument("-d", "--date", action="store_true", help="prefix the file's modified date")
    g.add_argument("--ext", help="change extension (empty string removes it)")
    g.add_argument("--lower-ext", action="store_true", help="lowercase the extension")
    g.add_argument("--strip", action="store_true", help="trim spaces/_/-/. from the ends")
    s = ap.add_argument_group("which files")
    s.add_argument("-o", "--only", action="append", help="only these extensions (repeatable)")
    s.add_argument("-m", "--match", help="only names matching this regex")
    s.add_argument("-a", "--all", action="store_true", help="include hidden files")
    s.add_argument("-s", "--sort", choices=["name", "mtime", "size"], default="name",
                   help="order used for numbering (default name)")
    ap.add_argument("--apply", action="store_true", help="actually rename (default is preview)")
    ap.add_argument("--undo", action="store_true", help="revert the last applied batch")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        print(f"  Not a folder: {folder}", file=sys.stderr)
        return 2
    if args.undo:
        return undo(folder)
    if args.regex:
        try:
            re.compile(args.regex)
        except re.error as e:
            print(f"  Bad regex: {e}", file=sys.stderr)
            return 2

    files = collect(folder, args)
    moves, problems = plan(files, args)
    print(f"\n  {len(files)} file(s) matched, {len(moves)} to rename\n")
    width = max((len(s.name) for s, _ in moves), default=0)
    for src, dst in moves:
        print(f"  {src.name.ljust(width)}  ->  {dst.name}")
    for p in problems:
        print(f"  ! skipped {p}")
    if not moves:
        print("  Nothing to do.")
        return 0
    if not args.apply:
        print("\n  Preview only. Add --apply to rename.")
        return 0
    apply(moves, folder)
    print(f"\n  Renamed {len(moves)} file(s). Undo with: python3 main.py {args.folder} --undo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
