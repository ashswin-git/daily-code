# Day 16 — URL Encoder/Decoder

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny command-line tool for URL percent-encoding. Encode text so it's safe inside a link, decode `%20`-style escapes back to readable text, and inspect a full URL to see its host, path, and query parameters at a glance. Standard library only.

## Features

- Encode, decode, and inspect with `encode` / `decode` / `inspect` (or `e` / `d` / `i`)
- Form style with `--plus` (spaces as `+`, like HTML forms)
- Keep chosen characters unencoded with `--safe "/:"`
- Unwrap double-encoded text with `--rounds 3`
- `inspect` splits a URL into scheme, host, port, path, fragment, and decoded query params
- Works on text, files, or stdin

## Run

```bash
cd day-16-url-encoder-decoder
python3 main.py --help
```

## Usage

```bash
python3 main.py encode --text "hello world & café?"
python3 main.py e -p -t "a b+c"
python3 main.py d -t "hello%20world%20%26%20caf%C3%A9%3F"
python3 main.py d -r 3 -t "caf%25C3%25A9"
python3 main.py i -t "https://example.com:8080/search%20page?q=python%20tips&lang=en#top"
echo -n "x y" | python3 main.py e
```

## Example

```text
$ python3 main.py encode --text "hello world & café?"
hello%20world%20%26%20caf%C3%A9%3F

$ python3 main.py d -r 3 -t "caf%25C3%25A9"
café

$ python3 main.py i -t "https://example.com:8080/search%20page?q=python%20tips&lang=en#top"
scheme:   https
host:     example.com
port:     8080
path:     /search page
fragment: top
query:    2 param(s)
  q    = python tips
  lang = en
```

## Requirements

Python 3.8+. No third-party packages.
