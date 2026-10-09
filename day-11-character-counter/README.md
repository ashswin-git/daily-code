# Day 11 — Character Counter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A command-line character counter that breaks text into letters, digits, spaces, punctuation and other symbols, with an uppercase/lowercase split and a mini bar chart of the most frequent characters. Works on files, piped text, or a quick `--text` string. Standard library only.

## Features

- Total characters and characters without spaces
- Letters (with uppercase / lowercase split), digits, spaces, punctuation, other
- Word and line counts
- Top characters with a text bar chart (`--top N`); whitespace skipped for a cleaner chart
- Several files at once, with a combined TOTAL
- `--json` output for scripts

## Run

```bash
cd day-11-character-counter
python3 main.py --help
```

## Usage

```bash
python3 main.py notes.txt
python3 main.py --text "Hello, World! 123"
echo "abc XYZ 99!!" | python3 main.py --top 5
python3 main.py a.txt b.txt --json
```

## Example

```text
$ python3 main.py --text "Hello, World! 123" --top 5

  inline text
  --------------------------------------
  Characters         17
  Chars (no spaces)  15
  Letters            10
    Uppercase        2
    Lowercase        8
  Digits             3
  Spaces             2
  Punctuation        2
  Other              0
  Words              3
  Lines              1

  Top characters
  l     3  ####################
  o     2  #############
  H     1  #######
  e     1  #######
  ,     1  #######
```

## Requirements

- Python 3.8+
- Standard library only (no `requirements.txt`)

## License

MIT
