# Day 13 — JSON Formatter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny command-line JSON formatter. Paste messy JSON, point at a file, or pipe it in, and get clean, indented output. If the JSON is broken, it shows the exact line and column of the problem. Standard library only.

## Features

- Pretty-prints with a custom indent (`--indent`)
- Optional alphabetical key sorting (`--sort-keys`)
- Validate-only mode (`--check`)
- Friendly error with a pointer to the broken spot
- Reads `--text`, a file, or stdin; can write to a file with `--output`

## Run

```bash
cd day-13-json-formatter
python3 main.py --help
```

## Usage

```bash
python3 main.py --text '{"b":1,"a":[1,2,3]}' --sort-keys
python3 main.py data.json --indent 4
cat data.json | python3 main.py
python3 main.py data.json --check
python3 main.py data.json --output pretty.json
```

## Example

```text
$ python3 main.py --text '{"name":"Ash","tags":["python","json"],"active":true}'
{
  "name": "Ash",
  "tags": [
    "python",
    "json"
  ],
  "active": true
}

$ python3 main.py --text '{"a": 1,}'
Invalid JSON: Illegal trailing comma before end of object (line 1, column 8)
  {"a": 1,}
         ^
```

## Requirements

Python 3.8+. No third-party packages.
