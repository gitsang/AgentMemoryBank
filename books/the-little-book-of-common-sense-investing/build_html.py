#!/usr/bin/env python3
"""Assemble index.html from the sections JSON produced by build_book.py.

Usage:
    SECTIONS_JSON=sections.json TRANSLATIONS_JSON=translations.json \
        python3 build_html.py <out.html>

SECTIONS_JSON defaults to /tmp/sections.json (build_book.py's default output).
When TRANSLATIONS_JSON points at a translations file, each translated paragraph
is followed by its Chinese rendering in a muted grey style.
"""

import html as html_mod
import json
import os
import re
import sys
import warnings

from bs4 import BeautifulSoup, NavigableString, XMLParsedAsHTMLWarning

from extract_paragraphs import (SKIP_SECTIONS, iter_paragraphs, plain,
                                selection, soup_of, src_key)

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

SECTIONS_PATH = os.environ.get('SECTIONS_JSON', '/tmp/sections.json')
TRANSLATIONS_PATH = os.environ.get('TRANSLATIONS_JSON', '')
ANNOTATIONS_PATH = os.environ.get('ANNOTATIONS_JSON', '')
GLOSSARY_PATH = os.environ.get('GLOSSARY_JSON', '')
HERE = os.path.dirname(os.path.abspath(__file__))

SECTIONS = json.load(open(SECTIONS_PATH))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/book_out/index.html'


def load_optional(path, default):
    if path and os.path.exists(path):
        return json.load(open(path))
    return default


ANNOTATIONS = load_optional(ANNOTATIONS_PATH, {}).get('sections', {})
GLOSSARY = load_optional(GLOSSARY_PATH, {}).get('terms', [])

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
  --note-bg: #f0ece2;
  --maxw: 44rem;
  --cjk: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun",
    ui-serif, Georgia, serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181a; --paper: #1e2023; --ink: #e6e2da; --muted: #9c958a;
    --rule: #33363a; --accent: #cbb083; --quote-bg: #24262a; --aside-bg: #24262a;
    --note-bg: #24262a;
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

/* ---------- floating icon toolbar ---------- */
.toolbar { position: fixed; right: 1rem; bottom: 1rem; z-index: 30;
  display: flex; flex-direction: column-reverse; gap: .55rem;
  align-items: center; }
.tool-btn { position: relative; width: 2.5rem; height: 2.5rem; padding: 0;
  display: grid; place-items: center;
  background: var(--paper); color: var(--accent); border: 1px solid var(--rule);
  border-radius: 50%; text-decoration: none; cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,.12);
  transition: color .15s, border-color .15s, opacity .15s; }
.tool-btn:hover, .tool-btn:focus-visible { color: var(--accent);
  border-color: var(--accent); }
.tool-btn .ic { width: 1.15rem; height: 1.15rem; display: block; }
.tool-btn.is-off { color: var(--muted); opacity: .68; }
.tool-btn .tool-tip { position: absolute; right: calc(100% + .6rem); top: 50%;
  transform: translateY(-50%) translateX(.3rem);
  white-space: nowrap; opacity: 0; pointer-events: none;
  background: var(--ink); color: var(--bg);
  font-family: var(--cjk); font-size: .7rem; line-height: 1; font-weight: 700;
  padding: .38rem .6rem; border-radius: .32rem;
  transition: opacity .15s, transform .15s; }
.tool-btn:hover .tool-tip, .tool-btn:focus-visible .tool-tip {
  opacity: 1; transform: translateY(-50%) translateX(0); }

/* ---------- parallel Chinese translation (对照翻译) ---------- */
p.tr, .tr {
  color: var(--muted);
  font-size: .9em;
  line-height: 1.62;
  text-align: left;
  hyphens: none;
  padding-left: .85rem;
  border-left: 2px solid var(--rule);
  margin: -.45rem 0 1.15rem;
  font-family: var(--cjk);
}
p.tr.q { font-style: normal; }
p.tr.pull { font-weight: 400; text-align: center; max-width: 30rem;
  margin: 1.1rem auto .2rem; border-left: 0; padding-left: 0; }
