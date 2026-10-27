# Day 29 — Duplicate File Finder

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Find files with identical content anywhere in one or more folders, see how much space the extra copies waste, and optionally delete them. It's fast because it only hashes files that could be duplicates: it groups by size first, then compares a quick 64 KB partial hash, and only then a full SHA-256. Standard library only.

## Features

- Scans one or more folders recursively (or a mix of files and folders)
- Size, then partial hash, then full SHA-256 comparison, so nothing is matched by name
- Shows each duplicate group, largest wasted space first, with a total "wasted" figure
- Filter by extension (`-e jpg -e png`) and minimum size (`-m 1000`)
- Hard links to the same data aren't reported as duplicates
- `--delete` removes the extra copies (asks first; `-y` skips the prompt)
- Choose which copy to keep with `-k first|newest|oldest|shortest`
- Skips hidden files unless `-a`; never follows symlinks
- `--json` output for scripts

## Run

```bash
cd day-29-duplicate-file-finder
python3 main.py --help
```

No install needed (Python 3.8+).

## Usage

```bash
python3 main.py                        # current folder
python3 main.py ~/Downloads ~/Desktop  # several folders at once
python3 main.py ~/Pictures -e jpg -e png -m 10000
python3 main.py ~/Downloads --delete -k newest
python3 main.py . --json
```

## Example

```
$ python3 main.py /tmp/demo

  Scanned 6 files
  Found 2 duplicate groups (2 extra copies, 200.01 KB wasted)

  [1] 200.00 KB x 2
      keep  /tmp/demo/a/big.bin
      dupe  /tmp/demo/b/big-copy.bin

  [2] 6 B x 2
      keep  /tmp/demo/a/x.txt
      dupe  /tmp/demo/b/y.txt
```

## Requirements

- Python 3.8+
- No third-party packages

> Tip: run without `--delete` first and check the list. Deleted files don't go to the trash.
