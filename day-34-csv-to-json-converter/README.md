# Day 34 — CSV to JSON Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Convert CSV files into clean JSON. Get a list of objects, a list of arrays, an object keyed by any column, or JSON Lines, with automatic delimiter detection and optional type conversion. Standard library only.

## Features

- Four output shapes: `records` (default), `arrays`, `keyed` (by a column with `-k`), `jsonl`
- Auto-detects comma, semicolon, tab or pipe delimiters (or set one with `-d`)
- `-t` turns `42`, `3.5`, `true/yes`, `false/no`, `null` and empty cells into real JSON types (leading-zero values like `007` stay strings)
- `--nested` expands headers like `address.city` into nested objects
- Pick columns with `-c name,age`, handle files without a header (`--no-header`), trim cells (`--strip`)
- Blank or duplicate headers get safe names, BOM-prefixed Excel CSVs are handled
- Reads stdin, writes to a file with `-o`, compact output with `--indent 0`

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py people.csv                     # list of objects
python main.py people.csv -t --nested         # real types + nested objects
python main.py people.csv -m keyed -k id -t   # {"1": {...}, "2": {...}}
python main.py people.csv -m jsonl -c name,age -o people.jsonl
cat data.csv | python main.py -m arrays --indent 0
```

## Example

`people.csv`:

```text
id,name,age,active,address.city
1,Ash,21,yes,Pune
2,Riya,24,no,Delhi
```

```bash
$ python main.py people.csv -m jsonl -c name,age -t
{"name":"Ash","age":21}
{"name":"Riya","age":24}
```

## Requirements

None (standard library only).
