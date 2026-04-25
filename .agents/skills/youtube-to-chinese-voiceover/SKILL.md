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
- **参考音频驱动的中文音色克隆**：默认从源视频中截取清晰人声作为参考；如果用户提供了参考音频，则使用用户提供的参考音频，中文配音尽量贴近该参考音色。

明确边界：本 skill 不负责自动从复杂原视频中提纯声纹，也不处理法律或授权风险高的“冒充原说话人”场景。

## 什么时候用

适用于：

- 用户给出 YouTube 链接或本地视频，要求制作中文旁白版。
- 用户要求中文配音、句子级同步、双语字幕、按标题命名的最终视频。
- 用户更重视低成本、透明过程、可复现证据，而不是专业录音棚成品。
- 用户要求音色克隆，希望默认使用源视频人声作为参考，或提供了单独参考音频。
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

| 产物                               | 说明                                                                                         |
| ---------------------------------- | -------------------------------------------------------------------------------------------- |
| `source/video.mp4`                 | 标准化后的视频输入                                                                           |
| `source/audio.mp3`                 | 从视频抽取或用户提供的音频                                                                   |
| `artifacts/transcript.en.txt`      | 英文转写文本                                                                                 |
| `artifacts/transcript.en.srt`      | 带时间轴的英文字幕                                                                           |
| `artifacts/script.zh.txt`          | 连续中文口播稿                                                                               |
| `artifacts/script.zh.segments.txt` | 句子级同步时的逐段中文稿                                                                     |
| `source/reference.*`               | 音色克隆模式下的参考音频和参考文本；默认来自源视频截取片段，用户提供参考音频时则使用用户文件 |
| `artifacts/narration*.wav/mp3`     | 真实生成的中文 TTS 音频                                                                      |
| `artifacts/final*.mp4`             | 候选中文旁白视频或内部合成产物                                                               |
| `artifacts/subtitles*.ass`         | 内部字幕产物                                                                                 |
| `output/{title}.mp4`               | 面向用户交付的干净中文旁白视频                                                               |
| `output/{title}.ass`               | 面向用户交付的外挂字幕文件                                                                   |
| `output/{title}-bilingual.mp4`     | 面向用户交付的双语字幕烧录版视频                                                             |
| `notes/commands.md`                | 实际执行过的命令                                                                             |
| `notes/issues.md`                  | 阻塞、失败、修复方式和限制                                                                   |
| `report.md`                        | 面向用户的最终总结                                                                           |

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

默认从源视频中截取一段清晰单人讲话作为 `source/reference.wav`，并把该片段对应原文写入 `source/reference.txt`。如果用户提供了参考音频，则改用用户提供的参考音频，并尽量要求用户同时提供对应参考文本。

参考音频尽量满足：

- 单人说话。
- 背景噪声低。
- 3-15 秒清晰人声。
- 不混入音乐、多人对话或强混响。
- 提供对应参考文本，提升克隆后端稳定性；默认从源视频截取时，可使用转写中对应时间段的英文文本。

从源视频截取参考段时，必须记录：截取时间范围、参考文本来源、音频质量限制，以及这不是外部参考样本。用户提供参考音频时，必须记录用户文件路径、可播放性、时长、说话人纯度和参考文本来源。

源视频参考段示例：

```bash
ffmpeg -y -ss 00:00:02.640 -to 00:00:15.000 \
  -i source/video.mp4 \
  -vn -ac 1 -ar 24000 -c:a pcm_s16le \
  source/reference.wav

printf '%s\n' 'Exact spoken text for this reference clip.' > source/reference.txt
```

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

| 脚本                                        | 用途                                                 |
| ------------------------------------------- | ---------------------------------------------------- |
| `scripts/transcribe_with_faster_whisper.py` | 把音频转成英文文本和 SRT                             |
| `scripts/scaffold_rewrite_prompt.py`        | 为中文改写生成可人工审阅的 prompt scaffold           |
| `scripts/generate_edge_tts.py`              | 把整段中文稿生成 MP3/WAV                             |
| `scripts/generate_qwen3_voice_clone.py`     | 用参考音频和中文稿生成整段中文音色克隆 MP3/WAV       |
| `scripts/build_aligned_dub.py`              | 逐段生成中文配音并按原始字幕开始时间拼到整条时间线上 |
| `scripts/build_bilingual_ass.py`            | 按英文时间轴生成中英双语 ASS 字幕                    |

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