blockquote .tr, aside.box .tr { border-left-color: var(--muted); }
li > .tr { margin: .3rem 0 .65rem; }
.note .tr { margin: 0 0 .7rem; }
body.no-tr .tr { display: none; }

.tr-toggle-note { display: none; }

/* ---------- chapter rail (wide screens) ---------- */
.rail { display: none; }
@media (min-width: 1400px) {
  .rail { display: block; position: fixed; left: 1.5rem; top: 50%;
    transform: translateY(-50%); width: 10.5rem; max-height: 78vh;
    overflow-y: auto; z-index: 10; font-family: var(--cjk);
    scrollbar-width: thin; }
  .rail-title { margin: 0 0 .5rem; padding-left: .5rem; color: var(--accent);
    font: 600 .66rem/1 ui-sans-serif, system-ui, sans-serif;
    letter-spacing: .16em; text-transform: uppercase; }
  .rail ol { margin: 0; padding: 0; list-style: none; }
  .rail li { margin: .05rem 0; }
  .rail a { display: flex; gap: .45rem; align-items: baseline;
    padding: .24rem .5rem; border-radius: .28rem;
    text-decoration: none; color: var(--muted);
    font-size: .76rem; line-height: 1.35; }
  .rail a:hover { color: var(--accent); background: var(--paper); }
  .rail a .n { flex: 0 0 1.3rem; text-align: right; color: var(--rule);
    font-family: ui-sans-serif, system-ui, sans-serif; font-size: .67rem;
    font-variant-numeric: tabular-nums; }
  .rail a.is-active { color: var(--accent); font-weight: 700;
    background: var(--paper); }
  .rail a.is-active .n { color: var(--accent); }
  .rail .rail-sep { margin: .45rem 0; border-top: 1px solid var(--rule); }
}

/* ---------- glossary terms + popover ---------- */
.term { font: inherit; color: inherit; background: none; border: 0; padding: 0;
  margin: 0; cursor: help; text-align: inherit;
  border-bottom: 1px dotted var(--accent); }
.term:hover, .term.is-open { color: var(--accent); border-bottom-style: solid; }
.glossary-pop { position: absolute; z-index: 40;
  width: min(22rem, calc(100vw - 24px));
  background: var(--paper); color: var(--ink);
  border: 1px solid var(--rule); border-radius: .5rem;
  padding: .85rem 1rem; box-shadow: 0 6px 24px rgba(0,0,0,.18);
  font-size: .85rem; line-height: 1.62; }
.gp-en { font: 600 .72rem/1.3 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: .05em; color: var(--muted); }
.gp-zh { font-family: var(--cjk); font-size: 1.02rem; font-weight: 700;
  margin: .2rem 0 .5rem; }
.gp-note { font-family: var(--cjk); }

/* ---------- margin annotations (批注) ---------- */
.sidenote { display: block; margin: .5rem 0 1.3rem; padding: .7rem .95rem;
  background: var(--note-bg); border-left: 3px solid var(--accent);
  border-radius: 0 .3rem .3rem 0;
  font-family: var(--cjk); font-size: .85rem; line-height: 1.7;
  color: var(--muted); }
.sidenote .sn-title { margin: 0 0 .35rem; font-size: .78rem; font-weight: 700;
  color: var(--accent); letter-spacing: .02em; }
.sidenote p { margin: 0; text-align: left; }
body.no-notes .sidenote { display: none; }

/* ---------- glossary appendix ---------- */
.glossary-appendix { margin: 3rem 0 1rem; padding: 1rem 1.25rem;
  background: var(--paper); border: 1px solid var(--rule); border-radius: .5rem; }
.glossary-appendix > summary { cursor: pointer; font: 600 .78rem/1.6
  ui-sans-serif, system-ui, sans-serif; letter-spacing: .1em;
  text-transform: uppercase; color: var(--accent); }
.glossary-appendix dl { margin: 1rem 0 0; }
.gl-entry { margin: 0 0 .9rem; }
.gl-entry dt { font-weight: 700; font-size: .88rem; }
.gl-entry dt .gl-zh { font-family: var(--cjk); font-weight: 700;
  color: var(--accent); margin-left: .5rem; }
