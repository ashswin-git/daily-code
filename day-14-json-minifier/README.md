# Day 14 — JSON Minifier

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny command-line JSON minifier. It removes every extra space and newline from your JSON and tells you how many bytes you saved. Broken JSON gets a clear error with the exact line and column. Standard library only.

## Features

- Strips all unnecessary whitespace (compact `,` and `:` separators)
- Prints a size summary: before, after, bytes and percent saved
- Optional alphabetical key sorting (`--sort-keys`) and ASCII escaping (`--ascii`)
- Friendly error with a pointer to the broken spot
- Reads `--text`, a file, or stdin; can write to a file with `--output`

## Run

```bash
cd day-14-json-minifier
python3 main.py --help
```

## Usage

```bash
python3 main.py --text '{"b": 1, "a": [1, 2]}' --sort-keys
python3 main.py data.json
cat data.json | python3 main.py
python3 main.py data.json --output data.min.json
python3 main.py data.json --quiet
```

## Example

```text
$ python3 main.py --text '{
  "name": "Ash",
  "tags": ["python", "json"],
  "active": true
}'
{"name":"Ash","tags":["python","json"],"active":true}
67 -> 53 bytes (saved 14, 20.9%)

$ python3 main.py --text '{"a": 1,}'
Invalid JSON: Illegal trailing comma before end of object (line 1, column 8)
  {"a": 1,}
         ^
```

The result goes to stdout and the size summary goes to stderr, so piping the output stays clean.

## Requirements

Python 3.8+. No third-party packages.
