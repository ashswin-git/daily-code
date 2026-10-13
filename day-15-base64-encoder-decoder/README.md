# Day 15 — Base64 Encoder/Decoder

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny command-line Base64 tool. Encode text or any file, decode it back, and use the URL-safe alphabet when you need it in links or tokens. Decoding forgives missing `=` padding and extra whitespace, and binary results get a safe hex preview instead of garbage in your terminal. Standard library only.

## Features

- Encode and decode with `encode` / `decode` (or the short `e` / `d`)
- URL-safe alphabet (`-` and `_`) with `--url-safe`, auto-detected when decoding
- Fixes missing padding and ignores line breaks while decoding
- Line wrapping for encoded output (`--wrap 76`, like email/MIME)
- Works on text, files, or stdin; writes raw bytes back out with `--output`
- Binary-safe: prints a hex preview when decoded data isn't text
- Clear error and exit code 2 for invalid Base64

## Run

```bash
cd day-15-base64-encoder-decoder
python3 main.py --help
```

## Usage

```bash
python3 main.py encode --text "Hello, daily-code!"
python3 main.py d --text "SGVsbG8sIGRhaWx5LWNvZGUh"
python3 main.py e -u -t "??>>"
python3 main.py e photo.png -w 76 -o photo.b64
python3 main.py d photo.b64 -o photo-copy.png
echo -n "hi there" | python3 main.py e | python3 main.py d -q
```

## Example

```text
$ python3 main.py encode --text "Hello, daily-code!"
SGVsbG8sIGRhaWx5LWNvZGUh
18 bytes -> 24 Base64 chars

$ python3 main.py d -t "SGVsbG8"
Hello
7 Base64 chars -> 5 bytes

$ python3 main.py d -t "Pz8-Pg"
??>>
6 Base64 chars -> 4 bytes

$ python3 main.py d -t "bad!"
Invalid Base64: Only base64 data is allowed
```

The result goes to stdout and the size summary goes to stderr, so piping stays clean. Use `--quiet` to hide the summary.

## Requirements

Python 3.8+. No third-party packages.
