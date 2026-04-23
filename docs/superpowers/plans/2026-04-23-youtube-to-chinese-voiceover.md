# YouTube to Chinese Voiceover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a personal-scale, low-cost workflow on YouTube video `3zgm60bXmQk` that produces a Chinese voiceover demo video, optionally using external-reference-audio voice cloning, captures reproducible evidence under `reports/`, and extracts a reusable skill under `skills/`.

**Architecture:** Create a dedicated report workspace for the sample video, bootstrap local CLI/Python tooling in an isolated `.venv`, download the source media, generate transcript artifacts, rewrite to Chinese narration, optionally feed a user-supplied reference clip into a cloning-capable TTS backend, assemble a playable MP4, then distill only the proven workflow into a reusable skill. The execution is evidence-first: every artifact referenced by the report or skill must exist in the report directory.

**Tech Stack:** Python 3.13, uv, ffmpeg/ffprobe, yt-dlp, faster-whisper, edge-tts, qwen-tts, local helper scripts, markdown reports, skill documentation.

---

## File Structure

- Create: `docs/superpowers/plans/2026-04-23-youtube-to-chinese-voiceover.md`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/report.md`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/commands.md`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/issues.md`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video-info.json`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.mp4`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/audio.mp3`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.txt`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.srt`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/script.zh.txt`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/transcribe.py`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/rewrite_to_zh.py`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/generate_tts.py`
- Create: `skills/youtube-to-chinese-voiceover/SKILL.md`

### Task 1: Bootstrap the execution workspace

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/commands.md`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/issues.md`

- [ ] **Step 1: Create the directory tree**

Run:
```bash
mkdir -p "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source"
mkdir -p "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts"
mkdir -p "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes"
mkdir -p "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts"
```
Expected: all four directories exist.

- [ ] **Step 2: Initialize command and issue logs**

Create `notes/commands.md` with this initial content:
```md
# Command Log

## Environment

- Python: `python3 --version`
- ffmpeg: `ffmpeg -version`
- ffprobe: `ffprobe -version`

## Commands Run

Add each material command in execution order.
```

Create `notes/issues.md` with this initial content:
```md
# Issues and Recovery Notes

Document missing tools, install failures, timing mismatches, and manual adjustments.
```

- [ ] **Step 3: Create a dedicated Python virtual environment**

Run:
```bash
uv venv "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv"
```
Expected: `.venv/` exists under the report directory.

### Task 2: Install and verify local tooling

**Files:**
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/commands.md`
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/issues.md`

- [ ] **Step 1: Install `yt-dlp` and `faster-whisper` into the venv**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/pip" install yt-dlp faster-whisper
```
Expected: pip exits 0 and reports both packages installed.

- [ ] **Step 2: Verify imports succeed**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" -c "import yt_dlp, faster_whisper; print('ok')"
```
Expected: output is `ok`.

- [ ] **Step 3: If install fails, record the blocker and install the narrowest missing dependency**

Write the exact failure into `notes/issues.md` and retry only the missing piece. For example, if a wheel build is missing a backend, record the error before installing that backend.

### Task 3: Download the sample video and capture metadata

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video-info.json`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.mp4`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/audio.mp3`
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/commands.md`

- [ ] **Step 1: Save the source metadata as JSON**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" -m yt_dlp --dump-single-json "https://www.youtube.com/watch?si=z8QygFvYQv-9WtO1&v=3zgm60bXmQk&feature=youtu.be"
```
Expected: JSON metadata prints to stdout; save it to `source/video-info.json`.

- [ ] **Step 2: Download the source video as MP4**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" -m yt_dlp -f "bestvideo+bestaudio/best" --merge-output-format mp4 -o "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.%(ext)s" "https://www.youtube.com/watch?si=z8QygFvYQv-9WtO1&v=3zgm60bXmQk&feature=youtu.be"
```
Expected: `source/video.mp4` exists.

- [ ] **Step 3: Extract MP3 audio for transcription**

