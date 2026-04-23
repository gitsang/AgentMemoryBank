from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

import edge_tts
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRT_PATH = ROOT / "artifacts" / "transcript.en.srt"
ZH_SEGMENTS_PATH = ROOT / "artifacts" / "script.zh.segments.txt"
VIDEO_PATH = ROOT / "source" / "video.mp4"
ALIGNED_WAV_PATH = ROOT / "artifacts" / "narration.zh.aligned.wav"
ALIGNMENT_REPORT_PATH = ROOT / "artifacts" / "narration.zh.aligned.json"
SEGMENT_DIR = ROOT / "artifacts" / "aligned-segments"
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"
SAMPLE_RATE = 24000
MAX_SPEEDUP = 1.5


@dataclass
class SubtitleSegment:
    index: int
    start: float
    end: float
    text_en: str
    text_zh: str


def parse_timestamp(value: str) -> float:
    hh, mm, rest = value.split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def parse_srt(path: Path) -> list[tuple[int, float, float, str]]:
    blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
    parsed: list[tuple[int, float, float, str]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        index = int(lines[0])
        start_raw, end_raw = lines[1].split(" --> ")
        text = " ".join(lines[2:])
        parsed.append(
            (index, parse_timestamp(start_raw), parse_timestamp(end_raw), text)
        )
    return parsed


def read_segments() -> list[SubtitleSegment]:
    en_segments = parse_srt(SRT_PATH)
    zh_lines = [
        line.rstrip("\n")
        for line in ZH_SEGMENTS_PATH.read_text(encoding="utf-8").splitlines()
    ]
    if len(zh_lines) != len(en_segments):
        raise SystemExit(
            f"Segment count mismatch: {len(en_segments)} srt blocks vs {len(zh_lines)} zh lines"
        )

    return [
        SubtitleSegment(
            index=index, start=start, end=end, text_en=text_en, text_zh=text_zh
        )
        for (index, start, end, text_en), text_zh in zip(
            en_segments, zh_lines, strict=True
        )
    ]


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


async def synthesize_segment(text: str, output_path: Path) -> None:
    communicator = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicator.save(str(output_path))


def mp3_to_wav(src: Path, dst: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(dst),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def read_wav_as_float(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    if channels != 1 or sample_width != 2 or frame_rate != SAMPLE_RATE:
        raise SystemExit(f"Unexpected WAV format for {path}")

    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    return samples


def write_wav_from_float(path: Path, samples: np.ndarray) -> None:
    clipped = np.clip(samples, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())


def build_atempo_filter(speedup: float) -> str:
    factors: list[float] = []
    remaining = speedup
    while remaining > 2.0:
        factors.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        factors.append(0.5)
        remaining /= 0.5
    factors.append(remaining)
    return ",".join(f"atempo={factor:.6f}" for factor in factors)


def speed_up_wav(src: Path, dst: Path, speedup: float) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-filter:a",
            build_atempo_filter(speedup),
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(dst),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> None:
    segments = read_segments()
    SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    video_duration = ffprobe_duration(VIDEO_PATH)
    total_samples = int(round(video_duration * SAMPLE_RATE))
    final_audio = np.zeros(total_samples, dtype=np.float32)
    report: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="aligned-dub-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        for idx, segment in enumerate(segments):
            start_sample = int(round(segment.start * SAMPLE_RATE))
            next_start = (
                segments[idx + 1].start if idx + 1 < len(segments) else video_duration
            )
            slot_duration = max(0.1, next_start - segment.start)
            slot_samples = int(round(slot_duration * SAMPLE_RATE))

            mp3_path = SEGMENT_DIR / f"segment-{segment.index:03d}.mp3"
            wav_path = SEGMENT_DIR / f"segment-{segment.index:03d}.wav"

            if not mp3_path.exists():
                asyncio.run(synthesize_segment(segment.text_zh, mp3_path))
            mp3_to_wav(mp3_path, wav_path)
            samples = read_wav_as_float(wav_path)
            original_samples = len(samples)
            speedup_applied = 1.0

            if len(samples) > slot_samples:
                requested_speedup = len(samples) / slot_samples
                speedup_applied = min(requested_speedup, MAX_SPEEDUP)
                sped_wav = temp_dir / f"segment-{segment.index:03d}-sped.wav"
                speed_up_wav(wav_path, sped_wav, speedup_applied)
                samples = read_wav_as_float(sped_wav)

            if len(samples) > slot_samples:
                samples = samples[:slot_samples]

            end_sample = min(total_samples, start_sample + len(samples))
            valid_samples = end_sample - start_sample
            if valid_samples > 0:
                final_audio[start_sample:end_sample] += samples[:valid_samples]

            report.append(
                {
                    "index": segment.index,
                    "start": segment.start,
                    "end": segment.end,
                    "slot_duration": slot_duration,
                    "text_en": segment.text_en,
                    "text_zh": segment.text_zh,
                    "generated_duration": round(original_samples / SAMPLE_RATE, 3),
                    "placed_duration": round(valid_samples / SAMPLE_RATE, 3),
                    "speedup_applied": round(speedup_applied, 3),
                    "truncated": original_samples > valid_samples,
                }
            )

    write_wav_from_float(ALIGNED_WAV_PATH, final_audio)
    ALIGNMENT_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {"segments": len(report), "output": str(ALIGNED_WAV_PATH)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
