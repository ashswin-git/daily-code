# Day 43: Digital Clock

Difficulty: Easy

A live big-digit clock for your terminal, with 12/24-hour modes and custom UTC offset. Python standard library only.

## Features
- Large ASCII digits updating every second
- 24h or 12h (AM/PM) format
- Optional UTC offset for other timezones
- Shows the full date

## Install
Requires Python 3.8+. No dependencies.

## Usage
```bash
python main.py              # live clock
python main.py --12h        # 12-hour format
python main.py --offset 5.5 # UTC+5:30
python main.py --no-seconds
python main.py --once       # print once and exit
```

## Example
```
###  # #     ###  ###
...
Thursday, 12 November 2026
```

## Requirements
Python 3.8+ (stdlib only).
