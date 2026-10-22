# Day 24 — Port Checker

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny, fast TCP port checker. Give it a host and some ports and it tells you which are open, closed or filtered (timed out), with the service name and connect time. Scans run in parallel, so the 26-port "common" preset finishes in about a second. Standard library only.

## Features

- Single ports, lists and ranges: `80`, `22,80,443`, `8000-8010`, or the `common` preset
- Open / closed / filtered detection with per-port latency
- Service names (ssh, http, postgres, redis...)
- Parallel scanning with `--workers`, adjustable `--timeout`
- `--open` to show only open ports, `--json` for scripts
- Exit code `0` if any port is open, `1` if none, `2` on bad input

## Run

```bash
cd day-24-port-checker
python3 main.py --help
```

## Usage

```bash
python3 main.py localhost                     # common ports
python3 main.py github.com -p 22,80,443       # specific ports
python3 main.py 192.168.1.10 -p 1-1024 --open # range, open only
python3 main.py example.com -p 443 --json     # JSON output
```

## Example

```
$ python3 main.py github.com -p 22,80,443 -t 2
Host github.com (140.82.121.4) - 3 port(s) in 0.05s

  PORT  STATE         TIME  SERVICE
    22  OPEN        48.2ms  ssh
    80  OPEN        47.9ms  http
   443  OPEN        48.0ms  https

3 open / 3 scanned
```

## Requirements

Python 3.8+. No external packages, no API key.

> Only scan hosts you own or have permission to test.
