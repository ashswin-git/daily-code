#!/usr/bin/env python3
"""Day 10 - Word Counter.

Count words, lines, sentences and characters, estimate reading time,
and show the most frequent words. Reads a file, piped stdin, or
inline text. Standard library only.

Examples:
  python3 main.py notes.txt
  python3 main.py --text "The quick brown fox jumps over the lazy dog"
  cat essay.txt | python3 main.py --top 5 --skip-common
  python3 main.py a.txt b.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019-][A-Za-z0-9]+)*")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")
READ_WPM = 238  # average adult silent reading speed
SPEAK_WPM = 150  # typical speaking pace

STOPWORDS = set(
    """a an and are as at be been but by for from has have he her his i if in
    into is it its me my no not of on or our she so than that the their them
    then there these they this to was we were what when which who will with
    you your""".split()
)


def fmt_minutes(minutes: float) -> str:
    seconds = round(minutes * 60)
    if seconds < 60:
        return f"{seconds} sec"
    m, s = divmod(seconds, 60)
    return f"{m} min {s} sec" if s else f"{m} min"


def analyze(text: str, top: int = 10, skip_common: bool = False) -> dict:
    words = WORD_RE.findall(text)
    lowered = [w.lower() for w in words]
    sentences = [s for s in SENTENCE_RE.findall(text) if WORD_RE.search(s)]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    pool = [w for w in lowered if not (skip_common and w in STOPWORDS)]
    count = len(words)
    return {
        "words": count,
        "unique_words": len(set(lowered)),
        "characters": len(text),
        "characters_no_spaces": len(re.sub(r"\s", "", text)),
        "lines": len(text.splitlines()),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "avg_word_length": round(sum(map(len, words)) / count, 2) if count else 0,
        "longest_word": max(words, key=len) if words else "",
        "reading_time": fmt_minutes(count / READ_WPM),
        "speaking_time": fmt_minutes(count / SPEAK_WPM),
        "top_words": Counter(pool).most_common(top),
    }


def bar(n: int, biggest: int, width: int = 20) -> str:
    return "#" * max(1, round(width * n / biggest)) if biggest else ""


def print_report(name: str, s: dict) -> None:
    print(f"\n  {name}")
    print("  " + "-" * 38)
    rows = [
        ("Words", s["words"]),
        ("Unique words", s["unique_words"]),
        ("Characters", s["characters"]),
        ("Chars (no spaces)", s["characters_no_spaces"]),
        ("Lines", s["lines"]),
        ("Sentences", s["sentences"]),
        ("Paragraphs", s["paragraphs"]),
        ("Avg word length", s["avg_word_length"]),
        ("Longest word", s["longest_word"] or "-"),
        ("Reading time", s["reading_time"]),
        ("Speaking time", s["speaking_time"]),
    ]
    for label, value in rows:
        print(f"  {label:<18} {value}")
    if s["top_words"]:
        print("\n  Top words")
        biggest = s["top_words"][0][1]
        pad = max(len(w) for w, _ in s["top_words"])
        for word, n in s["top_words"]:
            print(f"  {word:<{pad}}  {n:>4}  {bar(n, biggest)}")


def read_sources(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.text is not None:
        return [("inline text", args.text)]
    if args.files:
        out = []
        for f in args.files:
            path = Path(f)
            if not path.is_file():
                sys.exit(f"error: file not found: {f}")
            out.append((str(path), path.read_text(encoding="utf-8", errors="replace")))
        return out
    if not sys.stdin.isatty():
        return [("stdin", sys.stdin.read())]
    print("Type or paste text, then press Ctrl+D (Ctrl+Z then Enter on Windows):")
    return [("typed text", sys.stdin.read())]


def main() -> None:
    p = argparse.ArgumentParser(description="Count words, sentences and more.")
    p.add_argument("files", nargs="*", help="text files to analyze")
    p.add_argument("-t", "--text", help="analyze this text instead of a file")
    p.add_argument("--top", type=int, default=10, help="how many top words (default 10)")
    p.add_argument("--skip-common", action="store_true", help="ignore words like 'the', 'and'")
    p.add_argument("--json", action="store_true", help="print results as JSON")
    args = p.parse_args()

    sources = read_sources(args)
    results = {name: analyze(text, args.top, args.skip_common) for name, text in sources}

    if len(results) > 1:
        total = analyze("\n\n".join(t for _, t in sources), args.top, args.skip_common)
        results["TOTAL"] = total

    if args.json:
        print(json.dumps(results if len(results) > 1 else next(iter(results.values())), indent=2))
        return
    for name, stats in results.items():
        print_report(name, stats)
    print()


if __name__ == "__main__":
    main()
