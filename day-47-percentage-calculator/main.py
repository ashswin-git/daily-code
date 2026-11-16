#!/usr/bin/env python3
"""Percentage Calculator: common percentage operations from the CLI."""
import sys


def percent_of(p, x):
    return p / 100 * x


def what_percent(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b * 100


def change(old, new):
    if old == 0:
        raise ValueError("Old value cannot be zero")
    return (new - old) / abs(old) * 100


def increase(x, p):
    return x * (1 + p / 100)


def decrease(x, p):
    return x * (1 - p / 100)


def fmt(n):
    return f"{n:.4f}".rstrip("0").rstrip(".")


def run(cmd, args):
    a = [float(v) for v in args]
    if cmd == "of":
        return f"{fmt(a[0])}% of {fmt(a[1])} = {fmt(percent_of(*a))}"
    if cmd == "is":
        return f"{fmt(a[0])} is {fmt(what_percent(*a))}% of {fmt(a[1])}"
    if cmd == "change":
        c = change(*a)
        word = "increase" if c >= 0 else "decrease"
        return f"{fmt(a[0])} -> {fmt(a[1])}: {fmt(abs(c))}% {word}"
    if cmd == "increase":
        return f"{fmt(a[0])} increased by {fmt(a[1])}% = {fmt(increase(*a))}"
    if cmd == "decrease":
        return f"{fmt(a[0])} decreased by {fmt(a[1])}% = {fmt(decrease(*a))}"
    raise ValueError("Unknown command")


USAGE = """Usage:
  python main.py of P X         # P% of X
  python main.py is A B         # A is what % of B
  python main.py change OLD NEW # % change
  python main.py increase X P   # X increased by P%
  python main.py decrease X P   # X decreased by P%"""


def main():
    if len(sys.argv) < 4:
        print(USAGE)
        return 1
    try:
        print(run(sys.argv[1], sys.argv[2:4]))
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
