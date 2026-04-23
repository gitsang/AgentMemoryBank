from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRT_PATH = ROOT / "artifacts" / "transcript.en.srt"
ZH_SEGMENTS_PATH = ROOT / "artifacts" / "script.zh.segments.txt"
ASS_PATH = ROOT / "artifacts" / "subtitles.zh-en.ass"


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Bilingual,Noto Sans CJK SC,36,&H00FFFFFF,&H000000FF,&H00101010,&H64000000,0,0,0,0,100,100,0,0,1,2,0,2,80,80,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def parse_timestamp(value: str) -> tuple[int, int, int, int]:
    hh, mm, rest = value.split(":")
    ss, ms = rest.split(",")
    return int(hh), int(mm), int(ss), int(ms)


def to_ass_timestamp(value: str) -> str:
    hh, mm, ss, ms = parse_timestamp(value)
    centiseconds = round(ms / 10)
    if centiseconds == 100:
        centiseconds = 0
        ss += 1
        if ss == 60:
            ss = 0
            mm += 1
            if mm == 60:
                mm = 0
                hh += 1
    return f"{hh}:{mm:02d}:{ss:02d}.{centiseconds:02d}"


def escape_ass_text(value: str) -> str:
    return value.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def parse_srt_blocks(path: Path) -> list[tuple[str, str, str]]:
    blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
    items: list[tuple[str, str, str]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        start_raw, end_raw = lines[1].split(" --> ")
        text = " ".join(lines[2:])
        items.append((start_raw, end_raw, text))
    return items


def main() -> None:
    srt_entries = parse_srt_blocks(SRT_PATH)
    zh_lines = [
        line.rstrip("\n")
        for line in ZH_SEGMENTS_PATH.read_text(encoding="utf-8").splitlines()
    ]
    if len(srt_entries) != len(zh_lines):
        raise SystemExit(
            f"Segment count mismatch: {len(srt_entries)} subtitle blocks vs {len(zh_lines)} Chinese lines"
        )

    lines = [ASS_HEADER]
    for (start_raw, end_raw, en_text), zh_text in zip(
        srt_entries, zh_lines, strict=True
    ):
        start_ass = to_ass_timestamp(start_raw)
        end_ass = to_ass_timestamp(end_raw)
        zh_escaped = escape_ass_text(zh_text)
        en_escaped = escape_ass_text(en_text)
        text = f"{{\\fs40}}{zh_escaped}\\N{{\\fs28}}{en_escaped}"
        lines.append(f"Dialogue: 0,{start_ass},{end_ass},Bilingual,,0,0,0,,{text}")

    ASS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(ASS_PATH)


if __name__ == "__main__":
    main()
