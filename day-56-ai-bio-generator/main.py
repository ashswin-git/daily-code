#!/usr/bin/env python3
"""AI Bio Generator - short social media bios with the xAI (Grok) API.

Falls back to a simple template-based generator with --offline
or when no API key is configured.
"""
import argparse
import json
import os
import random
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"
PLATFORM_LIMITS = {"twitter": 160, "instagram": 150, "linkedin": 220, "github": 160, "tiktok": 80, "generic": 200}
TONES = ["professional", "casual", "funny", "creative", "minimal"]

TEMPLATES = {
    "professional": ["{name} | {role} | {interests}", "{role} focused on {interests}. Building things that matter."],
    "casual": ["{role} who loves {interests}.", "Hey, I'm {name}! {role} + {interests} enthusiast."],
    "funny": ["{role} by day, {interests} addict by night.", "{name}: powered by coffee, {interests} and questionable decisions."],
    "creative": ["Turning ideas into reality with {interests}. {role}.", "{name} - {role} dreaming in {interests}."],
    "minimal": ["{role}. {interests}.", "{name}. {role}."],
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


def trim(text, limit):
    """Trim to the character limit on a word boundary."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rsplit(" ", 1)[0].rstrip(",.;:-|")
    return cut + "…"


def ai_bios(name, role, interests, tone, platform, count, api_key, model):
    limit = PLATFORM_LIMITS[platform]
    prompt = (f"Write {count} different {tone} {platform} bios, each under {limit} characters, for {name}, "
              f"a {role} interested in {interests}. Return one bio per line, no numbering or commentary.")
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You write catchy, authentic social media bios."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    lines = [l.strip(" -*0123456789.") for l in data["choices"][0]["message"]["content"].splitlines() if l.strip()]
    return [trim(l, limit) for l in lines][:count]


def offline_bios(name, role, interests, tone, platform, count):
    limit = PLATFORM_LIMITS[platform]
    pool = TEMPLATES[tone][:]
    random.shuffle(pool)
    bios = [trim(t.format(name=name, role=role, interests=interests), limit) for t in pool]
    return bios[:count]


def main():
    p = argparse.ArgumentParser(description="Generate social media bios with AI.")
    p.add_argument("--name", required=True)
    p.add_argument("--role", required=True, help="e.g. 'Python developer'")
    p.add_argument("--interests", required=True, help="e.g. 'open source, AI, chai'")
    p.add_argument("-t", "--tone", choices=TONES, default="professional")
    p.add_argument("-p", "--platform", choices=PLATFORM_LIMITS, default="generic")
    p.add_argument("-n", "--count", type=int, default=3)
    p.add_argument("--offline", action="store_true", help="use the offline generator")
    a = p.parse_args()

    load_env()
    key = os.environ.get("XAI_API_KEY")
    if a.offline or not key:
        if not a.offline:
            print("[no XAI_API_KEY found - using offline generator]", file=sys.stderr)
        bios = offline_bios(a.name, a.role, a.interests, a.tone, a.platform, a.count)
    else:
        try:
            bios = ai_bios(a.name, a.role, a.interests, a.tone, a.platform, a.count, key,
                           os.environ.get("XAI_MODEL", DEFAULT_MODEL))
        except Exception as e:
            sys.exit(f"API error: {e}")
    for i, b in enumerate(bios, 1):
        print(f"{i}. {b}")


if __name__ == "__main__":
    main()
