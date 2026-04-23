from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "artifacts" / "script.zh.txt"
MP3_PATH = ROOT / "artifacts" / "narration.zh.mp3"
WAV_PATH = ROOT / "artifacts" / "narration.zh.wav"
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+8%"


async def synthesize() -> None:
    text = SCRIPT_PATH.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Chinese script is empty")

    communicator = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicator.save(str(MP3_PATH))


def convert_to_wav() -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(MP3_PATH),
            str(WAV_PATH),
        ],
        check=True,
    )


def main() -> None:
    asyncio.run(synthesize())
    convert_to_wav()
    print(WAV_PATH)


if __name__ == "__main__":
    main()
