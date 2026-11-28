# Day 59: AI Grammar Checker

Fix grammar, spelling and punctuation with the xAI (Grok) API, with an offline rule-based fallback.

**Difficulty:** Medium

## Features
- AI proofreading via xAI chat completions, with a list of changes
- Input from an argument, a file (`--file`) or stdin
- Offline checker (`--offline`, or automatic with no key): common typos, repeated words, extra spaces, "i" -> "I", capitalization, end punctuation

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py "i recieve teh the email yesterday"
python main.py --file draft.txt
echo "this is  a test" | python main.py --offline
```

## Example
```
$ python main.py --offline "hello world"
Hello world.
---
- sentence capitalization
- added end punctuation
```

## Requirements
No third-party packages.
