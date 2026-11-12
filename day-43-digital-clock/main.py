#!/usr/bin/env python3
"""Digital Clock: a live terminal clock with optional 12h format, date, and timezone offset."""
import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

DIGITS = {
    "0": ["###", "# #", "# #", "# #", "###"],
    "1": ["  #", "  #", "  #", "  #", "  #"],
    "2": ["###", "  #", "###", "#  ", "###"],
    "3": ["###", "  #", "###", "  #", "###"],
    "4": ["# #", "# #", "###", "  #", "  #"],
    "5": ["###", "#  ", "###", "  #", "###"],
    "6": ["###", "#  ", "###", "# #", "###"],
    "7": ["###", "  #", "  #", "  #", "  #"],
    "8": ["###", "# #", "###", "# #", "###"],
    "9": ["###", "# #", "###", "  #", "###"],
    ":": ["   ", " # ", "   ", " # ", "   "],
    " ": ["   "] * 5,
    "A": ["###", "# #", "###", "# #", "# #"],
    "P": ["###", "# #", "###", "#  ", "#  "],
    "M": ["# #", "###", "###", "# #", "# #"],
}


def render(text: str) -> str:
    return "\n".join("  ".join(DIGITS[c][r] for c in text) for r in range(5))


def now(offset_hours: float) -> datetime:
    if offset_hours is None:
        return datetime.now()
    return datetime.now(timezone(timedelta(hours=offset_hours)))


def format_time(dt: datetime, twelve: bool, seconds: bool) -> str:
    fmt = ("%I" if twelve else "%H") + ":%M" + (":%S" if seconds else "")
    s = dt.strftime(fmt)
    return s + (" " + dt.strftime("%p") if twelve else "")


def main() -> int:
    p = argparse.ArgumentParser(description="Live digital clock in your terminal")
    p.add_argument("--12h", dest="twelve", action="store_true", help="12-hour format")
    p.add_argument("--no-seconds", action="store_true", help="hide seconds")
    p.add_argument("--offset", type=float, help="UTC offset in hours, e.g. 5.5")
    p.add_argument("--once", action="store_true", help="print once and exit")
    a = p.parse_args()
    try:
        while True:
            dt = now(a.offset)
            out = render(format_time(dt, a.twelve, not a.no_seconds)) + "\n\n" + dt.strftime("%A, %d %B %Y")
            if a.once:
                print(out)
                return 0
            sys.stdout.write("\033[H\033[2J" + out + "\n\nCtrl+C to quit\n")
            sys.stdout.flush()
            time.sleep(1 - dt.microsecond / 1e6)
    except KeyboardInterrupt:
        print("\nBye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
