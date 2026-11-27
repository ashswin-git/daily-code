#!/usr/bin/env python3
"""AI Blog Idea Generator - brainstorm blog post ideas with the xAI (Grok) API.

Falls back to simple title templates with --offline or when no API key is set.
"""
import argparse
import json
import os
import random
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"
STYLES = ["how-to", "listicle", "opinion", "beginner", "case-study"]

TEMPLATES = {
    "how-to": ["How to Get Started with {t} in 30 Minutes", "A Step-by-Step Guide to {t}",
               "How I Learned {t} (and How You Can Too)"],
    "listicle": ["10 Things Nobody Tells You About {t}", "7 Common {t} Mistakes to Avoid",
                 "Top 5 Tools for {t}"],
    "opinion": ["Why {t} Is Overrated (and What to Do Instead)", "The Future of {t}: My Predictions",
                "Unpopular Opinion: {t} Is Easier Than You Think"],
    "beginner": ["{t} for Absolute Beginners", "What Is {t}? A Plain-English Explanation",
                 "The Beginner's Roadmap to {t}"],
    "case-study": ["How We Used {t} to Solve a Real Problem", "{t}: Lessons from a Real Project",
                   "Before and After: What {t} Changed for Us"],
}


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


def ai_ideas(topic, count, style, key, model):
    prompt = (f"Give {count} {style} blog post ideas about: {topic}. "
              "Format each as a numbered line: 'Title - one sentence angle'. No extra commentary.")
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a creative content strategist."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def offline_ideas(topic, count, style):
    pool = TEMPLATES[style][:]
    for s in STYLES:
        if s != style:
            pool += TEMPLATES[s]
    random.shuffle(pool[len(TEMPLATES[style]):])
    chosen = pool[:count]
    return "\n".join(f"{i}. {t.format(t=topic)}" for i, t in enumerate(chosen, 1))


def main():
    p = argparse.ArgumentParser(description="Generate blog post ideas with AI.")
    p.add_argument("topic", help="blog topic, e.g. 'python automation'")
    p.add_argument("-n", "--count", type=int, default=5, help="number of ideas (default 5)")
    p.add_argument("-s", "--style", choices=STYLES, default="how-to")
    p.add_argument("--offline", action="store_true", help="use offline templates")
    a = p.parse_args()
    if a.count < 1:
        sys.exit("count must be at least 1")

    load_env()
    key = os.environ.get("XAI_API_KEY")
    if a.offline or not key:
        if not a.offline:
            print("[no XAI_API_KEY found - using offline templates]", file=sys.stderr)
        print(offline_ideas(a.topic, a.count, a.style))
    else:
        try:
            print(ai_ideas(a.topic, a.count, a.style, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL)))
        except Exception as e:
            sys.exit(f"API error: {e}")


if __name__ == "__main__":
    main()
