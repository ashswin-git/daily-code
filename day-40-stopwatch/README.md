# Day 40 — Stopwatch

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A terminal stopwatch with lap splits and a fastest/slowest summary. Standard library only.

## Features

- Interactive mode: press Enter for a lap, `q` + Enter to stop
- `--live` shows a continuously updating timer
- `--duration N` runs non-interactively, with optional `--laps` auto-laps
- Millisecond precision using a monotonic clock

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py
python main.py --live
python main.py --duration 3 --laps 2
```

## Example

```bash
$ python main.py --duration 1 --laps 2
  Lap  1  split 00:00:00.333  total 00:00:00.333
  Lap  2  split 00:00:00.334  total 00:00:00.667

Total time: 00:00:01.001
Laps: 2  fastest 00:00:00.333 (#1)  slowest 00:00:00.334 (#2)
```

## Requirements

None beyond the Python standard library.
