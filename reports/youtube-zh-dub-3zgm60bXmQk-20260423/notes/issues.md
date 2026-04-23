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
