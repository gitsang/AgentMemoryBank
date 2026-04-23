---
name: youtube-to-chinese-voiceover
description: Use when需要把单个 YouTube 或本地视频素材做成低成本、可审计的中文旁白版，或基于外部参考音频生成中文音色克隆版，并把转写、中文稿、配音、对齐、字幕和交付物完整沉淀到 reports/ 中。
---

# YouTube 转中文旁白

## 概述

这个 skill 面向**单视频、个人可运行、强调可复现**的中文旁白工作流。它现在支持两种配音模式：

- **普通中文旁白**：使用标准 TTS 音色
- **参考音频驱动的中文音色克隆**：使用外部参考音频，让中文配音尽量贴近参考人的音色

目标依然不是口型同步或“百分百原声复刻”，而是把一个视频真实跑通为“中文旁白版 / 中文克隆音色版”，并把证据、命令、问题与交付物完整留在 `reports/` 中。

这个 skill 已经基于真实实跑修正过两个关键误区：

- **总时长对齐不等于真正同步**
- **中间产物跑通不等于最终交付完成**

同时，这个 skill 对音色克隆有一个明确边界：**第一版只支持外部参考音频**，不自动从原视频里切参考音色。

## 什么时候用

适用于这些场景：

- 你要把一个 YouTube 视频或用户提供的本地视频做成中文旁白版
- 你更在意低成本、透明流程、可复现，而不是棚录级成品
- 你需要保留 `reports/` 下的全过程证据
- 你可以在 TTS 前人工审阅中文稿
- 用户要求双语字幕、按标题命名交付，或者要求句子级时间对齐
- 用户提供了一段参考音频，希望中文配音尽量贴近该参考人的音色

不适用于这些场景：

- 目标是自动从复杂原视频中提纯参考声纹、声纹鉴权、或法律上高风险的“冒充原说话人”
- 目标是批量流水线化处理大量视频
- 你没有权限处理源视频或字幕内容

## 目录与交付约定

先在 `reports/` 下创建独立工作目录，例如：

```text
reports/<task-name>/
  source/
  artifacts/
  notes/
  scripts/
  report.md
```

最低建议产物：

- 原始视频或音频输入
- 标准化后的 `source/video.mp4` 与 `source/audio.mp3`
- 英文转写文本与 SRT
- 中文口播稿
- 在同步敏感场景下使用的逐段中文稿
- 在音色克隆模式下使用的参考音频
- 真实 TTS 音频
- 最终中文旁白视频
- 用户要求字幕交付时的字幕文件
- `notes/commands.md`
- `notes/issues.md`
- `report.md`

## 工作流顺序

1. **先做源获取验证**
   - 如果环境允许，先尝试直接下载。
   - 如果 `yt-dlp` 遇到 `429`、bot verification、登录验证，不要把它误判成普通 CLI 参数问题。
   - 用浏览器或 `chrome-devtools` 复核是不是网络/会话级拦截。
   - 如果浏览器也被拦截，立刻切换为用户提供的本地源文件。

2. **标准化媒体输入**
   - 用 `ffprobe` 保存源文件元信息。
   - 把用户上传的任意文件名统一转换成稳定路径，例如：
     - `source/video.mp4`
     - `source/audio.mp3`
   - 这样后续脚本不会被特殊字符文件名绊住。

3. **做英文转写**
   - 优先使用 `faster-whisper`。
   - 同时输出纯文本与 SRT。
   - 如果模型下载在开始前就失败，优先检查代理环境变量，再考虑换工具。
   - 可直接复用：`scripts/transcribe_with_faster_whisper.py`

4. **生成中文稿**
   - 中文稿要偏口播、自然、简短，优先保留原意而不是逐词直译。
   - 如果只需要整段旁白，准备一份完整中文稿。
   - 如果用户要求句子级同步，必须准备**逐段中文稿**，并保证每一行对应一个字幕块。
   - 这是人工审阅关口，不能跳过。
   - 可直接复用：`scripts/scaffold_rewrite_prompt.py`

5. **准备参考音频（仅音色克隆模式）**
   - 第一版只支持**外部提供的参考音频**。
   - 参考音频尽量满足：
     - 单人说话
     - 背景噪声低
     - 3-15 秒清晰人声
     - 与目标音色一致，不混入音乐或多人对话
   - 不要默认从原视频中自动裁切参考段；那是后续增强项，不是当前稳定流程。

