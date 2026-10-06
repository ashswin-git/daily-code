#!/usr/bin/env python3
"""Day 8 — Dice Roller.

Roll dice using tabletop notation like 2d6+3, 4d6kh3, or d20 with
advantage. Standard library only.

Examples:
  python3 main.py 2d6
  python3 main.py 1d20+5 3d8-1
  python3 main.py 4d6kh3 --times 6      # classic stat generation
  python3 main.py d20 --adv              # roll twice, keep higher
  python3 main.py                        # interactive mode
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from dataclasses import dataclass

DICE_RE = re.compile(
    r"^\s*(?P<count>\d*)d(?P<sides>\d+|%)"
    r"(?:k(?P<keep_mode>[hl])(?P<keep>\d+))?"
    r"(?P<mod>[+-]\d+)?\s*$",
    re.IGNORECASE,
)

FACES = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
MAX_DICE = 1000
MAX_SIDES = 1_000_000


@dataclass
class Spec:
    count: int
    sides: int
    keep_mode: str | None
    keep: int | None
    modifier: int
    text: str


@dataclass
class Result:
    spec: Spec
    rolls: list[int]
    kept: list[int]

    @property
    def total(self) -> int:
        return sum(self.kept) + self.spec.modifier


def parse(text: str) -> Spec:
    m = DICE_RE.match(text)
    if not m:
        raise ValueError(f"can't read '{text}' (try 2d6, d20+3, 4d6kh3)")
    count = int(m["count"] or 1)
    sides = 100 if m["sides"] == "%" else int(m["sides"])
    keep = int(m["keep"]) if m["keep"] else None
    mode = m["keep_mode"].lower() if m["keep_mode"] else None
    if not 1 <= count <= MAX_DICE:
        raise ValueError(f"dice count must be 1–{MAX_DICE}")
    if not 2 <= sides <= MAX_SIDES:
        raise ValueError(f"sides must be 2–{MAX_SIDES:,}")
    if keep is not None and not 1 <= keep <= count:
        raise ValueError(f"can only keep 1–{count} dice in '{text}'")
    return Spec(count, sides, mode, keep, int(m["mod"] or 0), text.strip().lower())


def roll(spec: Spec, rng: random.Random) -> Result:
    rolls = [rng.randint(1, spec.sides) for _ in range(spec.count)]
    kept = list(rolls)
    if spec.keep is not None:
        ordered = sorted(rolls, reverse=(spec.keep_mode == "h"))
        kept = ordered[: spec.keep]
    return Result(spec, rolls, kept)


def show_rolls(res: Result) -> str:
    sides = res.spec.sides
    pool = list(res.kept)
    parts = []
    for r in res.rolls:
        face = FACES.get(r, "") if sides == 6 else ""
        label = f"{face}{r}" if face else str(r)
        if r in pool:
            pool.remove(r)
            if sides >= 20 and r == sides:
                label += "!"   # natural max
            elif sides >= 20 and r == 1:
                label += "✗"   # natural 1
            parts.append(label)
        else:
            parts.append(f"~{label}~")  # dropped
    return "[" + ", ".join(parts) + "]"


def describe(res: Result) -> str:
    mod = res.spec.modifier
    mod_txt = f" {'+' if mod > 0 else '-'} {abs(mod)}" if mod else ""
    return f"  {res.spec.text:<10} {show_rolls(res)}{mod_txt}  →  {res.total}"


def stats(spec: Spec) -> str:
    kept = spec.keep or spec.count
    low = kept + spec.modifier
    high = kept * spec.sides + spec.modifier
    if spec.keep is None:
        avg = f"{spec.count * (spec.sides + 1) / 2 + spec.modifier:g}"
    else:
        avg = "n/a"
    return f"range {low}–{high}, average {avg}"


def run(expressions: list[str], times: int, adv: str | None,
        show_stats: bool, rng: random.Random) -> int:
    specs = [parse(e) for e in expressions]
    grand = 0
    for i in range(times):
        if times > 1:
            print(f"Roll {i + 1}:")
        for spec in specs:
            if adv:
                a, b = roll(spec, rng), roll(spec, rng)
                pick = max(a, b, key=lambda r: r.total) if adv == "adv" \
                    else min(a, b, key=lambda r: r.total)
                other = b if pick is a else a
                print(describe(pick) + f"   ({adv}, other: {other.total})")
                grand += pick.total
            else:
                res = roll(spec, rng)
                print(describe(res))
                grand += res.total
    if len(specs) * times > 1:
        print(f"  {'─' * 30}\n  Grand total: {grand}")
    if show_stats:
        for spec in specs:
            print(f"  {spec.text}: {stats(spec)}")
    return grand


def interactive(rng: random.Random) -> None:
    print("── Dice Roller ── (e.g. 2d6+1, d20, 4d6kh3 · blank to quit)")
    while True:
        try:
            line = input("🎲 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            break
        try:
            run(line.split(), 1, None, False, rng)
        except ValueError as exc:
            print(f"  ⚠ {exc}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Roll dice with tabletop notation (NdS, kh/kl, +/-mod).")
    p.add_argument("dice", nargs="*", help="e.g. 2d6, d20+5, 4d6kh3, d%%")
    p.add_argument("-n", "--times", type=int, default=1,
                   help="repeat the whole roll N times")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--adv", action="store_const", const="adv", dest="mode",
                   help="advantage: roll twice, keep higher total")
    g.add_argument("--dis", action="store_const", const="dis", dest="mode",
                   help="disadvantage: roll twice, keep lower total")
    p.add_argument("--stats", action="store_true",
                   help="show min/max/average for each expression")
    p.add_argument("--seed", type=int, help="seed for repeatable rolls")
    args = p.parse_args(argv)

    rng = random.Random(args.seed) if args.seed is not None else random.SystemRandom()
    if not args.dice:
        interactive(rng)
        return 0
    if not 1 <= args.times <= 100:
        p.error("--times must be 1–100")
    try:
        run(args.dice, args.times, args.mode, args.stats, rng)
    except ValueError as exc:
        p.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
