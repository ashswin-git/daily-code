#!/usr/bin/env python3
"""AI Text Summarizer - summarize text with the xAI (Grok) API.

Falls back to a simple offline extractive summarizer with --offline
or when no API key is configured.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from collections import Counter

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"


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


def ai_summary(text, sentences, api_key, model):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise summarizer."},
            {"role": "user", "content": f"Summarize the following text in about {sentences} sentences:\n\n{text}"},
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def offline_summary(text, sentences):
    """Score sentences by word frequency and keep the top ones in original order."""
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(parts) <= sentences:
        return " ".join(parts)
    words = re.findall(r"[a-z']+", text.lower())
    freq = Counter(w for w in words if len(w) > 3)
    scored = [(sum(freq[w] for w in re.findall(r"[a-z']+", s.lower())) / (len(s.split()) or 1), i)
              for i, s in enumerate(parts)]
    top = sorted(sorted(scored, reverse=True)[:sentences], key=lambda x: x[1])
    return " ".join(parts[i] for _, i in top)


def main():
    p = argparse.ArgumentParser(description="Summarize text with AI.")
    p.add_argument("file", nargs="?", help="text file (reads stdin if omitted)")
    p.add_argument("-n", "--sentences", type=int, default=3, help="target sentences (default 3)")
    p.add_argument("--offline", action="store_true", help="use the offline summarizer")
    args = p.parse_args()

    load_env()
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    if not text.strip():
        sys.exit("No input text provided.")

    key = os.environ.get("XAI_API_KEY")
    if args.offline or not key:
        if not args.offline:
            print("[no XAI_API_KEY found - using offline summarizer]", file=sys.stderr)
        print(offline_summary(text, args.sentences))
        return
    try:
        print(ai_summary(text, args.sentences, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL)))
    except Exception as e:  # network / auth errors
        sys.exit(f"API error: {e}")


if __name__ == "__main__":
    main()
