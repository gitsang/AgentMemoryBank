---
name: youtube-to-chinese-voiceover
description: Use when needing to turn a single YouTube or local video into a low-cost, auditable Chinese voiceover; generate Chinese dubbing, sentence-level alignment, bilingual subtitles, final video deliverables; or use external reference audio for Chinese voice cloning.
---

# YouTube 转中文旁白

## 概述

把单个 YouTube 或本地视频转换为中文旁白版时，优先追求**可复现、可审计、真实交付**，而不是追求棚录级质量或自动化批处理。

核心原则：每一步都要产出可检查的文件，所有命令、问题、修复方式和中间产物都沉淀到原始视频同级的工作目录中；最终交付物单独放到该目录下的 `output/` 中。不要把中间产物、占位音频、总时长对齐或理论步骤当作完成。

支持两种配音模式：

- **普通中文旁白**：使用标准普通话 TTS 音色。
- **外部参考音频驱动的中文音色克隆**：用户提供参考音频，中文配音尽量贴近该参考音色。

明确边界：本 skill 不负责自动从复杂原视频中提纯声纹，也不处理法律或授权风险高的“冒充原说话人”场景。

## 什么时候用

适用于：

- 用户给出 YouTube 链接或本地视频，要求制作中文旁白版。
- 用户要求中文配音、句子级同步、双语字幕、按标题命名的最终视频。
- 用户更重视低成本、透明过程、可复现证据，而不是专业录音棚成品。
- 用户提供外部参考音频，希望生成接近参考人的中文克隆音色。
- 需要在 TTS 前人工审阅中文稿，避免机械直译。

不适用于：

- 批量流水线处理大量视频。
- 目标是自动声纹提纯、声纹鉴权、口型同步或原声百分百复刻。
- 源视频、字幕或参考音频没有明确处理权限。
- 用户要求不可审计、不能保存中间证据的黑盒流程。

## 工作目录与交付约定

每个任务必须先在原始视频同级创建独立工作目录。目录名使用原始视频文件名去掉扩展名后的 stem：

```text
/path/to/Source-Video-Name.mp4  # 原始视频
/path/to/Source-Video-Name/     # 工作目录
/path/to/Source-Video-Name/output/  # 最终交付物目录
```

工作目录内部结构：

```text
/path/to/Source-Video-Name/
  source/       # 原始和标准化输入
  artifacts/    # 转写、脚本、音频、字幕、视频等中间产物
  notes/        # 命令、问题、限制、人工检查记录
  output/       # 面向用户交付的最终文件
  scripts/      # 从 skill 复制过来的可复用脚本
  report.md     # 最终报告
```

最低建议产物：

| 产物 | 说明 |
|---|---|
| `source/video.mp4` | 标准化后的视频输入 |
| `source/audio.mp3` | 从视频抽取或用户提供的音频 |
| `artifacts/transcript.en.txt` | 英文转写文本 |
| `artifacts/transcript.en.srt` | 带时间轴的英文字幕 |
| `artifacts/script.zh.txt` | 连续中文口播稿 |
| `artifacts/script.zh.segments.txt` | 句子级同步时的逐段中文稿 |
| `source/reference.*` | 音色克隆模式下的外部参考音频和可选参考文本 |
| `artifacts/narration*.wav/mp3` | 真实生成的中文 TTS 音频 |
| `artifacts/final*.mp4` | 候选中文旁白视频或内部合成产物 |
| `artifacts/subtitles*.ass` | 内部字幕产物 |
| `output/{title}.mp4` | 面向用户交付的干净中文旁白视频 |
| `output/{title}.ass` | 面向用户交付的外挂字幕文件 |
| `output/{title}-bilingual.mp4` | 面向用户交付的双语字幕烧录版视频 |
| `notes/commands.md` | 实际执行过的命令 |
| `notes/issues.md` | 阻塞、失败、修复方式和限制 |
| `report.md` | 面向用户的最终总结 |

## 推荐工作流

### 1. 获取并验证源素材

- 如果是 YouTube 链接，先尝试 `yt-dlp`，但不要把 `429`、bot verification、登录验证误判为普通参数问题。
- 需要复核网页、登录态、网络请求或 CAPTCHA 时，按仓库浏览器规则优先使用 `chrome-devtools`。
- 如果浏览器也被拦截，停止绕路，改让用户提供本地源文件。
- 保存源获取方式、失败信息和最终采用的输入来源。

### 2. 标准化媒体输入

- 用 `ffprobe` 保存输入元信息，确认时长、视频流、音频流。
- 在工作目录内把任意用户文件名转换成稳定路径，例如 `source/video.mp4` 与 `source/audio.mp3`。
- 后续脚本只引用标准化路径，避免空格、中文、特殊字符导致脚本失败。

