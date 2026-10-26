#!/usr/bin/env python3
"""Guard against unintentional size and dependency growth in public site assets.

This is a SOURCE-LEVEL performance budget, not a Lighthouse score or a
measurement of page loading time. Dependencies: Python standard library only.
"""
from html.parser import HTMLParser
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

# Conservative, uncompressed source-size limits. Keep them above current
# content size so routine copy edits do not trigger false alarms.
PAGE_LIMITS = {
    "index.html": 56 * 1024,
    "privacy.html": 16 * 1024,
    "404.html": 16 * 1024,
}
CSS_LIMIT = 25 * 1024
FAVICON_LIMIT = 8 * 1024
SHARE_IMAGE_LIMIT = 550 * 1024
ALLOWED_SCRIPTS = {"https://static.cloudflareinsights.com/beacon.min.js"}


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external_scripts = []
        self.inline_scripts = 0
        self.ending_script = False
        self.external_stylesheets = []
        self.remote_font_preloads = []
        self.images = []
        self.css = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self.ending_script = True
            if a.get("src"):
                self.external_scripts.append(a["src"])
            else:
                self.inline_scripts += 1
        if tag == "link" and a.get("rel") == "stylesheet":
            self.external_stylesheets.append(a.get("href", ""))
        if tag == "link" and a.get("rel") == "preload" and a.get("as") == "font":
            self.remote_font_preloads.append(a.get("href", ""))
        if tag == "img":
            self.images.append(a)

    def handle_endtag(self, tag):
        if tag == "script":
            self.ending_script = False


def validate_page(name, limit):
    path = ROOT / name
    if not path.is_file():
        ERRORS.append(f"Missing HTML page: {name}")
        return
    raw = path.read_bytes()
    page_size = len(raw)
    if page_size > limit:
        ERRORS.append(f"{name}: {page_size} B exceeds {limit} B HTML budget")
    content = raw.decode("utf-8")
    parser = Resources()
    parser.feed(content)
    css = content.split("<style>", 1)
    css_bytes = 0
    if len(css) > 1 and "</style>" in css[1]:
        css_bytes = len(css[1].split("</style>", 1)[0].encode("utf-8"))
        if css_bytes > CSS_LIMIT:
            ERRORS.append(f"{name}: inline CSS is {css_bytes} B, over budget")
    if set(parser.external_scripts) - ALLOWED_SCRIPTS:
        ERRORS.append(f"{name}: unexpected third-party script(s): {parser.external_scripts}")
    if len(parser.external_scripts) != 1:
        ERRORS.append(f"{name}: expected one allowlisted Cloudflare analytics script")
    if parser.inline_scripts:
        ERRORS.append(f"{name}: unexpected inline JavaScript ({parser.inline_scripts})")
    if parser.external_stylesheets:
        ERRORS.append(f"{name}: added external stylesheet(s): {parser.external_stylesheets}")
    if parser.remote_font_preloads:
        ERRORS.append(f"{name}: unexpected font download(s): {parser.remote_font_preloads}")
    if parser.images:
        for image in parser.images:
            if not image.get("alt"):
                ERRORS.append(f"{name}: image missing nonempty alt attribute")
    print(f"{name:14} HTML {page_size:6} B / {limit:6} B; inline CSS {css_bytes:6} B")


for filename, bytes_limit in PAGE_LIMITS.items():
    validate_page(filename, bytes_limit)

favicon = ROOT / "favicon.svg"
if not favicon.is_file():
    ERRORS.append("Missing favicon.svg")
elif favicon.stat().st_size > FAVICON_LIMIT:
    ERRORS.append(f"favicon.svg over {FAVICON_LIMIT} B")
else:
    print(f"favicon.svg    {favicon.stat().st_size:6} B / {FAVICON_LIMIT:6} B")

preview = ROOT / "social-preview.png"
if not preview.is_file():
    ERRORS.append("Missing social-preview.png")
else:
    data = preview.read_bytes()
    if len(data) > SHARE_IMAGE_LIMIT:
        ERRORS.append(f"social-preview.png over {SHARE_IMAGE_LIMIT} B")
    if len(data) < 24 or data[:8] != b"\\x89PNG\\r\\n\\x1a\\n":
        ERRORS.append("Invalid PNG header")
    else:
        width, height = struct.unpack(">II", data[16:24])
        if (width, height) != (1200, 630):
            ERRORS.append(f"Unexpected social preview dimensions: {width}x{height}")
        print(f"social-preview.png {len(data):6} B / {SHARE_IMAGE_LIMIT:6} B; {width}x{height}")
    print("Note: social-preview.png is referenced as link-preview metadata, not a rendered homepage image.")

if ERRORS:
    for error in ERRORS:
        print("FAIL:", error)
    sys.exit(1)

print("PASS: Source asset-size budgets and dependency allowlist.")
print("Limitations: This test DOES NOT measure LCP, CLS, INP, TTFB, accessibility, or live network performance.")
