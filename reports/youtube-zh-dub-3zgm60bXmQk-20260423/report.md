# YouTube 中文旁白工作流实跑记录

## 1. 输入视频

- 目标视频 ID：`3zgm60bXmQk`
- 原始 YouTube URL：`https://www.youtube.com/watch?v=3zgm60bXmQk`
- 本次实跑使用的实际输入：`source/What are AI agents？ [3zgm60bXmQk].webm`
- 说明：当前机器访问 YouTube 会遇到 Google 的 bot verification，因此最终通过本地上传源文件继续完成流程。

## 2. 环境与依赖

- 工作目录：`reports/youtube-zh-dub-3zgm60bXmQk-20260423/`
- Python 环境：`uv venv` 创建的 `.venv`（CPython 3.12.12）
- 系统工具：`ffmpeg 7.1.3`、`ffprobe 7.1.3`
- Python 包：`yt-dlp`、`faster-whisper`、`edge-tts`

## 3. 执行步骤

### 3.1 工作区初始化

创建了 `source/`、`artifacts/`、`notes/`、`scripts/`，并建立命令日志与问题日志。

### 3.2 下载链路验证与降级

最初尝试直接通过 `yt-dlp` 获取 YouTube 元信息和视频，但被 Google 返回 `HTTP 429` 和“Sign in to confirm you’re not a bot”。

为确认这不是单纯的 CLI 问题，又用 `chrome-devtools` 打开同一视频页，结果同样落到 Google 的 `sorry` / reCAPTCHA 页面。随后尝试更换 `yt-dlp` 的 player client，以及尝试 Invidious 作为替代源，依然无法稳定获取内容。

因此，源获取步骤改为：使用用户提供的本地视频文件继续执行。这一点被保留在日志和 skill 中，作为真实世界里的关键回退路径。

### 3.3 媒体标准化

对上传的 `webm` 文件做了两件事：

1. 用 `ffprobe` 重新写出 `source/video-info.json`
2. 用 `ffmpeg` 生成统一引用路径：
   - `source/video.mp4`
   - `source/audio.mp3`

这样后续脚本就不需要处理带特殊字符的原始文件名。

### 3.4 英文转写

编写了 `scripts/transcribe.py`，使用 `faster-whisper` 的 `small` 模型在 CPU 上转写，并输出：

- `artifacts/transcript.en.txt`
- `artifacts/transcript.en.srt`

中途遇到一个环境问题：`faster-whisper` 在下载模型前因为 `NO_PROXY=localhost,127.0.0.1,[::1]` 触发 `httpx.InvalidURL: Invalid port ':1]'`。将 `NO_PROXY` 临时清洗为 `localhost,127.0.0.1` 后，转写成功。

最终结果：

- 检测语言：`en`
- 音频时长：约 `356.99s`
- 分段数量：`131`

### 3.5 中文口播稿改写

转写稿整体质量足够好，因此直接根据英文稿手工整理为更适合中文旁白的版本，并保存为：

- `artifacts/script.zh.txt`

同时保留了 `scripts/rewrite_to_zh.py`，用于以后快速生成改写提示词 scaffold。

### 3.6 中文 TTS

本地没有现成中文 TTS CLI，因此选择了轻量、无 API Key 的 `edge-tts`。

编写 `scripts/generate_tts.py` 后，使用：

- Voice：`zh-CN-XiaoxiaoNeural`
- Rate：`+8%`

生成了：

- `artifacts/narration.zh.mp3`
- `artifacts/narration.zh.wav`

这里特意避免了“静音占位文件”这种假完成；只有生成真实中文语音后，流程才继续往下走。

### 3.7 第一版合成：连续中文旁白

最初的中文旁白音频时长约 `281.35s`，明显短于原视频约 `357.00s`。如果直接用 `-shortest` 合成，视频会被硬裁短，不利于保留原始画面结构。

因此第一版先采用 `apad` 给中文音轨补静音尾巴，再与原视频合成为：

- `artifacts/final-voiceover.mp4`

校验结果显示输出文件包含：

- 1 路 `av1` 视频流
- 1 路 `aac` 音频流

最终视频总时长约 `356.99s`，与源视频基本一致。

### 3.8 第二版合成：按原始时间轴逐段对齐

在用户指出“中文太快、音画不同步”之后，问题被重新定位：

- 第一版只能匹配总时长，不能保证每句话的开始时间
- 真正需要对齐的是原始字幕的 `start` 时间，而不是整段中文旁白的总长度

