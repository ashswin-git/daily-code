# Day 9 — URL Shortener

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A command-line URL shortener that uses free, keyless public services (TinyURL and is.gd), automatically falls back if one is down, can expand any short link to reveal where it really goes, and keeps an offline alias book in `links.json`. Standard library only, no API key needed.

## Features

- Shorten one or many URLs at once (`https://` added automatically)
- Two services, TinyURL (default) and is.gd, with automatic fallback
- Custom aliases with `--alias`
- `expand` follows redirects hop by hop, so you can check a short link before clicking it
- Offline `local` alias book: `add`, `get`, `list`, `remove` (saved to `links.json`, git-ignored)
- Shows how much shorter each link got

## Run

```bash
cd day-09-url-shortener
python3 main.py --help
```

## Usage

```bash
python3 main.py shorten github.com/ashswin-git/daily-code
python3 main.py shorten https://example.com/a/very/long/path --service isgd
python3 main.py shorten https://example.com --alias my-cool-link
python3 main.py expand https://tinyurl.com/2dqkjow5
python3 main.py local add https://docs.python.org/3/ --alias pydocs
python3 main.py local list
python3 main.py local get pydocs
```

## Example

```text
$ python3 main.py shorten github.com/ashswin-git/daily-code
  https://tinyurl.com/2dqkjow5  <-  https://github.com/ashswin-git/daily-code  (tinyurl, 32% shorter)

$ python3 main.py expand https://tinyurl.com/2dqkjow5
  start  https://tinyurl.com/2dqkjow5
  hop 1  https://github.com/ashswin-git/daily-code
  Final destination: https://github.com/ashswin-git/daily-code
```

## Requirements

- Python 3.10+
- Standard library only (no `requirements.txt`)
- Internet connection for `shorten` and `expand` (the `local` commands work offline)

## License

MIT