### 3. 英文转写

- 优先使用 `faster-whisper` 输出纯文本和 SRT。
- 转写完成后抽样检查质量，特别是专有名词、数字、断句。
- 如果模型下载在开始前失败，先检查代理和缓存路径，再考虑替换工具。

### 4. 生成中文口播稿

- 中文稿要自然、简洁、适合口播；保留原意优先于逐词直译。
- 连续旁白场景：准备 `script.zh.txt`。
- 句子级同步场景：准备 `script.zh.segments.txt`，每一行对应一个 SRT block。
- 这是人工审阅关口：确认文件里是最终中文稿，而不是 prompt scaffold。

### 5. 准备参考音频（仅音色克隆模式）

只使用用户提供或明确授权的外部参考音频。参考音频尽量满足：

- 单人说话。
- 背景噪声低。
- 3-15 秒清晰人声。
- 不混入音乐、多人对话或强混响。
- 可选提供对应参考文本，提升克隆后端稳定性。

不要默认从原视频自动裁切参考段；那属于后续增强项，不是稳定流程。

### 6. 生成真实中文 TTS

- 普通旁白优先使用轻量、可复现、无 API Key 依赖的普通话 TTS，例如 `edge-tts`。
- 音色克隆可使用支持 zero-shot voice cloning 的后端，例如 `Qwen3-TTS`。
- 沉默文件、空白文件、占位文件不算完成。
- 生成后必须试听或用音频工具确认非静音、时长合理、采样格式可被 `ffmpeg` 使用。

### 7. 按原始时间轴对齐

- 如果用户在意句子级同步，不要先合成整段旁白再拉伸到总时长。
- 以原始 SRT 的 `start` 时间作为锚点，把每段中文 TTS 放回对应字幕块开始时间。
- 中文过长时，先有限度加速，再在必要时裁切，并记录 timing report。
- “视频总时长没变”不等于“音画同步成功”。同步要看句子是否回到原始时间锚点。

### 8. 生成字幕产物

- 用户要求字幕时，优先输出独立字幕文件，再决定是否烧录。
- 双语字幕应复用英文 SRT 时间轴，并把逐段中文稿按 block 合并进去。
- 区分外挂字幕、硬字幕、软字幕，不要用一个产物冒充另一个产物。

### 9. 合成最终视频

- 用中文旁白音轨替换或覆盖源视频音轨。
- 用 `ffprobe` 确认最终 MP4 同时包含视频流和音频流。
- 保留 clean 版和字幕版的生成命令，确保后续可重跑。

### 10. 交付包装与报告

- 不要停在 `final-voiceover-aligned.mp4` 这类内部文件名。
- 最终交付物必须复制或导出到 `output/`，不要只留在 `artifacts/`。
- 如果用户要求按标题命名，在 `output/` 中导出他们要求的最终文件名。
- 报告只写当前环境真实跑通的做法，不写想象中的理想路径。

常见交付集合：

```text
output/{title}.mp4              # 干净中文旁白视频
output/{title}.ass              # 外挂字幕文件
output/{title}-bilingual.mp4    # 烧录双语字幕的视频
```

## 内置脚本

优先把 skill 自带脚本复制到工作目录的 `scripts/` 下再运行，避免污染 skill 目录，也方便报告完整归档。

| 脚本 | 用途 |
|---|---|
| `scripts/transcribe_with_faster_whisper.py` | 把音频转成英文文本和 SRT |
| `scripts/scaffold_rewrite_prompt.py` | 为中文改写生成可人工审阅的 prompt scaffold |
| `scripts/generate_edge_tts.py` | 把整段中文稿生成 MP3/WAV |
| `scripts/generate_qwen3_voice_clone.py` | 用参考音频和中文稿生成整段中文音色克隆 MP3/WAV |
| `scripts/build_aligned_dub.py` | 逐段生成中文配音并按原始字幕开始时间拼到整条时间线上 |
| `scripts/build_bilingual_ass.py` | 按英文时间轴生成中英双语 ASS 字幕 |

常用命令模板：

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
  --reference-text source/reference.txt \
  --mp3-out artifacts/narration.zh.clone.mp3 \
  --wav-out artifacts/narration.zh.clone.wav

python scripts/build_aligned_dub.py \
  --srt artifacts/transcript.en.srt \
  --zh-segments artifacts/script.zh.segments.txt \
  --video source/video.mp4 \
  --backend edge-tts \
  --wav-out artifacts/narration.zh.aligned.wav \
  --report-out artifacts/narration.zh.aligned.json \
  --segment-dir artifacts/aligned-segments

