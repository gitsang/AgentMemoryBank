#!/usr/bin/env python3
"""Convert _The Little Book of Common Sense Investing_ (2007 ed.) from EPUB to
per-section, figure-aware HTML.

Usage:
    python3 build_book.py <book.epub> [outdir]

The EPUB is unzipped into a temporary directory; each chapter/section found in
toc.ncx is rendered to JSON at <outdir>/../sections.json (written next to the
parser's cwd, see SECTIONS_JSON). Drop-in companion: build_html.py assembles
index.html from that JSON.
"""

import json
import os
import re
import shutil
import sys
import tempfile
import warnings
import zipfile

from bs4 import BeautifulSoup, NavigableString, Tag, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

SRC = None                  # populated from the EPUB argument
TEXT = IMAGES = None
MIN_FIG_PX = 150            # smaller images are chapter ornaments / stray glyphs
SECTIONS_JSON = os.environ.get('SECTIONS_JSON', '/tmp/sections.json')

# ------------------------------------------------------------------ structure
FRONT = [
    ('part0001.html', 'Little Book Big Profits Series'),
    ('part0002.html', 'Title Page'),
    ('part0003.html', 'Copyright'),
    ('part0004.html', 'Dedication'),
    ('part0005.html', 'Introduction'),
]
BACK = [
    ('part0024.html', 'Acknowledgments'),
    ('part0025.html', 'Notes'),
]

CH_NUM_WORDS = {
    'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6,
    'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10, 'Eleven': 11, 'Twelve': 12,
    'Thirteen': 13, 'Fourteen': 14, 'Fifteen': 15, 'Sixteen': 16,
    'Seventeen': 17, 'Eighteen': 18,
}

# classes that start their own block when nested inside a paragraph
BLOCKISH = {
    'liste', 'lsl', 'afmtx', 'centerAligned', 't', 'h', 'chabox', 'fmhbox',
    'fmtx', 'fmtx1', 'fmtx2', 'fmtx3', 'bmtx', 'cst', 'ctag', 'ctBT-T',
    'fmhBT-T', 'crt', 'fmhT', 'fmshT', 'fmhbox',
}

PARA_CLASS = {
    'fmtx': '',
    'fmtx1': 'ind',
    'fmtx2': 'q',
    'fmtx3': 'q ind',
}


def open_epub(path):
    """Unzip the EPUB and point TEXT/IMAGES at the extracted tree."""
    global SRC, TEXT, IMAGES
    SRC = tempfile.mkdtemp(prefix='book-epub-')
    with zipfile.ZipFile(path) as z:
        z.extractall(SRC)
    TEXT = os.path.join(SRC, 'text')
    IMAGES = os.path.join(SRC, 'images')
    for p in (TEXT, IMAGES, os.path.join(SRC, 'toc.ncx')):
        if not os.path.exists(p):
            raise SystemExit(f'{path}: expected {p} inside the EPUB')


def load_chapters():
    ncx = open(os.path.join(SRC, 'toc.ncx'), encoding='utf-8').read()
    out = []
    for m in re.finditer(
            r'<navPoint[^>]*>\s*<navLabel>\s*<text>(.*?)</text>\s*</navLabel>'
            r'\s*<content src="([^"]+)"', ncx, re.S):
        label = re.sub(r'\s+', ' ', m.group(1)).strip()
        cm = re.match(r'Chapter\s+(\w+)\s*-\s*(.*)$', label)
        if not cm:
            continue
        out.append({
            'file': os.path.basename(m.group(2).lstrip('./')),
            'num': CH_NUM_WORDS[cm.group(1)],
            'title': cm.group(2).strip(),
        })
    return out


def classes(tag):
    c = tag.get('class') or []
    return set(c if isinstance(c, list) else [c])


