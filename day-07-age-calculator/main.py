#!/usr/bin/env python3
"""Day 7 — Age Calculator.

Exact age in years/months/days, total days lived, weekday you were born,
and a countdown to your next birthday. Standard library only.

Usage:
  python3 main.py 2000-05-17
  python3 main.py 2000-05-17 --on 2030-01-01
  python3 main.py            # interactive
"""

from __future__ import annotations

import argparse
import sys
from calendar import monthrange
from datetime import date

DATE_FMT = "%Y-%m-%d"


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date '{text}' (use YYYY-MM-DD)")


def safe_birthday(year: int, born: date) -> date:
    """Birthday in a given year; Feb 29 falls back to Feb 28 in non-leap years."""
    try:
        return born.replace(year=year)
    except ValueError:
        return date(year, 2, 28)


def add_months(start: date, months: int, anchor_day: int) -> date:
    """Move `start` forward by `months`, clamping the day to the month's length."""
    total = start.month - 1 + months
    year, month = start.year + total // 12, total % 12 + 1
    return date(year, month, min(anchor_day, monthrange(year, month)[1]))


def exact_age(born: date, today: date) -> tuple[int, int, int]:
    """Return (years, months, days) between born and today (calendar-accurate)."""
    years = today.year - born.year
    if safe_birthday(today.year, born) > today:
        years -= 1
    anniversary = safe_birthday(born.year + years, born)
    months = 0
    while add_months(anniversary, months + 1, born.day) <= today:
        months += 1
    days = (today - add_months(anniversary, months, born.day)).days
    return years, months, days


def next_birthday(born: date, today: date) -> date:
    bday = safe_birthday(today.year, born)
    if bday < today:
        bday = safe_birthday(today.year + 1, born)
    return bday


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def report(born: date, today: date) -> str:
    if born > today:
        raise ValueError("birth date is in the future")
    y, m, d = exact_age(born, today)
    total_days = (today - born).days
    nb = next_birthday(born, today)
    until = (nb - today).days
    turning = nb.year - born.year

    lines = [
        "── Age Calculator ──",
        f"  Born:          {born:%d %b %Y} ({born:%A})",
        f"  As of:         {today:%d %b %Y}",
        f"  Age:           {plural(y, 'year')}, {plural(m, 'month')}, {plural(d, 'day')}",
        f"  Days lived:    {total_days:,}",
        f"  Weeks lived:   {total_days // 7:,}",
        f"  Months lived:  {y * 12 + m:,}",
    ]
    if until == 0:
        lines.append(f"  🎂 Happy birthday! You turn {turning} today.")
    else:
        lines.append(
            f"  Next birthday: {nb:%d %b %Y} ({nb:%A}) — {plural(until, 'day')} to go, turning {turning}"
        )
    return "\n".join(lines)


def interactive() -> tuple[date, date]:
    while True:
        raw = input("Birth date (YYYY-MM-DD): ")
        try:
            born = parse_date(raw)
            break
        except argparse.ArgumentTypeError as e:
            print(f"  {e}")
    raw = input("Calculate as of (YYYY-MM-DD, blank = today): ").strip()
    today = parse_date(raw) if raw else date.today()
    return born, today


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exact age + next birthday countdown.")
    parser.add_argument("birthdate", nargs="?", type=parse_date, help="YYYY-MM-DD")
    parser.add_argument("--on", type=parse_date, default=None,
                        help="reference date YYYY-MM-DD (default: today)")
    args = parser.parse_args(argv)

    try:
        if args.birthdate is None:
            born, today = interactive()
        else:
            born, today = args.birthdate, args.on or date.today()
        print(report(born, today))
    except (ValueError, argparse.ArgumentTypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
