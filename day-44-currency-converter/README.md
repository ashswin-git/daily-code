# Day 44: Currency Converter

Convert an amount between any two currencies using live exchange rates.

**Difficulty:** Easy

## Features
- Live rates from the free open.er-api.com endpoint
- Works with command-line arguments or interactive prompts
- Clear errors for unknown currencies and network problems

## Install
No dependencies; Python 3.8+ only.

## Usage
```bash
python main.py 100 USD INR
python main.py        # interactive
```

## Example
```
$ python main.py 100 USD INR
100.00 USD = <converted amount> INR
```

## Requirements
Python 3.8+ and an internet connection. No API key needed.
