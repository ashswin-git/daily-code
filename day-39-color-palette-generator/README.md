# Day 39 — Color Palette Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Build a color palette from a seed HEX or RGB color. Pick a harmony (analogous, complementary, triadic and more), export CSS variables or JSON, and preview swatches in the terminal. Standard library only.

## Features

- Harmonies: analogous, complementary, split-complementary, triadic, tetradic, monochromatic, shades, tints and tones
- `--random` invents a spaced palette using a golden-angle hue walk
- Accepts `#RGB` / `#RRGGBB` and `rgb(r,g,b)` (also via stdin)
- `--count N` controls size for scalable palettes (analogous, mono, shades, tints, tones, random)
- `--css` prints `:root` custom properties; `--json` is script-friendly
- ANSI truecolor preview swatch in the terminal (disable with `--no-swatch`)

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py '#FF5733'
python main.py '#3498db' --harmony triadic
python main.py '#FF5733' --harmony shades --count 6
python main.py --random --count 5 --json
python main.py '#FF5733' --css
echo '#0af' | python main.py --harmony complementary
```

## Example

```bash
$ python main.py '#FF5733' --harmony complementary
complementary palette  (2 colors)
seed  #FF5733
 1.  #FF5733  rgb(255, 87, 51)  hsl(10.6, 100.0%, 60.0%)
 2.  #33DBFF  rgb(51, 219, 255)  hsl(190.6, 100.0%, 60.0%)

$ python main.py '#FF5733' --css
:root {
  --color-1: #FF33DB;
  --color-2: #FF3375;
  --color-3: #FF5733;
  --color-4: #FFBD33;
  --color-5: #DBFF33;
}
```

## Requirements

- Python 3.8 or newer
- No third-party packages

## Built with

- Python standard library (`argparse`, `colorsys`, `json`, `random`, `re`)
