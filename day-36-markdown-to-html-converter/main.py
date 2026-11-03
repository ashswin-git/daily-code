#!/usr/bin/env python3
"""Day 36 - Markdown to HTML Converter.

A small, dependency-free Markdown to HTML converter. Supports headings,
paragraphs, bold/italic/strikethrough, inline code, fenced code blocks,
links, images, block quotes, ordered/unordered/task lists, horizontal
rules and pipe tables. Can output a fragment or a full styled page.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

CSS = """body{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#222}
pre{background:#f5f5f5;padding:.8rem;border-radius:6px;overflow:auto}code{background:#f0f0f0;padding:.1rem .3rem;border-radius:4px}
pre code{background:none;padding:0}blockquote{border-left:4px solid #ccc;margin:0;padding-left:1rem;color:#555}
table{border-collapse:collapse}th,td{border:1px solid #ccc;padding:.3rem .6rem}img{max-width:100%}"""


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def inline(text: str) -> str:
    """Convert inline Markdown (code, images, links, emphasis) to HTML."""
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<![\"=>])\b(https?://[^\s<]*[^\s<.,;:!?)])", r'<a href="\1">\1</a>', text)
    text = re.sub(r"(\*\*|__)(.+?)\1", r"<strong>\2</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    text = re.sub(r"  $", "<br>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def render_list(lines: list[str], i: int) -> tuple[str, int]:
    """Render a (possibly nested) list starting at lines[i]."""
    m = LIST_RE.match(lines[i])
    indent = len(m.group(1))
    tag = "ol" if m.group(2)[0].isdigit() else "ul"
    items: list[str] = []
    while i < len(lines):
        m = LIST_RE.match(lines[i])
        if not m or len(m.group(1)) < indent:
            break
        if len(m.group(1)) > indent:
            sub, i = render_list(lines, i)
            items[-1] = items[-1][:-5] + sub + "</li>"
            continue
        body = m.group(3)
        task = re.match(r"\[([ xX])\]\s+(.*)", body)
        if task:
            checked = " checked" if task.group(1) in "xX" else ""
            body_html = f'<input type="checkbox" disabled{checked}> {inline(task.group(2))}'
        else:
            body_html = inline(body)
        items.append(f"<li>{body_html}</li>")
        i += 1
    return f"<{tag}>" + "".join(items) + f"</{tag}>", i


def split_row(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def convert(md: str, anchors: bool = True) -> str:
    lines = md.replace("\r\n", "\n").replace("\t", "    ").split("\n")
    out: list[str] = []
    para: list[str] = []
    i = 0

    def flush() -> None:
        if para:
            out.append("<p>" + inline("\n".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        fence = re.match(r"^(```|~~~)\s*(\w*)", stripped)
        if fence:
            flush()
            lang = fence.group(2)
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence.group(1)):
                code.append(lines[i])
                i += 1
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
            i += 1
            continue
        if not stripped:
            flush()
            i += 1
            continue
        h = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", stripped)
        if h:
            flush()
            n, content = len(h.group(1)), inline(h.group(2))
            idattr = f' id="{slugify(content)}"' if anchors else ""
            out.append(f"<h{n}{idattr}>{content}</h{n}>")
            i += 1
            continue
        if re.match(r"^([-*_])(\s*\1){2,}$", stripped):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + convert("\n".join(quote), anchors) + "</blockquote>")
            continue
        if LIST_RE.match(line):
            flush()
            block, i = render_list(lines, i)
            out.append(block)
            continue
        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$", lines[i + 1]):
            flush()
            aligns = []
            for c in split_row(lines[i + 1]):
                aligns.append("center" if c.startswith(":") and c.endswith(":") else "right" if c.endswith(":") else "left" if c.startswith(":") else "")
            def cell(tag: str, text: str, k: int) -> str:
                a = aligns[k] if k < len(aligns) and aligns[k] else ""
                style = f' style="text-align:{a}"' if a else ""
                return f"<{tag}{style}>{inline(text)}</{tag}>"
            head = "".join(cell("th", c, k) for k, c in enumerate(split_row(line)))
            rows = []
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append("<tr>" + "".join(cell("td", c, k) for k, c in enumerate(split_row(lines[i]))) + "</tr>")
                i += 1
            out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>")
            continue
        para.append(line.rstrip("\n"))
        i += 1
    flush()
    return "\n".join(out)


def full_page(body: str, title: str, style: bool) -> str:
    css = f"<style>{CSS}</style>" if style else ""
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n{css}\n</head>\n<body>\n{body}\n</body>\n</html>\n")


def main() -> int:
    p = argparse.ArgumentParser(description="Convert Markdown to HTML (no dependencies).")
    p.add_argument("input", nargs="?", help="Markdown file (default: stdin)")
    p.add_argument("-o", "--output", help="write HTML to this file")
    p.add_argument("--page", action="store_true", help="wrap in a full HTML page")
    p.add_argument("--no-style", action="store_true", help="with --page, skip the built-in CSS")
    p.add_argument("--title", help="page title (default: first heading or file name)")
    p.add_argument("--no-anchors", action="store_true", help="don't add id attributes to headings")
    args = p.parse_args()

    if args.input:
        path = Path(args.input)
        if not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        md = path.read_text(encoding="utf-8")
    else:
        md = sys.stdin.read()

    body = convert(md, anchors=not args.no_anchors)
    if args.page:
        first = re.search(r"^#{1,6}\s+(.+)$", md, re.M)
        title = args.title or (re.sub(r"[*_`~]", "", first.group(1)).strip() if first else (Path(args.input).stem if args.input else "Document"))
        result = full_page(body, title, not args.no_style)
    else:
        result = body + "\n"

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"wrote {args.output} ({len(result)} chars)", file=sys.stderr)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
