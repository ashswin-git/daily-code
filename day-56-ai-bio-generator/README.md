# Day 56: AI Bio Generator

Generate short social media bios with the xAI (Grok) API, with an offline template fallback.

**Difficulty:** Medium

## Features
- AI bios via xAI chat completions
- Tones: professional, casual, funny, creative, minimal
- Platform presets with character limits (twitter, instagram, linkedin, github, tiktok, generic)
- Offline template generator (`--offline`, or automatic with no key)

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py --name Ash --role "Python developer" --interests "open source, AI" -t funny -p twitter -n 2
python main.py --name Ash --role "CSE student" --interests "coding" --offline
```

## Example
```
$ python main.py --name Ash --role "Python developer" --interests "open source" -t minimal --offline -n 2
1. Python developer. open source.
2. Ash. Python developer.
```

## Requirements
No third-party packages.
