#!/usr/bin/env python3
"""AI Email Generator - draft emails with the xAI (Grok) API.

Falls back to a simple template with --offline or when no API key is set.
"""
import argparse
import json
import os
import sys
import urllib.request

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-3-mini"
TONES = ["formal", "friendly", "persuasive", "apologetic", "concise"]

GREETING = {"formal": "Dear {to},", "friendly": "Hi {to},", "persuasive": "Hello {to},",
            "apologetic": "Dear {to},", "concise": "Hi {to},"}
CLOSING = {"formal": "Sincerely,", "friendly": "Cheers,", "persuasive": "Best regards,",
           "apologetic": "With apologies,", "concise": "Thanks,"}


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


def ai_email(to, sender, purpose, tone, key, model):
    prompt = (f"Write a {tone} email to {to} from {sender}. Purpose: {purpose}. "
              "Start with a line 'Subject: ...', then a blank line, then the body. No extra commentary.")
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You write clear, well-structured emails."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def offline_email(to, sender, purpose, tone):
    subject = purpose.strip().rstrip(".").capitalize()
    body = f"I'm writing regarding the following: {purpose.strip().rstrip('.')}."
    if tone == "apologetic":
        body = f"I sincerely apologize. {body} I will make sure it is resolved."
    elif tone == "persuasive":
        body += " I believe this is a great opportunity, and I'd love to discuss it."
    elif tone != "concise":
        body += " Please let me know if you have any questions."
    return (f"Subject: {subject}\n\n{GREETING[tone].format(to=to)}\n\n{body}\n\n"
            f"{CLOSING[tone]}\n{sender}")


def main():
    p = argparse.ArgumentParser(description="Generate an email draft with AI.")
    p.add_argument("--to", required=True, help="recipient name")
    p.add_argument("--sender", required=True, help="your name")
    p.add_argument("--purpose", required=True, help="what the email is about")
    p.add_argument("-t", "--tone", choices=TONES, default="formal")
    p.add_argument("--offline", action="store_true", help="use the offline template")
    a = p.parse_args()

    load_env()
    key = os.environ.get("XAI_API_KEY")
    if a.offline or not key:
        if not a.offline:
            print("[no XAI_API_KEY found - using offline template]", file=sys.stderr)
        print(offline_email(a.to, a.sender, a.purpose, a.tone))
    else:
        try:
            print(ai_email(a.to, a.sender, a.purpose, a.tone, key, os.environ.get("XAI_MODEL", DEFAULT_MODEL)))
        except Exception as e:
            sys.exit(f"API error: {e}")


if __name__ == "__main__":
    main()
