#!/usr/bin/env python3
"""《浮尘》完整版 MusicXML —— Basic Pitch 全部逐音数据 + Demucs 鼓轨 onset。

与 fuchen-score.musicxml（骨架谱）的区别：
  * 吉他/贝斯 = Basic Pitch 的全部音符（16 分量化、碎片合并、标准时值拆 tie），不是长音骨架
  * 鼓 = drums 轨 onset 检测，标准打击乐记谱（<unpitched> + GM drum map + channel 10）
    —— 修复"鼓播放成哨子声"（骨架版把鼓写成普通音高音符且没走 channel 10）
输出: drafts/fuchen-full.musicxml

移植到别的曲子时要改的常量：BPM / PHASE（下拍秒数）/ total_bars，
以及 main() 里的 CSV 路径、drum_grid() 里的鼓轨 wav 路径、输出路径。
本文件是《浮尘》实战的参考实现。
"""
import csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft

DIV = 480              # 每四分音符 divisions
U = DIV // 4           # 一个 16 分 = 120 divisions
BAR16 = 16             # 一小节 = 16 个 16 分（块/小节的时间轴用 16 分单位）
BPM = 92.29
PHASE = 0.542          # 音频 bar1 下拍
S16 = 60.0 / BPM / 4   # 一个 16 分的秒数

STEP = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

def pitch_xml(midi):
    n = STEP[midi % 12]
    alter = 1 if "#" in n else 0
    return f"<step>{n[0]}</step>" + (f"<alter>{alter}</alter>" if alter else "") + \
           f"<octave>{midi // 12 - 1}</octave>"

# ---------- 1. Basic Pitch CSV → 量化 + 碎片合并 ----------
def load_bp(path, min_dur=1):
    by_pitch = {}
    for r in csv.DictReader(open(path)):
        p = int(r["pitch_midi"])
        a = round((float(r["start_time_s"]) - PHASE) / S16)
        b = round((float(r["end_time_s"]) - PHASE) / S16)
        if b <= a: b = a + 1
        by_pitch.setdefault(p, []).append((max(a, 0), b))
    out = []
    for p, segs in by_pitch.items():
        segs.sort()
        cur_a, cur_b = segs[0]
        for a, b in segs[1:]:
            if a <= cur_b + 1:                    # 间隙 ≤1 个 16 分 → 并掉（BP 会把长音切碎）
                cur_b = max(cur_b, b)
            else:
                out.append((cur_a, cur_b - cur_a, p)); cur_a, cur_b = a, b
        out.append((cur_a, cur_b - cur_a, p))
    out.sort()
    return [n for n in out if n[1] >= min_dur]

# ---------- 2. 音符 → 和弦块（piano-roll 压缩） ----------
def chord_blocks(notes):
    edges = sorted({x for t, d, _ in notes for x in (t, t + d)})
    blocks = []
    for i in range(len(edges) - 1):
        t0, t1 = edges[i], edges[i + 1]
        pitches = sorted(p for t, d, p in notes if t <= t0 < t + d)
        if not pitches: continue
        if blocks and blocks[-1][0] + blocks[-1][1] == t0 and blocks[-1][2] == pitches:
            blocks[-1] = (blocks[-1][0], blocks[-1][1] + (t1 - t0), pitches)
        else:
            blocks.append((t0, t1 - t0, pitches))
    return blocks

# ---------- 3. 时值拆分 + tie ----------
STD = [(16, "whole", 0), (12, "half", 1), (8, "half", 0), (6, "quarter", 1),
       (4, "quarter", 0), (3, "eighth", 1), (2, "eighth", 0), (1, "16th", 0)]

def split_dur(d):
    out = []
    while d > 0:
        for u, ty, dot in STD:
            if u <= d:
                out.append((u, ty, dot)); d -= u; break
        else:
            out.append((1, "16th", 0)); d -= 1
    return out

