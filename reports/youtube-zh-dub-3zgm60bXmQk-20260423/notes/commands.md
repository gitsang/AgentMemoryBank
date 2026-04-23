# Command Log

## Environment

- `python3 --version` → `Python 3.13.5`
- `uv venv reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv` → created a venv using `CPython 3.12.12`
- `ffmpeg` and `ffprobe` available in `/usr/bin`

## Commands Run

1. `mkdir -p reports/youtube-zh-dub-3zgm60bXmQk-20260423/{source,artifacts,notes,scripts}`
2. `uv venv reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv`
3. `uv pip install --python reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python yt-dlp`
4. `UV_HTTP_TIMEOUT=240 uv pip install --python reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python faster-whisper`
5. `ffprobe -v quiet -print_format json -show_format -show_streams source/'What are AI agents？ [3zgm60bXmQk].webm' > source/video-info.json`
6. `ffmpeg -y -i source/'What are AI agents？ [3zgm60bXmQk].webm' -c:v copy -c:a aac source/video.mp4`
7. `ffmpeg -y -i source/'What are AI agents？ [3zgm60bXmQk].webm' -vn -q:a 0 -map a source/audio.mp3`
8. `NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 HF_HOME=... .venv/bin/python scripts/transcribe.py`
9. `uv pip install --python reports/youtube-zh-dub-3zgm60bXmQk-20260423/.venv/bin/python edge-tts`
10. `NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 .venv/bin/python scripts/generate_tts.py`
11. `ffmpeg -y -i source/video.mp4 -i artifacts/narration.zh.wav -filter_complex "[1:a]apad[a]" -map 0:v:0 -map "[a]" -c:v copy -c:a aac -shortest artifacts/final-voiceover.mp4`
12. `ffprobe -v error -show_entries stream=index,codec_type,codec_name artifacts/final-voiceover.mp4`
