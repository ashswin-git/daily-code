# Day 18 — Random Number Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny CLI for random integers, floats, lottery-style unique draws, and Gaussian samples. Use a seed for reproducibility or `--secure` for cryptographically strong picks. Standard library only.

## Features

- Random integers in an inclusive `--min` / `--max` range (default 1..100)
- Floating-point numbers with configurable `--decimals`
- Generate many at once with `-n`
- `--unique` for lottery / sample-without-replacement draws
- `--secure` via the `secrets` module (ignores `--seed`)
- `--seed` for reproducible sequences
- `--gauss MEAN STDEV` for normal-distribution samples
- `--sort`, custom `--sep`, and optional `--sum`

## Run

```bash
cd day-18-random-number-generator
python3 main.py --help
```

## Usage

```bash
python3 main.py                              # one int 1..100
python3 main.py -n 5                         # five ints
python3 main.py --min 10 --max 50 -n 3
python3 main.py --float --min 0 --max 1 -n 5 -d 4
python3 main.py --unique -n 6 --min 1 --max 49   # lottery
python3 main.py --secure -n 3 --min 1 --max 1000000
python3 main.py --seed 42 -n 5
python3 main.py --gauss 100 15 -n 8
python3 main.py -n 10 --sort --sep ','
```

## Example

```text
$ python3 main.py --seed 42 -n 5
81
14
3
94
35

$ python3 main.py --unique -n 6 --min 1 --max 49 --sort
4
12
19
27
33
41

$ python3 main.py --float --min 0 --max 1 -n 3 -d 4 --seed demo
0.6394
0.0250
0.2750
```

## Requirements

Python 3.8+. No third-party packages.
