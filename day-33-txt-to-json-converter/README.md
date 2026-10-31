# Day 33 — TXT to JSON Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Convert plain `.txt` files into clean JSON. It can turn lines into a list, `key: value` notes into an object, delimited text into a list of rows, or paragraphs into a list, and it guesses the right shape for you in `auto` mode. Standard library only.

## Features

- Four modes: `lines`, `kv`, `table`, `paragraphs`, plus `auto` detection (default)
- `kv` mode understands `key: value` and `key = value`; repeated keys become lists
- `table` mode auto-detects tab, comma, pipe, semicolon or whitespace columns (or use `-d`)
- `-t` turns `42`, `3.5`, `true/yes`, `false/no`, `null` into real JSON types
- Line numbers (`-n`), keep blank lines, trim lines, join wrapped paragraphs (`--join`)
- Skips `#` comment lines (change with `--comment`), reads stdin, writes to a file with `-o`

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py notes.txt                 # auto mode, print JSON
python main.py config.txt -m kv -t       # key/value with real types
python main.py scores.txt -m table -d '|' -o scores.json
python main.py story.txt -m paragraphs --join
cat list.txt | python main.py -m lines -n --indent 0
```

## Example

`profile.txt`:

```text
name: Ash
age = 21
active: yes
skills: python
skills: git
```

```bash
$ python main.py profile.txt -t
{
  "name": "Ash",
  "age": 21,
  "active": true,
  "skills": ["python", "git"]
}
```

## Requirements

None (standard library only).