## 故障排查

### python index

- index: https://pypi.tuna.tsinghua.edu.cn/simple
- extra-index-url: https://mirrors.nju.edu.cn/pytorch/whl/cu121

### `yt-dlp` 遇到 `429`、bot verification 或 CAPTCHA

**问题表现**：下载 YouTube 源视频或字幕时出现 `429`、bot verification、CAPTCHA、登录校验，或者长时间无响应。

**应该如何解决**：不要把这类问题当作普通参数错误反复重试。先用浏览器复核页面状态；若浏览器也被 CAPTCHA 或登录拦住，停止绕路，改让用户提供本地媒体或字幕文件，并把失败信息写入 `notes/issues.md`。

### Hugging Face、YouTube、ytscribe、PyPI 等网络请求超时

**问题表现**：`faster-whisper`、`yt-dlp`、`webfetch`、`pip`、`uv`、`curl` 访问外部服务超时、TLS EOF、connection reset，导致转写、字幕或依赖下载失败。

**应该如何解决**：先验证代理是否真的生效，例如：

```bash
curl -I https://huggingface.co
curl -I https://www.youtube.com
curl -I https://pypi.org/simple/
```

记录失败域名、错误和代理变量。不要把网络问题误判为脚本问题。代理恢复后重跑原命令；如果只有某个域名不可达，优先换镜像源或本地缓存，而不是更换整个工作流。

### Python/httpx 报代理格式错误，例如 `Invalid port: ':1]'`

**问题表现**：命令行 `curl` 可以访问网络，但 Python 包（如 `httpx`、`huggingface_hub`）报代理 URL 解析错误，常见错误包含 `Invalid port: ':1]'`。

**应该如何解决**：检查代理环境变量：

```bash

```

常见原因是 `NO_PROXY=localhost,127.0.0.1,[::1]` 中的 IPv6 写法被某些库解析异常。运行关键命令时可临时移除：

```bash

```

### faster-whisper 模型下载失败或无本地缓存

**问题表现**：英文转写阶段失败，提示无法下载 Whisper/faster-whisper 模型，或本地没有模型 snapshot。

**应该如何解决**：先检查代理和缓存目录：`~/.cache/huggingface`、`~/.cache/ctranslate2`、`~/.cache/whisper`。网络恢复后重跑转写命令。若仍失败，可让用户提供这个视频对应的英文 SRT/转写，或改用已经安装且可离线运行的 ASR 工具；不要手写伪造 SRT。

### Hugging Face 大模型权重跳转到 `cas-bridge.xethub.hf.co` 后 SSL EOF

**问题表现**：小文件能下载，但 Qwen 等大权重下载时被重定向到 Xet/CAS 地址，然后 SSL EOF、broken pipe 或 connection reset。

**应该如何解决**：先试：

```bash
HF_HUB_DISABLE_XET=1 python ...
```

如果仍然跳转 Xet/CAS，改用 ModelScope 下载模型快照到本地，再把 `--model-id` 指向本地目录，例如 `models/Qwen/Qwen3-TTS-12Hz-0___6B-Base`。报告中要记录实际模型来源和本地路径。

### `uv python install 3.12` 从 GitHub release 下载失败

**问题表现**：`uv python install 3.12` 下载 `python-build-standalone` 时出现 GitHub release TLS EOF、connection reset 或下载超时。

**应该如何解决**：使用 uv 的 `--mirror`，并先用 `curl -I -L` 测试镜像是否能返回 Python tarball。例如：

```bash
uv python install 3.12 \
  --mirror 'https://gh.llkk.cc/https://github.com/astral-sh/python-build-standalone/releases/download'
```

安装成功后用独立虚拟环境承载 TTS/GPU 依赖，不要污染主环境。

### 当前 Python 版本过新，旧版 GPU 兼容 PyTorch 没有合适 wheel

**问题表现**：系统只有 Python 3.13/3.14，但需要安装较旧的 CUDA PyTorch；pip 找不到对应 wheel，或解析出不兼容版本。

**应该如何解决**：新建 Python 3.12/3.11 环境，例如 `.venv-qwen-p4`。不要在现有环境硬降 Python 或混装多个 torch。先固定 Python，再安装目标 torch，最后补 Qwen 依赖。

### Tesla P4 报 `no kernel image is available for execution on the device`

