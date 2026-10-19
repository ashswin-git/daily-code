# Day 21 — Email Validator

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A tiny CLI that checks email addresses before you save or send to them: real syntax rules, typo hints for popular providers, disposable and role-inbox flags, and an optional domain lookup. Standard library only, no API key.

## Features

- Syntax checks with clear reasons: one `@`, 64-char local part, 254-char total, no `..`, valid domain labels and TLD
- Typo hints for popular domains (`gmial.com` → `gmail.com`, `yaho.com` → `yahoo.com`)
- Flags disposable providers (mailinator, yopmail, 10minutemail...) and role inboxes (`admin@`, `support@`...)
- Notes `+tag` aliases and lowercases the domain in the normalized address
- `--dns` checks that the domain actually resolves (needs internet)
- Check one address, many args, a file (`-f`), or piped stdin
- Output as readable `text`, `json` or `csv`; `--valid-only` cleans a mailing list
- Exit code `0` when all are valid, `1` otherwise (script-friendly)

## Run

```bash
cd day-21-email-validator
python3 main.py --help
```

## Usage

```bash
python3 main.py jane@gmail.com                    # check one
python3 main.py a@x.com b@gmial.com bad..x@y.com  # check many
python3 main.py -f emails.txt --format csv > report.csv
cat emails.txt | python3 main.py --valid-only > clean.txt
python3 main.py --dns hello@github.com            # also check the domain exists
python3 main.py --format json ravi@yaho.com
python3 main.py                                   # interactive prompt
```

## Example

```text
$ python3 main.py jane.doe@gmail.com john@gmial.com bad..dots@example.com admin@mailinator.com a@b.c
[VALID  ] jane.doe@gmail.com
[WARN   ] john@gmial.com
           ! did you mean @gmail.com?
[INVALID] bad..dots@example.com
           x local part has consecutive dots
[WARN   ] admin@mailinator.com
           ! disposable / temporary email provider
           ! role address (shared inbox, not a person)
[INVALID] a@b.c
           x invalid top-level domain '.c'

3/5 valid, 2 invalid
```

## Requirements

Python 3.8+. No third-party packages. Internet is only needed for `--dns`.

> Note: syntax checks can't prove an inbox exists; only sending a confirmation email can. `--dns` uses a plain A/AAAA lookup (the stdlib has no MX lookup), and some sandboxed or proxied networks resolve every name, so treat it as a hint.