因此新增了一套逐段对齐流程：

1. 用 `transcript.en.srt` 作为时间锚点
2. 新建 `artifacts/script.zh.segments.txt`，为每个字幕块准备一行中文
3. 编写 `scripts/build_aligned_dub.py`
4. 逐条调用 `edge-tts` 生成中文片段
5. 把每段音频放到它原始字幕的开始时间上，而不是简单顺序拼接
6. 如果某段中文超出自己的时间槽，就先做有限度加速，再在必要时裁到槽位内

这一步最终产出了：

- `artifacts/narration.zh.aligned.wav`
- `artifacts/narration.zh.aligned.json`
- `artifacts/final-voiceover-aligned.mp4`

其中 `narration.zh.aligned.json` 记录了每一段：

- 原始开始时间与结束时间
- 英文文本
- 中文文本
- 生成语音时长
- 实际放入时间轴的时长
- 是否应用了加速
- 是否发生裁切

最终校验结果：

- 对齐版音轨时长约 `356.999s`
- 对齐版视频时长约 `356.999s`
- 输出包含 `av1` 视频流和 `aac` 音频流

这个版本才真正满足“每句话从原始开始位置起播”的要求。

### 3.9 烧录中英双语字幕

在对齐版音画基础上，又新增了一步双语字幕烧录：

1. 编写 `scripts/build_bilingual_ass.py`
2. 用 `transcript.en.srt` 的时间轴作为基础
3. 把 `script.zh.segments.txt` 中的中文逐段合并进去
4. 生成 `artifacts/subtitles.zh-en.ass`
5. 用 `ffmpeg` 的 `ass` 滤镜把字幕硬烧到对齐版视频里

最终新增成片：

- `artifacts/final-voiceover-aligned-bilingual.mp4`

字幕布局为：

- 上行中文（较大字号）
- 下行英文（较小字号）

因为硬字幕需要重新编码视频，所以这个版本的视频编码变成了 `h264`，音频仍然是对齐后的中文 `aac`。

### 3.10 音色克隆复跑（Qwen3-TTS）

在完成普通中文旁白版之后，又继续尝试把同一个视频跑成“中文音色克隆版”。

这次没有额外的外部参考音频，所以为了验证工作流，先从源音频里截出一段较连续、较干净的人声作为最小回退：

- `source/reference.wav`：从 `32.09s` 到 `45.47s` 裁出的参考人声
- `source/reference.en.txt`：这段参考音频对应的英文文本

随后在原 report 的 `.venv` 里安装并调通了 `qwen-tts` 的 Python API 路径。这里踩到的关键点有两个：

1. `qwen-tts` 官方不是 CLI 路线，而是 Python API
2. 当前机器没有 GPU，必须改成 CPU-only 的 `torch` 安装路径，否则会默认拉取大量 CUDA 依赖

在依赖补齐后，先做了一个最小 smoke test，用很短的一句中文验证“参考音频 + 参考文本 + 中文文本”确实能生成克隆音色语音。这个 smoke test 成功产出了：

- `artifacts/narration.zh.clone.smoke.wav`
- `artifacts/narration.zh.clone.smoke.mp3`

但继续跑整片逐段克隆时，算力瓶颈立刻暴露出来：

- 使用 `Qwen/Qwen3-TTS-12Hz-0.6B-Base`
- 在 CPU-only 环境下，约 `1.6s` 的输出需要 `2 分 51 秒`
- 整片逐段克隆连续跑了约 `8 小时`，只生成到第 `17` 段

因此，这次没有在会话内完成全片 131 段的克隆版，而是把已成功生成的前 17 段复用起来，组装出一个可播放的真实样片：

- `artifacts/narration.zh.clone.first17.aligned.wav`
- `artifacts/narration.zh.clone.first17.aligned.json`
- `artifacts/final-voiceover-clone-first17.mp4`
- `artifacts/subtitles.zh-en.first17.ass`
- `artifacts/final-voiceover-clone-first17-bilingual.mp4`

另外又按标题复制出样片交付名：

- `artifacts/What are AI agents-cloned-first17.mp4`
- `artifacts/What are AI agents-cloned-first17.ass`
- `artifacts/What are AI agents-cloned-first17-bilingual.mp4`

## 4. 产物清单

### 最终交付文件（按标题命名）

