from __future__ import annotations

import argparse
from pathlib import Path


CONTINUOUS_PROMPT = """把下面英文视频字幕改写成适合中文视频解说的口播稿。要求：
1. 保留原意
2. 使用自然中文口语
3. 句子简短，适合配音
4. 不要书面腔
5. 输出纯中文稿，不要解释
"""

SEGMENT_PROMPT = """把下面英文字幕逐条改写成中文配音稿。要求：
1. 每个字幕块对应一行中文
2. 保留原意，避免逐词硬译
3. 优先简洁、自然、适合配音
4. 不要输出编号、解释或空行
5. 最终输出的中文行数必须和英文字幕块数量一致
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成中文改写用的 prompt scaffold。")
    parser.add_argument(
        "--transcript", type=Path, required=True, help="英文文本输入路径"
    )
    parser.add_argument("--output", type=Path, required=True, help="scaffold 输出路径")
    parser.add_argument(
        "--mode",
        choices=["continuous", "segments"],
        default="continuous",
        help="continuous=整段中文稿；segments=逐段中文稿",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transcript = args.transcript.read_text(encoding="utf-8").strip()
    prompt = CONTINUOUS_PROMPT if args.mode == "continuous" else SEGMENT_PROMPT

    output = (
        "# Manual step required\n\n"
        "请将下面 prompt 交给你选定的 LLM，然后用最终中文稿覆盖本文件。\n\n"
        f"{prompt}\n\n=== TRANSCRIPT START ===\n{transcript}\n=== TRANSCRIPT END ===\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
