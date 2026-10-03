#!/usr/bin/env python3
"""Day 5 — Tip Calculator: bill, tip percent, and split among people."""

from __future__ import annotations

import argparse
import sys

PRESET_TIPS = (10, 15, 18, 20, 25)


def money(amount: float, currency: str = "$") -> str:
    """Format money with 2 decimals and a currency symbol."""
    return f"{currency}{amount:,.2f}"


def calculate(bill: float, tip_percent: float, people: int = 1) -> tuple[float, float, float, float]:
    """Return (tip_amount, total, per_person_tip, per_person_total)."""
    if bill < 0:
        raise ValueError("bill amount cannot be negative")
    if tip_percent < 0:
        raise ValueError("tip percent cannot be negative")
    if people < 1:
        raise ValueError("people must be at least 1")
    tip_amount = bill * tip_percent / 100.0
    total = bill + tip_amount
    return tip_amount, total, tip_amount / people, total / people


def format_breakdown(
    bill: float,
    tip_percent: float,
    people: int,
    tip_amount: float,
    total: float,
    per_tip: float,
    per_total: float,
    currency: str = "$",
) -> str:
    lines = [
        "── Tip Calculator ──",
        f"  Bill:          {money(bill, currency)}",
        f"  Tip:           {tip_percent:g}% → {money(tip_amount, currency)}",
        f"  Total:         {money(total, currency)}",
    ]
    if people > 1:
        lines += [
            f"  Split ({people}):",
            f"    Tip each:   {money(per_tip, currency)}",
            f"    Total each: {money(per_total, currency)}",
        ]
    else:
        lines.append(f"  You pay:       {money(total, currency)}")
    return "\n".join(lines)


def interactive(currency: str = "$") -> int:
    print("Tip Calculator — interactive mode (Ctrl+C to quit)\n")
    presets = "/".join(str(p) for p in PRESET_TIPS)
    try:
        while True:
            raw_bill = input(f"Bill amount ({currency}): ").strip().replace(",", "")
            try:
                bill = float(raw_bill)
                if bill < 0:
                    raise ValueError
            except ValueError:
                print(f"  Invalid bill: {raw_bill!r}\n")
                continue

            raw_tip = input(f"Tip % [{presets} or custom]: ").strip().rstrip("%")
            try:
                tip_percent = float(raw_tip)
                if tip_percent < 0:
                    raise ValueError
            except ValueError:
                print(f"  Invalid tip: {raw_tip!r}\n")
                continue

            raw_people = input("Split among how many people? [1]: ").strip()
            try:
                people = 1 if not raw_people else int(raw_people)
                if people < 1:
                    raise ValueError
            except ValueError:
                print(f"  Invalid people count: {raw_people!r}\n")
                continue

            tip_amount, total, per_tip, per_total = calculate(bill, tip_percent, people)
            print()
            print(format_breakdown(bill, tip_percent, people, tip_amount, total, per_tip, per_total, currency))
            print()
            if input("Calculate another? [y/N]: ").strip().lower() not in ("y", "yes"):
                print("Bye!")
                return 0
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Calculate tip and split a bill among friends.",
        epilog=(
            "Examples:\n"
            "  python3 main.py 86.50 --tip 18\n"
            "  python3 main.py 120 --tip 20 --people 4\n"
            "  python3 main.py 50 --tip 15 --currency ₹\n"
            "  python3 main.py            # interactive\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("bill", nargs="?", type=float, help="Bill amount before tip")
    parser.add_argument(
        "--tip", "-t", type=float, metavar="PERCENT",
        help=f"Tip percent (common: {', '.join(str(p) for p in PRESET_TIPS)})",
    )
    parser.add_argument(
        "--people", "-p", type=int, default=1, metavar="N",
        help="Split the total among N people (default: 1)",
    )
    parser.add_argument(
        "--currency", "-c", default="$", metavar="SYM",
        help="Currency symbol for output (default: $)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.bill is None:
        if args.tip is not None:
            parser.error("provide BILL with --tip, or run with no args for interactive mode")
        return interactive(currency=args.currency)

    if args.tip is None:
        parser.error("provide --tip PERCENT with BILL, or run with no args for interactive mode")

    try:
        tip_amount, total, per_tip, per_total = calculate(args.bill, args.tip, args.people)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    print(format_breakdown(
        args.bill, args.tip, args.people, tip_amount, total, per_tip, per_total, args.currency,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
