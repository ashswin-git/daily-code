# Day 3 — QR Code Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A small command-line tool that turns text or URLs into QR codes. Prints a compact ASCII preview in the terminal and can save SVG/PNG (and a few other formats) via the lightweight [`segno`](https://pypi.org/project/segno/) library.

## Features

- Encode any text or URL
- Read payload from an argument, a file, or stdin
- Terminal ASCII preview (no GUI needed)
- Export `.svg`, `.png`, `.eps`, `.pdf`, or `.txt`
- Tunable scale, border, error-correction level, and colors
- One small dependency (`segno`); no Pillow required for SVG/terminal

## Setup

```bash
cd day-03-qr-code-generator
pip install -r requirements.txt
```

## Run

```bash
python3 main.py --help
```

## Usage

```bash
# ASCII QR in the terminal
python3 main.py "https://github.com/ashswin-git/daily-code"

# Save an SVG (and still print ASCII unless --no-terminal)
python3 main.py "Hello, Day 3!" -o hello.svg --no-terminal

# From a file
python3 main.py --file note.txt -o note.png --scale 10

# From stdin
echo "wifi-setup" | python3 main.py -o wifi.svg --no-terminal

# Stronger error correction + custom colors
python3 main.py "https://example.com" -o link.svg --error H --dark "#111827" --light "#f9fafb" --no-terminal
```

## Example

```text
$ python3 main.py "https://github.com/ashswin-git/daily-code" --no-terminal -o daily-code.svg
Saved: .../daily-code.svg
```

Scan the generated code with any phone camera QR reader.

## Requirements

- Python 3.10+
- `segno` (see `requirements.txt`)

## License

MIT
