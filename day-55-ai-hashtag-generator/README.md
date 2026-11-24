# Day 55: AI Hashtag Generator

Generate relevant hashtags for a post with the xAI (Grok) API, with an offline fallback.

**Difficulty:** Medium

## Features
- AI hashtags via xAI chat completions
- Platform presets (instagram, twitter, tiktok, linkedin, generic) with sensible default counts
- Offline keyword-based generator (`--offline`, or automatic with no key)
- CamelCase tags, de-duplicated

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py "sunset hike with friends in the mountains" -p instagram -n 8
echo "learning python every day" | python main.py --offline
```

## Example
```
$ python main.py "Learning python every day, python projects for beginners" --offline -n 4
#Python #Learning #Every #Day
```

## Requirements
No third-party packages.
