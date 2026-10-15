#!/usr/bin/env python3
"""Assemble index.html from the sections JSON produced by build_book.py.

Usage:
    SECTIONS_JSON=sections.json python3 build_html.py <out.html>

SECTIONS_JSON defaults to /tmp/sections.json (build_book.py's default output).
"""

import html as html_mod
import json
import os
import re
import sys

SECTIONS_PATH = os.environ.get('SECTIONS_JSON', '/tmp/sections.json')
SECTIONS = json.load(open(SECTIONS_PATH))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/book_out/index.html'

TITLE = 'The Little Book of Common Sense Investing'
SUBTITLE = 'The Only Way to Guarantee Your Fair Share of Stock Market Returns'
AUTHOR = 'John C. Bogle'

FRONT_IDS = [s['id'] for s in SECTIONS if s['kind'] == 'front']
BODY = [s for s in SECTIONS if s['kind'] == 'chapter']
BACK = [s for s in SECTIONS if s['kind'] == 'back']

CSS = """
:root {
  --bg: #f7f5f0;
  --paper: #fffdf8;
  --ink: #23201c;
  --muted: #6d6558;
  --rule: #ded6c8;
  --accent: #7a5c2e;
  --quote-bg: #f2ede3;
  --aside-bg: #f0ece2;
  --maxw: 44rem;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181a; --paper: #1e2023; --ink: #e6e2da; --muted: #9c958a;
    --rule: #33363a; --accent: #cbb083; --quote-bg: #24262a; --aside-bg: #24262a;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 400 18px/1.72 Georgia, "Times New Roman", serif;
}
.wrap { max-width: var(--maxw); margin: 0 auto; padding: 2.5rem 1.25rem 6rem; }
header.book { text-align: center; padding: 3rem 0 2.5rem; border-bottom: 1px solid var(--rule); }
header.book .kicker {
  font: 600 .7rem/1 ui-sans-serif, system-ui, sans-serif; letter-spacing: .18em;
  text-transform: uppercase; color: var(--accent); margin: 0 0 1rem;
}
header.book h1 { font-size: clamp(1.7rem, 5vw, 2.5rem); line-height: 1.2; margin: 0 0 .6rem; }
header.book .sub { color: var(--muted); font-style: italic; margin: 0 0 1rem; }
header.book .by { font: 600 .8rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 0; }

nav.toc { margin: 2.5rem 0 3rem; padding: 1.5rem 1.75rem; background: var(--paper);
  border: 1px solid var(--rule); border-radius: .5rem; }
nav.toc h2 { font: 600 .72rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .16em; text-transform: uppercase; color: var(--accent);
  margin: 0 0 1rem; }
nav.toc ol { margin: 0; padding-left: 1.4rem; }
nav.toc li { margin: .35rem 0; }
nav.toc a { color: var(--ink); text-decoration: none; border-bottom: 1px solid transparent; }
nav.toc a:hover { border-bottom-color: var(--accent); }
nav.toc .grp { margin-top: 1.1rem; color: var(--muted);
  font: 600 .68rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .14em; text-transform: uppercase; }

section { padding-top: 1.5rem; }
section.chapter { border-top: 1px solid var(--rule); margin-top: 3.5rem; }
section.front, section.back { margin-top: 3rem; border-top: 1px solid var(--rule); }

.chapter-label { font: 600 .72rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .16em; text-transform: uppercase; color: var(--accent);
  margin: 2.5rem 0 .6rem; }
h2 { font-size: clamp(1.35rem, 3.5vw, 1.75rem); line-height: 1.25; margin: .2rem 0 .5rem; }
.subtitle { font-size: 1.05rem; color: var(--muted); font-style: italic; margin: 0 0 1.5rem; }
.tagline { font-size: 1.02rem; color: var(--muted); font-style: italic;
  margin: 0 0 1.75rem; padding-bottom: 1rem; border-bottom: 1px solid var(--rule); }

p { margin: 0 0 1.05rem; text-align: justify; hyphens: auto; }
p.ind { text-indent: 1.4em; }
p.q { font-style: italic; }
p.q.ind { font-style: italic; text-indent: 1.4em; }
p.small { font-size: .82rem; line-height: 1.6; color: var(--muted); text-align: left; }
p.pull { font-weight: 700; text-align: center; font-size: 1.02rem;
  margin: 2rem auto; max-width: 34rem; line-height: 1.5; }

blockquote { margin: 1.4rem 0; padding: .9rem 1.3rem; background: var(--quote-bg);
  border-left: 3px solid var(--accent); border-radius: 0 .35rem .35rem 0; }
blockquote p { margin: 0 0 .8rem; font-style: italic; }
blockquote p:last-child { margin-bottom: 0; }

ul { margin: 1.1rem 0 1.3rem; padding-left: 1.5rem; }
li { margin: .5rem 0; text-align: justify; }

aside.box { margin: 2rem 0; padding: 1.25rem 1.5rem; background: var(--aside-bg);
  border: 1px solid var(--rule); border-radius: .5rem; }
aside.box .box-title { font: 600 .78rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
  margin: 0 0 .9rem; }
aside.box p { font-size: .95rem; }

figure { margin: 2rem 0; text-align: center; }
figure img { max-width: 100%; height: auto; }
figure.fig-table { overflow-x: auto; }
figure.fig-table table { margin: 0 auto; }
figcaption { margin-top: .7rem; font-size: .82rem; line-height: 1.5;
  color: var(--muted); text-align: center; }
table { border-collapse: collapse; font: 400 .85rem/1.5 ui-sans-serif, system-ui, sans-serif;
  border: 1px solid var(--rule); background: var(--paper); }
th, td { padding: .45rem .8rem; border-bottom: 1px solid var(--rule); text-align: left; }
th { background: var(--aside-bg); font-weight: 700; }
tr:last-child td { border-bottom: 0; }

.note { display: flex; gap: .7rem; margin: .8rem 0; font-size: .92rem; }
.note-num { flex: 0 0 1.6rem; font: 700 .75rem/1.7 ui-sans-serif, system-ui, sans-serif;
  color: var(--accent); text-align: right; }
.note p { margin: 0; }
.note p.q { font-style: normal; }

sup { font-size: .7em; line-height: 0; }
a { color: var(--accent); }
section:target { animation: flash 1.6s ease-out; }
@keyframes flash { from { background: rgba(122,92,46,.13); } to { background: transparent; } }

footer.book { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--rule);
  font-size: .8rem; line-height: 1.7; color: var(--muted); text-align: center; }

.back-to-top { position: fixed; right: 1rem; bottom: 1rem; z-index: 20;
  width: 2.5rem; height: 2.5rem; display: grid; place-items: center;
  background: var(--paper); color: var(--accent); border: 1px solid var(--rule);
  border-radius: 50%; text-decoration: none; font-size: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,.12); }
@media print {
  :root { --bg: #fff; --paper: #fff; --ink: #000; --rule: #bbb; --muted: #444; }
  .back-to-top, nav.toc { display: none; }
  section { break-before: page; }
  body { font-size: 11pt; }
}
"""


