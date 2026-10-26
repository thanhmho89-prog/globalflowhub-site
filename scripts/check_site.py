#!/usr/bin/env python3
"""Read-only checks for the public GlobalFlowHub static website.

Uses Python's standard library only. This is source QA, not a penetration test,
browser accessibility audit, or proof of search indexing.
"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://globalflowhub.org"
ERRORS = []


def fail(message):
    ERRORS.append(message)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.descriptions = []
        self.canonicals = []
        self.h1_count = 0
        self.og_images = []
        self.scripts = []
        self.aria_references = []
        self.lang = False
        self.viewport = False
        self.title_count = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        element_id = a.get("id")
        if element_id:
            if element_id in self.ids:
                fail(f"Duplicate id: {element_id}")
            self.ids.add(element_id)
        if tag == "html":
            self.lang = bool(a.get("lang"))
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))
        if tag == "link" and a.get("rel") == "icon":
            self.links.append(a.get("href", ""))
        if tag == "meta":
            if a.get("name") == "description":
                self.descriptions.append(a.get("content", ""))
            if a.get("name") == "viewport":
                self.viewport = True
            if a.get("property") == "og:image":
                self.og_images.append(a.get("content", ""))
            if a.get("name") == "twitter:image":
                self.og_images.append(a.get("content", ""))
        if tag == "h1":
            self.h1_count += 1
        if tag == "script":
            self.scripts.append(a)
        if a.get("aria-labelledby"):
            self.aria_references.extend(a["aria-labelledby"].split())
        if tag == "title":
            self.title_count += 1


def local_target(url):
    """Map a same-origin link to an expected file. Ignore off-site links."""
    if not url or url.startswith(("mailto:", "tel:", "#", "javascript:")):
        return None
    parsed = urlsplit(url)
    if parsed.scheme and parsed.scheme != "https":
        fail(f"Unexpected URL scheme in link: {url}")
        return None
    if parsed.netloc and parsed.netloc != "globalflowhub.org":
        return None
    path = unquote(parsed.path)
    if not path or path == "/":
        path = "/index.html"
    elif path.endswith("/"):
        path += "index.html"
    path = path.lstrip("/")
    if ".." in Path(path).parts:
        fail(f"Invalid traversal in link: {url}")
        return None
    return ROOT / path


def check_page(name, expected_canonical):
    path = ROOT / name
    if not path.exists():
        fail(f"Missing required page: {name}")
        return
    parser = Page()
    parser.feed(path.read_text(encoding="utf-8"))
    if not parser.lang or not parser.viewport:
        fail(f"{name}: missing HTML language or viewport")
    if parser.h1_count != 1 or parser.title_count != 1:
        fail(f"{name}: expected one h1 and one title")
    if len(parser.descriptions) != 1 or not parser.descriptions[0].strip():
        fail(f"{name}: missing unique nonempty description")
    if parser.canonicals != [expected_canonical]:
        fail(f"{name}: canonical URL mismatch: {parser.canonicals}")
    if not parser.ids.issuperset(parser.aria_references):
        fail(f"{name}: broken aria-labelledby references: {set(parser.aria_references) - parser.ids}")
    for url in parser.links:
        if url.startswith("#"):
            if url[1:] not in parser.ids:
                fail(f"{name}: broken anchor: {url}")
        else:
            target = local_target(url)
            if target is not None and not target.exists():
                fail(f"{name}: missing linked file: {url}")
    for url in parser.og_images:
        target = local_target(url)
        if target is None or not target.exists():
            fail(f"{name}: missing or off-site social image: {url}")
    if len(parser.scripts) != 1 or parser.scripts[0].get("src") != "https://static.cloudflareinsights.com/beacon.min.js":
        fail(f"{name}: analytics script changed or duplicated")
    elif "data-cf-beacon" not in parser.scripts[0]:
        fail(f"{name}: analytics beacon configuration missing")


def check_sitemap():
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        fail("Missing sitemap.xml")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    try:
        xml = ET.parse(sitemap)
        locations = [node.text or "" for node in xml.findall(".//sm:loc", ns)]
    except ET.ParseError as e:
        fail(f"Malformed sitemap XML: {e}")
        return
    expected = {ORIGIN + "/", ORIGIN + "/privacy.html"}
    if set(locations) != expected or len(locations) != len(expected):
        fail(f"Unexpected sitemap entries: {locations}")
    if not (ROOT / "robots.txt").exists() or "Sitemap: " + ORIGIN + "/sitemap.xml" not in (ROOT / "robots.txt").read_text():
        fail("robots.txt must advertise canonical sitemap URL")


def check_google_verification():
    matches = list(ROOT.glob("google*.html"))
    if not matches:
        fail("Google Search Console verification HTML file missing")
    for path in matches:
        if path.read_text(encoding="utf-8").strip() != "google-site-verification: " + path.name:
            fail(f"Google verification file content mismatch: {path.name}")


check_page("index.html", ORIGIN + "/")
check_page("privacy.html", ORIGIN + "/privacy.html")

# GitHub Pages serves 404.html for unknown paths. The error page is
# intentionally not canonicalized or included in search sitemaps.
not_found = ROOT / "404.html"
if not not_found.exists():
    fail("Missing public custom 404.html")
else:
    text_404 = not_found.read_text(encoding="utf-8")
    parser_404 = Page()
    parser_404.feed(text_404)
    if parser_404.h1_count != 1 or not parser_404.lang or not parser_404.viewport:
        fail("404.html: requires one heading, page language and viewport")
    if 'name="robots" content="noindex,nofollow"' not in text_404:
        fail("404.html: should not be indexed")
    if len(parser_404.scripts) != 1 or parser_404.scripts[0].get("src") != "https://static.cloudflareinsights.com/beacon.min.js":
        fail("404.html: analytics beacon missing or duplicated")
    for url in parser_404.links:
        target = local_target(url)
        if target is not None and not target.exists():
            fail(f"404.html: broken local link {url}")
    for ref in parser_404.aria_references:
        if ref not in parser_404.ids:
            fail(f"404.html: missing aria-labelledby target {ref}")

check_sitemap()
check_google_verification()

if ERRORS:
    for error in ERRORS:
        print("FAIL:", error)
    print(f"{len(ERRORS)} static-site issue(s) found.")
    sys.exit(1)

print("PASS: two pages, internal anchors, local files, sitemap, verification file and analytics configuration.")
print("Note: browser rendering, network behavior, privacy practices, and search indexing are not tested.")
