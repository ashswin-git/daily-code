#!/usr/bin/env python3
"""Day 19 - Random Quote Generator.

A tiny CLI that prints random quotes from a built-in offline collection,
with optional online quotes from the free ZenQuotes API (no key needed).

Examples:
  python3 main.py
  python3 main.py --category coding -n 3
  python3 main.py --daily
  python3 main.py --search simple
  python3 main.py --online
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import textwrap
import urllib.request
from datetime import date

QUOTES: list[dict[str, str]] = [
    # motivation
    {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain", "category": "motivation"},
    {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela", "category": "motivation"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "category": "motivation"},
    {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky", "category": "motivation"},
    {"text": "Whether you think you can, or you think you can't, you're right.", "author": "Henry Ford", "category": "motivation"},
    {"text": "Done is better than perfect.", "author": "Sheryl Sandberg", "category": "motivation"},
    {"text": "Do or do not. There is no try.", "author": "Yoda", "category": "motivation"},
    # wisdom
    {"text": "The only true wisdom is in knowing you know nothing.", "author": "Socrates", "category": "wisdom"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein", "category": "wisdom"},
    {"text": "Simplicity is the ultimate sophistication.", "author": "Leonardo da Vinci", "category": "wisdom"},
    {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Will Durant", "category": "wisdom"},
    {"text": "Be the change that you wish to see in the world.", "author": "Mahatma Gandhi", "category": "wisdom"},
    {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu", "category": "wisdom"},
    {"text": "Knowing yourself is the beginning of all wisdom.", "author": "Aristotle", "category": "wisdom"},
    # coding
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds", "category": "coding"},
    {"text": "Programs must be written for people to read, and only incidentally for machines to execute.", "author": "Harold Abelson", "category": "coding"},
    {"text": "Premature optimization is the root of all evil.", "author": "Donald Knuth", "category": "coding"},
    {"text": "First, solve the problem. Then, write the code.", "author": "John Johnson", "category": "coding"},
    {"text": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler", "category": "coding"},
    {"text": "Simple is better than complex.", "author": "Tim Peters", "category": "coding"},
    {"text": "Make it work, make it right, make it fast.", "author": "Kent Beck", "category": "coding"},
    {"text": "There are only two hard things in Computer Science: cache invalidation and naming things.", "author": "Phil Karlton", "category": "coding"},
    # life
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "category": "life"},
    {"text": "In three words I can sum up everything I've learned about life: it goes on.", "author": "Robert Frost", "category": "life"},
    {"text": "Life is really simple, but we insist on making it complicated.", "author": "Confucius", "category": "life"},
    {"text": "Life is like riding a bicycle. To keep your balance you must keep moving.", "author": "Albert Einstein", "category": "life"},
    {"text": "The purpose of our lives is to be happy.", "author": "Dalai Lama", "category": "life"},
    # humor
    {"text": "I have not failed. I've just found 10,000 ways that won't work.", "author": "Thomas Edison", "category": "humor"},
    {"text": "I can resist everything except temptation.", "author": "Oscar Wilde", "category": "humor"},
    {"text": "A day without sunshine is like, you know, night.", "author": "Steve Martin", "category": "humor"},
    {"text": "I love deadlines. I like the whooshing sound they make as they fly by.", "author": "Douglas Adams", "category": "humor"},
]

ZENQUOTES_URL = "https://zenquotes.io/api/random"


def categories() -> list[str]:
    return sorted({q["category"] for q in QUOTES})


def filter_quotes(category: str | None, author: str | None, search: str | None) -> list[dict[str, str]]:
    pool = QUOTES
    if category:
        pool = [q for q in pool if q["category"] == category.lower()]
    if author:
        a = author.lower()
        pool = [q for q in pool if a in q["author"].lower()]
    if search:
        s = search.lower()
        pool = [q for q in pool if s in q["text"].lower()]
    return pool


def quote_of_the_day(pool: list[dict[str, str]], day: date) -> dict[str, str]:
    """Same quote for everyone on the same date (stable hash, not random)."""
    digest = hashlib.sha256(day.isoformat().encode()).hexdigest()
    return pool[int(digest, 16) % len(pool)]


def fetch_online(timeout: float = 5.0) -> dict[str, str] | None:
    """One quote from ZenQuotes (free, no API key). Returns None on any failure."""
    try:
        req = urllib.request.Request(ZENQUOTES_URL, headers={"User-Agent": "daily-code-quote/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        item = data[0]
        if not item.get("q") or "too many requests" in item["q"].lower():
            return None
        return {"text": item["q"].strip(), "author": item.get("a", "Unknown").strip(), "category": "online"}
    except Exception:
        return None


def render(q: dict[str, str], width: int) -> str:
    body = textwrap.fill(f"\u201c{q['text']}\u201d", width=width)
    tag = f"  [{q['category']}]" if q.get("category") else ""
    return f"{body}\n    \u2014 {q['author']}{tag}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Print random quotes (offline collection or free online API).")
    p.add_argument("-n", "--count", type=int, default=1, help="how many quotes (default 1)")
    p.add_argument("-c", "--category", help="filter by category (see --list)")
    p.add_argument("-a", "--author", help="filter by author (substring match)")
    p.add_argument("-s", "--search", help="only quotes containing this text")
    p.add_argument("--daily", action="store_true", help="quote of the day (same all day)")
    p.add_argument("--seed", help="seed for reproducible picks")
    p.add_argument("--online", action="store_true", help="fetch from ZenQuotes, fall back to offline")
    p.add_argument("--json", action="store_true", help="output JSON")
    p.add_argument("-w", "--width", type=int, default=70, help="wrap width (default 70)")
    p.add_argument("--list", action="store_true", help="list categories with counts and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        for cat in categories():
            print(f"{cat:<12} {sum(q['category'] == cat for q in QUOTES)}")
        print(f"{'total':<12} {len(QUOTES)}")
        return 0

    if args.count < 1:
        print("error: --count must be at least 1", file=sys.stderr)
        return 2
    if args.category and args.category.lower() not in categories():
        print(f"error: unknown category '{args.category}'. Try: {', '.join(categories())}", file=sys.stderr)
        return 2

    picked: list[dict[str, str]] = []
    if args.online:
        for _ in range(args.count):
            q = fetch_online()
            if q is None:
                print("note: online quote unavailable, using offline collection", file=sys.stderr)
                break
            picked.append(q)

    if len(picked) < args.count:
        pool = filter_quotes(args.category, args.author, args.search)
        if not pool:
            print("error: no quotes match those filters", file=sys.stderr)
            return 1
        need = args.count - len(picked)
        if args.daily:
            start = pool.index(quote_of_the_day(pool, date.today()))
            picked.extend(pool[(start + i) % len(pool)] for i in range(need))
        else:
            rng = random.Random(args.seed)
            picked.extend(rng.sample(pool, need) if need <= len(pool) else [rng.choice(pool) for _ in range(need)])

    if args.json:
        print(json.dumps(picked if len(picked) > 1 else picked[0], indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(render(q, args.width) for q in picked))
    return 0


if __name__ == "__main__":
    sys.exit(main())
