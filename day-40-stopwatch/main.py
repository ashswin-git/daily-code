#!/usr/bin/env python3
"""Day 40 - Stopwatch.

A terminal stopwatch with laps. Standard library only.

Usage:
  python main.py              # interactive: Enter = lap, q + Enter = stop
  python main.py --live       # live display; Ctrl+C stops
  python main.py --duration 3 # run non-interactively for 3 seconds
"""

from __future__ import annotations

import argparse
import sys
import threading
import time


def format_elapsed(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm."""
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


class Stopwatch:
    def __init__(self, clock=time.perf_counter):
        self._clock = clock
        self._start = None
        self._accum = 0.0
        self.laps: list[float] = []  # cumulative times at each lap

    @property
    def running(self) -> bool:
        return self._start is not None

    def start(self) -> None:
        if not self.running:
            self._start = self._clock()

    def stop(self) -> None:
        if self.running:
            self._accum += self._clock() - self._start
            self._start = None

    def reset(self) -> None:
        self._start = None
        self._accum = 0.0
        self.laps.clear()

    def elapsed(self) -> float:
        extra = self._clock() - self._start if self.running else 0.0
        return self._accum + extra

    def lap(self) -> tuple[int, float, float]:
        """Record a lap; return (number, lap_time, total_time)."""
        total = self.elapsed()
        prev = self.laps[-1] if self.laps else 0.0
        self.laps.append(total)
        return len(self.laps), total - prev, total


def print_lap(n: int, split: float, total: float) -> None:
    print(f"  Lap {n:>2}  split {format_elapsed(split)}  total {format_elapsed(total)}")


def summary(sw: Stopwatch) -> None:
    print(f"\nTotal time: {format_elapsed(sw.elapsed())}")
    if sw.laps:
        splits = [b - a for a, b in zip([0.0] + sw.laps[:-1], sw.laps)]
        fast, slow = min(splits), max(splits)
        print(f"Laps: {len(splits)}  fastest {format_elapsed(fast)} (#{splits.index(fast)+1})"
              f"  slowest {format_elapsed(slow)} (#{splits.index(slow)+1})")


def run_interactive(sw: Stopwatch) -> None:
    print("Stopwatch started. Press Enter for a lap, 'q' + Enter to stop.")
    sw.start()
    try:
        for line in sys.stdin:
            if line.strip().lower() in ("q", "quit", "s", "stop"):
                break
            print_lap(*sw.lap())
    except KeyboardInterrupt:
        pass
    sw.stop()
    summary(sw)


def run_live(sw: Stopwatch) -> None:
    print("Live stopwatch. Press Enter for a lap, Ctrl+C to stop.")
    stop = threading.Event()

    def reader():
        for _ in sys.stdin:
            print("\r" + " " * 30 + "\r", end="")
            print_lap(*sw.lap())
        stop.set()

    threading.Thread(target=reader, daemon=True).start()
    sw.start()
    try:
        while not stop.is_set():
            print("\r" + format_elapsed(sw.elapsed()), end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    sw.stop()
    print()
    summary(sw)


def run_duration(sw: Stopwatch, seconds: float, laps: int) -> None:
    sw.start()
    interval = seconds / (laps + 1) if laps else seconds
    for _ in range(laps):
        time.sleep(interval)
        print_lap(*sw.lap())
    time.sleep(interval)
    sw.stop()
    summary(sw)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Terminal stopwatch with laps.")
    p.add_argument("--live", action="store_true", help="show a live updating display")
    p.add_argument("--duration", type=float, help="run for N seconds, then stop")
    p.add_argument("--laps", type=int, default=0, help="with --duration, auto-record N laps")
    args = p.parse_args(argv)
    sw = Stopwatch()
    if args.duration is not None:
        if args.duration <= 0:
            p.error("--duration must be positive")
        run_duration(sw, args.duration, max(args.laps, 0))
    elif args.live:
        run_live(sw)
    else:
        run_interactive(sw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
