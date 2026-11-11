#!/usr/bin/env python3
"""Pomodoro Timer: alternating work and break sessions in the terminal."""

import argparse
import sys
import time


def fmt(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def run_session(label, minutes, quiet, tick=1.0):
    total = int(minutes * 60)
    end = time.monotonic() + total
    while True:
        left = max(0, end - time.monotonic())
        if not quiet:
            sys.stdout.write(f"\r{label:<12} {fmt(left + 0.999 if left else 0)} remaining ")
            sys.stdout.flush()
        if left <= 0:
            break
        time.sleep(min(tick, left))
    if not quiet:
        sys.stdout.write("\n")
    sys.stdout.write("\a")
    sys.stdout.flush()


def plan(cycles, work, short, long_, every):
    """Yield (label, minutes) for the whole pomodoro plan."""
    for i in range(1, cycles + 1):
        yield f"Work #{i}", work
        if i == cycles:
            break
        if i % every == 0:
            yield "Long break", long_
        else:
            yield "Short break", short


def main():
    p = argparse.ArgumentParser(description="Simple Pomodoro timer")
    p.add_argument("--work", type=float, default=25, help="work minutes (default 25)")
    p.add_argument("--short", type=float, default=5, help="short break minutes (default 5)")
    p.add_argument("--long", type=float, default=15, help="long break minutes (default 15)")
    p.add_argument("--cycles", type=int, default=4, help="work sessions (default 4)")
    p.add_argument("--every", type=int, default=4, help="long break after N sessions")
    p.add_argument("--quiet", action="store_true", help="no live display")
    a = p.parse_args()
    if min(a.work, a.short, a.long) <= 0 or a.cycles < 1 or a.every < 1:
        p.error("durations and counts must be positive")
    try:
        for label, mins in plan(a.cycles, a.work, a.short, a.long, a.every):
            print(f"Starting {label} ({mins:g} min)")
            run_session(label, mins, a.quiet)
        print("All pomodoros done. Nice work!")
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