**问题表现**：Qwen 模型开始加载 GPU 后失败，PyTorch 报 `no kernel image is available for execution on the device`；日志显示 Tesla P4 compute capability `6.1`，但当前 torch 只支持 `sm_75+`。

**应该如何解决**：根因是 PyTorch wheel 不支持 P4 的 `sm_61`。换用支持该架构的旧版 CUDA PyTorch，例如 Python 3.12 + `torch==2.4.1+cu121`。安装后必须用最小 CUDA tensor 脚本验证：

```python
import torch
print(torch.__version__, torch.version.cuda)
print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))
x = torch.ones(4, device='cuda')
print((x * 2).sum().item())
```

只有这个验证通过后，才继续跑 Qwen 推理。

### 安装 `qwen-tts` 时自动升级到不兼容的 PyTorch

**问题表现**：先装好了 P4 兼容 torch，但安装 `qwen-tts` 后 torch 被 pip 解析器升级到新版本，重新出现 GPU 架构不兼容。

**应该如何解决**：先安装并验证目标 PyTorch，再用 `--no-deps` 安装 `qwen-tts`，随后根据导入错误逐项补依赖。这样可以避免 pip 重新解析并覆盖 torch。补依赖后再次验证 `torch.__version__` 和 CUDA tensor。

### `transformers`、`huggingface-hub`、`accelerate` 版本冲突

**问题表现**：导入 Qwen 或 Transformers 时出现版本约束错误，例如 `transformers 4.57.x` 要求 `huggingface-hub < 1.0`，或 `qwen-tts` 要求特定 `accelerate` 版本。

**应该如何解决**：按实际报错钉版本，不要盲目升级所有包。例如可将 `huggingface-hub` 钉到 `<1.0`，将 `accelerate` 钉到 `qwen-tts` 要求的版本。每次调整后运行导入检查，确认 torch 没被替换。

### 系统没有 `sox` 命令，Qwen 导入提示 `SoX could not be found`

**问题表现**：Qwen 或音频库导入时打印 `SoX could not be found`，但脚本可能仍继续运行。

**应该如何解决**：先判断这是否只是警告。如果生成能继续，记录限制即可；如果实际阻塞，再安装系统 SoX，或确认脚本是否只需要 Python `sox` 包。不要因为一个警告就重构整个 TTS 流程。

### 音色克隆没有用户提供的参考音频

**问题表现**：用户要求音色克隆，但没有上传独立参考音频或参考文本。

**应该如何解决**：默认从源视频中选择 3-15 秒清晰单人语音作为 `source/reference.wav`，并用对应转写文本写入 `source/reference.txt`。如果用户后来提供了参考音频，则改用用户提供的文件。无论哪种来源，都要记录参考音频来源、时间范围或文件路径、文本来源和质量限制。

### 音色克隆不像参考音色

**问题表现**：生成音色明显不像原视频或用户参考音频，或者稳定性差。

**应该如何解决**：优先检查参考音频质量：是否单人、是否 3-15 秒、是否有音乐/混响/多人重叠、参考文本是否精确匹配。源视频默认参考段不理想时，重新选择更干净的人声片段；用户参考音频不理想时，请用户提供更干净样本。

### 中文旁白比视频短很多

**问题表现**：整段中文音频明显短于视频，末尾空白很多。

**应该如何解决**：如果只在意总时长，可以补静音；如果在意句子同步，必须逐段对齐，不能只把整段音频拉伸到视频长度。

### 视频长度对了但句子越说越漂

**问题表现**：最终视频总时长正确，但中文句子越来越偏离画面或字幕。

**应该如何解决**：连续旁白不能保证句子同步。改用原始 SRT 的 start time 作为锚点逐段构建配音，并保存 timing report；中文过长时记录加速或裁切情况。

### 用户要求按标题命名但只有内部 artifact

**问题表现**：工作目录里只有 `artifacts/final-*.mp4`，没有用户可直接取用的最终命名文件。

**应该如何解决**：增加显式 packaging/export 步骤，把最终文件复制或导出到 `output/`，使用用户要求的标题命名，并验证文件真实存在。

### 用户要求字幕但只有视频文件

**问题表现**：交付物只有 MP4，没有外挂字幕、硬字幕或用户要求的字幕格式。

**应该如何解决**：补出 `.ass`、硬字幕视频或用户指定的字幕格式。报告中要区分外挂字幕、硬字幕和软字幕，不要用一个产物冒充另一个。

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
