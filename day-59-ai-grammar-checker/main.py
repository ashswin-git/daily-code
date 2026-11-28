#!/usr/bin/env python3
"""AI Grammar Checker - fix grammar and spelling with the xAI (Grok) API.

Falls back to a small rule-based checker with --offline or when no API key is set.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"

COMMON_TYPOS = {
    "teh": "the", "recieve": "receive", "adress": "address", "definately": "definitely",
    "seperate": "separate", "occured": "occurred", "wich": "which", "becuase": "because",
    "alot": "a lot", "untill": "until", "freind": "friend", "thier": "their",
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


def ai_check(text, key, model):
    prompt = ("Correct the grammar, spelling and punctuation of the text below. "
              "Reply with the corrected text first, then a line '---', then a short bullet list "
              "of the changes you made.\n\nText:\n" + text)
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a careful proofreader. Keep the author's meaning and tone."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def offline_check(text):
    """Simple rules: typos, double spaces, repeated words, capitalization, 'i', end punctuation."""
    changes = []
    out = text

    def typo(m):
        w = m.group(0)
        fixed = COMMON_TYPOS[w.lower()]
        changes.append(f"typo '{w}' -> '{fixed}'")
        return fixed.capitalize() if w[0].isupper() else fixed
    out = re.sub(r"\b(" + "|".join(COMMON_TYPOS) + r")\b", typo, out, flags=re.I)

    def rep(m):
        changes.append(f"repeated word '{m.group(1)}'")
        return m.group(1)
    out = re.sub(r"\b(\w+)\s+\1\b", rep, out, flags=re.I)

    if re.search(r"[ \t]{2,}", out):
        changes.append("extra spaces removed")
        out = re.sub(r"[ \t]{2,}", " ", out)
    if re.search(r"\bi\b", out):
        changes.append("pronoun 'i' -> 'I'")
        out = re.sub(r"\bi\b", "I", out)

    def cap(m):
        return m.group(1) + m.group(2).upper()
    new = re.sub(r"(^\s*|[.!?]\s+)([a-z])", cap, out)
    if new != out:
        changes.append("sentence capitalization")
        out = new
    out = out.strip()
    if out and out[-1] not in ".!?":
        out += "."
        changes.append("added end punctuation")
    report = "\n".join("- " + c for c in changes) if changes else "- no issues found"
    return out + "\n---\n" + report


def main():
    p = argparse.ArgumentParser(description="Check and fix grammar with AI.")
    p.add_argument("text", nargs="?", help="text to check (or use --file / stdin)")
    p.add_argument("-f", "--file", help="read text from a file")
    p.add_argument("--offline", action="store_true", help="use the rule-based checker")
    a = p.parse_args()

    if a.file:
        with open(a.file, encoding="utf-8") as f:
            text = f.read()
    elif a.text:
        text = a.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        p.error("provide text, --file, or pipe text via stdin")
    if not text.strip():
        sys.exit("empty text")

    load_env()
    key = os.environ.get("XAI_API_KEY")
    if a.offline or not key:
        if not a.offline:
            print("[no XAI_API_KEY found - using offline checker]", file=sys.stderr)
        print(offline_check(text))
    else:
        try:
            print(ai_check(text, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL)))
        except Exception as e:
            sys.exit(f"API error: {e}")


if __name__ == "__main__":
    main()
