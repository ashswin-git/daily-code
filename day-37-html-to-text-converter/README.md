# Day 37 — HTML to Text Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Turn HTML pages or fragments into clean, readable plain text from the command line. Scripts, styles and other noise are dropped, while headings, lists, quotes, code and tables keep a readable shape. Standard library only.

## Features

- Removes `<script>`, `<style>`, `<head>`, `<svg>`, `<iframe>` and similar noise
- Decodes HTML entities (`&amp;`, `&nbsp;`, `&#8217;` and friends)
- Headings, with `=` / `-` underlines for `h1` and `h2` (`--no-underline` to skip)
- Bulleted, numbered and nested lists (respects `<ol start>`)
- Block quotes prefixed with `>` and `<pre>` code kept as-is, indented
- Table rows rendered as `cell | cell`
- `--links` numbers each link and lists the URLs at the end
- `--images` shows image alt text as `[alt]`
- `--width N` wraps long lines
- Reads stdin, writes to a file with `-o`

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py page.html                      # text to stdout
python main.py page.html --links -w 72 -o page.txt
curl -s https://example.com | python main.py --links
```

## Example

`page.html`:

```html
<h1>Hello &amp; Welcome</h1>
<p>This is <b>bold</b> and a <a href="https://example.com">link</a>.</p>
<ul><li>First</li><li>Second<ol><li>Nested one</li></ol></li></ul>
<script>alert(1)</script>
```

Command: `python main.py page.html --links`

```text
HELLO & WELCOME
===============

This is bold and a link [1].

- First
- Second
  1. Nested one

Links:
[1] https://example.com
```

## Requirements

- Python 3.8 or newer
- No third-party packages

## Built with

- Python standard library (`argparse`, `html.parser`, `re`, `textwrap`, `pathlib`)
