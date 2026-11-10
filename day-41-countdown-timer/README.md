# Day 41 — Countdown Timer

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A terminal countdown timer. Count down from a duration or to a specific date and time. Standard library only.

## Features

- Flexible durations: `90`, `1h30m`, `2m 15s`, `05:00`, `01:30:00`
- `--until` counts down to a calendar date/time
- Live display that updates in place, `--quiet` to disable it
- Terminal bell when time is up (`--no-bell` to mute)
- Ctrl+C cancels cleanly

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py 1m30s
python main.py 05:00 --no-bell
python main.py --until "2026-12-31 23:59"
python main.py            # asks for a duration
```

## Example

```text
$ python main.py 3s
Counting down 00:00:03...
  Time left: 00:00:00
Time's up!
```

## Requirements

Python 3.8+. No third-party packages.
