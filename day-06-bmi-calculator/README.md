# Day 6 — BMI Calculator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A polished command-line Body Mass Index (BMI) calculator with metric and imperial units. One-shot flags or interactive prompts — standard library only. Categories follow WHO adult BMI ranges.

## Features

- Metric: weight in **kg**, height in **cm** or **m**
- Imperial: weight in **lb**, height as **ft+in** or total **inches**
- WHO categories: Underweight / Normal weight / Overweight / Obesity
- One-shot CLI via `argparse`
- Interactive mode when run with no arguments
- Clear formatted breakdown (inputs → BMI → category)

## Run

```bash
cd day-06-bmi-calculator
python3 main.py --help
```

## Usage

```bash
# Metric
python3 main.py --kg 70 --cm 175
python3 main.py --kg 70 --m 1.75

# Imperial
python3 main.py --lb 154 --ft 5 --in 9
python3 main.py --lb 154 --inches 69

# Interactive prompts
python3 main.py
```

## Example

```text
$ python3 main.py --kg 70 --cm 175
── BMI Calculator ──
  System:   metric
  Weight:   70 kg
  Height:   175 cm (1.75 m)
  BMI:      22.9
  Category: Normal weight

$ python3 main.py --lb 154 --ft 5 --in 9
── BMI Calculator ──
  System:   imperial
  Weight:   154 lb
  Height:   5'9" (69 in)
  BMI:      22.7
  Category: Normal weight
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)

## License

MIT
