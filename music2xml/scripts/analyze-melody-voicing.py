#!/usr/bin/env python3
"""《浮尘》扒谱 v3 — 旋律（频谱白化后寻 f0）+ 和弦 voicing。

白化：S / 频率轴中值 → 压掉宽带音墙，突出有音头的旋律线。
只在旋律/空当段落提取；按拍量化 + 3 帧中值滤波。
voicing：每个和弦块内取能量最大的若干谱峰（Hz → 音名），给吉他指法定音。
"""
# 源自实战脚本 fuchen-analyze-v3.py（《浮尘》案例），输入 wav 由 argv[1] 指定
import sys, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from scipy.ndimage import median_filter, uniform_filter1d

WAV = sys.argv[1] if len(sys.argv) > 1 else "wav/fuchen-1.wav"
sr, x = wavfile.read(WAV)
x = x.astype(np.float32)/32768.0
if x.ndim == 2: x = x.mean(axis=1)
DUR = len(x)/sr
NFFT, HOP = 4096, 1024
f, t, Z = stft(x, fs=sr, nperseg=NFFT, noverlap=NFFT-HOP)
S = np.abs(Z)
fps = sr/HOP

NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def nm(m): return NAMES[m%12]+str(m//12-1)

# 白化
med = median_filter(S, size=(31,1))
SW = S/(med+1e-9)
SW = np.clip(SW, 0, 8)

BPM = 92.29; beat = 60/BPM; bar = 4*beat; PHASE = 0.542

# ---------- 旋律：逐帧在 220-1000Hz 找最强白化峰 ----------
lo = np.searchsorted(f, 200); hi = np.searchsorted(f, 1100)
def frame_note(i):
    col = SW[lo:hi, i]
    if col.max() < 1.6:      # 没有突出的音头
        return None, 0
    fq = f[lo+col.argmax()]
    m = int(round(69+12*np.log2(fq/440)))
    return m, float(col.max())

notes, stren = [], []
for i in range(S.shape[1]):
    m, s = frame_note(i)
    notes.append(m if m else -1)
    stren.append(s)
notes = np.array(notes)
# 中值滤波去掉毛刺（5 帧 ≈ 0.12s）
valid = notes > 0
filled = notes.copy()
filled[~valid] = np.median(notes[valid]) if valid.any() else 0
sm = median_filter(filled, size=5)

def beat_seq(t0, t1, per=1):
    """每 per 拍输出一个音"""
    out = []
    n = t0
    while n < t1:
        a = int(round((n-PHASE)/(beat/per)*0))  # dummy
        i0 = int(round((n)*fps)); i1 = int(round((n+beat*per)*fps))
        seg = sm[i0:i1]
        if len(seg):
            m = int(np.median(seg))
            if m > 0:
                out.append(nm(m))
        n += beat*per
    return out

print("== 旋律线（每拍一个音 · 白化后 f0）==")
ZONES = [("intro 0-21s", 0.5, 21), ("A 21-42s", 21, 42), ("drop1 42-58s", 42, 58),
         ("melody 58-85s", 58, 85), ("wall 85-125s", 85, 125),
         ("drop2 125-144s", 125, 144), ("outro 144-190s", 144, 190)]
for label, a, b in ZONES:
    seq = beat_seq(a, b, 1)
    print(f"[{label}] " + " ".join(seq))

print("\n== 旋律长音（持续 ≥ 1.5s 的音，半拍采样）==")
half = beat/2
pts = []
for n in range(int(DUR/half)):
    t0 = n*half
    i = int(t0*fps)
    if i < len(sm):
        pts.append((t0, int(sm[i])))
runs = []
for i, (tt, m) in enumerate(pts):
    if runs and runs[-1][2] == m:
        runs[-1][1] = tt
    else:
        runs.append([tt, tt, m])
for a, b, m in runs:
    if b-a >= 1.5 and m > 0:
        print(f"  {a:6.1f}s-{b:5.1f}s  {nm(m)}")

# ---------- voicing：每个和弦块的能量谱峰 ----------
BLOCKS = [("Gmaj7", 57.8, 68.2), ("Dmaj7", 68.2, 78.6), ("Gmaj7", 78.6, 83.8),
          ("Dsus2", 83.8, 91.6), ("Gmaj7", 104.6, 109.8), ("Dmaj7", 109.8, 120.2),
          ("Gmaj7", 146.2, 156.6), ("Dmaj7", 167.0, 177.4)]
print("\n== 和弦 voicing（块内平均谱的前 10 峰）==")
for label, a, b in BLOCKS:
    i0, i1 = int(a*fps), int(b*fps)
    avg = S[:, i0:i1].mean(axis=1)
    # 局部峰
    peaks = []
    for i in range(2, len(avg)-2):
        if avg[i] > avg[i-1] and avg[i] >= avg[i+1] and avg[i] > avg[i-2] and avg[i] > avg[i+2]:
            peaks.append((avg[i], f[i]))
    peaks.sort(reverse=True)
    top = []
    for v, fq in peaks:
        m = int(round(69+12*np.log2(max(fq,1)/440)))
        if any(abs(m-x) < 2 for x in top):   # 避免同音名挤在一起
            continue
        top.append(m)
        if len(top) >= 10: break
    print(f"[{label} {a:.0f}-{b:.0f}s] " + " ".join(nm(m) for m in sorted(top)))
