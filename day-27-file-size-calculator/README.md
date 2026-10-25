# Day 27 — File Size Calculator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

How big is that file, really? This CLI shows the size of one or more files in human units, totals them with each file's share, estimates how long they'd take to download at a given speed, and converts raw sizes like `1.5GB` into every other unit (KB vs KiB included). Standard library only.

## Features

- Size of any files or glob patterns (`*.mp4`), with total and share per file
- Decimal units (KB/MB/GB) by default, `-b` for binary (KiB/MiB/GiB)
- `-c 1.5GB` converts a size to bytes, KB, MB, GB, TB, KiB, MiB, GiB, TiB
- `-s 50Mbps` or `-s 10MB/s` estimates download time
- `--sort` for largest first, `--json` output for scripts

## Run

```bash
cd day-27-file-size-calculator
python3 main.py --help
```

## Usage

```bash
python3 main.py video.mp4 photo.jpg
python3 main.py "*.zip" --sort -s 50Mbps
python3 main.py -c 1.5GB -s 50Mbps
python3 main.py -c "700 MiB" --json
```

## Example

```
$ python3 main.py -c 1.5GB -s 50Mbps
  1.5GB = 1,500,000,000 bytes
    KB  1,500,000.0000
    MB  1,500.0000
    GB  1.5000
    TB  0.0015
   KiB  1,464,843.7500
   MiB  1,430.5115
   GiB  1.3970
   TiB  0.0014

  Download at 50Mbps: 4m
```

## Requirements

Python 3.8+. No third-party packages.
