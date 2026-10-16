#!/usr/bin/env python3
"""Merge per-section translation files into the translations sidecar.

Translation work is done one section at a time, in files shaped like
``{"section": "ch01", "paragraphs": {"4": {"zh": "..."}}}``. This script folds
those into the single ``translations.json`` that ``build_html.py`` consumes,
carrying the ``src`` fingerprint across from the paragraph work queue so the
interleaver can still catch a drifted paragraph index.

The sections are translated independently, so mechanical conventions drift
between them. ``normalise`` settles the ones that are unambiguous and
reader-visible — quote marks, the "Exhibit x.y" label, whitespace the CJK
punctuation does not want — so the merged file reads as one book. It is
deliberately limited to conventions, never wording.

Usage:
    python3 collect_translations.py workdir/ paragraphs.json -o translations.json

    workdir/        directory of <section>.json files (only *.json is read)
    paragraphs.json output of extract_paragraphs.py, the fingerprint source

Only sections present in the input directory are emitted, so a partially
translated book builds fine. Missing or empty paragraphs are reported, and
``--strict`` turns them into a non-zero exit.
"""

import argparse
import json
import os
import re
import sys

# The figures keep their printed English labels ("EXHIBIT 2.1" in the caption),
# so the in-text cross-reference matches that label rather than inventing a
# Chinese one the reader cannot see on the figure.
EXHIBIT_RE = re.compile(r'图表 ?(\d+\.\d+)')
# a CJK letter glued to the Latin label
GLUED_RE = re.compile(r'([\u4e00-\u9fff])(Exhibit )')
# a full-width bracket padded with the spaces an English keyboard produces, and
# a space left sitting before a full-width comma or period
PAD_RE = re.compile(r'（[ \u3000]+|[ \u3000]+）|[ \u3000]+(?=[，。；：、！？])')


def normalise(text):
    """Settle the cross-section conventions that would otherwise drift.

    Only mechanical, reversible-in-principle rewrites: the double quotes a
    bilingual IME emits become the corner brackets the hand-written sidecars
    use, the figure reference takes the figure's own English label, and stray
    ASCII spaces around full-width punctuation are dropped. No wording is
    touched, and a paragraph without any of these is returned unchanged.
    """
    text = text.replace('“', '「').replace('”', '」')
    text = EXHIBIT_RE.sub(r'Exhibit \1', text)
    text = GLUED_RE.sub(r'\1 \2', text)
    text = PAD_RE.sub(lambda m: m.group(0).strip(), text)
    return text


def load_workdir(path):
    docs = {}
    for name in sorted(os.listdir(path)):
        if not name.endswith('.json'):
            continue
        doc = json.load(open(os.path.join(path, name), encoding='utf-8'))
        sid = doc.get('section') or name[:-5]
        paras = doc.get('paragraphs') or {}
        out = {}
        for k, v in paras.items():
            zh = (v.get('zh') if isinstance(v, dict) else v) or ''
            if str(zh).strip():
                out[int(k)] = normalise(str(zh).strip())
        docs[sid] = out
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workdir')
    ap.add_argument('queue')
    ap.add_argument('-o', '--out', default='translations.json')
    ap.add_argument('--label', default='\u4e2d\u6587',
                    help='floating toggle label for a straight translation')
    ap.add_argument('--strict', action='store_true',
                    help='exit non-zero when a queued paragraph is untranslated')
    args = ap.parse_args()

    queue = json.load(open(args.queue, encoding='utf-8'))
    docs = load_workdir(args.workdir)

    sections, problems, done, total = {}, [], 0, 0
    for sid, entry in queue.items():
        paras = entry['paragraphs']
        if not paras:
            continue
        zh = docs.get(sid, {})
        section = {}
        for p in paras:
            total += 1
            text = zh.get(p['i'])
            if not text:
                continue
            # half-width punctuation that should have been full-width, and the
            # reverse: a cheap mechanical check, not a style opinion
            bad = re.findall(r'[,;:!?]\s*[\u4e00-\u9fff]', text)
            if bad:
                problems.append(f'{sid}[{p["i"]}]: half-width punct {bad[:2]}')
            if text == p['text']:
                problems.append(f'{sid}[{p["i"]}]: identical to source')
            section[str(p['i'])] = {'src': p['src'], 'zh': text}
            done += 1
        if section:
            sections[sid] = section

    doc = {'label': args.label, 'sections': sections}
    json.dump(doc, open(args.out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print(f'wrote {args.out}')
    print(f'coverage: {done}/{total} paragraphs ({done / max(total, 1):.0%}) '
          f'across {len(sections)}/{len(queue)} sections')
    if problems:
        print(f'\n{len(problems)} thing(s) to look at:')
        for line in problems[:40]:
            print('  ' + line)
        if len(problems) > 40:
            print(f'  ... and {len(problems) - 40} more')
    if args.strict and done < total:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
