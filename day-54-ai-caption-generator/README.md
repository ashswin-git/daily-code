# Day 54: AI Caption Generator

Generate social media captions for any photo or post idea with the xAI (Grok) API, with an offline fallback.

**Difficulty:** Medium

## Features
- AI captions via xAI chat completions
- Tones: casual, funny, inspirational, professional, aesthetic
- Choose how many captions, with or without emojis
- Offline template generator (`--offline`, or automatic with no key)

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py "sunset at the beach with friends" -n 3 -t aesthetic
echo "my first marathon" | python main.py --offline --no-emoji
```

## Example
```
$ python main.py "sunset at the beach" --offline -n 2 -t aesthetic --no-emoji
1. quietly sunset at the beach
2. soft moments, sunset at the beach
```
(Offline output order is randomized.)

## Requirements
No third-party packages.
