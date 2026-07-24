#!/usr/bin/env python3
"""fetch_article.py — fetch a news URL and print a clean-ish text copy to stdout.

Usage:
    python3 scripts/fetch_article.py <url> > output/<slug>/source.txt

Stdlib only, so it runs anywhere. It strips scripts/styles/nav and collapses whitespace.
This is a convenience for keeping a saved record of the source; for drafting, Claude Code can
also just read the page directly. Always treat the original page as the source of truth.
"""
import sys
import re
import urllib.request
from html.parser import HTMLParser

SKIP_TAGS = {"script", "style", "noscript", "header", "footer", "nav", "svg"}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "div"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self.parts.append(text + " ")


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: fetch_article.py <url>")
    url = sys.argv[1]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ai-news-video)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    parser = TextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    print(f"SOURCE: {url}\n")
    print(text)


if __name__ == "__main__":
    main()
