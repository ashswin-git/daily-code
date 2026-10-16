#!/usr/bin/env python3
"""Day 18 — Random Number Generator.

Generate random integers, floats, or pick lottery-style unique numbers.
Supports a reproducible --seed or cryptographically secure --secure mode.
Standard library only.
"""

from __future__ import annotations

import argparse
import math
import random
import secrets
import sys
from typing import Sequence


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate random numbers (int, float, or unique lottery picks).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s                          # one int 1..100
  %(prog)s -n 5                     # five ints 1..100
  %(prog)s --min 10 --max 50 -n 3
  %(prog)s --float --min 0 --max 1 -n 5 -d 4
  %(prog)s --unique -n 6 --min 1 --max 49   # lottery draw
  %(prog)s --secure -n 3 --min 1 --max 1_000_000
  %(prog)s --seed 42 -n 5           # reproducible
  %(prog)s --gauss 100 15 -n 8      # normal distribution
""",
    )
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="how many numbers to generate (default: 1)",
    )
    p.add_argument(
        "--min",
        type=float,
        default=1.0,
        dest="lo",
        metavar="A",
        help="inclusive lower bound (default: 1)",
    )
    p.add_argument(
        "--max",
        type=float,
        default=100.0,
        dest="hi",
        metavar="B",
        help="inclusive upper bound for ints / exclusive for floats (default: 100)",
    )
    p.add_argument(
        "-f",
        "--float",
        action="store_true",
        dest="as_float",
        help="generate floating-point numbers instead of ints",
    )
    p.add_argument(
        "-d",
        "--decimals",
        type=int,
        default=6,
        metavar="D",
        help="decimal places for --float output (default: 6)",
    )
    p.add_argument(
        "-u",
        "--unique",
        action="store_true",
        help="no repeats (lottery / sample without replacement; ints only)",
    )
    p.add_argument(
        "--secure",
        action="store_true",
        help="use secrets module (cryptographically strong; ignores --seed)",
    )
    p.add_argument(
        "--seed",
        type=str,
        default=None,
        help="seed for reproducible results (ignored with --secure)",
    )
    p.add_argument(
        "--gauss",
        nargs=2,
        type=float,
        metavar=("MEAN", "STDEV"),
        help="draw from a normal distribution (mean, stdev); implies --float",
    )
    p.add_argument(
        "--sort",
        action="store_true",
        help="sort results ascending",
    )
    p.add_argument(
        "--sep",
        default="\n",
        metavar="S",
        help="separator between values (default: newline; use ',' for CSV)",
    )
    p.add_argument(
        "--sum",
        action="store_true",
        dest="show_sum",
        help="also print the sum of all generated numbers",
    )
    return p.parse_args(argv)


def validate(args: argparse.Namespace) -> None:
    if args.count < 1:
        sys.exit("error: --count must be at least 1")
    if args.decimals < 0:
        sys.exit("error: --decimals must be >= 0")
    if args.gauss is not None:
        mean, stdev = args.gauss
        if stdev < 0:
            sys.exit("error: gauss stdev must be >= 0")
        args.as_float = True
        return
    if args.lo > args.hi:
        sys.exit(f"error: --min ({args.lo}) cannot be greater than --max ({args.hi})")
    if not args.as_float:
        # int mode: bounds must be whole numbers after truncation
        lo_i, hi_i = int(math.floor(args.lo)), int(math.floor(args.hi))
        if lo_i > hi_i:
            sys.exit("error: integer range is empty after flooring bounds")
        span = hi_i - lo_i + 1
        if args.unique and args.count > span:
            sys.exit(
                f"error: cannot pick {args.count} unique ints from a range of {span}"
            )


def make_rng(args: argparse.Namespace) -> random.Random | None:
    """Return a Random instance, or None when using secrets."""
    if args.secure:
        return None
    rng = random.Random()
    if args.seed is not None:
        rng.seed(args.seed)
    return rng


def gen_ints(args: argparse.Namespace, rng: random.Random | None) -> list[int]:
    lo = int(math.floor(args.lo))
    hi = int(math.floor(args.hi))
    if args.unique:
        population = range(lo, hi + 1)
        if rng is None:
            # secrets has no sample; shuffle a copy with SystemRandom
            pool = list(population)
            secrets.SystemRandom().shuffle(pool)
            return pool[: args.count]
        return rng.sample(list(population), args.count)
    out: list[int] = []
    for _ in range(args.count):
        if rng is None:
            out.append(secrets.randbelow(hi - lo + 1) + lo)
        else:
            out.append(rng.randint(lo, hi))
    return out


def gen_floats(args: argparse.Namespace, rng: random.Random | None) -> list[float]:
    out: list[float] = []
    for _ in range(args.count):
        if args.gauss is not None:
            mean, stdev = args.gauss
            if rng is None:
                # Box-Muller via SystemRandom
                u1 = secrets.SystemRandom().random()
                u2 = secrets.SystemRandom().random()
                z = math.sqrt(-2.0 * math.log(max(u1, 1e-300))) * math.cos(
                    2.0 * math.pi * u2
                )
                out.append(mean + stdev * z)
            else:
                out.append(rng.gauss(mean, stdev))
        else:
            lo, hi = args.lo, args.hi
            if rng is None:
                # map [0,1) onto [lo, hi)
                out.append(lo + (hi - lo) * secrets.SystemRandom().random())
            else:
                out.append(rng.uniform(lo, hi))
    return out


def format_values(values: list[int] | list[float], args: argparse.Namespace) -> str:
    if args.as_float or args.gauss is not None:
        texts = [f"{v:.{args.decimals}f}" for v in values]
    else:
        texts = [str(v) for v in values]
    sep = args.sep.encode("utf-8").decode("unicode_escape") if "\\" in args.sep else args.sep
    return sep.join(texts)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate(args)
    rng = make_rng(args)

    if args.as_float or args.gauss is not None:
        if args.unique:
            sys.exit("error: --unique only works with integers (omit --float / --gauss)")
        values: list[int] | list[float] = gen_floats(args, rng)
    else:
        values = gen_ints(args, rng)

    if args.sort:
        values = sorted(values)  # type: ignore[assignment]

    print(format_values(values, args))
    if args.show_sum:
        total = sum(values)
        if args.as_float or args.gauss is not None:
            print(f"sum: {total:.{args.decimals}f}", file=sys.stderr)
        else:
            print(f"sum: {total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
