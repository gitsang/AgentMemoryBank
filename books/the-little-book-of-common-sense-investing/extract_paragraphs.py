#!/usr/bin/env python3
"""Extract the translatable paragraphs of every section into a work queue.

The paragraph selection lives here so that the extractor and the interleaver
used by build_html.py always agree on which elements exist, in which order.

Scope: prose elements (`<p>` and `<li>`) inside each `<section>`. Figure
captions, headings, the running nav and the copyright boilerplate are excluded.

Usage:
    SECTIONS_JSON=sections.json python3 extract_paragraphs.py [out.json]
"""

import json
import os
import re
import sys
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

SECTIONS_PATH = os.environ.get('SECTIONS_JSON', '/tmp/sections.json')
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else 'paragraphs.json'

# sections that are pure legal boilerplate and not worth translating
SKIP_SECTIONS = {'fm-copyright'}
# a paragraph shorter than this (in characters) is a fragment, not prose
MIN_CHARS = 2


def soup_of(html):
    return BeautifulSoup(f'<div id="__root__">{html}</div>', 'lxml')


def selection(root):
    """The translatable elements under a parsed root, in document order."""
    for el in root.find_all(['p', 'li']):
        # skip paragraphs that only contain a decorative <br/> run
        if not plain(el).strip():
            continue
        if len(plain(el)) < MIN_CHARS:
            continue
        yield el


def iter_paragraphs(html):
    """Yield the translatable elements of a section, in document order."""
    yield from selection(soup_of(html).find(id='__root__'))


def plain(el):
    return re.sub(r'\s+', ' ', el.get_text(' ')).strip()


def src_key(text, n=90):
    """A short, stable fingerprint of a paragraph's opening words."""
    return re.sub(r'\s+', ' ', text).strip()[:n]


def main():
    sections = json.load(open(SECTIONS_PATH))
    queue = {}
    for s in sections:
        if s['id'] in SKIP_SECTIONS:
            continue
        paras = []
        for i, el in enumerate(iter_paragraphs(s['html'])):
            cls = el.get('class') or []
            paras.append({
                'i': i,
                'kind': el.name,
                'class': ' '.join(cls),
                'src': src_key(plain(el)),
                'text': plain(el),
            })
        queue[s['id']] = {
            'title': s['title'],
            'kind': s['kind'],
            'paragraphs': paras,
        }

    json.dump(queue, open(OUT_PATH, 'w'), ensure_ascii=False, indent=1)
    total = sum(len(v['paragraphs']) for v in queue.values())
    words = sum(len(p['text'].split())
                for v in queue.values() for p in v['paragraphs'])
    print(f'wrote {OUT_PATH}')
    print(f'sections: {len(queue)} | paragraphs: {total} | words: {words}')
    print()
    print(f'{"section":26s} {"paras":>5s} {"words":>7s}  title')
    for sid, v in queue.items():
        w = sum(len(p['text'].split()) for p in v['paragraphs'])
        print(f'{sid:26s} {len(v["paragraphs"]):5d} {w:7d}  {v["title"]}')


if __name__ == '__main__':
    main()
