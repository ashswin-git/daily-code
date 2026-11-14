# Day 45: Simple Calculator

Evaluate arithmetic expressions from the command line or an interactive prompt.

**Difficulty:** Easy

## Features
- Supports `+ - * / // % **` and parentheses
- Safe parsing with Python's `ast` module (no `eval`)
- Clear errors for division by zero and invalid input

## Install
No dependencies; Python 3.8+ only.

## Usage
```bash
python main.py "2 + 3 * (4 - 1)"
python main.py        # interactive
```

## Example
```
$ python main.py "2 + 3 * (4 - 1)"
2 + 3 * (4 - 1) = 11
```

## Requirements
Python 3.8+.
