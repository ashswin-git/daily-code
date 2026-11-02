#!/usr/bin/env python3
"""Day 35 - JSON to CSV Converter.

Turn JSON (a list of objects, a list of arrays, a single object, an object
keyed by id, or JSON Lines) into a clean CSV file. Nested objects are
flattened into dotted columns like ``address.city``. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from typing import Any, Iterable


def load_json(text: str, jsonl: bool | None) -> Any:
    """Parse JSON or JSON Lines. Auto-detects JSON Lines when jsonl is None."""
    text = text.lstrip("\ufeff").strip()
    if not text:
        raise ValueError("input is empty")
    if jsonl is not True:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if jsonl is False:
                raise
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {n}: invalid JSON ({exc.msg})") from None
    return rows


def to_rows(data: Any, path: str | None, key_name: str | None) -> list:
    """Normalise parsed JSON into a list of rows."""
    if path:
        for part in path.split("."):
            if isinstance(data, list) and part.isdigit():
                data = data[int(part)]
            elif isinstance(data, dict) and part in data:
                data = data[part]
            else:
                raise ValueError(f"path '{path}' not found (stopped at '{part}')")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        values = list(data.values())
        # {"1": {...}, "2": {...}} -> one row per key
        if key_name and values and all(isinstance(v, dict) for v in values):
            return [{key_name: k, **v} for k, v in data.items()]
        if values and all(isinstance(v, dict) for v in values) and len(values) > 1:
            return [{"key": k, **v} for k, v in data.items()]
        return [data]
    return [{"value": data}]


def flatten(obj: Any, sep: str, prefix: str = "", out: dict | None = None) -> dict:
    """Flatten nested dicts into dotted keys. Lists become JSON strings."""
    out = {} if out is None else out
    if isinstance(obj, dict):
        if not obj and prefix:
            out[prefix] = ""
        for k, v in obj.items():
            key = f"{prefix}{sep}{k}" if prefix else str(k)
            flatten(v, sep, key, out)
    else:
        out[prefix or "value"] = obj
    return out


def cell(value: Any, list_mode: str) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        if list_mode == "join" and all(not isinstance(v, (dict, list)) for v in value):
            return "; ".join("" if v is None else str(v) for v in value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def build_table(rows: list, sep: str, flat: bool, columns: list[str] | None,
                list_mode: str) -> tuple[list[str], list[list[str]]]:
    if rows and all(isinstance(r, list) for r in rows):
        # list of arrays: first row is the header
        header = [str(h) for h in rows[0]]
        body = [[cell(v, list_mode) for v in r] for r in rows[1:]]
        return header, body
    dicts = []
    for r in rows:
        if not isinstance(r, dict):
            r = {"value": r}
        dicts.append(flatten(r, sep) if flat else r)
    header: list[str] = []
    seen = set()
    for d in dicts:  # keep first-seen column order across all rows
        for k in d:
            if k not in seen:
                seen.add(k)
                header.append(k)
    if columns:
        missing = [c for c in columns if c not in seen]
        if missing:
            raise ValueError(f"unknown column(s): {', '.join(missing)}")
        header = columns
    body = [[cell(d.get(k), list_mode) for k in header] for d in dicts]
    return header, body


def write_csv(header: Iterable[str], body: list[list[str]], delimiter: str,
              no_header: bool, out) -> None:
    writer = csv.writer(out, delimiter=delimiter, lineterminator="\n")
    if not no_header:
        writer.writerow(header)
    writer.writerows(body)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert JSON / JSON Lines to CSV.")
    p.add_argument("input", nargs="?", help="JSON file (default: stdin)")
    p.add_argument("-o", "--output", help="write CSV to this file (default: stdout)")
    p.add_argument("-d", "--delimiter", default=",",
                   help="output delimiter: ',', ';', 'tab' or '|' (default ',')")
    p.add_argument("-c", "--columns", help="comma-separated columns to keep, in order")
    p.add_argument("-p", "--path", help="dotted path to the array, e.g. data.items")
    p.add_argument("-k", "--key-name", help="column name for keys when input is an object of objects")
    p.add_argument("--sep", default=".", help="separator for flattened keys (default '.')")
    p.add_argument("--no-flatten", action="store_true", help="keep nested objects as JSON text")
    p.add_argument("--lists", choices=["json", "join"], default="json",
                   help="how to write lists: JSON text or '; '-joined (default json)")
    p.add_argument("--no-header", action="store_true", help="omit the header row")
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--jsonl", action="store_true", help="force JSON Lines input")
    fmt.add_argument("--json", action="store_true", help="force regular JSON input")
    p.add_argument("--excel", action="store_true", help="add a UTF-8 BOM so Excel opens it cleanly")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    delim = {"tab": "\t", "\\t": "\t"}.get(args.delimiter, args.delimiter)
    if len(delim) != 1:
        print("error: delimiter must be a single character or 'tab'", file=sys.stderr)
        return 2
    try:
        if args.input:
            with open(args.input, encoding="utf-8-sig") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
        jsonl = True if args.jsonl else False if args.json else None
        data = load_json(text, jsonl)
        rows = to_rows(data, args.path, args.key_name)
        cols = [c.strip() for c in args.columns.split(",")] if args.columns else None
        header, body = build_table(rows, args.sep, not args.no_flatten, cols, args.lists)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    buf = io.StringIO()
    write_csv(header, body, delim, args.no_header, buf)
    if args.output:
        enc = "utf-8-sig" if args.excel else "utf-8"
        with open(args.output, "w", encoding=enc, newline="") as f:
            f.write(buf.getvalue())
        print(f"Wrote {len(body)} row(s), {len(header)} column(s) to {args.output}",
              file=sys.stderr)
    else:
        sys.stdout.write(buf.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main())
