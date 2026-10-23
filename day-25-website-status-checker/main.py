#!/usr/bin/env python3
"""Day 25 - Website Status Checker.

Check if one or more websites are up: HTTP status, response time,
final URL after redirects and page title. Checks run in parallel.
Standard library only.

Usage:
  python3 main.py github.com example.com
  python3 main.py -f sites.txt --json
  python3 main.py https://httpbin.org/status/500 --timeout 5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (daily-code website-status-checker)"
TITLE_RE = re.compile(rb"<title[^>]*>(.*?)</title>", re.I | re.S)


def normalize(url: str) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url


def label(code: int | None) -> str:
    if code is None:
        return "DOWN"
    if code < 300:
        return "UP"
    if code < 400:
        return "REDIRECT"
    if code < 500:
        return "CLIENT ERR"
    return "SERVER ERR"


def check(url: str, timeout: float) -> dict:
    url = normalize(url)
    result = {"url": url, "status": None, "state": "DOWN", "ms": None,
              "final_url": None, "title": None, "error": None}
    start = time.perf_counter()
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read(65536)
            result["status"] = resp.status
            result["final_url"] = resp.geturl()
            m = TITLE_RE.search(body)
            if m:
                title = unescape(m.group(1).decode("utf-8", "replace"))
                result["title"] = " ".join(title.split())[:60]
    except HTTPError as e:
        result["status"] = e.code
        result["final_url"] = e.geturl()
    except URLError as e:
        result["error"] = str(e.reason)[:60]
    except Exception as e:  # timeouts, bad URLs, SSL issues
        result["error"] = (str(e) or type(e).__name__)[:60]
    result["ms"] = round((time.perf_counter() - start) * 1000, 1)
    result["state"] = label(result["status"])
    return result


def read_sites(args) -> list[str]:
    sites = list(args.sites)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    sites.append(line)
    return sites


def print_table(results: list[dict]) -> None:
    width = max(len(r["url"]) for r in results)
    print(f"  {'URL':<{width}}  {'STATE':<10}  CODE     TIME  DETAIL")
    for r in results:
        code = str(r["status"]) if r["status"] else "-"
        detail = r["error"] or r["title"] or ""
        if r["final_url"] and r["final_url"].rstrip("/") != r["url"].rstrip("/"):
            detail = f"-> {r['final_url']}  {detail}".strip()
        print(f"  {r['url']:<{width}}  {r['state']:<10}  {code:>4}  {r['ms']:>6.0f}ms  {detail}")
    up = sum(r["state"] == "UP" for r in results)
    print(f"\n{up} up / {len(results)} checked")


def main() -> int:
    p = argparse.ArgumentParser(description="Check if websites are up.")
    p.add_argument("sites", nargs="*", help="URLs or domains (https:// is added if missing)")
    p.add_argument("-f", "--file", help="text file with one URL per line")
    p.add_argument("-t", "--timeout", type=float, default=8.0, help="seconds per site (default 8)")
    p.add_argument("-w", "--workers", type=int, default=10, help="parallel checks (default 10)")
    p.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = p.parse_args()

    try:
        sites = read_sites(args)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if not sites:
        p.print_usage(sys.stderr)
        print("error: give at least one site or --file", file=sys.stderr)
        return 2

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(lambda s: check(s, args.timeout), sites))

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_table(results)
    return 0 if all(r["state"] == "UP" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