def plain_text(html):
    txt = html
    for a, b in (('&amp;', '&'), ('&nbsp;', ' '), ('&lt;', '<'), ('&gt;', '>'),
                 ('&quot;', '"'), ('&#8217;', "'"), ('&#8216;', "'"),
                 ('&#8220;', '"'), ('&#8221;', '"')):
        txt = txt.replace(a, b)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', txt)).strip()


def clean_inline(s):
    s = s.replace('\n', ' ')
    s = re.sub(r'[ \t\u00a0]+', ' ', s)
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    return s


def inline(node, skip_blocks=False):
    """Serialise inline content; optionally stop at nested block elements."""
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            out.append(str(ch))
            continue
        if not isinstance(ch, Tag):
            continue
        cls = classes(ch)
        if skip_blocks and (cls & BLOCKISH) and ch.name in ('div', 'table', 'ul'):
            continue
        name = ch.name
        if name == 'br':
            out.append('<br/>')
        elif name == 'img':
            continue
        elif name in ('i', 'em'):
            inner = inline(ch, skip_blocks)
            out.append(f'<em>{inner}</em>' if inner.strip() else inner)
        elif name in ('b', 'strong'):
            inner = inline(ch, skip_blocks)
            out.append(f'<strong>{inner}</strong>' if inner.strip() else inner)
        elif name == 'sup':
            out.append(f'<sup>{inline(ch, skip_blocks)}</sup>')
        elif name == 'a':
            inner = inline(ch, skip_blocks)
            if not inner.strip():
                continue
            href = ch.get('href', '')
            if href:
                href = re.sub(r'^[^#]*#', '#', href)
                attr = f' href="{href}"'
            else:
                attr = ''
            aid = ch.get('id')
            if aid:
                attr += f' id="{aid}"'
            out.append(f'<a{attr}>{inner}</a>')
        else:
            out.append(inline(ch, skip_blocks))
    return clean_inline(''.join(out)).strip()


