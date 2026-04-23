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

### 3.7 合成最终视频

中文旁白音频时长约 `281.35s`，明显短于原视频约 `357.00s`。如果直接用 `-shortest` 合成，视频会被硬裁短，不利于保留原始画面结构。

因此最终采用 `apad` 给中文音轨补静音尾巴，再与原视频合成为：

- `artifacts/final-voiceover.mp4`

校验结果显示输出文件包含：

- 1 路 `av1` 视频流
- 1 路 `aac` 音频流

最终视频总时长约 `356.99s`，与源视频基本一致。

## 4. 产物清单

### source/

- `What are AI agents？ [3zgm60bXmQk].webm`
- `video-info.json`
- `video.mp4`
- `audio.mp3`

### artifacts/

- `transcript.en.txt`
- `transcript.en.srt`
- `script.zh.txt`
- `narration.zh.mp3`
- `narration.zh.wav`
- `final-voiceover.mp4`

### scripts/

- `transcribe.py`
- `rewrite_to_zh.py`
- `generate_tts.py`

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

## 6. 成功与不足

### 成功

- 整个链路已经真实跑通：本地源文件 → 转写 → 中文稿 → 中文语音 → 最终成片
- 关键环境坑和回退策略都有记录，而不是只留下理想化说明
- 已经具备抽象成 skill 的条件

### 不足

- 这次不是“原作者本人在说中文”，只是中文旁白版
- 旁白稿经过压缩和口语化，节奏比原片更紧凑，末尾通过静音补齐时长
- 直连 YouTube 的下载问题没有在当前机器上彻底解决，因此 skill 必须明确记录本地文件回退路径

## 7. 版权与使用提醒

- 这次产物是技术演示，不代表拥有原视频的转载或商业使用权
- 如果后续要公开发布，需要额外评估原视频版权、平台规则，以及二创使用边界
