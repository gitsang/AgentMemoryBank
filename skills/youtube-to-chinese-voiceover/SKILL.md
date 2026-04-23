---
name: youtube-to-chinese-voiceover
description: Use when converting a single YouTube video into a low-cost Chinese voiceover demo with evidence captured in reports/ and a manually reviewed script.
---

# YouTube to Chinese Voiceover

## Overview

This skill is for a **single-video, personal-scale Chinese voiceover workflow**. The goal is not voice cloning or lip-sync. The goal is to produce a real, auditable Chinese narration version of one video and capture the evidence under `reports/`.

## When to Use

Use when:

- you need to turn one YouTube video into a Chinese旁白版
- low cost and reproducibility matter more than studio-grade dubbing
- you want every artifact and recovery step recorded in `reports/`
- a human can review the Chinese script before TTS

Do not use when:

- the target is voice cloning, lip-sync, or batch automation
- you do not have permission to work with the source material

## Required Artifacts

Create a dedicated directory under `reports/`, for example:

```text
reports/<task-name>/
  source/
  artifacts/
  notes/
  scripts/
  report.md
```

Minimum outputs:

- source video or audio
- normalized `video.mp4` and `audio.mp3`
- English transcript text and SRT
- final Chinese script
- real TTS audio
- final voiceover video
- `notes/commands.md`
- `notes/issues.md`
- `report.md`

## Workflow Order

1. **Try source intake**
   - Prefer direct download if the environment allows it.
   - If YouTube blocks you with 429 / bot verification, stop pretending it is a CLI bug.
   - Use browser inspection to confirm the blocker.
   - If still blocked, switch to a local source file provided by the user.

2. **Normalize the media**
   - Write source metadata with `ffprobe`.
   - Convert the source into stable internal paths such as `source/video.mp4` and `source/audio.mp3`.
   - Do this even if the user uploaded a differently named file.

3. **Transcribe to English**
   - Use `faster-whisper`.
   - Save both plain text and SRT.
   - If model download fails, inspect proxy environment before changing transcription tooling.

4. **Create the Chinese narration script**
   - Keep it conversational.
   - Preserve meaning over literal wording.
   - Shorter Chinese is acceptable, but note any pacing difference in the report.
   - This is a human review gate. Do not skip it.

5. **Generate real TTS audio**
   - Prefer a reproducible, lightweight path such as `edge-tts`.
   - Use a real Mandarin voice, such as `zh-CN-XiaoxiaoNeural`.
   - A silent placeholder file is not a completed result.

6. **Assemble the final video**
   - Replace the source audio with the Chinese narration.
   - If narration is shorter than the source video, pad silence instead of trimming the video unless trimming is intentional.
   - Verify the final MP4 has both a video stream and an audio stream.

7. **Write the report after the run**
   - Record commands, blockers, fixes, artifacts, and honest limitations.
   - Only include steps that actually worked in this environment.

## Minimal Toolchain

- `ffmpeg`
- `ffprobe`
- `uv` + local `.venv`
- `faster-whisper`
- `edge-tts` or another proven Mandarin TTS path

## Manual Review Gates

- after source intake fails, confirm whether the blocker is network/session-level
- after transcription, spot-check transcript quality before translation
- after Chinese rewrite, make sure the file contains final narration text, not a scaffold prompt
- after TTS, confirm the audio contains real speech
- after assembly, confirm the output video still has both streams and expected duration

## Common Failure Modes

| Failure | What to do |
|---|---|
| `yt-dlp` gets 429 or bot verification | Confirm in browser. If browser also hits CAPTCHA, switch to user-provided local media. |
| `faster-whisper` fails before model download | Inspect proxy variables. In this repo run, bracketed IPv6 in `NO_PROXY` broke `httpx`. |
| TTS package installs but CLI/module entrypoint differs | Check both import path and `.venv/bin/` commands before changing libraries. |
| Chinese narration is shorter than the video | Pad the audio with silence or revise the script/rate. Record which choice you made. |

## Red Flags

Do not claim the workflow is complete if any of these are true:

- you only have a prompt scaffold instead of a final Chinese script
- the TTS output is silence or a placeholder
- the final video was never checked with `ffprobe`
- the report describes a direct YouTube download that never actually worked
- the skill documents steps that were never validated in a real run
