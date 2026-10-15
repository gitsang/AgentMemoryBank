# The Little Book of Common Sense Investing

Single-page HTML reading edition of John C. Bogle's *The Little Book of Common
Sense Investing: The Only Way to Guarantee Your Fair Share of Stock Market
Returns* (John Wiley & Sons, 2007 — ISBN 978-0-470-10210-7).

Open [`index.html`](index.html) in a browser. It is one self-contained page with
a linked table of contents, chapter anchors, the 28 original exhibit figures and
the endnotes; light/dark themes follow your system preference.

## Layout

```
index.html          the book (chapters as anchored <section>s)
images/             exhibit figures referenced by index.html
build_book.py       EPUB  -> sections JSON (text + figures)
build_html.py       sections JSON -> index.html (translations, notes, glossary)
extract_paragraphs.py      sections JSON -> translatable-paragraph work queue
translations.example.json  worked example of the translation sidecar
glossary.json       terminology glossary (en / zh / explanation)
annotations.json    Chinese margin annotations, keyed by section + paragraph
page.js             reader-side JS: glossary popovers and visibility toggles
```

## Rebuilding

The two scripts are a small, dependency-light pipeline (`beautifulsoup4`,
`lxml`, `Pillow`). `build_book.py` unzips the EPUB itself:

```bash
SECTIONS_JSON=sections.json python3 build_book.py book.epub out/
SECTIONS_JSON=sections.json TRANSLATIONS_JSON=translations.json \
    ANNOTATIONS_JSON=annotations.json GLOSSARY_JSON=glossary.json \
    python3 build_html.py out/index.html
```

`SECTIONS_JSON` is the hand-off file between the two stages and defaults to
`/tmp/sections.json`.

## How the conversion works

The source is an EPUB of the 2007 first edition. `build_book.py` reads
`toc.ncx` for the chapter order, then renders each spine document by mapping the
publisher's CSS classes onto semantic HTML:

| EPUB class | meaning | output |
| --- | --- | --- |
| `fmhT` | "Chapter One" | `.chapter-label` |
| `cst` | chapter title | `<h2>` |
| `ctag` | chapter tagline | `.tagline` |
| `fmtx` / `fmtx1` | body paragraph | `<p>` / `<p class="ind">` |
| `fmtx2` / `fmtx3` | quoted or boxed passage | `<p class="q">` |
| `chabox` / `fmhbox` | "Don't Take My Word for It" | `<aside class="box">` |
| `h` | pull quote | `<p class="pull">` |
| `liste` / `lsl` | bullet/numbered list | `<ul>` / `<li>` |
| `t` | data table | `<table>` |
| `bmtx` | endnote (has `FTN-*` anchor) or normal paragraph | `.note` / `<p>` |

Notes on fidelity:

- **Figures.** Images larger than 150 px in either dimension are kept; anything
  smaller is a chapter ornament or stray glyph from the print layout and is
  dropped. The queueing of the `EXHIBIT x.y …` caption line means each figure
  keeps its caption, and the original `EXH-*` anchor id is preserved so the
  in-text "see Exhibit 2.1" cross-references still jump correctly.
- **Two exhibits are tables, not images** (Exhibits 10.1 and 12.2); they are
  emitted as captioned tables.
- **Endnotes.** The `bmtx` class marks endnotes in the Notes section but ordinary
  paragraphs in the Acknowledgments; the two are told apart by whether the block
  carries an `FTN-*` anchor.
- **Text integrity.** Every section was diffed word-by-word against the source
  document. The only differences are captions moving into `<figcaption>`,
  generated note numbers, and whitespace/punctuation normalisation — no body
  text is lost.

## Parallel translation (对照翻译)

The page can carry a second language interleaved under each paragraph. The
translation text is kept in a sidecar file rather than baked into the HTML, so
the page can be rebuilt at any time and partial work is fine.

Workflow:

```bash
# 1. dump the translatable paragraphs of every section
SECTIONS_JSON=sections.json python3 extract_paragraphs.py paragraphs.json

# 2. fill in paragraphs.json -> translations.json (see the format below)

# 3. rebuild with the translations interleaved
SECTIONS_JSON=sections.json TRANSLATIONS_JSON=translations.json \
    python3 build_html.py out/index.html
```

[`translations.example.json`](translations.example.json) is a short worked
example. The format is keyed by paragraph index, which makes sparse and
partial translations safe:

```json
{
  "sections": {
    "intro": {
      "2": { "src": "SUCCESSFUL INVESTING IS ALL about common sense.",
             "zh": "成功的投资全靠常识。……" }
    }
  }
}
```

- `src` is a fingerprint of the paragraph's opening words. The interleaver
  checks it against the paragraph it is about to attach the translation to; if
  it does not match, it locates the right paragraph by fingerprint instead of
  silently attaching the translation to the wrong place. Leftover mismatches are
  reported as `mismatched: N` at build time.
- Extracted paragraphs cover prose only (`<p>` and `<li>`): headings, figure
  captions and the copyright boilerplate are excluded.
- The translation mirrors the source paragraph's classes, so an indented, quoted
  or pull-quote paragraph keeps the same shape, plus a `tr` marker:
  `<p class="tr q">`. `build_html.py` reports the resulting coverage, e.g.
  `translation coverage: 6/611 paragraphs (1%)`.
- When translations are present the page gains a 中文 show/hide toggle
  (persisted in `localStorage`), and the translation styles collapse for print.

## Terminology glossary

`glossary.json` holds `{id, en, zh, note}` entries. At build time the list is
inlined as JSON and `page.js` wraps the **first occurrence of each term per
section** — so every chapter gets its own hints without turning the page into a
wall of dotted underlines. Clicking a term opens a popover with the English
term, the Chinese name and the explanation; `Esc` or a click outside dismisses
it. A full glossary is also appended at the end of the book.

Matching is word-boundary aware and longest-first, so `classic index fund` wins
over `index fund`, and aliases can be declared per term (`S&P 500`,
`price/earnings`, `ETF`). Terms are never wrapped inside links, footnote
markers, translations, margin notes or figure captions.

## Margin annotations

`annotations.json` holds Chinese commentary keyed by section and paragraph
index, with the same `src` fingerprint guard as translations:

```json
{
  "sections": {
    "ch01": {
      "5": { "src": "But after a while, a few fast-talking Helpers…",
             "title": "关键：所有权没变，钱却少了",
             "zh": "这一段的机关很容易被读漏。…" }
    }
  }
}
```

On viewports 1150px and wider the notes float into a right-hand margin column
beside the paragraph they discuss (the note is emitted *before* its paragraph so
the float starts at that paragraph's top). Below that width they collapse into
inline callouts above the paragraph, and a floating 批注 button hides or shows
them all. In print they stay inline and never split across pages.

Notes and glossary entries accept `**bold**` inline markup. The annotations here
are my own reading notes on the argument — context, caveats and where Bogle's
framing is doing rhetorical work rather than measurement — not a rendering of
the original text.

## Coverage

Front matter (series page, copyright, dedication), Introduction, all 18
chapters, Acknowledgments, and the 24 endnotes. The EPUB's own table-of-contents
page and title-page image are replaced by the generated navigation and header.

## Copyright

The book is under copyright and this directory is an unofficial conversion of an
unauthorised electronic copy — it is here for personal reading and reference
only, not for redistribution. All text and figures remain the property of the
author and publisher. Buy the book if you find it useful.
