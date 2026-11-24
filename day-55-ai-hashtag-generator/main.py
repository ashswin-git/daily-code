#!/usr/bin/env python3
"""AI Hashtag Generator - relevant hashtags with the xAI (Grok) API.

Falls back to a simple offline keyword-based generator with --offline
or when no API key is configured.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"
STOPWORDS = set("a an the and or but of to in on at for with from by is are was were be been it this that "
                "these those i my me we our you your as about into over just so very really more most".split())
PLATFORM_LIMITS = {"instagram": 30, "twitter": 3, "tiktok": 5, "linkedin": 5, "generic": 10}


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


def clean_tag(text):
    """Turn arbitrary text into a #CamelCase hashtag."""
    words = re.findall(r"[A-Za-z0-9]+", text)
    return "#" + "".join(w[:1].upper() + w[1:] for w in words) if words else ""


def ai_hashtags(desc, count, platform, api_key, model):
    prompt = (f"Generate {count} relevant, popular hashtags for {platform} for this post. "
              "Return them space-separated on one line, no commentary.\n\n" + desc)
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a social media growth expert."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    text = data["choices"][0]["message"]["content"]
    tags = [clean_tag(t) for t in re.findall(r"#?\w+", text)]
    return dedupe(tags)[:count]


def dedupe(tags):
    seen, out = set(), []
    for t in tags:
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def offline_hashtags(desc, count):
    """Rank non-stopword keywords by frequency, then add bigrams."""
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9']+", desc)]
    words = [w.replace("'", "") for w in words]
    keys = [w for w in words if w not in STOPWORDS and len(w) > 2]
    freq = {}
    for w in keys:
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: (-freq[w], keys.index(w)))
    tags = [clean_tag(w) for w in ranked]
    for a, b in zip(keys, keys[1:]):
        tags.append(clean_tag(a + " " + b))
    return dedupe(tags)[:count]


def main():
    p = argparse.ArgumentParser(description="Generate hashtags with AI.")
    p.add_argument("description", nargs="*", help="post text (reads stdin if omitted)")
    p.add_argument("-n", "--count", type=int, help="number of hashtags (default depends on platform)")
    p.add_argument("-p", "--platform", choices=PLATFORM_LIMITS, default="generic")
    p.add_argument("--offline", action="store_true", help="use the offline generator")
    args = p.parse_args()

    load_env()
    desc = " ".join(args.description) if args.description else sys.stdin.read()
    if not desc.strip():
        sys.exit("No description provided.")
    count = args.count or PLATFORM_LIMITS[args.platform]

    key = os.environ.get("XAI_API_KEY")
    if args.offline or not key:
        if not args.offline:
            print("[no XAI_API_KEY found - using offline generator]", file=sys.stderr)
        tags = offline_hashtags(desc, count)
    else:
        try:
            tags = ai_hashtags(desc, count, args.platform, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL))
        except Exception as e:
            sys.exit(f"API error: {e}")
    print(" ".join(tags))


if __name__ == "__main__":
    main()
