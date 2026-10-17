# Day 19 — Random Quote Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny CLI that prints random quotes from a built-in offline collection (31 quotes across 5 categories), with an optional `--online` mode that pulls a fresh quote from the free [ZenQuotes](https://zenquotes.io) API. No API key, standard library only.

## Features

- Random quote from an offline collection (works without internet)
- Filter by `--category`, `--author` (substring), or `--search` text
- `-n` for several quotes at once (no repeats when possible)
- `--daily` quote of the day: same quote all day, changes tomorrow
- `--seed` for reproducible picks
- `--online` fetches from ZenQuotes and falls back to offline if it fails
- `--json` output and adjustable `--width` wrapping
- `--list` shows categories with counts

## Run

```bash
cd day-19-random-quote-generator
python3 main.py --help
```

## Usage

```bash
python3 main.py                          # one random quote
python3 main.py -n 3                     # three quotes
python3 main.py --category coding        # coding quotes only
python3 main.py --author einstein -n 2
python3 main.py --search simple --json
python3 main.py --daily                  # quote of the day
python3 main.py --seed 42 -c coding -n 2 # reproducible
python3 main.py --online                 # free API, no key
python3 main.py --list
```

## Example

```text
$ python3 main.py -c coding -n 2 --seed 42
“There are only two hard things in Computer Science: cache
invalidation and naming things.”
    — Phil Karlton  [coding]

“First, solve the problem. Then, write the code.”
    — John Johnson  [coding]

$ python3 main.py --list
coding       8
humor        4
life         5
motivation   7
wisdom       7
total        31
```

## Requirements

Python 3.8+. No third-party packages. `--online` needs internet access; everything else works offline.
