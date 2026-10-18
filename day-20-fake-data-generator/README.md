# Day 20 — Fake Data Generator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny CLI that generates realistic-looking fake records (people, users, employees, addresses, orders) for testing, demos and seeding databases. Standard library only, fully offline, no API key.

## Features

- 5 ready presets: `person`, `user`, `employee`, `address`, `order`
- 28 fields to mix freely with `-f` (name, email, phone, city, ip, uuid `id`, price, status...)
- Consistent identities: a record's name, username and email match each other
- Output as an aligned `table`, `json`, `jsonl` or `csv`
- `-o` writes straight to a file (handy for seeding test data)
- `--seed` for reproducible names, emails and values
- Safe placeholder domains only (`example.com`, `.test`), so no real inboxes get hit

## Run

```bash
cd day-20-fake-data-generator
python3 main.py --help
```

## Usage

```bash
python3 main.py                                  # 5 people as a table
python3 main.py -n 3 -f name,email,city          # pick your own fields
python3 main.py --preset user -n 10 --format json
python3 main.py --preset order -n 100 --format csv -o orders.csv
python3 main.py --format jsonl -n 1000 -o seed.jsonl
python3 main.py --seed 42 -n 2                   # reproducible
python3 main.py --list                           # all fields + presets
```

## Example

```text
$ python3 main.py --seed 42 -n 3
name        email                    phone            age  city    country
----------  -----------------------  ---------------  ---  ------  -------
Arjun Iyer  arjun.iyer4@demo.dev     +91 73657 18289  65   Delhi   India
Mia Nguyen  mia.nguyen12@inbox.test  +91 90520 03905  23   Pune    India
Omar Das    omar.das4@inbox.test     +91 78928 54987  32   Austin  USA

$ python3 main.py -f name,email,city -n 2 --format jsonl --seed 1
{"name": "Kabir Lopez", "email": "kabir.lopez98@example.com", "city": "Kolkata"}
{"name": "Ananya Rossi", "email": "ananya.rossi98@sample.org", "city": "Austin"}
```

## Requirements

Python 3.8+. No third-party packages, no internet needed.

> Note: `birthdate` and `created_at` are relative to today, so with `--seed` they shift by date; every other field stays identical.
