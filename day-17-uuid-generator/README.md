# Day 17 — UUID Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny command-line tool that makes UUIDs and explains them. Generate random, time-based, or name-based IDs in whatever format you need, or paste any UUID to check it's valid and see its version, variant, and the moment it was created. Standard library only.

## Features

- Generate v1 (time + node), v3/v5 (name-based), v4 (random), and v7 (time-ordered, RFC 9562)
- Make many at once with `-n 10`
- Output as standard, `hex`, `braces`, `urn`, or `int`, with `--upper` for capitals
- Name-based IDs with built-in namespaces (`dns`, `url`, `oid`, `x500`) or your own UUID
- `inspect` validates UUIDs and shows version, variant, hex, int, and the creation time for v1/v7
- Reads UUIDs from arguments or stdin

## Run

```bash
cd day-17-uuid-generator
python3 main.py --help
```

## Usage

```bash
python3 main.py                         # one random v4 UUID
python3 main.py -n 3 -v 7               # three time-ordered v7 UUIDs
python3 main.py gen -v 5 --name example.com
python3 main.py g -v 1 -f urn -u
python3 main.py g -f braces
python3 main.py inspect 886313e1-3b8a-5372-9b90-0c9aee199e5d
python3 main.py -v 7 | python3 main.py i
```

## Example

```text
$ python3 main.py -n 3 -v 7
01a13dac-d659-71fd-bfc4-9698ec24aaf1
01a13dac-d659-7529-b707-af1e63be2eca
01a13dac-d659-72a5-b6f5-7c6b40313d82

$ python3 main.py gen -v 5 --name example.com
cfbff0d1-9375-5685-968c-48ce8b15ae17

$ python3 main.py i 01a13dac-d6b7-7b6c-99b4-03bc9c5a0f8c
uuid:     01a13dac-d6b7-7b6c-99b4-03bc9c5a0f8c
valid:    yes
version:  7
variant:  RFC 4122 / 9562
hex:      01a13dacd6b77b6c99b403bc9c5a0f8c
int:      2166438710690406707617700106462695308
created:  2026-10-15T03:48:19.767+00:00
```

`inspect` exits with code 1 if any input isn't a valid UUID, so it works in scripts too.

## Requirements

Python 3.8+. No third-party packages.
