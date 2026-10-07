#!/usr/bin/env python3
"""Day 9 — URL Shortener.

Shorten links with free, keyless public services (is.gd, TinyURL), expand
short links to see where they really go, or keep an offline local alias book.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "daily-code-url-shortener/1.0"}
TIMEOUT = 10
STORE = Path(__file__).with_name("links.json")


# ---------- helpers ----------

def normalize(url: str) -> str:
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parts = urllib.parse.urlparse(url)
    if parts.scheme not in ("http", "https") or "." not in parts.netloc or " " in url:
        raise ValueError(f"not a valid web URL: {url}")
    return url


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8").strip()


# ---------- online services (no API key needed) ----------

def shorten_isgd(url: str, alias: str | None = None) -> str:
    params = {"format": "simple", "url": url}
    if alias:
        params["shorturl"] = alias
    text = fetch("https://is.gd/create.php?" + urllib.parse.urlencode(params))
    if not text.startswith("http"):
        raise RuntimeError(f"is.gd: {text}")
    return text


def shorten_tinyurl(url: str, alias: str | None = None) -> str:
    params = {"url": url}
    if alias:
        params["alias"] = alias
    text = fetch("https://tinyurl.com/api-create.php?" + urllib.parse.urlencode(params))
    if not text.startswith("http"):
        raise RuntimeError(f"TinyURL: {text}")
    return text


SERVICES = {"tinyurl": shorten_tinyurl, "isgd": shorten_isgd}


def shorten(url: str, service: str, alias: str | None) -> tuple[str, str]:
    """Try the chosen service first, then fall back to the others."""
    order = [service] + [s for s in SERVICES if s != service]
    errors = []
    for name in order:
        try:
            return name, SERVICES[name](url, alias)
        except (urllib.error.URLError, RuntimeError, TimeoutError) as exc:
            errors.append(f"{name}: {exc}")
    raise RuntimeError("all services failed -> " + "; ".join(errors))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # stop and let us read Location
        return None


def expand(url: str, max_hops: int = 10) -> list[str]:
    """Follow redirects one hop at a time and return the full chain."""
    opener = urllib.request.build_opener(_NoRedirect)
    chain = [normalize(url)]
    for _ in range(max_hops):
        req = urllib.request.Request(chain[-1], headers=UA, method="HEAD")
        try:
            opener.open(req, timeout=TIMEOUT)
            break  # 2xx: final destination
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location")
            if exc.code in (301, 302, 303, 307, 308) and location:
                chain.append(urllib.parse.urljoin(chain[-1], location))
                continue
            break
    return chain


# ---------- offline alias book ----------

def load_store() -> dict[str, str]:
    if STORE.exists():
        return json.loads(STORE.read_text(encoding="utf-8"))
    return {}


def save_store(data: dict[str, str]) -> None:
    STORE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def local_code(url: str, length: int = 6) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:length]


def local_add(url: str, alias: str | None) -> str:
    data = load_store()
    code = alias or local_code(url)
    if code in data and data[code] != url:
        raise ValueError(f"alias '{code}' already points to {data[code]}")
    data[code] = url
    save_store(data)
    return code


# ---------- CLI ----------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Shorten, expand, and save links.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("shorten", help="shorten one or more URLs online")
    s.add_argument("urls", nargs="+")
    s.add_argument("--service", choices=SERVICES, default="tinyurl")
    s.add_argument("--alias", help="custom alias (single URL only)")

    e = sub.add_parser("expand", help="reveal where a short link goes")
    e.add_argument("url")

    l = sub.add_parser("local", help="offline alias book (links.json)")
    l.add_argument("action", choices=["add", "get", "list", "remove"])
    l.add_argument("value", nargs="?", help="URL for add, code for get/remove")
    l.add_argument("--alias")

    a = p.parse_args(argv)

    try:
        if a.cmd == "shorten":
            if a.alias and len(a.urls) > 1:
                p.error("--alias works with a single URL")
            for raw in a.urls:
                url = normalize(raw)
                used, short = shorten(url, a.service, a.alias)
                saved = 100 - round(len(short) / len(url) * 100)
                note = f"{saved}% shorter" if saved > 0 else "already short"
                via = used if used == a.service else f"{used}, fell back from {a.service}"
                print(f"  {short}  <-  {url}  ({via}, {note})")

        elif a.cmd == "expand":
            chain = expand(a.url)
            for i, hop in enumerate(chain):
                print(f"  {'start' if i == 0 else f'hop {i}':>5}  {hop}")
            print(f"  Final destination: {chain[-1]}")

        else:  # local
            if a.action == "list":
                data = load_store()
                if not data:
                    print("  (no saved links yet)")
                for code, url in data.items():
                    print(f"  {code:<12} {url}")
            elif not a.value:
                p.error(f"local {a.action} needs a value")
            elif a.action == "add":
                url = normalize(a.value)
                print(f"  saved  {local_add(url, a.alias)}  ->  {url}")
            elif a.action == "get":
                url = load_store().get(a.value)
                if not url:
                    raise ValueError(f"no link saved under '{a.value}'")
                print(url)
            else:
                data = load_store()
                if data.pop(a.value, None) is None:
                    raise ValueError(f"no link saved under '{a.value}'")
                save_store(data)
                print(f"  removed {a.value}")
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
