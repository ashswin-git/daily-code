#!/usr/bin/env python3
"""Day 37 - HTML to Text Converter.

Turn HTML pages or fragments into clean, readable plain text.
Standard library only.

Usage:
  python main.py page.html
  python main.py page.html --links --width 72 -o page.txt
  curl -s https://example.com | python main.py
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from html.parser import HTMLParser
from pathlib import Path

SKIP_TAGS = {"script", "style", "head", "noscript", "template", "svg", "iframe"}
BLOCK_TAGS = {
    "p", "div", "section", "article", "header", "footer", "main", "nav",
    "aside", "form", "table", "ul", "ol", "dl", "blockquote", "figure",
    "figcaption", "address", "fieldset", "details", "summary",
}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class TextExtractor(HTMLParser):
    def __init__(self, show_links: bool = False, show_images: bool = False):
        super().__init__(convert_charrefs=True)
        self.show_links = show_links
        self.show_images = show_images
        self.blocks: list[tuple[str, str]] = []  # (kind, text)
        self.buf: list[str] = []
        self.skip = 0
        self.pre = 0
        self.lists: list[list] = []  # [type, counter]
        self.quote = 0
        self.href_stack: list[str | None] = []
        self.links: list[str] = []
        self.row: list[str] = []
        self.cell: list[str] | None = None
        self.heading: str | None = None
        self.li_prefix = ""

    # -- helpers -------------------------------------------------------
    def flush(self, kind: str = "p") -> None:
        if self.lists and kind == "p" and self.li_prefix:
            kind = "li"
        text = "".join(self.buf)
        self.buf = []
        if self.pre:
            if text.strip("\n"):
                self.blocks.append(("pre", text.strip("\n")))
            return
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = "\n".join(line.strip() for line in text.split("\n")).strip()
        if kind == "li" and self.li_prefix:
            text = self.li_prefix + text if text else ""
            self.li_prefix = ""
        if text:
            if self.quote:
                kind = "quote"
            self.blocks.append((kind, text))

    def write(self, text: str) -> None:
        if self.cell is not None:
            self.cell.append(text)
        else:
            self.buf.append(text)

    # -- parser callbacks ---------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in BLOCK_TAGS or tag in HEADINGS or tag in ("li", "pre", "hr", "tr", "dt", "dd"):
            self.flush()
        if tag in HEADINGS:
            self.heading = tag
        elif tag == "br":
            self.write("\n")
        elif tag == "hr":
            self.blocks.append(("hr", ""))
        elif tag == "pre":
            self.pre += 1
        elif tag == "blockquote":
            self.quote += 1
        elif tag in ("ul", "ol"):
            start = int(a.get("start") or 1) if (a.get("start") or "1").isdigit() else 1
            self.lists.append([tag, start - 1])
        elif tag == "li":
            depth = max(len(self.lists) - 1, 0)
            indent = "  " * depth
            if self.lists and self.lists[-1][0] == "ol":
                self.lists[-1][1] += 1
                self.li_prefix = f"{indent}{self.lists[-1][1]}. "
            else:
                self.li_prefix = f"{indent}- "
        elif tag == "a":
            self.href_stack.append(a.get("href"))
        elif tag == "img" and self.show_images:
            alt = a.get("alt") or "image"
            self.write(f"[{alt}]")
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(self.skip - 1, 0)
            return
        if self.skip:
            return
        if tag == "a" and self.href_stack:
            href = self.href_stack.pop()
            if self.show_links and href and not href.startswith(("#", "javascript:")):
                if href not in self.links:
                    self.links.append(href)
                self.write(f" [{self.links.index(href) + 1}]")
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr":
            if any(self.row):
                self.blocks.append(("row", " | ".join(self.row)))
            self.row = []
        elif tag in HEADINGS:
            self.flush(self.heading or "h2")
            self.heading = None
        elif tag == "pre":
            self.flush()
            self.pre = max(self.pre - 1, 0)
        elif tag == "blockquote":
            self.flush()
            self.quote = max(self.quote - 1, 0)
        elif tag in ("ul", "ol"):
            self.flush("li")
            if self.lists:
                self.lists.pop()
        elif tag == "li":
            self.flush("li")
        elif tag in BLOCK_TAGS or tag in ("dt", "dd"):
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.write(data)

    def close(self):
        super().close()
        self.flush()


def render(blocks, links, width: int, underline: bool) -> str:
    out: list[str] = []
    prev = None
    for kind, text in blocks:
        tight = kind in ("li", "row") and prev == kind
        if out and not tight:
            out.append("")
        if kind == "hr":
            out.append("-" * min(width or 40, 40))
        elif kind == "pre":
            out.extend("    " + line for line in text.split("\n"))
        elif kind in HEADINGS:
            title = text.upper() if kind == "h1" else text
            out.append(title)
            if underline and kind in ("h1", "h2"):
                out.append(("=" if kind == "h1" else "-") * len(title))
        elif kind == "quote":
            for line in text.split("\n"):
                out.extend("> " + w for w in wrap(line, width - 2))
        elif kind == "li":
            m = re.match(r"(\s*(?:-|\d+\.) )", text)
            pad = " " * len(m.group(1)) if m else ""
            for i, line in enumerate(text.split("\n")):
                for j, w in enumerate(wrap(line, width - len(pad))):
                    out.append(w if (i == 0 and j == 0) else pad + w.lstrip())
        elif kind == "row":
            out.append(text)
        else:
            for line in text.split("\n"):
                out.extend(wrap(line, width))
        prev = kind
    if links:
        out += ["", "Links:"] + [f"[{i}] {u}" for i, u in enumerate(links, 1)]
    return "\n".join(out).strip() + "\n"


def wrap(line: str, width: int) -> list[str]:
    if width <= 0 or len(line) <= width:
        return [line]
    return textwrap.wrap(line, width, break_long_words=False, break_on_hyphens=False) or [""]


def html_to_text(html: str, links=False, images=False, width=0, underline=True) -> str:
    parser = TextExtractor(show_links=links, show_images=images)
    parser.feed(html)
    parser.close()
    return render(parser.blocks, parser.links, width, underline)


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert HTML to clean plain text.")
    ap.add_argument("file", nargs="?", help="HTML file (default: stdin)")
    ap.add_argument("-o", "--output", help="write text to this file")
    ap.add_argument("-w", "--width", type=int, default=0, help="wrap lines at N columns (0 = no wrap)")
    ap.add_argument("--links", action="store_true", help="number links and list URLs at the end")
    ap.add_argument("--images", action="store_true", help="show image alt text as [alt]")
    ap.add_argument("--no-underline", action="store_true", help="don't underline h1/h2 headings")
    ap.add_argument("--encoding", default="utf-8", help="input encoding (default utf-8)")
    args = ap.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        html = path.read_text(encoding=args.encoding, errors="replace")
    else:
        if sys.stdin.isatty():
            ap.print_help()
            return 1
        html = sys.stdin.read()

    text = html_to_text(html, args.links, args.images,
                        args.width, not args.no_underline)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        words = len(text.split())
        print(f"Wrote {args.output} ({words} words)", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
