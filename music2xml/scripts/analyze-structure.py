#!/usr/bin/env python3
"""《浮尘》扒谱 v2 — 每小节和弦 / 鼓点格律 / 旋律线。

方法：
  - 节拍网格：onset 通量自相关求 BPM + 相位（拿 kick onset 拟合下拍）
  - 每小节和弦：chroma 模板分 + 低音根音分 合并投票，再做中值平滑合并成块
  - 鼓点：kick/snare/hat 三个频带的 onset，映射到 16 分格统计占位率
  - 旋律：谐波显著度（f0 + 6 次谐波加权）在 250–1200Hz 寻 f0，按拍量化
"""
# 源自实战脚本 fuchen-analyze-v2.py（《浮尘》案例），输入 wav 由 argv[1] 指定
import sys, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft

WAV = sys.argv[1] if len(sys.argv) > 1 else "wav/fuchen-1.wav"
sr, x = wavfile.read(WAV)
x = x.astype(np.float32) / 32768.0
if x.ndim == 2:
    x = x.mean(axis=1)
DUR = len(x) / sr

NFFT, HOP = 4096, 1024
f, t, Z = stft(x, fs=sr, nperseg=NFFT, noverlap=NFFT - HOP)
S = np.abs(Z)
fps = sr / HOP

# ---------- BPM + 相位 ----------
flux = np.concatenate([[0], np.maximum(0, np.diff(S, axis=1)).sum(axis=0)])
flux = (flux - flux.mean()) / (flux.std() + 1e-9)
ac = np.correlate(flux, flux, "full")[len(flux)-1:]
lags = np.arange(int(fps*60/160), int(fps*60/70))
bpm = 60*fps/lags[np.argmax(ac[lags])]
beat = 60.0/bpm
bar = 4*beat
# 相位：让 beat 网格上 onset 均值最大
phases = np.linspace(0, beat, 24, endpoint=False)
grid = np.round((np.arange(0, DUR, beat))*fps).astype(int)
grid = grid[grid < len(flux)]
scores = [flux[np.clip(np.round(grid + p*fps).astype(int), 0, len(flux)-1)].mean() for p in phases]
phase = phases[int(np.argmax(scores))]
print(f"BPM={bpm:.2f} beat={beat:.3f}s bar={bar:.3f}s phase={phase:.3f}s")

def bar_time(n):   # 第 n 小节（0-based）起点
    return phase + n*bar
