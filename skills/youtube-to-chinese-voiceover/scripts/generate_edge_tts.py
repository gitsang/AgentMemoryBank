from __future__ import annotations

import argparse
import asyncio
import subprocess
from pathlib import Path

import edge_tts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 edge-tts 生成中文 MP3/WAV。")
    parser.add_argument("--script", type=Path, required=True, help="中文稿路径")
    parser.add_argument("--mp3-out", type=Path, required=True, help="MP3 输出路径")
    parser.add_argument("--wav-out", type=Path, required=True, help="WAV 输出路径")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="edge-tts 音色")
    parser.add_argument("--rate", default="+8%", help="edge-tts 语速")
    return parser.parse_args()


async def synthesize(text: str, voice: str, rate: str, mp3_out: Path) -> None:
    communicator = edge_tts.Communicate(text, voice, rate=rate)
    await communicator.save(str(mp3_out))


def convert_to_wav(mp3_out: Path, wav_out: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_out), str(wav_out)],
        check=True,
    )


def main() -> None:
    args = parse_args()
    text = args.script.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Chinese script is empty")

    args.mp3_out.parent.mkdir(parents=True, exist_ok=True)
    args.wav_out.parent.mkdir(parents=True, exist_ok=True)

    asyncio.run(synthesize(text, args.voice, args.rate, args.mp3_out))
    convert_to_wav(args.mp3_out, args.wav_out)
    print({"mp3": str(args.mp3_out), "wav": str(args.wav_out)})


if __name__ == "__main__":
    main()
