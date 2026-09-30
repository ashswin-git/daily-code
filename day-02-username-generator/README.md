# Day 2 — Username Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

A tiny command-line tool that builds readable usernames from adjective + noun pairs, with optional digits and separators. Uses Python's `secrets` module for picks.

## Features

- Several styles: `adj-noun`, `noun-adj`, glued `adjnoun`, or single `word`
- Configurable separator and trailing digits
- Optional capitalization
- Unique batch generation (no duplicates in one run)
- Zero third-party dependencies

## Run

```bash
cd day-02-username-generator
python3 main.py --help
```

No `pip install` step is required.

## Usage

```bash
# Default: 5 usernames like calm_otter42
python3 main.py

# Ten usernames, no digits
python3 main.py --count 10 --digits 0

# Camel-ish words with no separator
python3 main.py --style adjnoun --separator "" --capitalize --digits 3

# Noun first
python3 main.py --style noun-adj --separator "-"
```

## Example

```text
$ python3 main.py --count 3
swift_falcon17
neon_orbit04
quiet_maple88
```

## Requirements

- Python 3.10+
- Standard library only

## License

MIT
