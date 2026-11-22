# Day 53: AI Title Generator

Generate catchy titles for any topic or text with the xAI (Grok) API, with an offline fallback.

**Difficulty:** Medium

## Features
- AI titles via xAI chat completions
- Styles: catchy, professional, clickbait, seo, funny
- Choose how many titles you want
- Offline template generator (`--offline`, or automatic with no key)

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py "learning python for beginners" -n 5 -s seo
echo "my article text" | python main.py --offline
```

## Example
```
$ python main.py "learning python" --offline -n 3 -s professional
1. Understanding in Depth Learning Python
2. An Introduction to Learning Python
3. Learning Python: Key Concepts and Best Practices
```
(Offline output order is randomized.)

## Requirements
No third-party packages.
