# Day 7 — Age Calculator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tidy command-line age calculator: exact age in years, months, and days, total days/weeks/months lived, the weekday you were born, and a countdown to your next birthday. Standard library only.

## Features

- Calendar-accurate age (handles month lengths and leap years)
- Feb 29 birthdays celebrated on Feb 28 in non-leap years
- Days, weeks, and months lived
- Weekday you were born
- Next birthday date, weekday, and days to go (with a 🎂 on the day itself)
- `--on` flag to calculate age as of any date
- Interactive mode when run with no arguments

## Run

```bash
cd day-07-age-calculator
python3 main.py --help
```

## Usage

```bash
# Age as of today
python3 main.py 2000-05-17

# Age as of a specific date
python3 main.py 2000-05-17 --on 2030-01-01

# Interactive prompts
python3 main.py
```

## Example

```text
$ python3 main.py 2000-05-17 --on 2026-10-05
── Age Calculator ──
  Born:          17 May 2000 (Wednesday)
  As of:         05 Oct 2026
  Age:           26 years, 4 months, 18 days
  Days lived:    9,637
  Weeks lived:   1,376
  Months lived:  316
  Next birthday: 17 May 2027 (Monday) — 224 days to go, turning 27
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)

## License

MIT
