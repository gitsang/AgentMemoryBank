# The Little Book of Common Sense Investing

Single-page HTML reading edition of John C. Bogle's *The Little Book of Common
Sense Investing: The Only Way to Guarantee Your Fair Share of Stock Market
Returns* (John Wiley & Sons, 2007 — ISBN 978-0-470-10210-7).

Open [`index.html`](index.html) in a browser. It is one self-contained page with
chapter anchors, the 28 original exhibit figures and the endnotes; light/dark
themes follow your system preference, and on wide screens a fixed left rail
navigates the chapters.

## Layout

```
index.html          the book (chapters as anchored <section>s)
images/             exhibit figures referenced by index.html
build_book.py       EPUB  -> sections JSON (text + figures)
build_html.py       sections JSON -> index.html (translations, notes, glossary)
extract_paragraphs.py      sections JSON -> translatable-paragraph work queue
collect_translations.py    per-section translation files -> translations.json
translations.json   the Chinese running text (394 paragraphs)
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

The page carries a Chinese translation interleaved under each paragraph. The
translation text is kept in a sidecar file rather than baked into the HTML, so
the page can be rebuilt at any time and partial work is fine.

**Current coverage: the full running text.** The Introduction and all 18
chapters are translated — 394 of 394 paragraphs. Out of scope by choice:
front matter (dropped at conversion), the back matter (Acknowledgments,
endnotes), and the display typography — chapter labels, taglines, and the
centered pull quotes, which restate the argument rather than carry it. So the
page is the argument itself, not its apparatus. A build reports
`running text: 394/394 paragraphs (100% of the body)` and notes separately how
many prose paragraphs exist in total, rather than presenting the excluded
material as an untranslated gap.

Workflow:

```bash
# 1. dump the translatable paragraphs of the running text
SECTIONS_JSON=sections.json python3 extract_paragraphs.py --body-only queue.json

# 2. translate the queued paragraphs, one file per section, into a workdir:
#      workdir/ch01.json = {"section": "ch01", "paragraphs": {"4": {"zh": "…"}}}

# 3. merge the per-section files into the sidecar
python3 collect_translations.py workdir/ queue.json -o translations.json --strict

# 4. rebuild with the translations interleaved
SECTIONS_JSON=sections.json TRANSLATIONS_JSON=translations.json \
    python3 build_html.py out/index.html
```

`--body-only` narrows the queue to the running text: it drops the chapter
label, the subtitle and tagline, the centered pull quotes, and everything
inside a "Don't Take My Word for It" aside. Paragraph indices stay those of the *full* selection even when
apparatus is filtered out, so an index in the queue always means the same thing
to `build_html.py`'s interleaver. Both sides import the same `body_only`
predicate, so the work queue and the build's coverage count cannot drift apart.

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
  reported as `mismatched: N` at build time. `collect_translations.py` carries
  the fingerprint across from the work queue, so a translator only ever supplies
  `zh`.
- Because the 19 sections were translated independently, mechanically drifting
  conventions are settled once, in `collect_translations.normalise`, rather than
  baked into the HTML by hand: the IME's `“ ”` become the corner brackets the
  hand-written sidecars use, an in-text figure reference takes the English label
  printed on the figure (`Exhibit 2.1`, matching the `EXHIBIT 2.1` caption,
  rather than inventing a Chinese label the reader cannot see on the figure),
  and stray ASCII spaces around full-width punctuation are dropped. It never
  touches wording — term and number consistency across sections was checked
  separately.
- The translation mirrors the source paragraph's classes, so an indented, quoted
  or pull-quote paragraph keeps the same shape, plus a `tr` marker:
  `<p class="tr q">`.
- When translations are present the page gains a 中文 show/hide toggle
  (persisted in `localStorage`), and the translation styles collapse for print.

## Terminology glossary

`glossary.json` holds `{id, en, zh, note}` entries. At build time the list is
inlined as JSON and `page.js` wraps the **first occurrence of each term per
section** — so every chapter gets its own hints without turning the page into a
wall of dotted underlines. Clicking a term opens a popover with the English
term, the Chinese name and the explanation; `Esc` or a click outside dismisses
it.

The full list is also available as a dialog opened from the 术语 button in the
floating toolbar — a filter box narrows it by English term or Chinese name, and
an empty-state line appears when nothing matches. The dialog is rendered once
and reused: a popup on screen, and unhidden as a plain list at the end of the
document when printing, so the entries are not duplicated in the markup.

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

An optional `label` field in the sidecar renames the floating toggle, so a
sidecar that is not a straight translation is not presented as one.

### Floating toolbar

Three round icon buttons sit bottom-right, stacked: back-to-top, the language
toggle, and the annotation toggle — plus a 术语 button when a glossary is
present. They share one `.toolbar` flex container
(`column-reverse`, so the first child renders at the bottom) and one `.tool-btn`
style. Hovering or focusing one reveals `.tool-tip` to its **left**; the tip text
tracks state (`隐藏批注` / `显示批注`) and `aria-label` / `aria-pressed` update with
it. A disabled layer is dimmed via `.is-off`. The whole toolbar is hidden in
print.

### Chapter rail

A fixed left rail (`#rail`) lists the Introduction, the 18 chapters and the back
matter, numbered, using the section titles as published. Titles are set
`nowrap` so none of them wrap; the width is sized for the longest one measured
at the *active* (bold) weight, which is wider than the resting state.

Sizing this needs care, because the wrap is a 68rem box and the rail has to fit
in the space left over. Reserving that space on the left —
`margin-left: max(1.25rem + var(--rail-w) + var(--rail-gap), 50% - 34rem)` —
keeps the column centred when the viewport is roomy and shifts it right only
when the rail needs the room. Centring alone would instead require the rail to
fit inside the *gutter*, which costs roughly 400px of viewport for nothing.

`--rail-w`, the 68rem wrap and the media-query width are one calculation: the
breakpoint is where `--rail-w` + 1.25rem + 1.5rem + 68rem still fits, currently
24rem + 70.75rem ≈ 95rem → 1530px. The same value is duplicated in `page.js`'s
`matchMedia`; change both together. Narrower viewports keep the in-page table of
contents, and the same list is rendered as the narrow-screen menu below.

### Narrow screens

Below that width the rail is replaced by a `<details>` menu rendered from the
same `rail_items()`, pinned with `position: sticky` so it stays reachable while
scrolling. Using `<details>` means it works without JS; `page.js` only adds the
close-on-navigate behaviour and the shared highlight.

The rail and the menu carry the same links and are driven by one mechanism: the
highlight code collects `linksById` across both, so whichever is on screen shows
the current chapter.

`page.js` marks the current section by **position, not by event**: on each
scroll (rAF-throttled) it takes the last section whose top has crossed a reading
line at 28% viewport height. Deriving the answer from where the reader is means
exactly one entry is ever highlighted and it stays correct when jumping
backwards — an `IntersectionObserver` latch instead keeps whatever was visited
last, which is not the same thing.

## Coverage

Introduction, all 18 chapters, Acknowledgments, and the 24 endnotes. The EPUB's
own table-of-contents page, title page, series blurb, copyright page and
dedication are not carried over. Of these, the running text (Introduction plus
the 18 chapters) is translated into Chinese; the Acknowledgments and endnotes
are left in English.

## Copyright

The book is under copyright and this directory is an unofficial conversion of an
unauthorised electronic copy — it is here for personal reading and reference
only, not for redistribution. All text and figures remain the property of the
author and publisher. Buy the book if you find it useful.
