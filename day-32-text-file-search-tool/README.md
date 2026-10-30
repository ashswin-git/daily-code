# Day 32 — Text File Search Tool

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny grep-style search for text files. Find a word, phrase or regex in one file or a whole folder and get file names, line numbers, highlighted matches and optional context lines. Binary files and junk folders (`.git`, `node_modules`, `__pycache__`, virtualenvs) are skipped automatically. Standard library only.

## Features

- Plain text by default, regex with `-r`, whole words with `-w`, case-insensitive with `-i`
- Context lines around each hit (`-C 2`), inverted search (`-v`)
- Counts per file (`-c`) or just matching file names (`-l`), cap hits per file (`-m 5`)
- Filter files with `--include '*.py'` / `--exclude '*.log'` (repeatable)
- Skips binary files, hidden files (unless `--hidden`) and files over `--max-size` MB
- Colored output in a terminal (`--no-color` or `NO_COLOR=1` to turn off)
- Exit code 0 when something matched, 1 when nothing did (handy in scripts)

## Run

```bash
cd day-32-text-file-search-tool
python3 main.py --help
```

No install needed (Python 3.8+).

## Usage

```bash
python3 main.py TODO                          # search current folder
python3 main.py -i hello notes.txt            # one file, ignore case
python3 main.py -r "def \w+\(" src --include "*.py"
python3 main.py -w error logs -C 2            # whole word with 2 lines of context
python3 main.py -c -i todo .                  # count per file
python3 main.py -l password ~/projects        # just list files that match
```

## Example

```
$ python3 main.py todo notes -i -C1
notes/a.txt
      2- foo bar
      3: TODO: fix this
      4- hello again

notes/sub/b.md
      1: todo list
      2- nothing

2 matching line(s) in 2 of 2 file(s) searched
```

## Requirements

Python 3.8+ only, no third-party packages.
