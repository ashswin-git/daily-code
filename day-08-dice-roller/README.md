# Day 8 — Dice Roller

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A command-line dice roller that speaks tabletop notation: `2d6+3`, `d20`, `4d6kh3`, `d%`. Roll several expressions at once, repeat rolls, roll with advantage or disadvantage, and see the range and average for any roll. Standard library only.

## Features

- Standard `NdS` notation with `+`/`-` modifiers (`3d8-1`, `d20+5`)
- Keep highest / lowest dice (`4d6kh3`, `2d20kl1`)
- Percentile dice with `d%`
- `--adv` / `--dis` to roll twice and keep the higher or lower total
- `--times N` to repeat a roll (great for stat blocks)
- `--stats` shows min, max, and average
- Dice faces for d6 (⚀–⚅), dropped dice shown as `~x~`, natural max/1 flagged on d20+
- `--seed` for repeatable rolls, interactive mode when run with no arguments

## Run

```bash
cd day-08-dice-roller
python3 main.py --help
```

## Usage

```bash
python3 main.py 2d6
python3 main.py 1d20+5 3d8-1 --stats
python3 main.py 4d6kh3 --times 6     # classic D&D stat generation
python3 main.py d20 --adv
python3 main.py                      # interactive prompt
```

## Example

```text
$ python3 main.py 1d20+5 3d8-1 --stats --seed 7
  1d20+5     [11] + 5  →  16
  3d8-1      [3, 7, 1] - 1  →  10
  ──────────────────────────────
  Grand total: 26
  1d20+5: range 6–25, average 15.5
  3d8-1: range 2–23, average 12.5
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)

## License

MIT
