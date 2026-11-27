# Day 58: AI Blog Idea Generator

Brainstorm blog post ideas with the xAI (Grok) API, with an offline template fallback.

**Difficulty:** Medium

## Features
- AI-generated titles with a one-line angle via xAI chat completions
- Styles: how-to, listicle, opinion, beginner, case-study
- Choose how many ideas you want
- Offline template generator (`--offline`, or automatic with no key)

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py "python automation" -n 5 -s how-to
python main.py "fitness for students" --offline
```

## Example
```
$ python main.py "python automation" -n 3 -s listicle --offline
1. 10 Things Nobody Tells You About python automation
2. 7 Common python automation Mistakes to Avoid
3. Top 5 Tools for python automation
```

## Requirements
No third-party packages.
