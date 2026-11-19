# Day 50: To-Do CLI

A tiny command-line task manager. Tasks are stored in a local JSON file.

## Features
- Add, list, complete, remove tasks
- Clear all completed tasks
- Custom storage file via `TODO_FILE` env var

## Install
No dependencies — Python 3.8+ standard library only.

## Usage
```bash
python main.py add Buy milk
python main.py add Write code
python main.py list
python main.py done 1
python main.py list --all
python main.py remove 2
python main.py clear
```

## Example
```
$ python main.py list
[ ]   1  Buy milk
[ ]   2  Write code
```

## Requirements
Python 3.8+
