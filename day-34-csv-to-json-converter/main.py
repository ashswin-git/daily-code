#!/usr/bin/env python3
"""Day 34 - CSV to JSON Converter.

Convert CSV files (or stdin) into JSON: a list of objects, a list of
arrays, an object keyed by a column, or JSON Lines. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path


def convert_value(text: str):
    """Turn '42', '3.5', 'true', 'null', '' into real JSON types."""
    s = text.strip()
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "none", "nan", ""):
        return None
    try:
        if s.lstrip("+-").isdigit() and not (len(s.lstrip("+-")) > 1 and s.lstrip("+-").startswith("0")):
            return int(s)
        return float(s) if any(c.isdigit() for c in s) else s
    except ValueError:
        return s


def detect_dialect(sample: str, delimiter: str | None):
    if delimiter:
        return delimiter
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def set_nested(obj: dict, key: str, value, sep: str) -> None:
    """Expand 'address.city' into {'address': {'city': ...}}."""
    parts = key.split(sep)
    cur = obj
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt
    cur[parts[-1]] = value


def unique_headers(headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for i, h in enumerate(headers):
        name = h.strip() or f"column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        out.append(name)
    return out


def read_rows(text: str, delimiter: str | None):
    sample = text[:4096]
    delim = detect_dialect(sample, delimiter)
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [r for r in reader if any(cell.strip() for cell in r)]
    return rows, delim


def build(rows, args):
    if not rows:
        return [] if args.mode != "keyed" else {}
    if args.no_header:
        width = max(len(r) for r in rows)
        headers = [f"column_{i + 1}" for i in range(width)]
        data = rows
    else:
        headers = unique_headers(rows[0])
        data = rows[1:]

    if args.columns:
        wanted = [c.strip() for c in args.columns.split(",")]
        missing = [c for c in wanted if c not in headers]
        if missing:
            raise SystemExit(f"error: unknown column(s): {', '.join(missing)}")
        idx = [headers.index(c) for c in wanted]
    else:
        idx = list(range(len(headers)))

    def cell(row, i):
        val = row[i] if i < len(row) else ""
        if args.strip:
            val = val.strip()
        return convert_value(val) if args.types else val

    if args.mode == "arrays":
        out = [[headers[i] for i in idx]] if not args.no_header else []
        out += [[cell(r, i) for i in idx] for r in data]
        return out

    records = []
    for r in data:
        rec: dict = {}
        for i in idx:
            if args.nested:
                set_nested(rec, headers[i], cell(r, i), args.nested)
            else:
                rec[headers[i]] = cell(r, i)
        records.append(rec)

    if args.mode == "keyed":
        if not args.key:
            raise SystemExit("error: --mode keyed needs --key COLUMN")
        if args.key not in headers:
            raise SystemExit(f"error: key column '{args.key}' not found")
        keyed = {}
        for rec, r in zip(records, data):
            k = r[headers.index(args.key)].strip() if headers.index(args.key) < len(r) else ""
            rec.pop(args.key, None)
            keyed[k] = rec
        return keyed
    return records


def main() -> int:
    p = argparse.ArgumentParser(description="Convert CSV to JSON.")
    p.add_argument("file", nargs="?", help="CSV file (default: stdin)")
    p.add_argument("-o", "--output", help="write JSON to this file")
    p.add_argument("-m", "--mode", choices=["records", "arrays", "keyed", "jsonl"],
                   default="records", help="output shape (default: records)")
    p.add_argument("-k", "--key", help="column to key by in keyed mode")
    p.add_argument("-d", "--delimiter", help="delimiter (default: auto-detect)")
    p.add_argument("-c", "--columns", help="comma-separated columns to keep")
    p.add_argument("-t", "--types", action="store_true",
                   help="convert numbers, booleans and null to JSON types")
    p.add_argument("--nested", nargs="?", const=".", metavar="SEP",
                   help="expand 'a.b' headers into nested objects (default sep '.')")
    p.add_argument("--no-header", action="store_true", help="first row is data")
    p.add_argument("--strip", action="store_true", help="trim spaces in cells")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (0 = compact)")
    p.add_argument("--encoding", default="utf-8-sig", help="input encoding")
    args = p.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding=args.encoding)
    else:
        if sys.stdin.isatty():
            p.print_help()
            return 1
        text = sys.stdin.read()

    rows, delim = read_rows(text, args.delimiter)
    mode = args.mode
    if mode == "jsonl":
        args.mode = "records"
    result = build(rows, args)

    indent = args.indent if args.indent > 0 else None
    seps = None if indent else (",", ":")
    if mode == "jsonl":
        out = "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in result)
    else:
        out = json.dumps(result, indent=indent, ensure_ascii=False, separators=seps)

    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        count = len(result)
        print(f"Wrote {count} item(s) to {args.output} (delimiter {delim!r})", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
