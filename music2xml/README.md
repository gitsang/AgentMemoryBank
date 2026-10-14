# music2xml —— 把成品音乐扒成乐队谱（MusicXML）的完整流程

> 以《浮尘》（盯鞋 shoegaze 纯音乐，D 大调，92 BPM，3′11″，失真吉他音墙）为实战案例。
> 最终产出可用 MuseScore / Finale / Sibelius / Dorico 打开的总谱 + 分谱。
> 核心结论先说：**没有"一键出准确乐队谱"的模型**，可行路径是
> `DSP 分析（骨架） + Demucs（分轨） + Basic Pitch（逐音） + 人工校对（合成）`。

---

## 0. 流程总览

```
原始音频 (wav)
   │
   ├─① 信号分析（numpy/scipy 手扒）──────────► 调性 / BPM / 和弦循环 / 曲式 / 鼓点格律
   │                                            （给出"骨架"，也是后面校验 AI 的基准）
   ├─② Demucs 分轨（本地 CPU）───────────────► vocals / drums / bass / guitar / piano / other
   │
   ├─③ Basic Pitch 逐声部转谱（本地 CPU）────► 每轨逐音 CSV（onset/offset/pitch/velocity）
   │
   └─④ 量化合并 → MusicXML 生成器 ──────────► fuchen-full.musicxml（完整版）
                                               fuchen-score.musicxml（骨架版，可读性好）
```

为什么是两条腿：
- **混音直转**（Basic Pitch 听全曲）只能拿到和声骨架，音墙密集处大量漏音；
- **先分轨再转谱**，旋律长音、贝斯根音才立得住（实测两者交叉验证逐小节吻合）；
- **DSP 手扒**不用训练数据、零成本，负责 AI 不可靠的项目（速度、相位、和弦循环、鼓点格律）。

---

## 1. 环境准备（本机 8 核 / 31GB / 无 GPU）

```bash
# ⚠️ 必须用 Python 3.11（3.13 下 basic-pitch 的老 numpy 要源码编译，必挂）
python3.11 -m venv ~/.venvs/music
~/.venvs/music/bin/pip install --upgrade pip setuptools wheel

# ⚠️ 先装 CPU 版 torch，再装 demucs——否则 pip 会拉 3GB 的 CUDA 版 torch（没 GPU 白下）
~/.venvs/music/bin/pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
~/.venvs/music/bin/pip install basic-pitch demucs music21 "setuptools<81"
```

| 依赖 | 版本 | 用途 | 许可证 |
| --- | --- | --- | --- |
| Demucs | 4.1.0 | 音源分离（htdemucs / htdemucs_6s） | MIT |
| Basic Pitch | 0.4.0 | 音频→逐音 MIDI（Spotify） | Apache 2.0 |
| music21 | 10.5 | MIDI↔MusicXML、乐理对象 | LGPL/BSD |
| numpy / scipy / librosa(可选) | — | 信号分析 | — |

**两个必踩的坑：**
- `resampy` 仍 `import pkg_resources`，setuptools ≥81 已移除 → 必须 `setuptools<81`
- Demucs 首次运行从 huggingface/dl.fbaipublicfiles.com 拉权重（~80MB/模型），
  缓存在 `~/.cache/torch/hub/checkpoints/`，之后可离线

全部本地运行，音频不出机器。速度参考（CPU）：3 分钟音频，Demucs 约 2 分钟，Basic Pitch 约 1 分钟。

---

## 2. Step ①：DSP 信号分析（打骨架）

脚本：`scripts/analyze-structure.py`（速度/相位/和弦/低音/鼓点）、`scripts/analyze-melody-voicing.py`（旋律 f0 + 和弦 voicing）

```bash
python3 scripts/analyze-structure.py <input.wav>      # 输出 BPM、每小节和弦、鼓点 16 分格占位率
python3 scripts/analyze-melody-voicing.py <input.wav> # 输出旋律长音、每和弦块的能量谱峰
```

要点：
- **BPM + 相位**：STFT 频谱通量自相关求速度，再用 kick onset 拟合下拍相位（相位错了，鼓点格律全偏 1/16）
- **和弦**：chroma 与 12×7 种和弦模板相关，**加低音根音先验**（±0.25 加权）比纯 chroma 稳得多
- **旋律**：失真音墙下 f0 检测会八度模糊（F#4/F#5 同时出现）→ **先做频谱白化**（除以频率轴中值滤波），突出有音头的声部
- **鼓点**：低频 35–110Hz=kick、120–350Hz=snare、5k–13k=hat 的 onset，映射到 16 分格统计占位率

