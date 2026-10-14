#!/usr/bin/env python3
"""drafts/fuchen-score.mid → MusicXML（总谱 + 分谱）。

music21 解析 MIDI 后补齐声部名/乐器/谱号，导出：
  drafts/fuchen-score.musicxml        总谱（4 声部）
  drafts/fuchen-parts/<声部>.musicxml 分谱

移植到别的曲子时要改：SRC/输出路径、PARTS 里的声部名与乐器、
KeySignature(2)（本例 D 大调两个升号）。
本文件是《浮尘》实战的参考实现。
"""
import os
from music21 import converter, instrument, metadata, clef, key

SRC = "drafts/fuchen-score.mid"
OUT_FULL = "drafts/fuchen-score.musicxml"
OUT_DIR = "drafts/fuchen-parts"

PARTS = [
    ("Lead Guitar",  "主奏吉他", "Lead Gtr",  instrument.ElectricGuitar(), clef.TrebleClef()),
    ("Rhythm Guitar","节奏吉他", "Rhythm",    instrument.ElectricGuitar(), clef.TrebleClef()),
    ("Bass",         "贝斯",     "Bass",      instrument.ElectricBass(),   clef.BassClef()),
    ("Drums",        "鼓",       "Drums",     instrument.Percussion(),     clef.PercussionClef()),
]

s = converter.parse(SRC)

md = metadata.Metadata()
md.title = "浮尘（乐队谱 · 扒谱版）"
md.composer = "小超 (AI)"
md.movementName = "D 大调 · 4/4 · BPM 92.3"
s.metadata = md

parts = list(s.parts)
assert len(parts) == len(PARTS), f"声部数不对: {len(parts)}"
for p, (en, zh, ab, inst, cl) in zip(parts, PARTS):
    p.partName = f"{zh} {en}"
    p.partAbbreviation = ab
    p.insert(0, inst)
    # 谱号/调号写进第一小节（插在 part 顶层会被导出器忽略/错置）
    m1 = p.getElementsByClass("Measure")[0]
    m1.clef = cl
    if not isinstance(inst, instrument.Percussion):
        m1.insert(0, key.KeySignature(2))   # D 大调：两个升号（鼓谱不记调号）
    for m in p.getElementsByClass("Measure"):
        if m.clef is None:
            m.clef = cl

os.makedirs(OUT_DIR, exist_ok=True)
s.write("musicxml", fp=OUT_FULL)
for p, (en, zh, ab, inst, cl) in zip(parts, PARTS):
    fp = os.path.join(OUT_DIR, en.lower().replace(" ", "-") + ".musicxml")
    p.write("musicxml", fp=fp)
    print("  ✓", fp)
print("✓", OUT_FULL)