Run:
```bash
ffmpeg -i "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.mp4" -vn -q:a 0 -map a "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/audio.mp3"
```
Expected: `source/audio.mp3` exists and has non-zero duration.

### Task 4: Generate transcript artifacts

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/transcribe.py`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.txt`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.srt`
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/issues.md`

- [ ] **Step 1: Create the transcription script**

Write `scripts/transcribe.py` with this content:
```python
from pathlib import Path
from faster_whisper import WhisperModel


ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = ROOT / "source" / "audio.mp3"
TXT_PATH = ROOT / "artifacts" / "transcript.en.txt"
SRT_PATH = ROOT / "artifacts" / "transcript.en.srt"


def format_ts(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, rem = divmod(milliseconds, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main() -> None:
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(AUDIO_PATH), beam_size=5, vad_filter=True)
    segment_list = list(segments)

    TXT_PATH.write_text(
        "\n".join(segment.text.strip() for segment in segment_list if segment.text.strip()) + "\n",
        encoding="utf-8",
    )

    with SRT_PATH.open("w", encoding="utf-8") as handle:
        for index, segment in enumerate(segment_list, start=1):
            text = segment.text.strip()
            if not text:
                continue
            handle.write(f"{index}\n")
            handle.write(f"{format_ts(segment.start)} --> {format_ts(segment.end)}\n")
            handle.write(f"{text}\n\n")

    print({
        "language": info.language,
        "duration": info.duration,
        "segments": len(segment_list),
    })


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the transcription script**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/transcribe.py"
```
Expected: script prints language/duration/segment count and writes both transcript files.

- [ ] **Step 3: Inspect the transcript and record any major recognition issues**

Review `artifacts/transcript.en.txt`. If the source language is not English or the transcript is poor enough to block translation, write the finding to `notes/issues.md` before changing models or flags.

### Task 5: Create the Chinese voiceover script

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/rewrite_to_zh.py`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/script.zh.txt`

- [ ] **Step 1: Create the rewrite helper**

Write `scripts/rewrite_to_zh.py` with this content:
```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "artifacts" / "transcript.en.txt"
DST = ROOT / "artifacts" / "script.zh.txt"


PROMPT = """把下面英文视频字幕改写成适合中文视频解说的口播稿。要求：
1. 保留原意
2. 使用自然中文口语
3. 句子简短，适合配音
4. 不要书面腔
5. 输出纯中文稿，不要解释
"""


def main() -> None:
    transcript = SRC.read_text(encoding="utf-8").strip()
    output = (
        "# Manual step required\n\n"
        "Use the following prompt with your preferred LLM, then replace this file with the final Chinese script.\n\n"
        f"{PROMPT}\n\n=== TRANSCRIPT START ===\n{transcript}\n=== TRANSCRIPT END ===\n"
    )
    DST.write_text(output, encoding="utf-8")
    print(DST)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the helper to create the prompt scaffold**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/rewrite_to_zh.py"
```
Expected: `artifacts/script.zh.txt` exists with the prompt scaffold.

- [ ] **Step 3: Replace the scaffold with the final Chinese narration copy**

Use the transcript as input and write the final Chinese script directly into `artifacts/script.zh.txt`. Expected: the file contains only the Chinese narration content, ready for TTS.

### Task 6: Generate the TTS narration

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/generate_tts.py`
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav`
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/issues.md`

- [ ] **Step 1: Create a local-first TTS script with explicit fallback behavior**

Write `scripts/generate_tts.py` with this content:
```python
from pathlib import Path
import wave


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "artifacts" / "script.zh.txt"
OUTPUT_PATH = ROOT / "artifacts" / "narration.zh.wav"


