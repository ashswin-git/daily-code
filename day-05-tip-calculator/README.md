# Day 5 — Tip Calculator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A polished command-line tip calculator for everyday dining math. Enter a bill, choose a tip percent (presets or custom), optionally split among friends — one-shot flags or interactive prompts. Standard library only.

## Features

- Bill amount with clear 2-decimal money formatting
- Tip percent: presets **10 / 15 / 18 / 20 / 25** or any custom value
- Split the tip and total among **N** people
- One-shot CLI via `argparse` (`BILL --tip PERCENT [--people N]`)
- Interactive mode when run with no arguments
- Optional `--currency` symbol (default `$`)
- Clean breakdown: bill → tip → total → per-person shares

## Run

```bash
cd day-05-tip-calculator
python3 main.py --help
```

## Usage

```bash
# One-shot calculations
python3 main.py 86.50 --tip 18
python3 main.py 120 --tip 20 --people 4
python3 main.py 50 --tip 15 --currency ₹

# Interactive prompts (bill → tip % → people)
python3 main.py
```

## Example

```text
$ python3 main.py 86.50 --tip 18
── Tip Calculator ──
  Bill:          $86.50
  Tip:           18% → $15.57
  Total:         $102.07
  You pay:       $102.07

$ python3 main.py 120 --tip 20 --people 4
── Tip Calculator ──
  Bill:          $120.00
  Tip:           20% → $24.00
  Total:         $144.00
  Split (4):
    Tip each:   $6.00
    Total each: $36.00
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)

## License

MIT
