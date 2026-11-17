# Day 48: EMI Calculator

A command-line calculator for loan EMIs (reducing-balance method).

**Difficulty:** Easy

## Features
- Monthly EMI, total interest and total payment
- Tenure in months or years
- Optional month-by-month amortization table
- Handles 0% interest

## Install
No dependencies; Python 3.8+ only.

## Usage
```bash
python main.py 500000 8.5 5 --years
python main.py 100000 12 12 --table
```

## Example
```
$ python main.py 500000 8.5 5 --years
Monthly EMI    : 10,258.27
Total interest : 115,495.94
Total payment  : 615,495.94
```

## Requirements
Python 3.8+
