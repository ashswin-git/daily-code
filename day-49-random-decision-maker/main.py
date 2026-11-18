"""Random Decision Maker: pick an option, flip a coin, or roll a die."""
import argparse
import random
import sys


def decide(options, seed=None):
    if not options:
        raise ValueError("Provide at least one option")
    rng = random.Random(seed)
    return rng.choice(options)


def weighted_decide(options, seed=None):
    """Options may be 'name:weight'."""
    names, weights = [], []
    for o in options:
        name, _, w = o.rpartition(":")
        if name and w.replace(".", "", 1).isdigit():
            names.append(name)
            weights.append(float(w))
        else:
            names.append(o)
            weights.append(1.0)
    return random.Random(seed).choices(names, weights=weights, k=1)[0]


def main():
    p = argparse.ArgumentParser(description="Let fate decide.")
    p.add_argument("options", nargs="*", help="Options; use name:weight for weighted odds")
    p.add_argument("--coin", action="store_true", help="Flip a coin")
    p.add_argument("--dice", type=int, metavar="SIDES", help="Roll a die with SIDES sides")
    p.add_argument("--seed", type=int, help="Seed for repeatable results")
    a = p.parse_args()
    if a.coin:
        print("Result:", decide(["Heads", "Tails"], a.seed))
    elif a.dice:
        if a.dice < 2:
            sys.exit("Dice needs at least 2 sides")
        print("Result:", decide(list(range(1, a.dice + 1)), a.seed))
    elif a.options:
        print("Result:", weighted_decide(a.options, a.seed))
    else:
        p.error("give options, --coin or --dice")


if __name__ == "__main__":
    main()
