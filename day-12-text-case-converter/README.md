# Day 12 — Text Case Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

A command-line text case converter. Turn any text into UPPER, lower, Title, Sentence, camelCase, PascalCase, snake_case, kebab-case, CONSTANT_CASE and more. Works on inline text, files, or piped input. Standard library only.

## Features

- 12 styles: `upper`, `lower`, `title`, `sentence`, `swap`, `alternating`, `camel`, `pascal`, `snake`, `kebab`, `constant`, `dot`
- Smart word splitting: understands spaces, `_`, `-` and camelCase boundaries (`HTTPServer` becomes `http_server`)
- `--all` shows every style at once
- Reads `--text`, a file, or stdin

## Run

```bash
cd day-12-text-case-converter
python3 main.py --help
```

## Usage

```bash
python3 main.py --text "hello world" --to snake
python3 main.py --text "user_profile_id" --to camel
echo "make this a title" | python3 main.py --to title
python3 main.py notes.txt --to upper
python3 main.py --text "Hello World" --all
python3 main.py --list
```

## Example

```text
$ python3 main.py --text "hello world" --all

upper        HELLO WORLD
lower        hello world
title        Hello World
sentence     Hello world
swap         HELLO WORLD
alternating  hElLo WoRlD
camel        helloWorld
pascal       HelloWorld
snake        hello_world
kebab        hello-world
constant     HELLO_WORLD
dot          hello.world
```

## Requirements

- Python 3.8+
- Standard library only (no `requirements.txt`)

## License

MIT
