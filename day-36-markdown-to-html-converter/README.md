# Day 36 — Markdown to HTML Converter

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Turn Markdown into clean HTML from the command line. Output a fragment to paste anywhere, or a full styled page ready to open in a browser. Standard library only.

## Features

- Headings with automatic anchor ids (`--no-anchors` to skip)
- Paragraphs, **bold**, *italic*, ~~strikethrough~~, `inline code` and hard line breaks
- Fenced code blocks with a `language-xxx` class, HTML-escaped safely
- Links, images and bare `https://` autolinks
- Block quotes (nested Markdown inside works)
- Unordered, ordered, nested and task lists (`- [x] done`)
- Pipe tables with left, center and right alignment
- Horizontal rules
- `--page` wraps the result in a full HTML document with light built-in CSS (`--no-style` to drop it)
- Reads stdin, writes to a file with `-o`

## Install

Python 3.8+ only, nothing to install.

## Usage

```bash
python main.py notes.md                      # HTML fragment to stdout
python main.py notes.md --page -o notes.html # full styled page
python main.py notes.md --page --title "My Notes" --no-style
cat README.md | python main.py > readme.html
```

## Example

`notes.md`:

```markdown
# Hello *World*

Some **bold** and `code`. See [docs](https://example.com).

- [x] done task
- todo
```

Output:

```html
<h1 id="hello-world">Hello <em>World</em></h1>
<p>Some <strong>bold</strong> and <code>code</code>. See <a href="https://example.com">docs</a>.</p>
<ul><li><input type="checkbox" disabled checked> done task</li><li>todo</li></ul>
```

## Requirements

- Python 3.8 or newer
- No third-party packages

## Built with

- Python standard library (`argparse`, `html`, `re`, `pathlib`)
