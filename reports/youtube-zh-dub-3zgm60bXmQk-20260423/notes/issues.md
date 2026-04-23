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
