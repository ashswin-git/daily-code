#!/usr/bin/env python3
"""Day 22 - Phone Number Validator.

Check phone numbers offline: cleans messy input, detects the country from
the calling code, validates length and mobile prefixes for common countries,
and prints the number in E.164 and a friendly national format.

Standard library only. No API key.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys

# code -> (country, ISO, national number lengths, mobile-prefix regex or None, trunk prefix)
COUNTRIES = {
    "1":   ("United States / Canada", "US", {10}, None, "1"),
    "44":  ("United Kingdom", "GB", {10}, r"^7", "0"),
    "91":  ("India", "IN", {10}, r"^[6-9]", "0"),
    "61":  ("Australia", "AU", {9}, r"^4", "0"),
    "49":  ("Germany", "DE", set(range(7, 12)), r"^1[5-7]", "0"),
    "33":  ("France", "FR", {9}, r"^[67]", "0"),
    "81":  ("Japan", "JP", {9, 10}, r"^[789]0", "0"),
    "86":  ("China", "CN", {11}, r"^1[3-9]", "0"),
    "971": ("United Arab Emirates", "AE", {8, 9}, r"^5", "0"),
    "92":  ("Pakistan", "PK", {10}, r"^3", "0"),
    "880": ("Bangladesh", "BD", {10}, r"^1[3-9]", "0"),
    "977": ("Nepal", "NP", {8, 10}, r"^9[78]", "0"),
    "94":  ("Sri Lanka", "LK", {9}, r"^7", "0"),
    "65":  ("Singapore", "SG", {8}, r"^[89]", ""),
    "55":  ("Brazil", "BR", {10, 11}, r"^\d{2}9", "0"),
    "7":   ("Russia / Kazakhstan", "RU", {10}, r"^9", "8"),
    "234": ("Nigeria", "NG", {10}, r"^[789]", "0"),
    "27":  ("South Africa", "ZA", {9}, r"^[6-8]", "0"),
}
ISO_TO_CODE = {v[1]: k for k, v in COUNTRIES.items()}
ISO_TO_CODE.update({"CA": "1", "KZ": "7"})

ALLOWED = re.compile(r"^[\d\s().\-+/]+$")


def clean(raw: str) -> tuple[str, str | None]:
    """Return (digits-with-optional-plus, extension)."""
    raw = raw.strip()
    ext = None
    m = re.search(r"\s*(?:ext\.?|x|#)\s*(\d{1,6})$", raw, re.I)
    if m:
        ext, raw = m.group(1), raw[: m.start()]
    if raw.startswith("00"):
        raw = "+" + raw[2:]
    plus = raw.startswith("+")
    return ("+" if plus else "") + re.sub(r"\D", "", raw), ext if m else None


def split_code(digits: str) -> tuple[str | None, str]:
    for size in (3, 2, 1):
        if digits[:size] in COUNTRIES:
            return digits[:size], digits[size:]
    return None, digits


def fmt_national(code: str, nsn: str) -> str:
    if code == "1":
        return f"({nsn[:3]}) {nsn[3:6]}-{nsn[6:]}"
    if code == "91":
        return f"{nsn[:5]} {nsn[5:]}"
    if code in ("44", "61", "33", "27"):
        return f"{nsn[:-6]} {nsn[-6:-3]} {nsn[-3:]}"
    if len(nsn) > 6:
        return f"{nsn[:-7]} {nsn[-7:-4]} {nsn[-4:]}".strip()
    return nsn


def validate(raw: str, default: str | None = None) -> dict:
    res = {"input": raw, "valid": False, "e164": None, "national": None,
           "country": None, "type": None, "errors": [], "notes": []}
    if not raw.strip():
        res["errors"].append("empty input")
        return res
    body = re.sub(r"\s*(?:ext\.?|x|#)\s*\d{1,6}$", "", raw.strip(), flags=re.I)
    if not ALLOWED.match(body):
        res["errors"].append("contains letters or symbols that aren't part of a phone number")
        return res
    num, ext = clean(raw)
    if ext:
        res["notes"].append(f"extension {ext}")
    digits = num.lstrip("+")
    if not digits:
        res["errors"].append("no digits found")
        return res

    if num.startswith("+"):
        code, nsn = split_code(digits)
        if code is None:
            res["errors"].append(f"unknown or unsupported country code +{digits[:3]}")
            return res
    elif default:
        code = ISO_TO_CODE.get(default.upper())
        if not code:
            res["errors"].append(f"unsupported default country '{default}'")
            return res
        nsn = digits
        trunk = COUNTRIES[code][4]
        if code == "1" and len(nsn) == 11 and nsn.startswith("1"):
            nsn = nsn[1:]
        elif trunk and code != "1" and nsn.startswith(trunk):
            nsn = nsn[len(trunk):]
            res["notes"].append(f"removed national prefix '{trunk}'")
        elif nsn.startswith(code) and len(nsn) - len(code) in COUNTRIES[code][2]:
            nsn = nsn[len(code):]
            res["notes"].append("country code given without '+'")
    else:
        res["errors"].append("no country code: start with + or pass --country")
        return res

    name, iso, lengths, mobile_re, _ = COUNTRIES[code]
    res["country"] = f"{name} ({iso}, +{code})"
    if code != "1" and nsn.startswith("0"):
        nsn = nsn[1:]
        res["notes"].append("dropped a leading 0 after the country code")
    if len(nsn) not in lengths:
        want = "/".join(str(n) for n in sorted(lengths)) if len(lengths) < 4 else f"{min(lengths)}-{max(lengths)}"
        res["errors"].append(f"{len(nsn)} digits after +{code}, expected {want}")
        return res
    if code == "1":
        if nsn[0] in "01" or nsn[3] in "01":
            res["errors"].append("area code and exchange can't start with 0 or 1")
            return res
        if nsn[3:6] == "555" and nsn[6:8] == "01":
            res["notes"].append("fictional 555-01xx number (used in movies)")
        res["type"] = "mobile or landline"
    elif mobile_re:
        res["type"] = "mobile" if re.match(mobile_re, nsn) else "landline / other"
    if code == "91" and nsn[0] in "15":
        res["errors"].append("Indian numbers start with 2-4 (landline) or 6-9 (mobile)")
        res["type"] = None
        return res
    if len(set(nsn)) == 1:
        res["notes"].append("all digits are the same, probably a dummy number")

    res["valid"] = True
    res["e164"] = f"+{code}{nsn}"
    res["national"] = fmt_national(code, nsn)
    return res


def show_text(results: list[dict]) -> None:
    for r in results:
        tag = "VALID  " if r["valid"] else "INVALID"
        print(f"[{tag}] {r['input']}")
        if r["valid"]:
            print(f"           {r['e164']}  |  {r['national']}  |  {r['country']}  |  {r['type']}")
        for e in r["errors"]:
            print(f"           x {e}")
        for n in r["notes"]:
            print(f"           ! {n}")
    ok = sum(r["valid"] for r in results)
    if len(results) > 1:
        print(f"\n{ok}/{len(results)} valid, {len(results) - ok} invalid")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate and format phone numbers (offline).")
    ap.add_argument("numbers", nargs="*", help="phone numbers to check (quote ones with spaces)")
    ap.add_argument("-c", "--country", help="default country for numbers without + (e.g. IN, US, GB)")
    ap.add_argument("-f", "--file", help="read one number per line from a file")
    ap.add_argument("--format", choices=("text", "json", "csv"), default="text")
    ap.add_argument("--valid-only", action="store_true", help="print only valid numbers in E.164")
    ap.add_argument("--list-countries", action="store_true", help="show supported countries")
    a = ap.parse_args(argv)

    if a.list_countries:
        for code, (name, iso, *_rest) in sorted(COUNTRIES.items(), key=lambda kv: kv[1][0]):
            print(f"{iso}  +{code:<4} {name}")
        return 0

    items = list(a.numbers)
    if a.file:
        with open(a.file, encoding="utf-8") as fh:
            items += [ln.strip() for ln in fh if ln.strip()]
    if not items and not sys.stdin.isatty():
        items = [ln.strip() for ln in sys.stdin if ln.strip()]
    if not items:
        try:
            items = [input("Phone number: ")]
        except (EOFError, KeyboardInterrupt):
            return 1

    results = [validate(x, a.country) for x in items]
    if a.valid_only:
        for r in results:
            if r["valid"]:
                print(r["e164"])
    elif a.format == "json":
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    elif a.format == "csv":
        w = csv.writer(sys.stdout)
        w.writerow(["input", "valid", "e164", "national", "country", "type", "errors", "notes"])
        for r in results:
            w.writerow([r["input"], r["valid"], r["e164"] or "", r["national"] or "",
                        r["country"] or "", r["type"] or "", "; ".join(r["errors"]), "; ".join(r["notes"])])
    else:
        show_text(results)
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
