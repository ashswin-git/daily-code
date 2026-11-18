# Day 49: Random Decision Maker

A command-line tool that makes a decision for you.

**Difficulty:** Easy

## Features
- Pick randomly from any list of options
- Optional weights (`name:weight`)
- Coin flip and dice roll modes
- Seed option for repeatable results

## Install
No dependencies; Python 3.8+ only.

## Usage
```bash
python main.py pizza burger sushi
python main.py pizza:3 burger:1
python main.py --coin
python main.py --dice 20
```

## Example
```
$ python main.py pizza burger sushi --seed 1
Result: burger
```

## Requirements
Python 3.8+ (standard library only).