6. **生成真实中文 TTS / 中文音色克隆 TTS**
   - 优先使用轻量、可复现、无 API Key 依赖的路径，例如 `edge-tts`。
   - 普通中文旁白建议使用真实普通话音色，例如 `zh-CN-XiaoxiaoNeural`。
   - 音色克隆模式优先使用支持 zero-shot voice cloning 的后端，例如 `Qwen3-TTS`。
   - 沉默文件、占位文件、空白音轨都不算完成。
   - 如果是整段旁白，可直接用：`scripts/generate_edge_tts.py`
   - 如果是整段音色克隆，可直接用：`scripts/generate_qwen3_voice_clone.py`
   - 如果是逐段同步配音，则不要先合成整段，改走逐段构建。

7. **按原始时间轴对齐**
   - 把原始 SRT 的 `start` 时间当成真正时间锚点。
   - 每一段中文 TTS 都应放到对应字幕块的原始开始时间。
   - `scripts/build_aligned_dub.py` 支持 `--backend edge-tts` 和 `--backend qwen3-tts`。
   - 当 `--backend qwen3-tts` 时，必须提供 `--reference-audio`。
   - 如果某段中文过长，先做有限度加速，再在必要时裁切。
   - 不要把“视频总时长没变”误判成“音画同步成功”。
   - 可直接复用：`scripts/build_aligned_dub.py`

8. **生成字幕产物**
   - 如果用户要求中英双语字幕，按英文时间轴合并逐段中文稿。
   - 优先输出独立字幕文件，再决定是否烧录。
   - 可直接复用：`scripts/build_bilingual_ass.py`

9. **合成最终视频**
   - 用对齐后的中文音轨替换源视频音轨。
   - 用 `ffprobe` 确认最终 MP4 同时保留视频流和音频流。
   - 如果做了逐段对齐，保留逐段 timing report，便于审计哪些片段被加速或裁切。

10. **明确做最终交付包装**
   - 不要停在 `final-voiceover-aligned.mp4` 这类内部产物名。
   - 如果用户要求按标题命名，就必须额外导出他们要的最终文件名。
   - 常见交付集合：

```text
{title}.mp4              # 无字幕版
{title}.ass              # 字幕文件
{title}-bilingual.mp4    # 双语字幕版（硬字幕）
```

   - 这一步是**交付包装**，和中间产物不是一回事。

11. **最后写报告**
    - 如实记录命令、阻塞点、修复方式、产物与限制。
    - 只写本环境里真实跑通的做法，不要写想象中的理想路径。

## skill 内置脚本

这个 skill 现在自带可复用脚本，优先把它们复制到当前 `reports/<task>/scripts/` 下再跑，避免直接污染 skill 目录。

| 脚本 | 用途 |
|---|---|
| `scripts/transcribe_with_faster_whisper.py` | 把音频转成英文文本 + SRT |
| `scripts/scaffold_rewrite_prompt.py` | 为中文改写生成可人工审阅的 prompt scaffold |
| `scripts/generate_edge_tts.py` | 把整段中文稿生成 MP3/WAV |
| `scripts/generate_qwen3_voice_clone.py` | 用参考音频 + 中文稿生成整段中文音色克隆 MP3/WAV |
| `scripts/build_aligned_dub.py` | 逐段生成中文配音并按原始字幕开始时间拼到整条时间线上 |
| `scripts/build_bilingual_ass.py` | 按英文时间轴生成中英双语 ASS 字幕 |

建议调用方式示例：

