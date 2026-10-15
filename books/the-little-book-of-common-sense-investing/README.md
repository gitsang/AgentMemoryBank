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
build_html.py       sections JSON -> index.html
```

## Rebuilding

The two scripts are a small, dependency-light pipeline (`beautifulsoup4`,
`lxml`, `Pillow`). `build_book.py` unzips the EPUB itself:

```bash
SECTIONS_JSON=sections.json python3 build_book.py book.epub out/
SECTIONS_JSON=sections.json python3 build_html.py out/index.html
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

## Coverage

Front matter (series page, copyright, dedication), Introduction, all 18
chapters, Acknowledgments, and the 24 endnotes. The EPUB's own table-of-contents
page and title-page image are replaced by the generated navigation and header.

## Copyright

The book is under copyright and this directory is an unofficial conversion of an
unauthorised electronic copy — it is here for personal reading and reference
only, not for redistribution. All text and figures remain the property of the
author and publisher. Buy the book if you find it useful.
