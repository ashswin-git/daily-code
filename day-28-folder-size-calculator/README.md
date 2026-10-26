# Day 28 — Folder Size Calculator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Where did all my disk space go? This CLI scans a folder and shows its total size, a bar-chart breakdown of its subfolders and files (largest first), the biggest individual files, and which file types take the most space. Think of it as a friendly mini `du`. Standard library only.

## Features

- Total size, file count and folder count for any folder (or several)
- Breakdown of immediate children with share bars, largest first
- Top N biggest files (`-f`) and space by file extension (`-t`)
- Decimal units by default, `-b` for KiB/MiB/GiB
- Skips hidden files unless `-a`; doesn't follow symlinks unless `-L`
- `--json` output for scripts

## Run

```bash
cd day-28-folder-size-calculator
python3 main.py --help
```

## Usage

```bash
python3 main.py                 # current folder
python3 main.py ~/Downloads -n 10 -f 10
python3 main.py ~/Projects -b -t 8
python3 main.py . --json
```

## Example

```
$ python3 main.py .. -n 3 -f 2 -t 2

  /workspace/daily-code
  Total: 228.75 KB  (228,749 bytes) in 85 files, 30 folders

  Contents (largest first)
  #...................   5.0%     11.53 KB  day-20-fake-data-generator/
  #...................   4.9%     11.17 KB  day-22-phone-number-validator/
  #...................   4.7%     10.82 KB  day-19-random-quote-generator/

  Biggest files
      9.26 KB  day-20-fake-data-generator/main.py
      8.86 KB  day-19-random-quote-generator/main.py

  Space by file type
         .py    162.83 KB   71.2%
         .md     65.90 KB   28.8%
```

## Requirements

Python 3.8+. No third-party packages.
