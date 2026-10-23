# Day 25 — Website Status Checker

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Is it down for everyone or just me? Give this CLI a few URLs (or a file of them) and it checks them in parallel, showing UP / REDIRECT / CLIENT ERR / SERVER ERR / DOWN, the HTTP code, response time, the final URL after redirects and the page title. Standard library only.

## Features

- Pass domains or full URLs (`https://` is added if missing)
- `-f sites.txt` to check a list (one per line, `#` comments allowed)
- Parallel checks with `--workers`, adjustable `--timeout`
- Follows redirects and shows where you landed, plus the page `<title>`
- `--json` output for scripts and cron jobs
- Exit code `0` if every site is up, `1` if any isn't, `2` on bad input

## Run

```bash
cd day-25-website-status-checker
python3 main.py --help
```

## Usage

```bash
python3 main.py github.com example.com
python3 main.py -f sites.txt --timeout 5
python3 main.py example.com --json
```

## Example

```
$ python3 main.py github.com example.com https://httpbin.org/status/500
  URL                             STATE       CODE     TIME  DETAIL
  https://github.com              UP           200      44ms  GitHub · Change is constant. GitHub keeps you ahead.
  https://example.com             UP           200      43ms  Example Domain
  https://httpbin.org/status/500  SERVER ERR   500      54ms

2 up / 3 checked
```

## Requirements

Python 3.8+. No external packages, no API key.
