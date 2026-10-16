#!/usr/bin/env python3
"""Extract the translatable paragraphs of every section into a work queue.

The paragraph selection lives here so that the extractor and the interleaver
used by build_html.py always agree on which elements exist, in which order.

Scope: prose elements (`<p>` and `<li>`) inside each `<section>`. Figure
captions, headings, the running nav and the copyright boilerplate are excluded.

Usage:
    SECTIONS_JSON=sections.json python3 extract_paragraphs.py [out.json]

Pass ``--body-only`` to narrow the queue to the running text: the Introduction
and the 18 numbered chapters, minus the chapter labels, taglines and quoted
"Don't Take My Word for It" asides. Front and back matter are dropped too, so
the queue is exactly the prose a translation of the book is expected to cover
and ``--strict`` can be a meaningful 100% check. ``build_html.py`` imports
the same definitions for its coverage accounting, so the numerator and
denominator cannot drift apart.
"""

import json
import os
import re
import sys
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

SECTIONS_PATH = os.environ.get('SECTIONS_JSON', '/tmp/sections.json')
OUT_PATH = next((a for a in sys.argv[1:] if not a.startswith('-')),
                'paragraphs.json')

# sections that are pure legal boilerplate and not worth translating
# sections to leave out of the translatable work queue (the copyright page used
# to be listed here; front matter is now dropped in build_book.py instead)
SKIP_SECTIONS = set()
# a paragraph shorter than this (in characters) is a fragment, not prose
MIN_CHARS = 2
# the running text of a chapter: everything else is apparatus (chapter labels,
# taglines, the quoted "Don't Take My Word for It" asides)
APPARATUS_CLASSES = {'chapter-label', 'subtitle', 'tagline', 'box-title'}
# the running text of the book. Single source of truth: the work queue and
# build_html.py's coverage count both scope themselves to this set.
BODY_SECTION_IDS = frozenset({'intro'} | {f'ch{i:02d}' for i in range(1, 19)})


def soup_of(html):
    return BeautifulSoup(f'<div id="__root__">{html}</div>', 'lxml')


def selection(root, body_only=False):
    """The translatable elements under a parsed root, in document order."""
    for el in root.find_all(['p', 'li']):
        # skip paragraphs that only contain a decorative <br/> run
        if not plain(el).strip():
            continue
        if len(plain(el)) < MIN_CHARS:
            continue
        if body_only and _is_apparatus(el):
            continue
        yield el


def _is_apparatus(el):
    """True for a label, tagline or quoted aside rather than running text."""
    if set(el.get('class') or []) & APPARATUS_CLASSES:
        return True
    return el.find_parent('aside', class_='box') is not None


def body_only(root):
    """Just the running text, for both the work queue and its coverage count."""
    yield from selection(root, body_only=True)


def iter_paragraphs(html, body_only=False):
    """Yield the translatable elements of a section, in document order."""
    yield from selection(soup_of(html).find(id='__root__'), body_only=body_only)


def plain(el):
    return re.sub(r'\s+', ' ', el.get_text(' ')).strip()


def src_key(text, n=90):
    """A short, stable fingerprint of a paragraph's opening words."""
    return re.sub(r'\s+', ' ', text).strip()[:n]


def main():
    only_body = '--body-only' in sys.argv[1:]
    sections = json.load(open(SECTIONS_PATH))
    queue = {}
    for s in sections:
        if s['id'] in SKIP_SECTIONS:
            continue
        if only_body and s['id'] not in BODY_SECTION_IDS:
            continue
        paras = []
        # `i` is always the paragraph's position in the full selection, even
        # when apparatus is filtered out, so the index stays comparable with
        # the one build_html.py's interleave() derives. --body-only changes
        # which paragraphs are queued, never how they are numbered.
        for i, el in enumerate(iter_paragraphs(s['html'])):
            if only_body and _is_apparatus(el):
                continue
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
