from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "artifacts" / "transcript.en.txt"
DST = ROOT / "artifacts" / "script.zh.txt"


PROMPT = """把下面英文视频字幕改写成适合中文视频解说的口播稿。要求：
1. 保留原意
2. 使用自然中文口语
3. 句子简短，适合配音
4. 不要书面腔
5. 输出纯中文稿，不要解释
"""


def main() -> None:
    transcript = SRC.read_text(encoding="utf-8").strip()
    output = (
        "# Manual step required\n\n"
        "Use the following prompt with your preferred LLM, then replace this file with the final Chinese script.\n\n"
        f"{PROMPT}\n\n=== TRANSCRIPT START ===\n{transcript}\n=== TRANSCRIPT END ===\n"
    )
    DST.write_text(output, encoding="utf-8")
    print(DST)


if __name__ == "__main__":
    main()
