#!/usr/bin/env python3
"""AI Caption Generator - social media captions with the xAI (Grok) API.

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
TONES = ["casual", "funny", "inspirational", "professional", "aesthetic"]
EMOJIS = {"casual": "😊✨🙌", "funny": "😂🤪🙈", "inspirational": "🌟💪🚀",
          "professional": "📈🤝💼", "aesthetic": "🌿🤍🌅"}


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


def ai_captions(desc, count, tone, emoji, api_key, model):
    prompt = (f"Write {count} {tone} social media captions for this photo/post description. "
              f"{'Include emojis.' if emoji else 'No emojis.'} "
              f"Return one caption per line, no numbering, no extra commentary.\n\n{desc}")
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a creative social media copywriter."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    lines = data["choices"][0]["message"]["content"].strip().splitlines()
    return [re.sub(r"^[\d\-\*\.\)\s]+", "", l).strip(' "') for l in lines if l.strip()][:count]


TEMPLATES = {
    "casual": ["Just {d} and loving it", "Today's mood: {d}", "{d}, no filter needed"],
    "funny": ["Me pretending I planned {d}", "{d} - zero regrets, mild chaos", "Plot twist: {d}"],
    "inspirational": ["Every step of {d} is a step forward", "Dream big, start with {d}", "{d}: the journey is the reward"],
    "professional": ["Sharing a moment of {d}", "{d}: lessons and takeaways", "Proud to share: {d}"],
    "aesthetic": ["soft moments, {d}", "{d} and golden light", "quietly {d}"],
}


def offline_captions(desc, count, tone, emoji):
    """Build captions from templates using a short phrase."""
    words = re.findall(r"[A-Za-z0-9']+", desc)
    phrase = " ".join(words[:6]).lower() if words else "this moment"
    pool = [t.format(d=phrase) for t in TEMPLATES[tone]]
    random.shuffle(pool)
    while len(pool) < count:
        pool.append(f"{phrase} #{len(pool) + 1}")
    pool = pool[:count]
    if emoji:
        pool = [f"{c} {random.choice(EMOJIS[tone])}" for c in pool]
    return pool


def main():
    p = argparse.ArgumentParser(description="Generate social media captions with AI.")
    p.add_argument("description", nargs="*", help="what the photo/post is about (reads stdin if omitted)")
    p.add_argument("-n", "--count", type=int, default=3, help="number of captions (default 3)")
    p.add_argument("-t", "--tone", choices=TONES, default="casual")
    p.add_argument("--no-emoji", action="store_true", help="omit emojis")
    p.add_argument("--offline", action="store_true", help="use the offline generator")
    args = p.parse_args()

    load_env()
    desc = " ".join(args.description) if args.description else sys.stdin.read()
    if not desc.strip():
        sys.exit("No description provided.")
    emoji = not args.no_emoji

    key = os.environ.get("XAI_API_KEY")
    if args.offline or not key:
        if not args.offline:
            print("[no XAI_API_KEY found - using offline generator]", file=sys.stderr)
        caps = offline_captions(desc, args.count, args.tone, emoji)
    else:
        try:
            caps = ai_captions(desc, args.count, args.tone, emoji, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL))
        except Exception as e:
            sys.exit(f"API error: {e}")
    for i, c in enumerate(caps, 1):
        print(f"{i}. {c}")


if __name__ == "__main__":
    main()
