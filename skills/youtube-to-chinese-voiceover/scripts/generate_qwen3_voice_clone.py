from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 Qwen3-TTS 与参考音频生成中文音色克隆语音。"
    )
    parser.add_argument("--script", type=Path, required=True, help="中文稿路径")
    parser.add_argument(
        "--reference-audio", type=Path, required=True, help="参考音色音频路径"
    )
    parser.add_argument("--mp3-out", type=Path, required=True, help="MP3 输出路径")
    parser.add_argument("--wav-out", type=Path, required=True, help="WAV 输出路径")
    parser.add_argument(
        "--qwen-tts-bin",
        default="qwen-tts",
        help="Qwen3-TTS CLI 可执行文件名或路径",
    )
    parser.add_argument(
        "--sample-rate", type=int, default=24000, help="输出 wav 采样率"
    )
    return parser.parse_args()


def synthesize(
    script: Path, reference_audio: Path, mp3_out: Path, qwen_tts_bin: str
) -> None:
    text = script.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Chinese script is empty")

    subprocess.run(
        [
            qwen_tts_bin,
            "synthesize",
            "--text",
            text,
            "--prompt-audio",
            str(reference_audio),
            "--output",
            str(mp3_out),
        ],
        check=True,
    )


def convert_to_wav(mp3_out: Path, wav_out: Path, sample_rate: int) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_out),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-c:a",
            "pcm_s16le",
            str(wav_out),
        ],
        check=True,
    )


def main() -> None:
    args = parse_args()
    args.mp3_out.parent.mkdir(parents=True, exist_ok=True)
    args.wav_out.parent.mkdir(parents=True, exist_ok=True)

    synthesize(args.script, args.reference_audio, args.mp3_out, args.qwen_tts_bin)
    convert_to_wav(args.mp3_out, args.wav_out, args.sample_rate)
    print(
        {
            "reference_audio": str(args.reference_audio),
            "mp3": str(args.mp3_out),
            "wav": str(args.wav_out),
        }
    )


if __name__ == "__main__":
    main()
