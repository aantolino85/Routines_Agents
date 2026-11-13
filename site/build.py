#!/usr/bin/env python3
"""Build the public pages from the markdown reports.

  python3 site/build.py            # builds site/out/weekend.html and site/out/deals.html

Each page holds every issue (newest first) with a picker, in the Evening Close Out style.
Everything is inlined, so the page works for anyone with the link, signed in or not.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "site" / "template.html").read_text()
OUT = ROOT / "site" / "out"

PAGES = {
    "weekend": {
        "src": ROOT / "personal" / "reports",
        "title": "Weekend Outlook",
        "h1": "Weekend<br>Outlook",
        "tagline": "Snow, shows, and what's on for Eddie: the weekend near Andover, MA.",
        "footer": "Compiled each week by Claude from resort reports, summit forecasts and event listings. "
                  "Check times and tickets with the venue before you go.",
        "accent": ("#1F5C52", "#5FB3A3"),
        "max_issues": 26,
    },
    "deals": {
        "src": ROOT / "professional" / "digests",
        "title": "Deal Desk",
        "h1": "Deal<br>Desk",
        "tagline": "The week's energy and data center deals, financings and policy moves.",
        "footer": "Not investment advice. Compiled each week by Claude from press releases, filings and trade "
                  "press; items marked “reported” are unconfirmed. Verify figures with the primary source.",
        "accent": ("#1F5C52", "#5FB3A3"),
        "max_issues": 26,
    },
}


def render_issue(md_text: str) -> tuple[str, str]:
    """Return (title, html) for one report."""
    lines = md_text.strip().splitlines()
    title = ""
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:].strip()
    # Python-Markdown needs a blank line before a list; the agents don't always leave one.
    fixed, prev = [], ""
    for ln in lines:
        is_item = bool(re.match(r"\s*(?:[-*+]|\d+\.)\s", ln))
        prev_item = bool(re.match(r"\s*(?:[-*+]|\d+\.)\s", prev))
        if is_item and prev.strip() and not prev_item:
            fixed.append("")
        fixed.append(ln)
        prev = ln
    src = "\n".join(fixed).replace("<", "&lt;")          # never pass raw HTML through
    body = markdown.markdown(src, extensions=["tables", "sane_lists"])
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # Link bare URLs (outside existing tags/links).
    parts = re.split(r'(<a\b.*?</a>|<[^>]+>)', body, flags=re.S)
    for i, part in enumerate(parts):
        if part and not part.startswith("<"):
            parts[i] = re.sub(r'(https?://[^\s<)]+[^\s<).,;:])',
                              lambda m: f'<a href="{m.group(1)}">{m.group(1).split("://", 1)[1]}</a>', part)
    body = "".join(parts)
    body = re.sub(r'<a href="', '<a rel="noopener noreferrer" href="', body)
    # Sources section: smaller type.
    body = re.sub(r'(<h2>[^<]*Sources[^<]*</h2>)(.*)$', r'\1<div class="sources">\2</div>', body, flags=re.S)
    # Lead block: the opening TL;DR / Top 3 paragraph (and a list right after it) gets a card.
    m = re.match(r'\s*((?:<p><em>.*?</em></p>\s*)?)(<p><strong>(?:TL;DR|Top 3)[^<]*</strong>.*?</p>(?:\s*<ul>.*?</ul>)?)',
                 body, flags=re.S)
    if m:
        body = body[:m.start(2)] + f'<div class="lead">{m.group(2)}</div>' + body[m.end(2):]
    return title, body


def build(name: str, cfg: dict) -> Path:
    issues = []
    for f in sorted(cfg["src"].glob("*.md"), reverse=True)[: cfg["max_issues"]]:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.stem):
            continue
        title, body = render_issue(f.read_text())
        issues.append({"date": f.stem, "title": title, "html": body})
    data = json.dumps(issues, ensure_ascii=False).replace("</", "<\\/")
    page = (TEMPLATE
            .replace("__TITLE__", html.escape(cfg["title"]))
            .replace("__H1__", cfg["h1"])
            .replace("__TAGLINE__", html.escape(cfg["tagline"]))
            .replace("__FOOTER__", html.escape(cfg["footer"]))
            .replace("__ACCENT_DARK__", cfg["accent"][1])
            .replace("__ACCENT__", cfg["accent"][0])
            .replace("__BUILT__", dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
            .replace("__DATA__", data))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{name}.html"
    out.write_text(page)
    return out


if __name__ == "__main__":
    for name, cfg in PAGES.items():
        p = build(name, cfg)
        print(f"{name}: {p} ({p.stat().st_size // 1024} KB)")
