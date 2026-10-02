# Day 4 — Unit Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A polished command-line unit converter for everyday length, mass, temperature, and volume units. Supports one-shot flags and a simple interactive prompt — standard library only.

## Features

- Length: mm, cm, m, km, in, ft, yd, mi
- Mass: mg, g, kg, oz, lb
- Temperature: C, F, K
- Volume: ml, l, tsp, tbsp, cup, floz, pt, qt, gal
- One-shot CLI via `argparse` (`VALUE FROM --to TO`)
- Interactive mode when run with no arguments
- `--list` to print every supported unit by category
- Clear formatted output (e.g. `100 km = 62.1371 mi`)

## Run

```bash
cd day-04-unit-converter
python3 main.py --help
```

## Usage

```bash
# One-shot conversions
python3 main.py 100 km --to mi
python3 main.py 212 F --to C
python3 main.py 5 kg --to lb
python3 main.py 1 gal --to l

# List supported units
python3 main.py --list

# Interactive prompts (category → value → from → to)
python3 main.py
```

## Example

```text
$ python3 main.py 100 km --to mi
100 km = 62.1371 mi

$ python3 main.py 212 F --to C
212 F = 100 C
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)

## License

MIT