class Renderer:
    def __init__(self):
        self.figures = []
        self.warnings = []
        self.pending_caption = None
        self.pending_caption_id = None

    # -------------------------------------------------------------- figures
    def figure(self, tag):
        # some exhibits are rendered as tables, not images
        table = tag.find('table')
        if table is not None:
            return self.table(table)
        img = tag.find('img')
        if not img:
            return ''
        m = re.search(r'([0-9]+\.[a-z]+)$', img.get('src', ''))
        if not m:
            return ''
        name = m.group(1)
        try:
            w, h = Image.open(os.path.join(IMAGES, name)).size
        except Exception:
            self.warnings.append(f'unreadable image {name}')
            return ''
        if max(w, h) < MIN_FIG_PX:
            return ''
        cap, cap_id = self.pending_caption, self.pending_caption_id
        self.pending_caption = self.pending_caption_id = None
        self.figures.append((name, cap))
        alt = re.sub(r'[<>&"]', '', cap or 'figure')
        attr = f' id="{cap_id}"' if cap_id else ''
        html = f'<figure{attr}><img src="images/{name}" alt="{alt}"/>'
        if cap:
            html += f'<figcaption>{cap}</figcaption>'
        return html + '</figure>'

    # --------------------------------------------------------------- blocks
    def blocks(self, parent):
        """Render a parent's children in order, flushing paragraph runs."""
        parts, buf = [], []

        def flush():
            if not buf:
                return
            text = clean_inline(''.join(buf)).strip()
            buf.clear()
            if not plain_text(text):
                return
            if plain_text(text).upper().startswith('EXHIBIT'):
                self.pending_caption = plain_text(text)
                return
            parts.append(f'<p>{text}</p>')

        for ch in parent.children:
            if isinstance(ch, NavigableString):
                if str(ch).strip():
                    buf.append(str(ch))
                continue
            if not isinstance(ch, Tag):
                continue
            cls = classes(ch)
            is_block = bool(cls & BLOCKISH) or ch.name in ('table', 'h1', 'ul')
            if is_block:
                flush()
                parts.append(self.block(ch))
            else:
                buf.append(inline(ch))
        flush()
        return ''.join(parts)

    def block(self, tag):
        name, cls = tag.name, classes(tag)

        if name == 'table' or 't' in cls:
            return self.table(tag)
        if name == 'h1' or 'h' in cls:
            t = unwrap_bold(inline(tag))
            return f'<p class="pull">{t}</p>' if t else ''

        if 'chabox' in cls or 'fmhbox' in cls:
            return self.box(tag)

        if 'centerAligned' in cls:
            return self.figure(tag)

        if 'liste' in cls:
            inner = ''.join(self.block(c) for c in tag.find_all(recursive=False)
                            if isinstance(c, Tag))
            return f'<ul>{inner}</ul>' if inner.strip() else ''

        if 'lsl' in cls:
            body = inline(tag, skip_blocks=True)
            nested = ''.join(self.block(c) for c in tag.find_all(recursive=False)
                             if isinstance(c, Tag))
            if not body.strip() and not nested.strip():
                return ''
            return f'<li>{body}{nested}</li>'

        if 'bmtx' in cls:
            aid = next((a['id'] for a in tag.find_all('a')
                        if a.get('id', '').startswith('FTN')), None)
            if aid:
                # the leading anchor only carries the note number, which we
                # render ourselves — skip it to avoid a duplicate
                body = ''.join(
                    self.block(c) for c in tag.find_all(recursive=False)
                    if isinstance(c, Tag) and not c.get('id', '').startswith('FTN'))
                body = body or inline(tag, skip_blocks=True)
                num = aid.split('-')[-1]
                return (f'<div class="note" id="{aid}">'
                        f'<span class="note-num">{num}</span>{body}</div>')
            return self.para(tag, 'fmtx')

        if 'afmtx' in cls:
            return f'<blockquote>{self.blocks(tag)}</blockquote>'

        if 'fmhT' in cls or 'fmh' in cls:
            t = inline(tag)
            return f'<p class="chapter-label">{t}</p>' if t else ''
        if 'fmshT' in cls:
            t = inline(tag)
            return f'<p class="subtitle">{t}</p>' if t else ''
        if 'cst' in cls:
            t = unwrap_bold(inline(tag))
            return f'<h2 id="title-{slug(t)}">{t}</h2>' if t else ''
        if 'ctag' in cls:
            t = inline(tag)
            return f'<p class="tagline">{t}</p>' if t else ''
        if 'ctBT-T' in cls or 'fmhBT-T' in cls:
            t = unwrap_bold(inline(tag))
            return f'<p class="box-title">{t}</p>' if t else ''
        if 'crt' in cls:
            t = inline(tag)
            return f'<p class="small">{t}</p>' if t else ''

        key = next((k for k in PARA_CLASS if k in cls), None)
        if key:
            return self.para(tag, key)

        if name == 'div':
            inner = self.blocks(tag)
            return inner

        return self.blocks(tag) if list(tag.children) else ''

    def para(self, tag, key):
        """A paragraph div that may contain nested blocks."""
        nested = [c for c in tag.find_all(recursive=False)
                  if isinstance(c, Tag) and (classes(c) & BLOCKISH)]
        attr = f' class="{PARA_CLASS.get(key, "")}"' if PARA_CLASS.get(key) else ''
        if not nested:
            t = inline(tag)
            if not t or not plain_text(t):
                return ''
            if plain_text(t).upper().startswith('EXHIBIT'):
                self.pending_caption = plain_text(t)
                self.pending_caption_id = self.anchor_id(tag)
                return ''
            return f'<p{attr}>{t}</p>'

        # mixed content: keep the document order
        parts, buf = [], []

        def flush():
            if not buf:
                return
            t = clean_inline(''.join(buf)).strip()
            buf.clear()
            if not plain_text(t):
                return
            if plain_text(t).upper().startswith('EXHIBIT'):
                self.pending_caption = plain_text(t)
                self.pending_caption_id = self.anchor_id(tag)
            else:
                parts.append(f'<p{attr}>{t}</p>')

        for ch in tag.children:
            if isinstance(ch, NavigableString):
                buf.append(str(ch))
            elif isinstance(ch, Tag):
                if classes(ch) & BLOCKISH:
                    flush()
                    parts.append(self.block(ch))
                else:
                    buf.append(inline(ch))
        flush()
        return ''.join(parts)

    @staticmethod
    def anchor_id(tag):
        a = tag.find('a')
        return a.get('id') if a and a.get('id') else None

    def box(self, tag):
        parts = []
        for c in tag.find_all(recursive=False):
            if isinstance(c, Tag):
                parts.append(self.block(c))
        return '<aside class="box">' + ''.join(parts) + '</aside>'

    def table(self, tag):
        rows = []
        for tr in tag.find_all('tr'):
            cells = []
            for cell in tr.find_all(['th', 'td']):
                t = 'th' if cell.name == 'th' else 'td'
                span = cell.get('colspan')
                a = f' colspan="{span}"' if span else ''
                cells.append(f'<{t}{a}>{inline(cell, skip_blocks=True)}</{t}>')
            if cells:
                rows.append('<tr>' + ''.join(cells) + '</tr>')
        table = '<table>' + ''.join(rows) + '</table>'
        # some exhibits are tables rather than images; the caption is queued
        cap, cap_id = self.pending_caption, self.pending_caption_id
        if cap:
            self.pending_caption = self.pending_caption_id = None
            attr = f' id="{cap_id}"' if cap_id else ''
            table = (f'<figure class="fig-table"{attr}>{table}'
                     f'<figcaption>{cap}</figcaption></figure>')
        return table


