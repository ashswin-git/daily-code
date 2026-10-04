#!/usr/bin/env python3
"""Day 6 — BMI Calculator: body mass index with metric and imperial units."""

from __future__ import annotations

import argparse
import sys

# WHO adult BMI categories (kg/m²)
CATEGORIES: tuple[tuple[float, str], ...] = (
    (18.5, "Underweight"),
    (25.0, "Normal weight"),
    (30.0, "Overweight"),
    (float("inf"), "Obesity"),
)


def classify(bmi: float) -> str:
    """Return WHO adult category for a BMI value."""
    for upper, label in CATEGORIES:
        if bmi < upper:
            return label
    return "Obesity"


def bmi_metric(weight_kg: float, height_m: float) -> float:
    """BMI = weight (kg) / height (m)²."""
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    if height_m <= 0:
        raise ValueError("height must be positive")
    return weight_kg / (height_m ** 2)


def bmi_imperial(weight_lb: float, height_in: float) -> float:
    """BMI = 703 × weight (lb) / height (in)²."""
    if weight_lb <= 0:
        raise ValueError("weight must be positive")
    if height_in <= 0:
        raise ValueError("height must be positive")
    return 703.0 * weight_lb / (height_in ** 2)


def feet_inches_to_inches(feet: float, inches: float = 0.0) -> float:
    """Convert feet + inches to total inches."""
    total = feet * 12.0 + inches
    if total <= 0:
        raise ValueError("height must be positive")
    return total


def format_result(
    bmi: float,
    weight_label: str,
    height_label: str,
    system: str,
) -> str:
    category = classify(bmi)
    return "\n".join(
        [
            "── BMI Calculator ──",
            f"  System:   {system}",
            f"  Weight:   {weight_label}",
            f"  Height:   {height_label}",
            f"  BMI:      {bmi:.1f}",
            f"  Category: {category}",
        ]
    )


def interactive() -> int:
    print("BMI Calculator — interactive mode (Ctrl+C to quit)\n")
    try:
        while True:
            system = input("Units — metric (kg/m) or imperial (lb/in)? [m/i]: ").strip().lower()
            if system in ("m", "metric", "kg"):
                try:
                    weight = float(input("Weight (kg): ").strip().replace(",", ""))
                    height_cm = float(input("Height (cm): ").strip().replace(",", ""))
                    height_m = height_cm / 100.0
                    bmi = bmi_metric(weight, height_m)
                    print()
                    print(
                        format_result(
                            bmi,
                            f"{weight:g} kg",
                            f"{height_cm:g} cm ({height_m:.2f} m)",
                            "metric",
                        )
                    )
                except ValueError as err:
                    print(f"  Error: {err}\n")
                    continue
            elif system in ("i", "imperial", "lb", "us"):
                try:
                    weight = float(input("Weight (lb): ").strip().replace(",", ""))
                    height_raw = input("Height (e.g. 5'10 or 70 for inches): ").strip()
                    height_in = parse_imperial_height(height_raw)
                    bmi = bmi_imperial(weight, height_in)
                    feet = int(height_in // 12)
                    inches = height_in % 12
                    print()
                    print(
                        format_result(
                            bmi,
                            f"{weight:g} lb",
                            f"{feet}'{inches:g}\" ({height_in:g} in)",
                            "imperial",
                        )
                    )
                except ValueError as err:
                    print(f"  Error: {err}\n")
                    continue
            else:
                print("  Enter m/metric or i/imperial.\n")
                continue

            print()
            if input("Calculate another? [y/N]: ").strip().lower() not in ("y", "yes"):
                print("Bye!")
                return 0
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        return 0


def parse_imperial_height(raw: str) -> float:
    """Parse '5\\'10', '5 10', '5ft 10in', or plain inches."""
    s = raw.strip().lower().replace('"', "").replace("in", "").replace("ft", "'")
    if "'" in s:
        parts = s.split("'", 1)
        feet = float(parts[0].strip() or 0)
        inches = float(parts[1].strip() or 0)
        return feet_inches_to_inches(feet, inches)
    # space-separated feet inches, e.g. "5 10"
    tokens = s.replace(",", " ").split()
    if len(tokens) == 2:
        return feet_inches_to_inches(float(tokens[0]), float(tokens[1]))
    if len(tokens) == 1:
        return float(tokens[0])
    raise ValueError(f"cannot parse height: {raw!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Calculate Body Mass Index (BMI) with metric or imperial units.",
        epilog=(
            "Examples:\n"
            "  python3 main.py --kg 70 --cm 175\n"
            "  python3 main.py --lb 154 --ft 5 --in 9\n"
            "  python3 main.py --lb 154 --inches 69\n"
            "  python3 main.py            # interactive\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    metric = parser.add_argument_group("metric")
    metric.add_argument("--kg", type=float, metavar="KG", help="Weight in kilograms")
    metric.add_argument("--cm", type=float, metavar="CM", help="Height in centimeters")
    metric.add_argument("--m", type=float, metavar="M", help="Height in meters (alt to --cm)")

    imperial = parser.add_argument_group("imperial")
    imperial.add_argument("--lb", type=float, metavar="LB", help="Weight in pounds")
    imperial.add_argument("--ft", type=float, metavar="FT", help="Height feet (with --in)")
    imperial.add_argument(
        "--in", dest="inches_part", type=float, default=0.0, metavar="IN",
        help="Extra inches when used with --ft",
    )
    imperial.add_argument(
        "--inches", type=float, metavar="IN",
        help="Total height in inches (alt to --ft/--in)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    metric_given = args.kg is not None or args.cm is not None or args.m is not None
    imperial_given = (
        args.lb is not None
        or args.ft is not None
        or args.inches is not None
        or (args.inches_part and args.inches_part != 0.0)
    )

    if not metric_given and not imperial_given:
        return interactive()

    if metric_given and imperial_given:
        parser.error("use either metric (--kg/--cm/--m) or imperial (--lb/--ft/--in/--inches), not both")

    try:
        if metric_given:
            if args.kg is None:
                parser.error("--kg is required for metric mode")
            if args.cm is not None and args.m is not None:
                parser.error("provide --cm or --m, not both")
            if args.cm is not None:
                height_m = args.cm / 100.0
                height_label = f"{args.cm:g} cm ({height_m:.2f} m)"
            elif args.m is not None:
                height_m = args.m
                height_label = f"{args.m:g} m"
            else:
                parser.error("provide --cm or --m with --kg")
            bmi = bmi_metric(args.kg, height_m)
            print(format_result(bmi, f"{args.kg:g} kg", height_label, "metric"))
            return 0

        # imperial
        if args.lb is None:
            parser.error("--lb is required for imperial mode")
        if args.inches is not None and args.ft is not None:
            parser.error("provide --inches or --ft/--in, not both")
        if args.inches is not None:
            height_in = args.inches
        elif args.ft is not None:
            height_in = feet_inches_to_inches(args.ft, args.inches_part)
        else:
            parser.error("provide --inches or --ft (optional --in) with --lb")
        feet = int(height_in // 12)
        rem = height_in % 12
        height_label = f"{feet}'{rem:g}\" ({height_in:g} in)"
        bmi = bmi_imperial(args.lb, height_in)
        print(format_result(bmi, f"{args.lb:g} lb", height_label, "imperial"))
        return 0
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