def main() -> None:
    text = SCRIPT_PATH.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Chinese script is empty")

    # Placeholder fallback: generate a short silent WAV if no TTS engine is available.
    # Replace this file with a real engine path once one is proven in this environment.
    sample_rate = 22050
    seconds = max(3, min(30, len(text) // 20))
    total_frames = sample_rate * seconds
    with wave.open(str(OUTPUT_PATH), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * total_frames)

    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script and immediately verify whether it produced real speech or a fallback artifact**

Run:
```bash
"/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python" "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/scripts/generate_tts.py"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav"
```
Expected: a WAV file exists; if it is only a placeholder or silence, record that in `notes/issues.md` and replace the script with the first real TTS method that works.

- [ ] **Step 3: Upgrade to a real TTS engine before claiming success**

If a real TTS engine is unavailable locally, install the lightest viable option, or document the blocker in `notes/issues.md` and stop before final verification. A silent placeholder is acceptable only as a diagnostic artifact, not as the final deliverable.

### Task 7: Assemble and verify the Chinese voiceover video

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4`
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/notes/commands.md`

- [ ] **Step 1: Merge the original video with the Chinese narration**

Run:
```bash
ffmpeg -i "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.mp4" -i "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4"
```
Expected: `artifacts/final-voiceover.mp4` exists and is playable.

- [ ] **Step 2: Verify the output streams**

Run:
```bash
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of default=noprint_wrappers=1 "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4"
```
Expected: at least one `video` stream and one `audio` stream are listed.

### Task 8: Write the report and extract the reusable skill

**Files:**
- Create: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/report.md`
- Create: `skills/youtube-to-chinese-voiceover/SKILL.md`

- [ ] **Step 1: Write `report.md` from actual artifacts only**

Include these sections:
```md
# YouTube 中文旁白工作流实跑记录

## 1. 输入视频
## 2. 环境与依赖
## 3. 执行步骤
## 4. 产物清单
## 5. 遇到的问题与修复
## 6. 成功与不足
## 7. 版权与使用提醒
```

- [ ] **Step 2: Baseline-test the future skill before writing it**

Create a short pressure scenario in `report.md` or `notes/issues.md` that captures what an agent would likely miss without the skill, such as skipping artifact logging, writing an aspirational workflow without running it, or claiming success with placeholder TTS. Record the baseline failure before finalizing the skill.

- [ ] **Step 3: Write `skills/youtube-to-chinese-voiceover/SKILL.md` from the verified run**

The skill must include:
```md
---
name: youtube-to-chinese-voiceover
description: Use when converting a single YouTube video into a low-cost Chinese voiceover demo with evidence captured in reports/ and a manually reviewed script.
---
```

Then cover:
- when to use
- artifact directory structure
- minimal toolchain
- exact workflow order
- manual review gates
- common failure modes
- what not to claim as done

- [ ] **Step 4: Verify the skill references only proven steps**

Cross-check every instruction in the skill against the real artifacts and commands in the report directory.

### Task 9: Final verification

**Files:**
- Modify: `reports/youtube-zh-dub-3zgm60bXmQk-20260423/report.md`
- Modify: `skills/youtube-to-chinese-voiceover/SKILL.md`

- [ ] **Step 1: Confirm all required artifacts exist**

Required paths:
```text
reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video-info.json
reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/video.mp4
reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/audio.mp3
reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.txt
reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/transcript.en.srt
reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/script.zh.txt
reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav
reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4
reports/youtube-zh-dub-3zgm60bXmQk-20260423/report.md
skills/youtube-to-chinese-voiceover/SKILL.md
```

- [ ] **Step 2: Run lightweight verification commands**

Run:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/source/audio.mp3"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/narration.zh.wav"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "/home/sang/src/github.com/gitsang/AgentMemoryBank/reports/youtube-zh-dub-3zgm60bXmQk-20260423/artifacts/final-voiceover.mp4"
```
Expected: all three durations print and are non-zero.

- [ ] **Step 3: Summarize remaining gaps honestly**

If the run required a fallback or manual step, document it in the final summary instead of overstating automation.

---

Plan complete and saved to `docs/superpowers/plans/2026-04-23-youtube-to-chinese-voiceover.md`.

The user has already chosen execution, so proceed inline from this plan rather than pausing for an execution-mode prompt.
