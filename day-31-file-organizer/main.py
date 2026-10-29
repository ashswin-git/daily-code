#!/usr/bin/env python3
"""Day 31 - File Organizer.

Sort the files in a folder into subfolders by type, extension, or modified date.
Preview by default; --apply moves files; --undo reverts the last batch.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

UNDO_FILE = ".organizer_undo.json"

CATEGORIES = {
    "Images": {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "heic", "tiff", "ico"},
    "Videos": {"mp4", "mkv", "mov", "avi", "webm", "flv", "wmv", "m4v"},
    "Audio": {"mp3", "wav", "flac", "aac", "ogg", "m4a", "opus"},
    "Documents": {"pdf", "doc", "docx", "txt", "rtf", "odt", "md", "epub"},
    "Spreadsheets": {"xls", "xlsx", "csv", "ods", "tsv"},
    "Presentations": {"ppt", "pptx", "odp", "key"},
    "Archives": {"zip", "rar", "7z", "tar", "gz", "bz2", "xz", "tgz"},
    "Code": {"py", "js", "ts", "html", "css", "java", "c", "cpp", "h", "go", "rs",
             "rb", "php", "sh", "json", "yaml", "yml", "xml", "sql", "ipynb"},
    "Executables": {"exe", "msi", "apk", "deb", "rpm", "dmg", "appimage"},
    "Fonts": {"ttf", "otf", "woff", "woff2"},
}
EXT_TO_CAT = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}


def ext_of(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def target_folder(path: Path, mode: str, other: str) -> str:
    ext = ext_of(path)
    if mode == "type":
        return EXT_TO_CAT.get(ext, other)
    if mode == "ext":
        return ext.upper() if ext else "NO_EXT"
    stamp = datetime.fromtimestamp(path.stat().st_mtime)
    if mode == "year":
        return stamp.strftime("%Y")
    return stamp.strftime("%Y-%m")  # month


def unique_dest(dest: Path, taken: set[Path]) -> Path:
    """Return a free destination, adding ' (1)', ' (2)' ... if needed."""
    if not dest.exists() and dest not in taken:
        return dest
    n = 1
    while True:
        cand = dest.with_name(f"{dest.stem} ({n}){dest.suffix}")
        if not cand.exists() and cand not in taken:
            return cand
        n += 1


def plan_moves(folder: Path, args) -> list[tuple[Path, Path]]:
    skip_names = {UNDO_FILE}
    only = {e.lower().lstrip(".") for e in (args.only or [])}
    moves: list[tuple[Path, Path]] = []
    taken: set[Path] = set()
    for item in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_file() or item.is_symlink() or item.name in skip_names:
            continue
        if not args.hidden and item.name.startswith("."):
            continue
        if only and ext_of(item) not in only:
            continue
        sub = target_folder(item, args.by, args.other)
        dest = unique_dest(folder / sub / item.name, taken)
        taken.add(dest)
        moves.append((item, dest))
    return moves


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def show_plan(folder: Path, moves: list[tuple[Path, Path]]) -> None:
    groups: dict[str, list[tuple[Path, Path]]] = {}
    for src, dest in moves:
        groups.setdefault(dest.parent.name, []).append((src, dest))
    for name in sorted(groups):
        items = groups[name]
        size = sum(s.stat().st_size for s, _ in items)
        print(f"\n{name}/  ({len(items)} files, {human(size)})")
        for src, dest in items:
            note = f"  -> {dest.name}" if dest.name != src.name else ""
            print(f"  {src.name}{note}")


def apply_moves(folder: Path, moves: list[tuple[Path, Path]]) -> int:
    done = []
    for src, dest in moves:
        dest.parent.mkdir(exist_ok=True)
        shutil.move(str(src), str(dest))
        done.append([str(src.relative_to(folder)), str(dest.relative_to(folder))])
    (folder / UNDO_FILE).write_text(json.dumps(done, indent=2))
    return len(done)


def undo(folder: Path) -> int:
    log = folder / UNDO_FILE
    if not log.exists():
        print("Nothing to undo.")
        return 0
    entries = json.loads(log.read_text())
    restored = 0
    for src_rel, dest_rel in reversed(entries):
        src, dest = folder / src_rel, folder / dest_rel
        if dest.exists() and not src.exists():
            shutil.move(str(dest), str(src))
            restored += 1
            try:
                dest.parent.rmdir()  # only removes it if now empty
            except OSError:
                pass
        else:
            print(f"  skipped {dest_rel} (missing, or original name is taken)")
    log.unlink()
    print(f"Restored {restored} of {len(entries)} files.")
    return restored


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Organize files in a folder into subfolders (preview by default).")
    p.add_argument("folder", nargs="?", default=".", help="folder to organize (default: .)")
    p.add_argument("-b", "--by", choices=["type", "ext", "month", "year"], default="type",
                   help="how to group files (default: type)")
    p.add_argument("-o", "--only", action="append", metavar="EXT",
                   help="only move files with this extension (repeatable)")
    p.add_argument("--other", default="Others", help="folder for unknown types (default: Others)")
    p.add_argument("--hidden", action="store_true", help="include hidden files")
    p.add_argument("--apply", action="store_true", help="actually move the files")
    p.add_argument("--undo", action="store_true", help="revert the last applied batch")
    p.add_argument("--list-types", action="store_true", help="show the type categories and exit")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.list_types:
        for cat, exts in CATEGORIES.items():
            print(f"{cat:14} {', '.join(sorted(exts))}")
        return 0
    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1
    if args.undo:
        undo(folder)
        return 0
    moves = plan_moves(folder, args)
    if not moves:
        print("No files to organize.")
        return 0
    show_plan(folder, moves)
    if args.apply:
        count = apply_moves(folder, moves)
        print(f"\nMoved {count} files. Run with --undo to revert.")
    else:
        print(f"\nPreview only: {len(moves)} files would move. Add --apply to do it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
