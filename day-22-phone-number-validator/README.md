# Day 22 — Phone Number Validator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny offline CLI that cleans up messy phone numbers, detects the country from the calling code, checks the length and mobile prefixes, and prints each number in E.164 (`+919876543210`) and a friendly national format. Standard library only, no API key.

## Features

- Accepts messy input: spaces, dashes, dots, brackets, `00` international prefix, `ext 22` / `x22` extensions
- Detects 18 common countries from the calling code (India, US/Canada, UK, UAE, Australia, Germany, Japan, Singapore and more)
- `--country IN` for local numbers without `+` (strips the national `0` trunk prefix)
- Length checks per country with clear reasons when a number is wrong
- Mobile vs landline hint, NANP area-code rules, fictional `555-01xx` and dummy-number warnings
- Output as readable `text`, `json` or `csv`; `--valid-only` prints clean E.164 numbers for contact lists
- Check one number, many args, a file (`-f`), or piped stdin
- Exit code `0` when all are valid, `1` otherwise (script-friendly)

## Run

```bash
cd day-22-phone-number-validator
python3 main.py --help
```

## Usage

```bash
python3 main.py "+91 98765 43210"                     # check one
python3 main.py "+1 (415) 555-2671" "+44 7911 123456"  # check many
python3 main.py -c IN 09876543210                      # local number, default country
python3 main.py -f contacts.txt --format csv > report.csv
cat contacts.txt | python3 main.py -c IN --valid-only > clean.txt
python3 main.py --format json "+971 50 123 4567"
python3 main.py --list-countries
python3 main.py                                        # interactive prompt
```

## Example

```text
$ python3 main.py "+91 98765 43210" "+1 (415) 555-2671" "0091-22-1234-5678" "+91 12345 67890" "+999 123" 9876543210
[VALID  ] +91 98765 43210
           +919876543210  |  98765 43210  |  India (IN, +91)  |  mobile
[VALID  ] +1 (415) 555-2671
           +14155552671  |  (415) 555-2671  |  United States / Canada (US, +1)  |  mobile or landline
[VALID  ] 0091-22-1234-5678
           +912212345678  |  22123 45678  |  India (IN, +91)  |  landline / other
[INVALID] +91 12345 67890
           x Indian numbers start with 2-4 (landline) or 6-9 (mobile)
[INVALID] +999 123
           x unknown or unsupported country code +999
[INVALID] 9876543210
           x no country code: start with + or pass --country

3/6 valid, 3 invalid
```

## Notes

This is a lightweight rule-based checker, not a full numbering database. It confirms a number is well-formed for its country, not that it is in service. For carrier-grade validation, look at the `phonenumbers` library.

## Requirements

Python 3.8+. No third-party packages, no internet needed.
