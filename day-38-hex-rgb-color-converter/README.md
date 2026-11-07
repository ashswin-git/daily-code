# Day 38 — HEX/RGB Color Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Convert colors between HEX, RGB and HSL from the command line. Accepts `#RGB` / `#RRGGBB`, `rgb()`, `hsl()`, bare `r,g,b` and a small set of CSS names. Optional ANSI truecolor swatch, WCAG contrast check, random colors and JSON output. Standard library only.

## Features

- HEX ↔ RGB ↔ HSL round-trips (`#FF5733`, `rgb(255, 87, 51)`, `hsl(11, 100%, 60%)`)
- Short hex (`#F53`), optional alpha ignored, percent RGB channels
- ANSI truecolor preview swatch in the terminal (disable with `--no-swatch`)
- `--name` picks the closest CSS named color from a compact built-in list
- `--contrast` prints the WCAG contrast ratio for exactly two colors
- `--random N` generates N random colors
- `--json` for scripts; reads colors from stdin one per line

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py '#FF5733'
python main.py rgb(255,87,51) --name
python main.py '#FF5733' '#3498db' --contrast
python main.py --random 3 --json
echo '#0f0' | python main.py
```

## Example

```bash
$ python main.py '#FF5733' --name
████  #FF5733  rgb(255, 87, 51)  hsl(11.0, 100.0%, 60.0%)  ~tomato

$ python main.py '#000000' '#FFFFFF' --contrast
████  #000000  rgb(0, 0, 0)  hsl(0.0, 0.0%, 0.0%)
████  #FFFFFF  rgb(255, 255, 255)  hsl(0.0, 0.0%, 100.0%)
contrast 21.0:1  (AAA)
```

## Requirements

- Python 3.8 or newer
- No third-party packages

## Built with

- Python standard library (`argparse`, `colorsys`, `json`, `re`, `random`)