```bash
python scripts/transcribe_with_faster_whisper.py \
  --audio source/audio.mp3 \
  --txt-out artifacts/transcript.en.txt \
  --srt-out artifacts/transcript.en.srt

python scripts/scaffold_rewrite_prompt.py \
  --transcript artifacts/transcript.en.txt \
  --output artifacts/script.zh.txt \
  --mode continuous

python scripts/generate_edge_tts.py \
  --script artifacts/script.zh.txt \
  --mp3-out artifacts/narration.zh.mp3 \
  --wav-out artifacts/narration.zh.wav

python scripts/generate_qwen3_voice_clone.py \
  --script artifacts/script.zh.txt \
  --reference-audio source/reference.wav \
  --mp3-out artifacts/narration.zh.clone.mp3 \
  --wav-out artifacts/narration.zh.clone.wav

python scripts/build_aligned_dub.py \
  --srt artifacts/transcript.en.srt \
  --zh-segments artifacts/script.zh.segments.txt \
  --video source/video.mp4 \
  --backend qwen3-tts \
  --reference-audio source/reference.wav \
  --wav-out artifacts/narration.zh.aligned.wav \
  --report-out artifacts/narration.zh.aligned.json \
  --segment-dir artifacts/aligned-segments

python scripts/build_bilingual_ass.py \
  --srt artifacts/transcript.en.srt \
  --zh-segments artifacts/script.zh.segments.txt \
  --ass-out artifacts/subtitles.zh-en.ass
```

## 最终交付模式

当用户在意输出包装时，明确区分这三类：

| 交付物 | 含义 | 常见来源 |
|---|---|---|
| `{title}.mp4` | 干净的中文旁白视频，不烧字幕 | 对齐后的成片 |
| `{title}.ass` | 外挂字幕文件，通常是双语样式 | 生成出的 ASS 字幕 |
| `{title}-bilingual.mp4` | 烧录双语字幕的视频 | 干净成片 + ASS 烧录 |

如果用户说的是“软字幕版”，那是另一种交付，不要和外挂 `.ass` 文件混为一谈。

## 最小工具链

- `ffmpeg`
- `ffprobe`
- `uv` + 本地 `.venv`
- `faster-whisper`
- `edge-tts` 或其他已验证的普通话 TTS 路径
- `qwen-tts`（当使用参考音频驱动的音色克隆时）
- `numpy`（逐段对齐脚本需要）

## 人工审阅关口

- 源获取失败后，确认是不是网络/会话级阻塞
- 转写完成后，抽样检查英文稿质量
- 中文改写完成后，确认文件里是最终中文稿，不是 prompt scaffold
- 做逐段同步时，确认逐段中文稿的行数与 SRT block 数一致
- 做音色克隆时，确认参考音频存在、可播放、且是单人清晰语音
- TTS 完成后，确认输出是**真实语音**
- 合成完成后，用 `ffprobe` 确认视频和音频流都还在
- 交付前，确认最终命名文件真实存在，并且符合用户要求的包装形式

## 常见失败模式

| 失败现象 | 处理方式 |
|---|---|
| `yt-dlp` 遇到 429 或 bot verification | 用浏览器复核；如果浏览器也被 CAPTCHA 拦住，就切换到用户提供的本地媒体 |
| `faster-whisper` 在模型下载前就报错 | 先检查代理变量；本仓库实跑里，`NO_PROXY` 的 IPv6 写法会让 `httpx` 解析失败 |
| TTS 包装好了但命令入口不对 | 同时检查 Python import 路径和 `.venv/bin/` 里的 CLI，而不是立刻换库 |
| 切到音色克隆后声音不像参考音色 | 优先检查参考音频质量、长度和说话人纯度；不要先怪对齐逻辑 |
| Qwen3-TTS CLI 不存在或子命令不匹配 | 先确认本机安装的 `qwen-tts` CLI 语法，再修正脚本包装层 |
| 中文旁白比视频短很多 | 如果只在意总时长，可以补静音；如果在意同步，必须切到逐段对齐流程 |
| 视频长度对了但句子还是越说越漂 | 你很可能做的是连续旁白；要改成基于字幕开始时间的逐段构建 |
| 用户要求按标题命名，你却只产出内部 artifact 名 | 加显式 packaging/export 步骤，并验证最终文件名 |
| 用户要求字幕交付，你却只有视频文件 | 交付前补出 `.ass` 或用户指定的字幕格式 |

## 红旗

如果下面任一条成立，就不要宣称流程完成：

- 你手里只有 prompt scaffold，没有最终中文稿
- 你宣称做了音色克隆，但根本没有参考音频
- TTS 输出是沉默文件、空白文件或占位文件
- 最终视频从未用 `ffprobe` 复核
- 报告声称 YouTube 直连下载成功，但实际上没有跑通
- skill 记录的是理论步骤，不是真实验证过的做法
- 你只是把总时长对齐，却称之为“同步成功”
- 用户要求最终命名交付，但你只交了中间产物
- 用户要求字幕交付，但你只交了视频