.gl-entry dd { margin: .2rem 0 0; font-family: var(--cjk);
  font-size: .82rem; line-height: 1.65; color: var(--muted); }

/* ---------- wide screens: annotations in the right margin ---------- */
@media (min-width: 1150px) {
  .wrap { max-width: 68rem; padding-right: 23rem; }
  .sidenote { float: right; clear: right; width: 20rem;
    margin: .1rem -21.5rem 1.7rem 0; padding: 0 0 0 .85rem;
    background: transparent; border-left: 2px solid var(--rule);
    border-radius: 0; font-size: .8rem; line-height: 1.62; }
  .sidenote .sn-title { font-size: .74rem; }
  .glossary-appendix { max-width: 44rem; }
}

@media print {
  :root { --bg: #fff; --paper: #fff; --ink: #000; --rule: #bbb; --muted: #555; }
  .back-to-top, nav.toc, .toolbar, .glossary-pop, .rail { display: none; }
  section { break-before: page; }
  body { font-size: 11pt; }
  p.tr, .tr, .sidenote { break-inside: avoid; }
  .sidenote { float: none; clear: none; width: auto; margin: .5rem 0 1rem;
    padding: .5rem .7rem; background: #f4f2ee;
    border-left: 2px solid #999; }
  .term { border-bottom: 0; }
}
"""


def page_script():
    """Reader-side JS (glossary popovers, toggles), inlined into the page."""
    with open(os.path.join(HERE, 'page.js'), encoding='utf-8') as fh:
        return fh.read()



def normalise_entries(entries):
    """Accept either {index: entry} or a positional list of entries."""
    out = {}
    if isinstance(entries, dict):
        for k, v in entries.items():
            try:
                out[int(k)] = v
            except (TypeError, ValueError):
                continue
    elif isinstance(entries, list):
        out = dict(enumerate(entries))
    return out


def interleave(section_html, entries):
    """Insert each paragraph's translation directly after it.

    Entries are keyed by paragraph index (a list is accepted too, and treated
    as positional). The translation mirrors the source paragraph's classes so
    that quoted or indented paragraphs keep the same shape, plus a `tr` marker
    for styling. Each entry carries a `src` fingerprint of the paragraph it
    belongs to; if the fingerprint does not match, the correct paragraph is
    looked up by fingerprint rather than being silently misplaced.
    """
    soup = soup_of(section_html)
    root = soup.find(id='__root__')
    els = list(selection(root))
    inserted = mismatched = 0

    for i, entry in sorted(normalise_entries(entries).items()):
        zh = (entry.get('zh') or '').strip()
        if not zh:
            continue
        want = (entry.get('src') or '').strip()[:60]
        el = els[i] if 0 <= i < len(els) else None
        if el is None or (want and not plain(el).startswith(want)):
            el = next((e for e in els if want and plain(e).startswith(want)), None)
            if el is None:
                mismatched += 1
                continue
        cls = ['tr'] + list(el.get('class') or [])
        if el.name == 'li':
            node = soup.new_tag('div')
            node['class'] = cls
            node.string = zh
            el.append(node)
        else:
            node = soup.new_tag('p')
            node['class'] = cls
            node.string = zh
            el.insert_after(node)
        inserted += 1

    return ''.join(str(c) for c in root.children), inserted, mismatched


def md_inline(text):
    """Render the small subset of inline markup used in the notes (**bold**)."""
    parts = text.split('**')
    return ''.join(
        html_mod.escape(p) if i % 2 == 0
        else f'<strong>{html_mod.escape(p)}</strong>'
        for i, p in enumerate(parts))


def rich_nodes(soup, text):
    """Same as md_inline, but built as nodes for parsing-created elements."""
    nodes = []
    for i, part in enumerate(text.split('**')):
        if not part:
            continue
        if i % 2:
            node = soup.new_tag('strong')
            node.string = part
        else:
            node = NavigableString(part)
        nodes.append(node)
    return nodes


def add_sidenotes(section_html, entries):
    """Insert Chinese margin annotations before the paragraphs they discuss.

    Placement is deliberate: the note is emitted *before* its paragraph so the
    right float starts at that paragraph's top rather than beside whatever
    follows it. Entries accept the same index + `src` fingerprint pairing as
    translations, so a drifted index relocates instead of mis-attaching.
    """
    soup = soup_of(section_html)
    root = soup.find(id='__root__')
    els = list(selection(root))
    added = mismatched = 0

    for i, entry in sorted(normalise_entries(entries).items()):
        body = (entry.get('zh') or '').strip()
        if not body:
            continue
        want = (entry.get('src') or '').strip()[:60]
        el = els[i] if 0 <= i < len(els) else None
        if el is None or (want and not plain(el).startswith(want)):
            el = next((e for e in els if want and plain(e).startswith(want)), None)
            if el is None:
                mismatched += 1
                continue
        note = soup.new_tag('aside')
        note['class'] = 'sidenote'
        if entry.get('title'):
            head = soup.new_tag('p')
            head['class'] = 'sn-title'
            head.string = entry['title']
            note.append(head)
        para = soup.new_tag('p')
        for node in rich_nodes(soup, body):
            para.append(node)
        note.append(para)
        el.insert_before(note)
        added += 1

    return ''.join(str(c) for c in root.children), added, mismatched


def glossary_appendix(terms):
    rows = []
    for t in terms:
        rows.append(
            f'<div class="gl-entry"><dt>{html_mod.escape(t["en"])}'
            f'<span class="gl-zh">{html_mod.escape(t["zh"])}</span></dt>'
            f'<dd>{md_inline(t["note"])}</dd></div>')
    return ('<details class="glossary-appendix" id="glossary">'
            f'<summary>\u672f\u8bed\u5bf9\u7167\u8868\uff08{len(terms)} \u6761\uff09</summary>'
            f'<dl>{"".join(rows)}</dl></details>')


# Inline SVG icons, kept in the same 24x24 / 1.7 stroke idiom so the floating
# buttons read as one set.
IC_TOP = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
          'aria-hidden="true"><path d="M12 19V6"/><path d="M6 12l6-6 6 6"/></svg>')
IC_NOTE = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
           'aria-hidden="true"><path d="M4 6h11M4 11h11M4 16h6"/>'
           '<path d="M15 14h5v6l-3-2.4h-2z"/></svg>')
IC_GUIDE = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true"><path d="M4 5h8v14H4z"/><path d="M12 9h8v10h-8z"/>'
            '<path d="M6.5 9h3M6.5 12h3M14.5 12.5h3"/></svg>')

# Short Chinese labels for the chapter rail. These are my own descriptive
# labels, not the publisher's chapter titles (which stay on the section heads).
RAIL_LABELS = {
    'intro': '\u5f15\u8a00',
    'ch01': '\u5bd3\u8a00',
    'ch02': '\u7406\u6027\u7e41\u8363',
    'ch03': '\u62bc\u6ce8\u4f01\u4e1a',
    'ch04': '\u8d62\u5bb6\u53d8\u8f93\u5bb6',
    'ch05': '\u5927\u5e7b\u89c9',
    'ch06': '\u7a0e\u4e5f\u662f\u6210\u672c',
    'ch07': '\u597d\u65e5\u5b50\u4e0d\u518d',
    'ch08': '\u6311\u9009\u8d62\u5bb6',
    'ch09': '\u6628\u5929\u7684\u8d62\u5bb6',
    'ch10': '\u627e\u4eba\u6311\u57fa\u91d1',
    'ch11': '\u6700\u4f4e\u8d39\u7387',
    'ch12': '\u7b80\u6734\u7684\u5c0a\u4e25',
    'ch13': '\u503a\u5238\u4e0e\u8d27\u57fa',
    'ch14': '\u627f\u8bfa\u8d85\u989d\u6536\u76ca',
    'ch15': 'ETF \u4e0e\u4ea4\u6613',
    'ch16': '\u683c\u96f7\u5384\u59c6\u4e4b\u95ee',
    'ch17': '\u65e0\u60c5\u7b97\u672f',
    'ch18': '\u6211\u8be5\u505a\u4ec0\u4e48',
    'back-acknowledgments': '\u81f4\u8c22',
    'back-notes': '\u6ce8\u91ca',
}


def tool_button(btn_id, label, icon):
    esc = html_mod.escape(label)
    return (f'<button class="tool-btn" id="{btn_id}" type="button" '
            f'data-label="{esc}" aria-pressed="true" aria-label="{esc}">'
            f'{icon}<span class="tool-tip">{esc}</span></button>')


def chapter_rail():
    """Fixed left-hand rail listing the sections, for quick chapter jumps."""
    items, sep_done = [], False
    for s in SECTIONS:
        if s['id'].startswith('fm-'):
            continue
        if s['kind'] == 'back' and not sep_done:
            items.append('<li class="rail-sep"></li>')
            sep_done = True
        label = RAIL_LABELS.get(s['id'], s['title'])
        num = s['id'][2:].lstrip('0') if s['id'].startswith('ch') else '\u00b7'
        items.append(
            f'<li><a href="#{s["id"]}" title="{html_mod.escape(s["title"])}">'
            f'<span class="n">{num}</span>{html_mod.escape(label)}</a></li>')
    return ('<nav class="rail" id="rail" aria-label="\u7ae0\u8282\u5bfc\u822a">'
            '<p class="rail-title">\u76ee\u5f55</p><ol>'
            + ''.join(items) + '</ol></nav>')


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
    tr_doc = load_optional(TRANSLATIONS_PATH, {})
    translations = tr_doc.get('sections', {})
    tr_label = tr_doc.get('label', '\u4e2d\u6587')

    parts, inserted, mismatched, notes, note_mismatch = [], 0, 0, 0, 0
    for s in SECTIONS:
        html = s['html']
        if s['id'] in translations:
            html, ins, mis = interleave(html, translations[s['id']])
            inserted += ins
            mismatched += mis
        if s['id'] in ANNOTATIONS:
            html, add, mis2 = add_sidenotes(html, ANNOTATIONS[s['id']])
            notes += add
            note_mismatch += mis2
        if s['id'] != 'fm-title-page':
            parts.append(html)
    body = '\n'.join(parts)

    total_paras = sum(1 for s in SECTIONS if s['id'] not in SKIP_SECTIONS
                      for _ in iter_paragraphs(s['html']))
    if translations:
        pct = inserted / max(total_paras, 1)
        print(f'translation: {inserted}/{total_paras} paragraphs '
              f'({pct:.0%}), mismatched {mismatched}')
    if ANNOTATIONS:
        print(f'annotations: {notes} notes across {len(ANNOTATIONS)} sections, '
              f'mismatched {note_mismatch}')

    buttons = []
    if translations:
        buttons.append(tool_button('trToggle', tr_label, IC_GUIDE))
    if ANNOTATIONS:
        buttons.append(tool_button('noteToggle', '\u6279\u6ce8', IC_NOTE))
    to_top = ('<a class="tool-btn" id="toTop" href="#top" '
              'aria-label="\u56de\u5230\u9876\u90e8">' + IC_TOP +
              '<span class="tool-tip">\u56de\u5230\u9876\u90e8</span></a>')
    # column-reverse renders the first child at the bottom of the stack
    toolbar = ('<div class="toolbar" role="group">'
               + to_top + ''.join(buttons) + '</div>')

    glossary_data = appendix = ''
    if GLOSSARY:
        payload = json.dumps({'terms': GLOSSARY}, ensure_ascii=False)
        payload = payload.replace('<', '\\u003c')
        glossary_data = ('<script type="application/json" id="glossary-data">'
                         + payload + '</script>')
        appendix = glossary_appendix(GLOSSARY)

    script = f'<script>{page_script()}</script>'

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
{chapter_rail()}
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

{appendix}

<footer class="book">
  <p><strong>{TITLE}: {SUBTITLE}</strong><br/>
  by {AUTHOR} — John Wiley &amp; Sons, 2007. ISBN 978-0-470-10210-7.</p>
  <p>Plain-text edition converted from EPUB for personal reading.
  Figures reproduced from the original. All rights remain with the author and publisher.</p>
</footer>

</div>
{toolbar}
{glossary_data}
{script}
</body>
</html>
"""
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('wrote', OUT, len(doc), 'bytes')

if __name__ == '__main__':
    main()