def note_xml(pitches, units, tie_stop=False, tie_start=False, is_drum=False, drum_map=None):
    parts = split_dur(units)
    xml = ""
    for i, (u, ty, dot) in enumerate(parts):
        inner_tie = i > 0            # 与前一段时值相连
        last = i == len(parts) - 1
        for j, p in enumerate(pitches):
            xml += "<note>"
            if j > 0: xml += "<chord/>"
            if is_drum:
                disp, inst = drum_map[p]
                xml += (f"<unpitched><display-step>{disp[0]}</display-step>"
                        f"<display-octave>{disp[1]}</display-octave></unpitched>")
                xml += f'<instrument id="{inst}"/>'
            else:
                xml += f"<pitch>{pitch_xml(p)}</pitch>"
            xml += f"<duration>{u * U}</duration>"
            ties = []
            if tie_stop or inner_tie: ties.append("stop")
            if tie_start or not last: ties.append("start")
            for tg in ties: xml += f'<tie type="{tg}"/>'
            xml += f"<voice>1</voice><type>{ty}</type>" + ("<dot/>" if dot else "")
            if ties:
                xml += "<notations>" + "".join(f'<tied type="{tg}"/>' for tg in ties) + "</notations>"
            xml += "</note>"
    return xml

def rest_xml(units):
    xml = ""
    for u, ty, dot in split_dur(units):
        xml += (f"<note><rest/><duration>{u * U}</duration><voice>1</voice>"
                f"<type>{ty}</type>" + ("<dot/>" if dot else "") + "</note>")
    return xml

# ---------- 4. 鼓 onset（Demucs drums 轨） ----------
DRUM_MAP = {36: (("F", 4), "P3-I1"), 38: (("C", 5), "P3-I2"),
            42: (("G", 5), "P3-I3"), 49: (("G", 5), "P3-I4")}
DRUM_MIDI = {"P3-I1": 36, "P3-I2": 38, "P3-I3": 42, "P3-I4": 49}

def drum_grid():
    sr, x = wavfile.read("analysis/separated/htdemucs/fuchen-1/drums.wav")
    x = x.astype(np.float32) / 32768
    if x.ndim == 2: x = x.mean(axis=1)
    f, t, Z = stft(x, fs=sr, nperseg=4096, noverlap=3072)
    S = np.abs(Z)
    def onsets(lo, hi, thr=1.2):
        e = S[(f >= lo) & (f <= hi), :].sum(axis=0)
        d = np.maximum(0, np.diff(e))
        d = (d - d.mean()) / (d.std() + 1e-9)
        out = []
        for i in range(1, len(d) - 1):
            if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
                p = float(t[i + 1])
                if not out or p - out[-1] > 0.12: out.append(p)
        return out
    grid = {}
    for midi, times in [(36, onsets(35, 110)), (38, onsets(120, 350)), (42, onsets(5000, 13000, 1.0))]:
        for p in times:
            u = round((p - PHASE) / S16)
            if u >= 0: grid.setdefault(u, set()).add(midi)
    for n in (9, 23, 56):                      # 段落起点 crash
        grid.setdefault((n - 1) * BAR16, set()).add(49)
    return grid

# ---------- 5. 每小节 XML ----------
def measures_from_blocks(blocks, total_bars):
    out = []
    for b in range(total_bars):
        pos, meas, cur, mxml = b * BAR16, (b + 1) * BAR16, b * BAR16, ""
        for t, d, pitches in blocks:
            if t + d <= pos or t >= meas: continue
            s0, s1 = max(t, pos), min(t + d, meas)
            if s0 > cur: mxml += rest_xml(s0 - cur); cur = s0
            if s1 > cur:
                mxml += note_xml(pitches, s1 - cur,
                                 tie_stop=(t < pos), tie_start=(t + d > meas))
                cur = s1
        if cur < meas: mxml += rest_xml(meas - cur)
        out.append(mxml)
    return out

