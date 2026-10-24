# Day 26 — File Extension Finder

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

What's actually in this folder? Point this CLI at any directory and it tells you every file extension inside, how many files and how much space each takes, and what kind of file it is (image, video, code, document, archive...). Or pass `-e py` to list every file with that extension. Standard library only.

## Features

- Summary table: extension, category, file count, total size, share
- `-e EXT` lists all files with one extension (`py`, `.jpg`, `tar.gz` all work)
- Recursive by default; `-n` for top folder only
- Skips `.git`, `node_modules`, `__pycache__`, virtualenvs and hidden files (`-a` to include hidden)
- Sort by `--sort count` or `--sort size`, limit with `--top N`
- `--json` output for scripts

## Run

```bash
cd day-26-file-extension-finder
python3 main.py --help
```

## Usage

```bash
python3 main.py ~/Downloads
python3 main.py . --sort size --top 5
python3 main.py ~/Projects -e py
python3 main.py . --json
```

## Example

```
$ python3 main.py .. --top 3
  EXTENSION    CATEGORY       FILES       SIZE  SHARE
  .md          document          51    60.5 KB  64.6%
  .py          code              27   148.0 KB  34.2%
  .txt         document           1       16 B   1.3%

  79 files, 3 extensions, 208.5 KB total
```

## Requirements

Python 3.8+. No third-party packages.