NBARS = int((DUR - phase)//bar) + 1
def time_to_bar(tm):
    return (tm - phase)/bar

# ---------- 和弦 ----------
hz = f
NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
valid = (hz >= 70) & (hz <= 2200)
midi_all = 69 + 12*np.log2(hz[valid]/440.0)
pc_all = np.round(midi_all).astype(int) % 12
chroma = np.zeros((12, S.shape[1]))
for i, p in enumerate(pc_all):
    chroma[p] += S[valid][i]
chroma /= (chroma.max(axis=0, keepdims=True)+1e-9)

bmask = (hz >= 35) & (hz <= 200)
bfreq = hz[bmask]
Bspec = S[bmask, :]
def bass_root(i):
    col = Bspec[:, i]
    if col.max() < 0.02*S[:, i].max():
        return None
    fq = bfreq[col.argmax()]
    if fq <= 0: return None
    return int(round(69 + 12*np.log2(fq/440.0))) % 12

QUALS = [("maj7",[0,4,7,11]),("maj",[0,4,7]),("min7",[0,3,7,10]),("min",[0,3,7]),
         ("sus2",[0,2,7]),("sus4",[0,5,7]),("5",[0,7])]
def chord_scores(cv, root_hint):
    out = []
    for root in range(12):
        for qn, ivs in QUALS:
            tmpl = np.zeros(12)
            for iv in ivs: tmpl[(root+iv)%12] = 1.0
            tmpl /= np.linalg.norm(tmpl)
            sc = float(np.dot(cv/(np.linalg.norm(cv)+1e-9), tmpl))
            if root_hint is not None:
                sc += 0.25 if root == root_hint else -0.05
            out.append((sc, root, qn))
    out.sort(reverse=True)
    return out[0]

# 每小节投票（每小节内每 5 帧取一次）
bar_chords = []
for n in range(NBARS):
    t0, t1 = bar_time(n), bar_time(n+1)
    idx = np.where((t >= t0) & (t < t1))[0]
    if len(idx) == 0:
        bar_chords.append(None); continue
    votes = {}
    for i in idx[::5]:
        rh = bass_root(i)
        sc, root, qn = chord_scores(chroma[:, i], rh)
        name = f"{NAMES[root]}{'' if qn=='maj' else ('m' if qn=='min' else qn)}"
        votes[name] = votes.get(name, 0) + 1
    top = sorted(votes.items(), key=lambda kv: -kv[1])
    bar_chords.append(top[0][0] if top else None)
# 合并连续相同和弦
print("\n== 每小节和弦（bar:chord） ==")
blocks, cur, start = [], None, 0
for n, c in enumerate(bar_chords+[None]):
    if c != cur:
        if cur is not None:
            blocks.append((start, n, cur))
        cur, start = c, n
for a, b, c in blocks:
    print(f"  bar {a+1:>2}-{b:<2} ({bar_time(a):5.1f}s-{bar_time(b):5.1f}s)  {c}")

# ---------- 鼓点格律 ----------
def band_onset(lo, hi):
    bm = (hz >= lo) & (hz <= hi)
    e = S[bm, :].sum(axis=0)
    d = np.maximum(0, np.diff(e))
    return np.concatenate([[0], (d - d.mean())/(d.std()+1e-9)])
kick, snare, hat = band_onset(35,110), band_onset(150,350), band_onset(5000,12000)
def onsets(env, thr=1.6):
    out = []
    for i in range(1, len(env)-1):
        if env[i] > thr and env[i] >= env[i-1] and env[i] >= env[i+1]:
            p = float(t[i])
            if not out or p - out[-1] > 0.12:
                out.append(p)
    return out
KO, SO, HO = onsets(kick), onsets(snare), onsets(hat)

def grid_stats(t0, t1, onl, div=4):
    """统计 [t0,t1) 内 onset 落在每个 16 分格的概率"""
    g = np.zeros(4*div)
    tot = 0
    for p in onl:
        if t0 <= p < t1:
            pos = (p - phase) % bar / (bar/(4*div))
            g[int(pos) % (4*div)] += 1
            tot += 1
    return g/max(tot,1), tot

SECTIONS = [("intro", 0, 21), ("A", 21, 42), ("drop1", 42, 58),
            ("wall1", 58, 125), ("drop2", 125, 144), ("outro", 144, DUR)]
print("\n== 鼓点 16 分格占位率（kick / snare / hat）==")
for nm, a, b in SECTIONS:
    if b - a < 4: continue
    kg, kt = grid_stats(a, b, KO)
    sg, st = grid_stats(a, b, SO)
    hg, ht = grid_stats(a, b, HO)
    fmt = lambda g: " ".join(f"{v:.2f}" for v in g)
    print(f"[{nm}] n={kt}/{st}/{ht}")
    print("   kick :", fmt(kg))
    print("   snare:", fmt(sg))
    print("   hat  :", fmt(hg))

# ---------- 旋律：谐波显著度寻 f0 ----------
mel_lo, mel_hi = 250, 1300
midx = np.where((hz >= 20) & (hz <= 4000))[0]
mfreq = hz[midx]
MS = S[midx, :]
cand = np.arange(57, 86)   # A3..D6
f0s = 440*2**((cand-69)/12)
def bin_of(fq):
    return int(round(fq/(sr/NFFT)))
sal = np.zeros((len(cand), S.shape[1]))
for j, fq in enumerate(f0s):
    s = np.zeros(S.shape[1])
    for k in range(1, 7):
        b = bin_of(fq*k)
        if b < MS.shape[0]:
            s += MS[b]/k
    sal[j] = s
best_idx = sal.argmax(axis=0)
best_val = sal.max(axis=0)
notes_at = cand[best_idx]
# 每 1/2 拍取众数中值
half = beat/2
mel_seq = []
for n in range(int(DUR/half)):
    t0 = n*half
    idx = np.where((t >= t0) & (t < t0+half))[0]
    if len(idx) == 0: continue
    seg = notes_at[idx]
    val = best_val[idx]
    keep = seg[val > 0.25*val.max()] if val.max() > 0 else seg
    if len(keep) == 0: continue
    m = int(np.median(keep))
    mel_seq.append((round(t0,2), m, NAMES[m%12]+str(m//12-1)))

print("\n== 旋律线（半拍量化，只列各段代表 16 拍） ==")
for nm, a, b in SECTIONS:
    seq = [x for x in mel_seq if a <= x[0] < b]
    if not seq: continue
    # 去掉连续重复
    simp = []
    for x in seq:
        if not simp or simp[-1][1] != x[1]:
            simp.append(x)
    print(f"[{nm}] " + " ".join(f"{n}" for _,_,n in simp[:28]))

json.dump({"bpm": bpm, "beat": beat, "bar": bar, "phase": phase,
           "bars": [[a,b,c] for a,b,c in blocks],
           "melody": mel_seq,
           "kick": KO, "snare": SO, "hat": HO},
          open("analysis/fuchen-v2.json","w"), ensure_ascii=False)
print("\n✓ analysis/fuchen-v2.json")