- `artifacts/What are AI agents.mp4`：无字幕版
- `artifacts/What are AI agents.ass`：字幕文件
- `artifacts/What are AI agents-bilingual.mp4`：双语字幕版
- `artifacts/What are AI agents-cloned-first17.mp4`：音色克隆样片（前 17 段）
- `artifacts/What are AI agents-cloned-first17.ass`：音色克隆样片字幕
- `artifacts/What are AI agents-cloned-first17-bilingual.mp4`：音色克隆样片双语字幕版

### source/

- `What are AI agents？ [3zgm60bXmQk].webm`
- `video-info.json`
- `video.mp4`
- `audio.mp3`

### artifacts/

- `transcript.en.txt`
- `transcript.en.srt`
- `script.zh.txt`
- `script.zh.segments.txt`
- `narration.zh.mp3`
- `narration.zh.wav`
- `narration.zh.aligned.wav`
- `narration.zh.aligned.json`
- `narration.zh.clone.smoke.wav`
- `narration.zh.clone.smoke.mp3`
- `narration.zh.clone.first17.aligned.wav`
- `narration.zh.clone.first17.aligned.json`
- `narration.zh.clone.first17.trimmed.wav`
- `final-voiceover.mp4`
- `final-voiceover-aligned.mp4`
- `subtitles.zh-en.ass`
- `final-voiceover-aligned-bilingual.mp4`
- `transcript.en.first17.srt`
- `script.zh.first17.txt`
- `subtitles.zh-en.first17.ass`
- `final-voiceover-clone-first17.mp4`
- `final-voiceover-clone-first17-bilingual.mp4`

### scripts/

- `transcribe.py`
- `rewrite_to_zh.py`
- `generate_tts.py`
- `build_aligned_dub.py`
- `build_bilingual_ass.py`

### notes/

- `commands.md`
- `issues.md`

## 5. 遇到的问题与修复

### 问题 1：YouTube 直连下载失败

- 现象：`yt-dlp` 返回 429 和登录验证提示
- 验证：浏览器打开同视频页也落到 Google `sorry` 页面
- 结论：问题在当前出口网络 / 会话，不是单独的下载命令写错
- 修复：改用用户上传的本地视频继续流程

### 问题 2：`faster-whisper` 模型下载报 `Invalid port`

- 现象：`httpx.InvalidURL: Invalid port ':1]'`
- 排查：代理变量存在，`NO_PROXY` 包含 `[::1]`
- 修复：运行转写时临时改用 `NO_PROXY=localhost,127.0.0.1`

### 问题 3：中文音频短于原视频

- 现象：中文旁白约 4 分 41 秒，原视频约 5 分 57 秒
- 处理：合成时对中文音频做 `apad`，保留完整视频时长

### 问题 4：总时长对了，但句子起点不对

- 现象：第一版中文旁白虽然能播完整段视频，但句子没有和原始音频/字幕的开始位置对齐
- 根因：整段连续中文旁白无法天然保留每个字幕块的原始时间锚点
- 修复：改成逐段中文稿 + 逐段 TTS + 按原 SRT 开始时间摆放的新流程

## 6. 成功与不足

### 成功

- 整个链路已经真实跑通：本地源文件 → 转写 → 中文稿 → 中文语音 → 最终成片
- 对齐版流程已经跑通：逐段中文稿 → 逐段 TTS → 按原始开始时间对齐 → 对齐版成片
- 双语字幕版本也已经跑通：中英双语 ASS → 硬烧录 → 双语成片
- Qwen3-TTS 的参考音频驱动音色克隆在当前机器上已经真实跑通至少一个 smoke case，以及前 17 段的片段样片
- 关键环境坑和回退策略都有记录，而不是只留下理想化说明
- 已经具备抽象成 skill 的条件

### 不足

- 这次不是“原作者本人在说中文”，只是中文旁白版
- 对齐版为了保住每句起点，有些片段做了轻微加速，个别片段仍可能因为中文更长而被裁到时间槽内
- 直连 YouTube 的下载问题没有在当前机器上彻底解决，因此 skill 必须明确记录本地文件回退路径
- 整片中文音色克隆版没有在本次会话内跑完，根因是当前机器没有 GPU，CPU-only 下 `Qwen3-TTS` 速度太慢；这次只完成了前 17 段样片

## 7. 版权与使用提醒

- 这次产物是技术演示，不代表拥有原视频的转载或商业使用权
- 如果后续要公开发布，需要额外评估原视频版权、平台规则，以及二创使用边界
