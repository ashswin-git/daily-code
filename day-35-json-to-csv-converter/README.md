# Day 35 — JSON to CSV Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Convert JSON or JSON Lines into a clean CSV. Nested objects are flattened into dotted columns, columns from every row are merged in first-seen order, and lists are kept as JSON text or joined. Standard library only.

## Features

- Accepts a list of objects, a list of arrays (first row = header), a single object, an object keyed by id, or JSON Lines (auto-detected)
- Flattens nested objects into `address.city` style columns (`--sep` to change, `--no-flatten` to keep JSON text)
- Merges columns across rows, so missing fields become empty cells
- Lists written as JSON text or `; `-joined (`--lists join`)
- Pick and order columns with `-c name,age`, reach a nested array with `-p data.items`
- Name the key column for keyed objects with `-k id`
- Comma, semicolon, tab or pipe output (`-d tab`), optional header (`--no-header`)
- Reads stdin, writes to a file with `-o`, `--excel` adds a BOM for Excel

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py people.json                         # CSV to stdout
python main.py people.json -o people.csv --excel   # file for Excel
python main.py people.json -c name,address.city --lists join
python main.py api.json -p data.items -d ';'
cat events.jsonl | python main.py -d tab
```

## Example

`people.json`:

```json
[{"id": 1, "name": "Ash", "active": true, "address": {"city": "Pune"}, "tags": ["dev", "py"]},
 {"id": 2, "name": "Riya, R", "active": false, "address": {"city": "Delhi", "pin": "110001"}, "tags": []}]
```

```bash
$ python main.py people.json
id,name,active,address.city,tags,address.pin
1,Ash,true,Pune,"[""dev"",""py""]",
2,"Riya, R",false,Delhi,[],110001
```

## Requirements

None (standard library only).
