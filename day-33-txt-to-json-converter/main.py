#!/usr/bin/env python3
"""Day 33: TXT to JSON Converter.

Turn plain text files into JSON in a few handy shapes:
  lines     -> ["line 1", "line 2", ...]
  kv        -> {"key": "value", ...}   from "key: value" or "key=value" lines
  table     -> [{"col": "val", ...}]    from delimited lines with a header row
  paragraphs-> ["para 1", "para 2"]     split on blank lines
  auto      -> guesses the best mode from the content

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KV_RE = re.compile(r"^\s*([^:=#][^:=]*?)\s*[:=]\s*(.*?)\s*$")
DELIMS = ["\t", ",", "|", ";"]


def coerce(value: str):
    """Turn '42', '3.5', 'true', 'null' into real JSON types."""
    v = value.strip()
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "none", ""):
        return None
    if re.fullmatch(r"-?\d+", v) and not (len(v) > 1 and v.lstrip("-").startswith("0")):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+([eE][-+]?\d+)?", v):
        return float(v)
    return v


def clean_lines(text: str, keep_blank: bool, comment: str | None) -> list[str]:
    out = []
    for line in text.splitlines():
        line = line.rstrip()
        if comment and line.lstrip().startswith(comment):
            continue
        if not line.strip() and not keep_blank:
            continue
        out.append(line)
    return out


def to_lines(text, args):
    lines = clean_lines(text, args.keep_blank, args.comment)
    if args.strip:
        lines = [l.strip() for l in lines]
    if args.numbered:
        return [{"line": i, "text": l} for i, l in enumerate(lines, 1)]
    return lines


def to_kv(text, args):
    data, bad = {}, []
    for i, line in enumerate(clean_lines(text, False, args.comment), 1):
        m = KV_RE.match(line)
        if not m:
            bad.append(i)
            continue
        key, val = m.group(1).strip(), m.group(2)
        val = coerce(val) if args.types else val
        if key in data:  # repeated key -> list
            if not isinstance(data[key], list):
                data[key] = [data[key]]
            data[key].append(val)
        else:
            data[key] = val
    if bad and not args.quiet:
        print(f"warning: skipped {len(bad)} line(s) without key/value: {bad[:10]}", file=sys.stderr)
    return data


def detect_delim(lines: list[str]) -> str | None:
    sample = lines[:20]
    for d in DELIMS:
        counts = {l.count(d) for l in sample}
        if len(counts) == 1 and counts.pop() > 0:
            return d
    if sample and all(len(l.split()) == len(sample[0].split()) > 1 for l in sample):
        return "whitespace"
    return None


def split_row(line: str, delim: str) -> list[str]:
    parts = line.split() if delim == "whitespace" else line.split(delim)
    return [p.strip() for p in parts]


def to_table(text, args):
    lines = clean_lines(text, False, args.comment)
    if not lines:
        return []
    delim = args.delimiter or detect_delim(lines)
    if delim is None:
        sys.exit("error: could not detect a delimiter, pass one with -d")
    if delim == "\\t":
        delim = "\t"
    header = split_row(lines[0], delim)
    rows = []
    for line in lines[1:]:
        cells = split_row(line, delim)
        cells += [""] * (len(header) - len(cells))
        row = {}
        for h, c in zip(header, cells):
            row[h] = coerce(c) if args.types else c
        rows.append(row)
    return rows


def to_paragraphs(text, args):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [" ".join(p.split()) for p in paras] if args.join else paras


def guess_mode(text: str) -> str:
    lines = clean_lines(text, False, "#")
    if not lines:
        return "lines"
    kv_hits = sum(1 for l in lines if KV_RE.match(l))
    if kv_hits / len(lines) >= 0.8:
        return "kv"
    if len(lines) >= 2 and detect_delim(lines) not in (None, "whitespace"):
        return "table"
    if re.search(r"\n\s*\n", text.strip()):
        return "paragraphs"
    return "lines"


MODES = {"lines": to_lines, "kv": to_kv, "table": to_table, "paragraphs": to_paragraphs}


def main() -> int:
    p = argparse.ArgumentParser(description="Convert plain text files to JSON.")
    p.add_argument("input", nargs="?", default="-", help="text file (default: stdin)")
    p.add_argument("-o", "--output", help="write JSON here (default: stdout)")
    p.add_argument("-m", "--mode", choices=["auto", *MODES], default="auto")
    p.add_argument("-d", "--delimiter", help="table delimiter (default: auto-detect)")
    p.add_argument("-t", "--types", action="store_true", help="convert numbers/booleans/null")
    p.add_argument("-n", "--numbered", action="store_true", help="lines mode: include line numbers")
    p.add_argument("--keep-blank", action="store_true", help="lines mode: keep empty lines")
    p.add_argument("--strip", action="store_true", help="lines mode: trim each line")
    p.add_argument("--join", action="store_true", help="paragraphs mode: join wrapped lines")
    p.add_argument("--comment", default="#", help="skip lines starting with this ('' to disable)")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (0 = compact)")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args()
    args.comment = args.comment or None

    try:
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    mode = guess_mode(text) if args.mode == "auto" else args.mode
    data = MODES[mode](text, args)
    out = json.dumps(data, indent=args.indent or None, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        if not args.quiet:
            n = len(data)
            print(f"[{mode}] wrote {n} item(s) to {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
