# Day 10 — Word Counter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A command-line word counter that goes beyond `wc`: words, unique words, characters, lines, sentences and paragraphs, plus reading and speaking time and a mini bar chart of your most-used words. Works on files, piped text, or a quick `--text` string. Standard library only.

## Features

- Words, unique words, characters (with and without spaces), lines, sentences, paragraphs
- Average word length and longest word
- Estimated reading time (238 wpm) and speaking time (150 wpm)
- Top words with a text bar chart (`--top N`), optionally skipping common words (`--skip-common`)
- Several files at once, with a combined TOTAL
- `--json` output for scripts

## Run

```bash
cd day-10-word-counter
python3 main.py --help
```

## Usage

```bash
python3 main.py notes.txt
python3 main.py --text "The quick brown fox jumps over the lazy dog"
cat essay.txt | python3 main.py --top 5 --skip-common
python3 main.py a.txt b.txt --json
```

## Example

```text
$ python3 main.py --text "The quick brown fox jumps over the lazy dog. Isn't it fast? Yes!" --top 3

  inline text
  --------------------------------------
  Words              13
  Unique words       12
  Characters         64
  Chars (no spaces)  52
  Lines              1
  Sentences          3
  Paragraphs         1
  Avg word length    3.77
  Longest word       quick
  Reading time       3 sec
  Speaking time      5 sec

  Top words
  the       2  ####################
  quick     1  ##########
  brown     1  ##########
```

## Requirements

- Python 3.8+
- Standard library only (no `requirements.txt`)

## License

MIT