def body_or_face():
    pre = []

    pre.append('<div class="grp">Front Matter</div><ol>')
    for s in SECTIONS:
        if s['kind'] == 'front' and s['id'] != 'fm-title-page':
            pre.append(f'<li><a href="#{s["id"]}">{html_mod.escape(s["title"])}</a></li>')
    pre.append('</ol>')

    pre.append('<div class="grp">Chapters</div><ol>')
    for s in BODY:
        label = html_mod.escape(s['title'])
        pre.append(f'<li><a href="#{s["id"]}">{label}</a></li>')
    pre.append('</ol>')

    if BACK:
        pre.append('<div class="grp">Back Matter</div><ol>')
        for s in BACK:
            pre.append(f'<li><a href="#{s["id"]}">{html_mod.escape(s["title"])}</a></li>')
        pre.append('</ol>')

    return ''.join(pre)


def main():
    parts = [s['html'] for s in SECTIONS if s['id'] != 'fm-title-page']
    body = '\n'.join(parts)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{TITLE} — {AUTHOR}</title>
<meta name="description" content="{SUBTITLE}"/>
<meta name="author" content="{AUTHOR}"/>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<header class="book" id="top">
  <p class="kicker">Little Book, Big Profits</p>
  <h1>{TITLE}</h1>
  <p class="sub">{SUBTITLE}</p>
  <p class="by">{AUTHOR}</p>
</header>

<nav class="toc">
  <h2>Contents</h2>
  {body_or_face()}
</nav>

{body}

<footer class="book">
  <p><strong>{TITLE}: {SUBTITLE}</strong><br/>
  by {AUTHOR} — John Wiley &amp; Sons, 2007. ISBN 978-0-470-10210-7.</p>
  <p>Plain-text edition converted from EPUB for personal reading.
  Figures reproduced from the original. All rights remain with the author and publisher.</p>
</footer>

</div>
<a class="back-to-top" href="#top" aria-label="Back to top">↑</a>
</body>
</html>
"""
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('wrote', OUT, len(doc), 'bytes')


if __name__ == '__main__':
    main()