def unwrap_bold(html):
    """Headings are already bold; drop a redundant wrapping <strong>."""
    return re.sub(r'^<strong>(.*)</strong>$', r'\1', html.strip(), flags=re.S)


def slug(t):
    t = re.sub(r'<[^>]+>', '', t or '')
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower()
    return t or 'x'


def build():
    chapters = load_chapters()
    r = Renderer()
    sections = []

    def section(fid, sid, title, kind):
        soup = BeautifulSoup(open(os.path.join(TEXT, fid), encoding='utf-8').read(),
                             'lxml')
        html = r.blocks(soup.find('body'))
        return {'id': sid, 'title': title, 'kind': kind,
                'html': f'<section id="{sid}" class="{kind}">\n{html}\n</section>'}

    for fid, title in FRONT:
        intro = title == 'Introduction'
        sid = 'intro' if intro else 'fm-' + slug(title)
        sections.append(section(fid, sid, title, 'chapter' if intro else 'front'))

    for ch in chapters:
        sections.append(section(ch['file'], f'ch{ch["num"]:02d}',
                                ch['title'], 'chapter'))

    for fid, title in BACK:
        sections.append(section(fid, 'back-' + slug(title), title, 'back'))
    return sections, r


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    epub = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/book_out'
    open_epub(epub)
    sections, r = build()

    imgdir = os.path.join(out, 'images')
    if os.path.isdir(imgdir):
        shutil.rmtree(imgdir)
    os.makedirs(imgdir, exist_ok=True)
    for name, _ in r.figures:
        shutil.copy2(os.path.join(IMAGES, name), os.path.join(imgdir, name))

    total = 0
    print(f'{"id":22s} {"words":>7s}  title')
    for s in sections:
        w = len(plain_text(s['html']).split())
        total += w
        print(f'{s["id"]:22s} {w:7d}  {s["title"]}')
    print(f'{"TOTAL":22s} {total:7d}')
    print(f'\nfigures: {len(r.figures)}, with captions: '
          f'{sum(1 for _, c in r.figures if c)}')
    if r.warnings:
        print('warnings:', r.warnings)

    json.dump(sections, open(SECTIONS_JSON, 'w'), ensure_ascii=False)
    print('wrote', SECTIONS_JSON)


if __name__ == '__main__':
    main()