这一步的产出（调性/BPM/和弦循环/曲式表）本身就是可用的乐队谱骨架，
也是下一步 AI 结果的**交叉验证基准**。

---

## 3. Step ②：Demucs 分轨

```bash
~/.venvs/music/bin/python -m demucs -n htdemucs_6s -o analysis/separated <input.wav>
# → analysis/separated/htdemucs_6s/<名字>/{vocals,drums,bass,guitar,piano,other}.wav
```

- `htdemucs` = 4 轨（吉他在 other 里）；`htdemucs_6s` = 6 轨（多 guitar/piano），扒吉他用 6s
- **先看 vocals 轨是不是静音**——纯音乐的话应该 -70dB 以下，这是分轨质量的免费体检
- 分轨是全流程质量的天花板：分不干净，转谱必然漏音

## 4. Step ③：Basic Pitch 逐声部转谱

```bash
for f in guitar bass drums; do
  mkdir -p analysis/bp-$f
  ~/.venvs/music/bin/basic-pitch analysis/bp-$f analysis/separated/htdemucs_6s/.../$f.wav \
      --save-note-events --save-midi
done
```

产出 `<轨>_basic_pitch.csv`（逐音：start/end/pitch_midi/velocity/pitch_bend）——
**这是"完整版"乐谱的数据源，别像我第一次那样只拿 MIDI 合成骨架**。

鼓轨不用 Basic Pitch（它不做打击乐）：
- 轻量：鼓轨上跑频带 onset（Step ① 的方法，分轨后干净得多）
- 正经：**ADTOF**（github.com/xavriley/adtof_plus_drum_transcription，kick/snare/hihat/cymbal/tom 分类）

---

## 5. Step ④：量化合并 → MusicXML

脚本：`scripts/bp-to-musicxml.py`（完整版）、`scripts/midi-to-musicxml.py`（骨架版，经 music21）

逐音 CSV → 可读乐谱要做四件事：

1. **16 分量化**：`unit = round((t - phase) / sixteenth_seconds)`，`phase` 是 Step ① 测的下拍
2. **碎片合并**：Basic Pitch 会把一个长音切成 N 段，同音高、间隙 ≤1 个 16 分的段要并起来
   （《浮尘》吉他轨 1381 个原始音片 → 合并后 531 个真实音）
3. **piano-roll 压缩**：按 onset/offset 切边界，相邻区间发声集合相同就延长时值 → 和弦块
4. **标准时值拆 tie**：非标准时值（5 个 16 分之类）贪心拆成 whole/dotted-half/half/…/16th 并加 tie；
   跨小节同样拆 + tie

**⭐ 鼓部必须用标准打击乐记谱**，否则播放器会拿旋律乐器播（我们踩过：鼓变哨子声）：

```xml
<!-- part-list 里：每个鼓件一个 score-instrument + midi-instrument -->
<score-instrument id="P3-I1"><instrument-name>Kick</instrument-name></score-instrument>
<midi-instrument id="P3-I1">
  <midi-channel>10</midi-channel>          <!-- GM 打击乐通道 -->
  <midi-unpitched>36</midi-unpitched>      <!-- 36=kick 38=snare 42=hihat 49=crash -->
</midi-instrument>

<!-- 音符本体用 <unpitched> 而不是 <pitch> -->
<note>
  <unpitched><display-step>F</display-step><display-octave>4</display-octave></unpitched>
  <duration>120</duration><instrument id="P3-I1"/>
  <voice>1</voice><type>16th</type>
</note>
```

调号（D 大调 = `<fifths>2</fifths>`）、拍号、谱号（吉他 G2 / 贝斯 F4 / 鼓 percussion）写在第 1 小节的
`<attributes>`；鼓谱不写调号。

---

## 6. Step ⑤：校验（别跳过）

```python
# 每小节时值必须正好凑满 4/4（divisions=480 → 1920）；和弦音带 <chord/> 不计时值
for m in part.findall('measure'):
    total = sum(int(n.find('duration').text)
                for n in m.findall('note') if n.find('chord') is None)
    assert total == 1920, (part.get('id'), m.get('number'), total)
```

以及**交叉验证**：DSP 手扒 vs AI 转谱逐项对比（《浮尘》的对照表）：

| 验证项 | 手扒 | AI（Demucs+Basic Pitch） | 结论 |
| --- | --- | --- | --- |
| 调性 | D 大调 | 音高类零调外音 | ✅ |
| 贝斯根音 | G/D 交替 | 逐小节 G-G-D-D 循环 | ✅ 逐小节吻合 |
| 中段旋律长音 | B4 @63.4–67.0 / 75.4–77.4 | B4 @65.2–66.0 / 73.8–77.6 | ✅ |
| 尾音 | F#5 @188.5 | F#5 @187 | ✅ |

