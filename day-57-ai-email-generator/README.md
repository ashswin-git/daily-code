# Day 57: AI Email Generator

Draft emails with the xAI (Grok) API, with an offline template fallback.

**Difficulty:** Medium

## Features
- AI-written subject and body via xAI chat completions
- Tones: formal, friendly, persuasive, apologetic, concise
- Offline template generator (`--offline`, or automatic with no key)

## Install
Python 3.8+, standard library only.

## API setup
Copy `.env.example` to `.env` and put your key from https://console.x.ai in `XAI_API_KEY`.

## Usage
```bash
python main.py --to Priya --sender Ash --purpose "request a meeting next week" -t friendly
python main.py --to Sir --sender Ash --purpose "leave application for Friday" --offline
```

## Example
```
$ python main.py --to Priya --sender Ash --purpose "request a meeting next week" -t concise --offline
Subject: Request a meeting next week

Hi Priya,

I'm writing regarding the following: request a meeting next week.

Thanks,
Ash
```

## Requirements
No third-party packages.
