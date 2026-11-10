#!/usr/bin/env python3
"""Countdown Timer: count down from a duration or to a target date/time."""

import argparse
import re
import sys
import time
from datetime import datetime

UNITS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """Parse '90', '1h30m', '2m 15s', '01:30:00', '05:00' into seconds."""
    text = text.strip().lower()
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)
    if ":" in text:
        parts = [float(p) for p in text.split(":")]
        if len(parts) > 3:
            raise ValueError("use at most HH:MM:SS")
        total = 0.0
        for p in parts:
            total = total * 60 + p
        return total
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*([dhms])", text)
    if not matches or re.sub(r"(\d+(?:\.\d+)?)\s*([dhms])|\s", "", text):
        raise ValueError(f"cannot understand duration: {text!r}")
    return sum(float(n) * UNITS[u] for n, u in matches)


def parse_target(text):
    """Return seconds from now until a datetime like '2026-12-31 23:59'."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return (datetime.strptime(text, fmt) - datetime.now()).total_seconds()
        except ValueError:
            continue
    raise ValueError("target must look like 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM[:SS]'")


def fmt(seconds):
    seconds = max(0, int(round(seconds)))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    base = f"{h:02d}:{m:02d}:{s:02d}"
    return f"{d}d {base}" if d else base


def run(total, quiet=False, bell=True):
    end = time.monotonic() + total
    try:
        while True:
            left = end - time.monotonic()
            if left <= 0:
                break
            if not quiet:
                sys.stdout.write(f"\r  Time left: {fmt(left)}   ")
                sys.stdout.flush()
            time.sleep(min(0.2, left))
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    if not quiet:
        sys.stdout.write(f"\r  Time left: {fmt(0)}   \n")
    print("Time's up!" + ("\a" if bell else ""))
    return 0


def main():
    p = argparse.ArgumentParser(description="Simple countdown timer")
    p.add_argument("duration", nargs="?", help="e.g. 90, 1h30m, 05:00")
    p.add_argument("--until", help="target date/time, e.g. '2026-12-31 23:59'")
    p.add_argument("--quiet", action="store_true", help="no live display")
    p.add_argument("--no-bell", action="store_true")
    a = p.parse_args()
    try:
        if a.until:
            total = parse_target(a.until)
        elif a.duration:
            total = parse_duration(a.duration)
        else:
            total = parse_duration(input("Duration (e.g. 1m30s): "))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if total <= 0:
        print("Error: duration must be in the future.", file=sys.stderr)
        return 2
    print(f"Counting down {fmt(total)}...")
    return run(total, a.quiet, not a.no_bell)


if __name__ == "__main__":
    sys.exit(main())