def drum_measures(total_bars):
    grid = drum_grid()
    out = []
    for b in range(total_bars):
        pos, meas, cur, mxml = b * BAR16, (b + 1) * BAR16, b * BAR16, ""
        for u in sorted(k for k in grid if pos <= k < meas):
            if u > cur: mxml += rest_xml(u - cur)
            mxml += note_xml(sorted(grid[u]), 1, is_drum=True, drum_map=DRUM_MAP)
            cur = u + 1
        if cur < meas: mxml += rest_xml(meas - cur)
        out.append(mxml)
    return out

# ---------- 6. 组装 ----------
CLEF_TREBLE = '<clef><sign>G</sign><line>2</line></clef>'
CLEF_BASS = '<clef><sign>F</sign><line>4</line></clef>'
CLEF_PERC = '<clef><sign>percussion</sign><line>2</line></clef>'

def write_score(path, parts):
    x = '<?xml version="1.0" encoding="UTF-8"?>\n'
    x += '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
    x += '<score-partwise version="3.1"><work><work-title>浮尘（AI 转谱 · 完整版）</work-title></work>'
    x += '<movement-title>D 大调 · 4/4 · BPM 92.3 · 扒谱：Demucs + Basic Pitch</movement-title><part-list>'
    for pid, name, prog, clef, meas, drums in parts:
        x += f'<score-part id="{pid}"><part-name>{name}</part-name>'
        if drums:
            for iid, iname in drums:
                x += (f'<score-instrument id="{iid}"><instrument-name>{iname}</instrument-name></score-instrument>'
                      f'<midi-instrument id="{iid}"><midi-channel>10</midi-channel>'
                      f'<midi-unpitched>{DRUM_MIDI[iid]}</midi-unpitched></midi-instrument>')
        else:
            x += (f'<score-instrument id="{pid}-I1"><instrument-name>{name}</instrument-name></score-instrument>'
                  f'<midi-instrument id="{pid}-I1"><midi-channel>1</midi-channel>'
                  f'<midi-program>{prog}</midi-program></midi-instrument>')
        x += '</score-part>'
    x += '</part-list>'
    for pid, name, prog, clef, meas, drums in parts:
        x += f'<part id="{pid}">'
        for i, m in enumerate(meas):
            x += f'<measure number="{i + 1}">'
            if i == 0:
                x += (f'<attributes><divisions>{DIV}</divisions><key><fifths>2</fifths></key>'
                      '<time><beats>4</beats><beat-type>4</beat-type></time>'
                      f'{clef}</attributes>'
                      '<direction placement="above"><direction-type><metronome>'
                      '<beat-unit>quarter</beat-unit><per-minute>92.3</per-minute>'
                      '</metronome></direction-type><sound tempo="92.3"/></direction>')
            x += m + '</measure>'
        x += '</part>'
    x += '</score-partwise>'
    open(path, "w", encoding="utf-8").write(x)

def main():
    guitar = load_bp("analysis/bp-guitar/guitar_basic_pitch.csv")
    bass = load_bp("analysis/bp-bass/bass_basic_pitch.csv")
    g_blocks, b_blocks = chord_blocks(guitar), chord_blocks(bass)
    print(f"guitar: {len(guitar)} 音 → {len(g_blocks)} 和弦块")
    print(f"bass:   {len(bass)} 音 → {len(b_blocks)} 音块")
    total_bars = 74
    write_score("drafts/fuchen-full.musicxml", [
        ("P1", "吉他（AI 转谱全音）", 30, CLEF_TREBLE, measures_from_blocks(g_blocks, total_bars), []),
        ("P2", "贝斯", 34, CLEF_BASS, measures_from_blocks(b_blocks, total_bars), []),
        ("P3", "鼓", None, CLEF_PERC, drum_measures(total_bars),
         [("P3-I1", "Kick"), ("P3-I2", "Snare"), ("P3-I3", "Hi-Hat"), ("P3-I4", "Crash")]),
    ])
    print("✓ drafts/fuchen-full.musicxml")

if __name__ == "__main__":
    main()