两个独立方法撞在同一结论上，才敢写进谱；单源结果标"近似/存疑"。

---

## 7. 模型选型（实测 + 调研）

| 方案 | 定位 | 实测/口碑 |
| --- | --- | --- |
| **Demucs + Basic Pitch**（本流程） | 免费、全本地、CPU 可跑 | 和声/贝斯/旋律长音可靠；密集音墙漏音，装饰音弱 |
| **YourMT3+**（github.com/mimbres/yourmt3） | 多乐器 transformer，强于 Basic Pitch | 有 **HF Spaces 免费 GPU demo + Colab**，无 GPU 也能试；本地 CPU 很慢 |
| MT3（Google Magenta） | 多乐器转谱开山之作 | YourMT3+ 是其改进版 |
| **Melodyne Studio / RipX DAW** | 商业、AI 初稿+人工修 | 混音场景最稳，弯音/滑音这类细节只有它能处理 |
| **ADTOF** | 鼓转谱专用 | kick/snare/hihat/cymbal/tom 分类，比 onset 检测正经 |
| Song2Tabs（2025 论文） | 吉他六线谱基础模型 | ⚠️ 开源/可试用状态未能确认 |
| Klangio Guitar2Tabs / AnthemScore | 在线/买断 | 单件乐器或干净录音可用，混音不行 |

**针对失真音墙的最佳组合**：Demucs(6s) 分轨 → YourMT3+ 或 Basic Pitch 转谱 →
ADTOF 转鼓 → Melodyne 手工补漏。预期管理：2025 年一项评测显示仅曲风/录音条件变化
就能让 AMT 模型 F1 掉 20–50 个点，"一个不漏"目前无解。

---

## 8. 踩坑记录（都是真实翻过的车）

| 坑 | 真相 / 解法 |
| --- | --- |
| Python 3.13 装 basic-pitch | 老 numpy 无 wheel，源码编译挂在 `pkgutil.ImpImporter` → 用 3.11 |
| `pkg_resources` 不存在 | setuptools ≥81 移除 → `pip install "setuptools<81"` |
| 装 demucs 拉了 3GB | pip 默认 torch 是 CUDA 版 → 先装 CPU 版 torch 再装 demucs |
| 鼓播放成哨子声 | MusicXML 里鼓写成 `<pitch>` 且没走 channel 10 → 用 `<unpitched>` + GM 映射 |
| 小节时值 120 倍爆满 | 单位混用：音块时间轴是"16 分个数"，小节边界是"divisions" → 统一单位再算 |
| 长音被切成一串短音 | Basic Pitch 输出碎片化 → 同音高、间隙 ≤1 个 16 分就合并 |
| 旋律八度乱跳 | 音墙 f0 八度模糊 → 频谱白化 + 长音双源核对，只信长音位置 |
| 直接给骨架谱用户 | "只剩主要音符"→ 逐音 CSV 才是完整数据源，骨架谱只配当排练简谱 |
| 和弦模板摇摆 | Gmaj7/Gsus2 之间反复横跳（9 音太近）→ 谱面取常用 voicing，别跟着模板抖 |

---

## 9. 实例产物（《浮尘》）

原始工程：`~/.pi/scheduler/jobs/music-gen/`（`wav/fuchen-1.wav`、`analysis/`、`drafts/`）

| 产物 | 说明 |
| --- | --- |
| `drafts/fuchen-score.md` | 乐队谱（文字版）：曲式/和弦/鼓点格律/简谱旋律/存疑清单/交叉验证表 |
| `drafts/fuchen-full.musicxml` | 完整版：吉他 2024 音 + 贝斯 532 音 + 鼓 1152 击点 |
| `drafts/fuchen-score.musicxml` + `drafts/fuchen-parts/` | 骨架版总谱 + 分谱 |
| `drafts/fuchen-score.mid` | 排练用骨架 MIDI（4 轨） |
| `analysis/bp-{guitar,bass,full}/` | Basic Pitch 逐音 CSV / MIDI |
| `analysis/separated/` | Demucs 分轨 wav |

复算命令：

```bash
~/.venvs/music/bin/python -m demucs -n htdemucs_6s -o analysis/separated wav/fuchen-1.wav
~/.venvs/music/bin/basic-pitch analysis/bp-guitar analysis/separated/htdemucs_6s/fuchen-1/guitar.wav --save-note-events
python3 scripts/bp-to-musicxml.py    # 需按实际路径/PHASE/BPM 改脚本头部常量
```
