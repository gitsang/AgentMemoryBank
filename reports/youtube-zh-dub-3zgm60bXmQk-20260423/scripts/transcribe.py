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
        "\n".join(
            segment.text.strip() for segment in segment_list if segment.text.strip()
        )
        + "\n",
        encoding="utf-8",
    )

    with SRT_PATH.open("w", encoding="utf-8") as handle:
        output_index = 1
        for segment in segment_list:
            text = segment.text.strip()
            if not text:
                continue
            handle.write(f"{output_index}\n")
            handle.write(f"{format_ts(segment.start)} --> {format_ts(segment.end)}\n")
            handle.write(f"{text}\n\n")
            output_index += 1

    print(
        {
            "language": info.language,
            "duration": info.duration,
            "segments": len(segment_list),
        }
    )


if __name__ == "__main__":
    main()
