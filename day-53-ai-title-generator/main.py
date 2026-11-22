#!/usr/bin/env python3
"""AI Title Generator - generate catchy titles for a topic or text with the xAI (Grok) API.

Falls back to a simple offline template generator with --offline
or when no API key is configured.
"""
import argparse
import json
import os
import random
import re
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"
STYLES = ["catchy", "professional", "clickbait", "seo", "funny"]


def load_env(path=".env"):
    """Tiny .env loader (no dependencies)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ai_titles(topic, count, style, api_key, model):
    prompt = (f"Generate {count} {style} titles for the following topic or text. "
              f"Return one title per line, no numbering, no extra commentary.\n\n{topic}")
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a creative headline writer."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    lines = data["choices"][0]["message"]["content"].strip().splitlines()
    return [re.sub(r"^[\d\-\*\.\)\s]+", "", l).strip(' "') for l in lines if l.strip()][:count]


TEMPLATES = {
    "catchy": ["{t}: What Nobody Tells You", "The Ultimate Guide to {t}", "Why {t} Matters More Than You Think", "{t} Made Simple"],
    "professional": ["An Introduction to {t}", "{t}: Key Concepts and Best Practices", "Understanding {t} in Depth", "A Practical Overview of {t}"],
    "clickbait": ["You Won't Believe What {t} Can Do", "10 Secrets About {t} Revealed", "I Tried {t} for 30 Days - Here's What Happened", "Stop Ignoring {t}!"],
    "seo": ["{t}: A Complete Beginner's Guide ({y})", "How to Get Started with {t}", "Best {t} Tips and Tricks", "{t} Explained: Everything You Need to Know"],
    "funny": ["{t}: Because Why Not?", "My Awkward Relationship with {t}", "{t} and Other Things I Pretend to Understand", "Send Help: {t} Edition"],
}


def offline_titles(topic, count, style):
    """Build titles from templates using a short topic phrase."""
    words = re.findall(r"[A-Za-z0-9']+", topic)
    phrase = " ".join(words[:5]).title() if words else "Your Topic"
    pool = [t.format(t=phrase, y="2026") for t in TEMPLATES[style]]
    random.shuffle(pool)
    while len(pool) < count:
        pool.append(f"{phrase} - Idea #{len(pool) + 1}")
    return pool[:count]


def main():
    p = argparse.ArgumentParser(description="Generate titles with AI.")
    p.add_argument("topic", nargs="*", help="topic or text (reads stdin if omitted)")
    p.add_argument("-n", "--count", type=int, default=5, help="number of titles (default 5)")
    p.add_argument("-s", "--style", choices=STYLES, default="catchy")
    p.add_argument("--offline", action="store_true", help="use the offline generator")
    args = p.parse_args()

    load_env()
    topic = " ".join(args.topic) if args.topic else sys.stdin.read()
    if not topic.strip():
        sys.exit("No topic provided.")

    key = os.environ.get("XAI_API_KEY")
    if args.offline or not key:
        if not args.offline:
            print("[no XAI_API_KEY found - using offline generator]", file=sys.stderr)
        titles = offline_titles(topic, args.count, args.style)
    else:
        try:
            titles = ai_titles(topic, args.count, args.style, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL))
        except Exception as e:
            sys.exit(f"API error: {e}")
    for i, t in enumerate(titles, 1):
        print(f"{i}. {t}")


if __name__ == "__main__":
    main()
