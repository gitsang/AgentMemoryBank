# Issues and Recovery Notes

## Initial findings

- `yt-dlp` was not preinstalled on PATH.
- `faster-whisper` was not preinstalled in the system Python.
- No obvious local TTS CLI was preinstalled (`espeak` and `piper` were not found on PATH).

## Install-time issues

- `uv venv` created a Python environment without a bundled `pip` entrypoint; package installation needs to go through `uv pip`.
- First attempt to install `yt-dlp` + `faster-whisper` via `uv pip` failed while extracting `ctranslate2==4.7.1` because the wheel download timed out at `UV_HTTP_TIMEOUT=30`.

## Source access blocker

- `yt-dlp` metadata fetch and download both failed for `https://www.youtube.com/watch?v=3zgm60bXmQk` with `HTTP Error 429: Too Many Requests` followed by `Sign in to confirm you’re not a bot`.
- `chrome-devtools` opening the same URL reached Google `sorry` / reCAPTCHA instead of the video page, so the challenge is at the network/session level rather than a pure CLI extractor bug.
- A minimal extractor change (`youtube:player_client=tv_simply_embedded`) did not bypass the challenge.
- Two alternative Invidious access attempts timed out from this environment, so a third-party mirror is not yet a reliable fallback here.

## Current conclusion

- The workflow is blocked at source intake until a human completes the verification challenge in a browser session, provides an already-downloaded local source file, or provides a reusable authenticated cookie source that works from this machine.

## Transcription environment issue

- After the local source file was provided, `faster-whisper` failed before model download with `httpx.InvalidURL: Invalid port: ':1]'`.
- Investigation showed proxy variables were present and `NO_PROXY` was set to `localhost,127.0.0.1,[::1]`.
- `curl https://huggingface.co` succeeded through the proxy, so the likely issue is the bracketed IPv6 loopback entry conflicting with `httpx` URL parsing. The next minimal fix is to rerun the model download with a sanitized `NO_PROXY` value.
- Re-running `scripts/transcribe.py` with `NO_PROXY=localhost,127.0.0.1` and a local `HF_HOME` cache fixed the model download path and produced a valid English transcript.

## TTS and timing notes

- `edge-tts` worked as a lightweight no-key TTS path in this environment using `zh-CN-XiaoxiaoNeural`.
- The generated Chinese narration is about `281.35s`, while the source video is about `357.00s`.
- To preserve the full video length, the final assembly pads the Chinese narration with silence instead of trimming the video.

## Sync correction

- The first Chinese voiceover version used one continuous narration track, so it could preserve total video length but could not preserve sentence-level start times.
- The corrected workflow switches to segment-based dubbing: each Chinese line is generated independently and then placed at the original subtitle `start` timestamp.
- The new builder writes `artifacts/narration.zh.aligned.json`, which records per-segment generated duration, placed duration, applied speed-up, and truncation.
- If a segment is longer than its available subtitle slot, the builder first applies bounded speed-up and then trims to fit the slot. This keeps each segment's start time aligned even when Chinese takes longer than English.

## Skill baseline failure to guard against

- Without a workflow skill, an agent is likely to make at least one of these mistakes: assume direct YouTube download will work from any network, claim a placeholder TTS file counts as completion, or write a reusable workflow before a real run proves the edge cases.
- Another likely failure is to generate a single continuous Chinese narration track and mistake duration matching for real sync. The corrected workflow treats original subtitle start times as the actual timing source.

## Skill update test evidence

- Baseline test against `skills/youtube-to-chinese-voiceover/SKILL.md` failed on final packaging guidance: it did not specify `{title}.mp4`, `{title}.ass`, `{title}-bilingual.mp4`, or clearly separate intermediate artifacts from final deliverables.
- After updating the skill, a re-test passed: the skill now explicitly documents title-based naming, external ASS delivery, burned bilingual export, and a review gate that checks final named deliverables before handoff.

## Voice cloning rerun notes

- 为了继续在 `What are AI agents` 这个视频上实跑音色克隆，这次临时从源音频中抽取了 `32.09s-45.47s` 的连续英文人声，生成 `source/reference.wav`，并把对应文本保存为 `source/reference.en.txt`。这和“第一版只支持外部参考音频”的 skill 边界不完全一致，属于为了本次验证而做的最小回退。
- `qwen-tts` 官方可用的是 Python API，不是先前假设的 CLI。仓库里的 skill 脚本后来已经修正为 Python API 路径。
- 首次安装 `qwen-tts` 时，默认 `torch` 解析到了 CUDA 轮子，开始下载大量 NVIDIA 依赖并超时；改成 `https://download.pytorch.org/whl/cpu` 的 CPU-only torch 后才稳定安装。
- `qwen_tts` 在当前环境里还要求 `transformers==4.57.3`、`accelerate==1.12.0` 等推理依赖；版本不匹配时会在 import 阶段报 `check_model_inputs()` 相关错误。
- 当前机器没有 GPU，`Qwen/Qwen3-TTS-12Hz-0.6B-Base` 在 CPU 上可以跑，但非常慢。一次 1.6s 左右的 smoke 输出大约需要 2 分 51 秒。
- 整片逐段克隆长跑持续 8 小时，只生成了前 17 段缓存（`aligned-segments-clone/segment-001.wav` 到 `segment-017.wav`），没能在本次会话内完成 131 段全片。
- 因此，本次真实交付改为：基于已经生成成功的前 17 段，组装出一个约 `55.31s` 的中文音色克隆片段样片，并明确记录整片版本仍受算力约束。
