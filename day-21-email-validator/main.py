#!/usr/bin/env python3
"""Day 21 - Email Validator.

Check email addresses for valid syntax (practical RFC 5322 subset),
catch common typos in popular domains, flag disposable/role addresses,
and optionally verify the domain has MX/A records (needs internet).

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import socket
import sys
from difflib import get_close_matches

LOCAL_RE = re.compile(r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*$")
LABEL_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")

POPULAR = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "live.com", "aol.com", "protonmail.com", "proton.me", "zoho.com",
    "yandex.com", "gmx.com", "mail.com", "rediffmail.com", "yahoo.co.in",
]
DISPOSABLE = {
    "mailinator.com", "10minutemail.com", "guerrillamail.com", "tempmail.com",
    "temp-mail.org", "yopmail.com", "trashmail.com", "sharklasers.com",
    "getnada.com", "throwawaymail.com", "dispostable.com", "maildrop.cc",
}
ROLE = {"admin", "info", "support", "sales", "contact", "noreply", "no-reply",
        "help", "office", "webmaster", "postmaster", "billing", "hr", "team"}


def check_syntax(email: str) -> list[str]:
    """Return a list of syntax errors (empty list = valid syntax)."""
    errors = []
    if not email:
        return ["empty address"]
    if len(email) > 254:
        errors.append("address longer than 254 characters")
    if email.count("@") != 1:
        return errors + ["must contain exactly one '@'"]
    local, domain = email.split("@")
    if not local:
        errors.append("missing part before '@'")
    elif len(local) > 64:
        errors.append("local part longer than 64 characters")
    elif ".." in local:
        errors.append("local part has consecutive dots")
    elif local.startswith(".") or local.endswith("."):
        errors.append("local part starts or ends with a dot")
    elif not LOCAL_RE.match(local):
        errors.append("local part has invalid characters")
    if not domain:
        errors.append("missing domain after '@'")
        return errors
    labels = domain.split(".")
    if len(labels) < 2:
        errors.append("domain needs a dot (e.g. example.com)")
    for label in labels:
        if not label:
            errors.append("domain has an empty label (check the dots)")
            break
        if not LABEL_RE.match(label):
            errors.append(f"invalid domain label '{label}'")
            break
    tld = labels[-1]
    if tld and (len(tld) < 2 or tld.isdigit()):
        errors.append(f"invalid top-level domain '.{tld}'")
    return errors


def suggest_domain(domain: str) -> str | None:
    domain = domain.lower()
    if domain in POPULAR:
        return None
    match = get_close_matches(domain, POPULAR, n=1, cutoff=0.8)
    return match[0] if match else None


def has_dns(domain: str, timeout: float = 3.0) -> bool:
    """True if the domain resolves (A/AAAA). Stdlib has no MX lookup."""
    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        socket.getaddrinfo(domain, None)
        return True
    except (socket.gaierror, socket.timeout, UnicodeError):
        return False
    finally:
        socket.setdefaulttimeout(old)


def validate(raw: str, dns: bool = False) -> dict:
    email = raw.strip()
    result = {"email": email, "valid": False, "errors": [], "warnings": [],
              "suggestion": None}
    errors = check_syntax(email)
    result["errors"] = errors
    if errors:
        return result
    local, domain = email.split("@")
    domain_l = domain.lower()
    result["normalized"] = f"{local}@{domain_l}"
    fix = suggest_domain(domain_l)
    if fix:
        result["suggestion"] = f"{local}@{fix}"
        result["warnings"].append(f"did you mean @{fix}?")
    if domain_l in DISPOSABLE:
        result["warnings"].append("disposable / temporary email provider")
    if local.lower() in ROLE:
        result["warnings"].append("role address (shared inbox, not a person)")
    if "+" in local:
        result["warnings"].append("uses +tag alias")
    if dns:
        ok = has_dns(domain_l)
        result["dns"] = ok
        if not ok:
            result["errors"].append(f"domain '{domain_l}' does not resolve")
            return result
    result["valid"] = True
    return result


def status_icon(r: dict) -> str:
    if not r["valid"]:
        return "INVALID"
    return "WARN" if r["warnings"] else "VALID"


def print_text(results: list[dict]) -> None:
    for r in results:
        print(f"[{status_icon(r):7}] {r['email'] or '(empty)'}")
        for e in r["errors"]:
            print(f"           x {e}")
        for w in r["warnings"]:
            print(f"           ! {w}")
    total = len(results)
    ok = sum(r["valid"] for r in results)
    if total > 1:
        print(f"\n{ok}/{total} valid, {total - ok} invalid")


def read_inputs(args: argparse.Namespace) -> list[str]:
    items = list(args.emails)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            items += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if not items and not sys.stdin.isatty():
        items = [ln.strip() for ln in sys.stdin if ln.strip()]
    return items


def main() -> int:
    p = argparse.ArgumentParser(description="Validate email addresses (syntax, typos, disposable, DNS).")
    p.add_argument("emails", nargs="*", help="email addresses to check")
    p.add_argument("-f", "--file", help="text file with one email per line")
    p.add_argument("--dns", action="store_true", help="also check the domain resolves (needs internet)")
    p.add_argument("--format", choices=["text", "json", "csv"], default="text")
    p.add_argument("--valid-only", action="store_true", help="print only valid addresses (for cleaning lists)")
    args = p.parse_args()

    items = read_inputs(args)
    if not items:
        try:
            items = [input("Email to check: ")]
        except EOFError:
            p.error("no email given")

    results = [validate(e, dns=args.dns) for e in items]

    if args.valid_only:
        for r in results:
            if r["valid"]:
                print(r["normalized"])
    elif args.format == "json":
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    elif args.format == "csv":
        w = csv.writer(sys.stdout)
        w.writerow(["email", "status", "errors", "warnings", "suggestion"])
        for r in results:
            w.writerow([r["email"], status_icon(r), "; ".join(r["errors"]),
                        "; ".join(r["warnings"]), r["suggestion"] or ""])
    else:
        print_text(results)
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
