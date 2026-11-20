# Day 51: Notes CLI

A tiny command-line note taker. Notes are stored in a local JSON file.

**Difficulty:** Easy

## Features
- Add, list, view, edit, delete notes
- Search notes by keyword
- Custom storage file via `NOTES_FILE` env var

## Install
No dependencies — Python 3.8+ standard library only.

## Usage
```bash
python main.py add Buy milk tomorrow
python main.py list
python main.py view 1
python main.py edit 1 Buy milk and bread
python main.py search milk
python main.py delete 1
```

## Example
```
$ python main.py list
  1  2026-11-20 09:30  Buy milk tomorrow
```

## Requirements
Python 3.8+
