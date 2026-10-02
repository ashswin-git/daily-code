#!/usr/bin/env python3
"""Day 4 — Unit Converter: convert length, mass, temperature, and volume."""

from __future__ import annotations

import argparse
import sys
# ---------------------------------------------------------------------------
# Conversion tables (to / from a SI base unit per category)
# ---------------------------------------------------------------------------

LENGTH_TO_M: dict[str, float] = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
    "in": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,
    "mi": 1609.344,
}

MASS_TO_KG: dict[str, float] = {
    "mg": 1e-6,
    "g": 0.001,
    "kg": 1.0,
    "oz": 0.028349523125,
    "lb": 0.45359237,
}

VOLUME_TO_L: dict[str, float] = {
    "ml": 0.001,
    "l": 1.0,
    "tsp": 0.00492892159375,
    "tbsp": 0.01478676478125,
    "cup": 0.2365882365,
    "floz": 0.0295735295625,
    "pt": 0.473176473,
    "qt": 0.946352946,
    "gal": 3.785411784,
}

TEMP_UNITS = ("c", "f", "k")

CATEGORIES: dict[str, dict[str, float] | tuple[str, ...]] = {
    "length": LENGTH_TO_M,
    "mass": MASS_TO_KG,
    "temperature": TEMP_UNITS,
    "volume": VOLUME_TO_L,
}

# Flat lookup: unit -> category name
UNIT_CATEGORY: dict[str, str] = {}
for _cat, _units in CATEGORIES.items():
    if isinstance(_units, dict):
        for _u in _units:
            UNIT_CATEGORY[_u] = _cat
    else:
        for _u in _units:
            UNIT_CATEGORY[_u] = _cat


def normalize_unit(unit: str) -> str:
    return unit.strip().lower()


def convert_linear(value: float, from_u: str, to_u: str, table: dict[str, float]) -> float:
    base = value * table[from_u]
    return base / table[to_u]


def c_to_k(c: float) -> float:
    return c + 273.15


def k_to_c(k: float) -> float:
    return k - 273.15


def f_to_c(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def convert_temperature(value: float, from_u: str, to_u: str) -> float:
    from_u, to_u = from_u.lower(), to_u.lower()
    if from_u == to_u:
        return value
    # Normalize to Celsius
    if from_u == "c":
        c = value
    elif from_u == "f":
        c = f_to_c(value)
    elif from_u == "k":
        c = k_to_c(value)
    else:
        raise ValueError(f"unknown temperature unit: {from_u}")

    if to_u == "c":
        return c
    if to_u == "f":
        return c_to_f(c)
    if to_u == "k":
        return c_to_k(c)
    raise ValueError(f"unknown temperature unit: {to_u}")


def convert(value: float, from_unit: str, to_unit: str) -> tuple[float, str]:
    """Convert value. Returns (result, category)."""
    from_u = normalize_unit(from_unit)
    to_u = normalize_unit(to_unit)

    if from_u not in UNIT_CATEGORY:
        raise ValueError(f"unsupported unit: {from_unit!r}")
    if to_u not in UNIT_CATEGORY:
        raise ValueError(f"unsupported unit: {to_unit!r}")

    cat_from = UNIT_CATEGORY[from_u]
    cat_to = UNIT_CATEGORY[to_u]
    if cat_from != cat_to:
        raise ValueError(
            f"cannot convert {from_u} ({cat_from}) to {to_u} ({cat_to}) — different categories"
        )

    if cat_from == "temperature":
        result = convert_temperature(value, from_u, to_u)
    elif cat_from == "length":
        result = convert_linear(value, from_u, to_u, LENGTH_TO_M)
    elif cat_from == "mass":
        result = convert_linear(value, from_u, to_u, MASS_TO_KG)
    elif cat_from == "volume":
        result = convert_linear(value, from_u, to_u, VOLUME_TO_L)
    else:
        raise ValueError(f"unknown category: {cat_from}")

    return result, cat_from


def format_number(n: float) -> str:
    """Pretty-print: trim trailing zeros, keep useful precision."""
    if abs(n) >= 1e6 or (0 < abs(n) < 1e-4):
        return f"{n:.6g}"
    text = f"{n:.6f}".rstrip("0").rstrip(".")
    return text if text else "0"


def format_result(value: float, from_unit: str, result: float, to_unit: str) -> str:
    fu = normalize_unit(from_unit)
    tu = normalize_unit(to_unit)
    # Preserve common display casing for temperature
    display = {"c": "C", "f": "F", "k": "K"}
    fu_out = display.get(fu, fu)
    tu_out = display.get(tu, tu)
    return f"{format_number(value)} {fu_out} = {format_number(result)} {tu_out}"


def list_units() -> str:
    lines = ["Supported units by category:", ""]
    order = ("length", "mass", "temperature", "volume")
    labels = {
        "length": "Length (base: meter)",
        "mass": "Mass (base: kilogram)",
        "temperature": "Temperature",
        "volume": "Volume (base: liter)",
    }
    for cat in order:
        units = CATEGORIES[cat]
        if isinstance(units, dict):
            names = ", ".join(units.keys())
        else:
            names = ", ".join(u.upper() if u in TEMP_UNITS else u for u in units)
        lines.append(f"  {labels[cat]}")
        lines.append(f"    {names}")
        lines.append("")
    lines.append("Temperature: use C, F, or K (case-insensitive).")
    return "\n".join(lines).rstrip() + "\n"


def interactive() -> int:
    print("Unit Converter — interactive mode (Ctrl+C to quit)\n")
    print(list_units())
    try:
        while True:
            category = input("Category [length/mass/temperature/volume]: ").strip().lower()
            if category not in CATEGORIES:
                print(f"  Unknown category: {category!r}. Try again.\n")
                continue

            units = CATEGORIES[category]
            if isinstance(units, dict):
                unit_hint = ", ".join(units.keys())
            else:
                unit_hint = ", ".join(u.upper() for u in units)
            print(f"  Units: {unit_hint}")

            raw = input("Value: ").strip()
            try:
                value = float(raw)
            except ValueError:
                print(f"  Not a number: {raw!r}\n")
                continue

            from_u = input("From unit: ").strip()
            to_u = input("To unit: ").strip()
            try:
                result, _ = convert(value, from_u, to_u)
            except ValueError as err:
                print(f"  Error: {err}\n")
                continue

            print(f"  → {format_result(value, from_u, result, to_u)}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Convert between common length, mass, temperature, and volume units.",
        epilog=(
            "Examples:\n"
            "  python3 main.py 100 km --to mi\n"
            "  python3 main.py 212 F --to C\n"
            "  python3 main.py 5 kg --to lb\n"
            "  python3 main.py --list\n"
            "  python3 main.py            # interactive\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "value",
        nargs="?",
        type=float,
        help="Numeric value to convert",
    )
    parser.add_argument(
        "from_unit",
        nargs="?",
        help="Source unit (e.g. km, F, kg)",
    )
    parser.add_argument(
        "--to",
        "-t",
        dest="to_unit",
        metavar="UNIT",
        help="Target unit (e.g. mi, C, lb)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all supported units by category",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print(list_units(), end="")
        return 0

    # No args → interactive
    if args.value is None and args.from_unit is None and args.to_unit is None:
        return interactive()

    if args.value is None or args.from_unit is None or args.to_unit is None:
        parser.error("provide VALUE FROM_UNIT --to TO_UNIT, or use --list, or run with no args")

    try:
        result, _ = convert(args.value, args.from_unit, args.to_unit)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    print(format_result(args.value, args.from_unit, result, args.to_unit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
