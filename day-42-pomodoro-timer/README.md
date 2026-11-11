# Day 42 — Pomodoro Timer

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A terminal Pomodoro timer that alternates work sessions with short and long breaks. Standard library only.

## Features

- Configurable work, short break and long break lengths
- Long break after every N work sessions
- Live countdown, `--quiet` to disable it
- Terminal bell at the end of each session
- Ctrl+C stops cleanly

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py
python main.py --work 50 --short 10 --long 20 --cycles 3
python main.py --work 0.05 --short 0.02 --cycles 2   # quick demo
```

## Example

```
Starting Work #1 (0.05 min)
Work #1      00:00 remaining
Starting Short break (0.02 min)
...
All pomodoros done. Nice work!
```

## Requirements

None beyond Python 3.8+.