python scripts/build_bilingual_ass.py \
  --srt artifacts/transcript.en.srt \
  --zh-segments artifacts/script.zh.segments.txt \
  --ass-out artifacts/subtitles.zh-en.ass
```

音色克隆逐段对齐时，`build_aligned_dub.py` 必须提供参考音频：

```bash
python scripts/build_aligned_dub.py \
  --srt artifacts/transcript.en.srt \
  --zh-segments artifacts/script.zh.segments.txt \
  --video source/video.mp4 \
  --backend qwen3-tts \
  --reference-audio source/reference.wav \
  --reference-text source/reference.txt \
  --segment-dir artifacts/aligned-segments-clone \
  --wav-out artifacts/narration.zh.clone.aligned.wav \
  --report-out artifacts/narration.zh.clone.aligned.json
```

## 最小工具链

- `ffmpeg` 和 `ffprobe`：抽取音频、检查媒体流、合成最终视频。
- Python 虚拟环境：建议在工作目录内隔离依赖。
- `faster-whisper`：英文转写和 SRT 生成。
- `edge-tts`：普通中文旁白。
- `qwen-tts`：外部参考音频驱动的音色克隆。
- `numpy`、`soundfile` 等音频处理依赖：逐段对齐和 WAV 拼接需要。

## 人工审阅关口

在这些节点必须停下来检查真实产物：

- 源获取失败后，确认是否是网络、登录态、CAPTCHA 或会话级阻塞。
- 转写完成后，抽样检查英文稿和 SRT block 数。
- 中文改写完成后，确认是最终中文稿，不是提示词草稿。
- 做逐段同步时，确认逐段中文稿行数与 SRT block 数一致。
- 做音色克隆时，确认参考音频存在、可播放、单人清晰。
- TTS 完成后，确认输出是真实语音，不是静音或占位。
- 合成完成后，用 `ffprobe` 确认视频流和音频流都存在。
- 交付前，确认最终命名文件真实存在于 `output/` 并符合用户要求。

## 常见失败模式

| 失败现象 | 处理方式 |
|---|---|
| `yt-dlp` 遇到 `429` 或 bot verification | 用浏览器复核；若浏览器也被 CAPTCHA 拦住，切换为用户提供的本地媒体 |
| 模型下载前就失败 | 先检查代理变量、缓存目录、证书和网络，再考虑换工具 |
| TTS 命令入口跑不通 | 同时检查 Python import 路径、虚拟环境和包提供的 CLI，不要立刻换库 |
| 音色克隆不像参考音色 | 优先检查参考音频质量、长度、说话人纯度和后端输入格式 |
| 中文旁白比视频短很多 | 只在意总时长可补静音；在意同步则必须逐段对齐 |
| 视频长度对了但句子越说越漂 | 连续旁白不能保证句子同步；改用字幕开始时间锚定的逐段构建 |
| 用户要求按标题命名但只有内部 artifact | 增加显式 packaging/export 步骤，把最终文件导出到 `output/` 并验证最终文件名 |
| 用户要求字幕但只有视频文件 | 补出 `.ass`、硬字幕视频或用户指定的字幕格式 |

## 红旗

任一条成立，就不要宣称完成：

- 只有 prompt scaffold，没有最终中文稿。
- 宣称做了音色克隆，但没有外部参考音频或授权来源。
- TTS 输出是沉默文件、空白文件或占位文件。
- 只做了总时长对齐，却称为句子级同步成功。
- 最终视频从未用 `ffprobe` 复核。
- 报告声称 YouTube 下载成功，但实际没有跑通。
- 用户要求最终命名交付，但 `output/` 里没有最终文件。
- 用户要求字幕交付，但只交了视频。
- 工作目录的 `notes/` 没有记录命令、失败和限制。

## 完成前检查清单

- [ ] 工作目录位于原始视频同级，且目录名等于原始视频 stem。
- [ ] 工作目录内部结构完整，并包含 `output/`。
- [ ] 源视频、音频、转写、中文稿、TTS、字幕和最终视频都有明确路径。
- [ ] 关键命令写入 `notes/commands.md`。
- [ ] 阻塞点、降级方案、质量限制写入 `notes/issues.md` 或 `report.md`。
- [ ] 如果逐段同步，已保存 timing report 并说明加速或裁切情况。
- [ ] 如果音色克隆，已记录参考音频来源、质量和限制。
- [ ] 最终 MP4 经过 `ffprobe` 验证含视频流和音频流。
- [ ] 用户要求的最终文件名、字幕形式和包装形式全部存在于 `output/`。
