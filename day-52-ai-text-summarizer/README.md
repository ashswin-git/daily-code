# Day 52: AI Text Summarizer

Summarize any text with the xAI (Grok) API, with an offline fallback.

**Difficulty:** Medium

## Features
- AI summaries via xAI chat completions
- Choose the number of sentences
- Offline extractive summarizer (`--offline`, or automatic with no key)
- Reads a file or stdin

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py article.txt -n 3
cat article.txt | python main.py --offline
```

## Example
```
$ python main.py notes.txt --offline -n 2
Python is a popular language. Python is used for web, data and automation.
```

## Requirements
No third-party packages.
