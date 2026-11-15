# Day 46: Scientific Calculator

A command-line calculator with trigonometry, logarithms, roots and constants.

**Difficulty:** Easy

## Features
- Operators `+ - * / // % ** ^` and parentheses
- Functions: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, sqrt, log (base 10), ln, exp, abs, fact, floor, ceil, round, deg, rad
- Constants: pi, e, tau
- Safe parsing with `ast` (no `eval`)

## Install
No dependencies; Python 3.8+ only.

## Usage
```bash
python main.py "sqrt(16) + sin(pi/2)"
python main.py        # interactive
```

## Example
```
$ python main.py "sqrt(16) + sin(pi/2)"
sqrt(16) + sin(pi/2) = 5.0
```

## Requirements
Python 3.8+. Trig functions use radians (use `rad()` for degrees).
