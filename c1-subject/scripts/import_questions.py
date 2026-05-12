#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

SOURCE = "DrivingTestSubjectOne"
SOURCE_URL = "https://github.com/doupoa/DrivingTestSubjectOne"
SOURCE_DATA_URL = (
    "https://raw.githubusercontent.com/doupoa/DrivingTestSubjectOne/main/q.json"
)
SOURCE_LICENSE = "MIT"
ANSWER_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _string(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _answer_text(answer: str, options: list[str]) -> str:
    if len(answer) != 1 or answer not in ANSWER_LETTERS:
        raise ValueError(f"C1 科目一只支持单答案题，发现答案 {answer!r}")
    index = ANSWER_LETTERS.index(answer)
    if index >= len(options):
        raise ValueError(f"答案 {answer!r} 超出选项范围")
    return options[index]


def _question_type(options: list[str]) -> str:
    normalized = [option.strip() for option in options]
    if normalized == ["正确", "错误"]:
        return "true_false"
    return "single_choice"


def _topic(
    question: str, answer_skill: str, chapter_id: str
) -> tuple[str, str, list[str], str]:
    text = f"{question} {answer_skill}"
    tags = [f"chapter:{chapter_id}"] if chapter_id else []
    if any(
        word in text
        for word in ["扣", "记分", "满分", "12分", "9分", "6分", "3分", "1分"]
    ):
        return "law", "points", tags + ["扣分"], "公安部令第163号"
    if any(
        word in text for word in ["驾驶证", "换证", "补证", "实习期", "准驾", "申领"]
    ):
        return "law", "driver-license", tags + ["驾驶证"], "公安部令第172号"
    if any(word in text for word in ["登记", "号牌", "行驶证", "临时号牌", "检验"]):
        return "law", "vehicle-registration", tags + ["登记"], "公安部令第164号"
    if any(word in text for word in ["标志", "标线", "信号灯", "交警", "手势"]):
        return (
            "traffic-signals",
            "signals-signs-markings",
            tags + ["交通信号"],
            "道路交通安全法实施条例",
        )
    if any(
        word in text
        for word in ["高速", "速度", "车距", "超车", "会车", "灯光", "停车", "让行"]
    ):
        return (
            "safe-driving",
            "road-rules",
            tags + ["安全行车"],
            "道路交通安全法实施条例",
        )
    return "unknown", "unknown", tags, ""


def stale_risk(question: str, answer_skill: str) -> str:
    text = f"{question} {answer_skill}"
    if (
        re.search(r"(?<![0-9])2分", text)
        or re.search(r"(?<![0-9])记\s*2", text)
        or re.search(r"(?<![0-9])扣\s*2", text)
    ):
        return "high"
    risky = ["60周岁", "91号", "111号", "123号", "124号", "回核发地"]
    if any(token in text for token in risky):
        return "high"
    if any(token in text for token in ["162号", "旧规", "新规"]):
        return "medium"
    return "low"


def normalize_question(
    raw: dict[str, Any], source_retrieved_at: str | None = None
) -> dict[str, Any]:
    source_id = _string(raw.get("id"))
    subject = _string(raw.get("subject"))
    chapter_id = _string(raw.get("chapterId"))
    question = _string(raw.get("question"))
    answer = _string(raw.get("answer")).upper()
    answer_skill = _string(raw.get("answerSkill"))
    image_url = _string(raw.get("url") or raw.get("coverUrl"))
    options = [
        _string(option)
        for option in (raw.get("itemsDescArray") or [])
        if _string(option)
    ]

    if len(answer) != 1:
        raise ValueError(f"C1 科目一只支持判断题和单选题，发现多答案记录 {source_id}")
    if len(options) < 2:
        raise ValueError(f"题目 {source_id} 缺少选项")

    answer_text = _answer_text(answer, options)
    question_type = _question_type(options)
    topic, subtopic, tags, primary_source = _topic(question, answer_skill, chapter_id)

    return {
        "id": source_id,
        "source": SOURCE,
        "source_id": source_id,
        "source_url": SOURCE_DATA_URL,
        "source_license": SOURCE_LICENSE,
        "source_retrieved_at": source_retrieved_at or date.today().isoformat(),
        "subject": subject,
        "chapter_id": chapter_id,
        "question_type": question_type,
        "question": question,
        "image_url": image_url,
        "options": options,
        "answer": answer,
        "answer_text": answer_text,
        "answer_skill": answer_skill,
        "tags": tags,
        "topic": topic,
        "subtopic": subtopic,
        "vehicle_scope": "C1-general",
        "primary_source": primary_source,
        "article_refs": [],
        "effective_date": None,
        "last_verified": None,
        "stale_risk": stale_risk(question, answer_skill),
        "validation_notes": "Imported from third-party practice bank; verify statutory topics against current regulations.",
    }


def normalize_questions(
    rows: list[dict[str, Any]], source_retrieved_at: str | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    invalid: list[dict[str, str]] = []
    subject_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    chapter_counts: Counter[str] = Counter()
    answer_shape_counts: Counter[str] = Counter()

    for row in rows:
        subject = _string(row.get("subject"))
        subject_counts[subject] += 1
        if subject != "1":
            continue
        answer_shape_counts[str(len(_string(row.get("answer"))))] += 1
        try:
            item = normalize_question(row, source_retrieved_at=source_retrieved_at)
        except ValueError as exc:
            invalid.append({"source_id": _string(row.get("id")), "reason": str(exc)})
            continue
        normalized.append(item)
        type_counts[item["question_type"]] += 1
        chapter_counts[item["chapter_id"]] += 1

    metadata = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "source_data_url": SOURCE_DATA_URL,
        "source_license": SOURCE_LICENSE,
        "source_retrieved_at": source_retrieved_at or date.today().isoformat(),
        "raw_count": len(rows),
        "processed_subject1_count": len(normalized),
        "invalid_subject1_count": len(invalid),
        "subject_counts": dict(sorted(subject_counts.items())),
        "question_type_counts": dict(sorted(type_counts.items())),
        "chapter_counts": dict(sorted(chapter_counts.items())),
        "answer_length_counts": dict(sorted(answer_shape_counts.items())),
        "question_type_policy": "C1 科目一只建模判断题 true_false 和单选题 single_choice。",
    }
    return normalized, invalid, metadata


def write_outputs(
    questions: list[dict[str, Any]],
    invalid: list[dict[str, str]],
    metadata: dict[str, Any],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "questions.json").write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if invalid:
        (output_dir / "invalid-records.json").write_text(
            json.dumps(invalid, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    fields = [
        "id",
        "question_type",
        "question",
        "answer",
        "answer_text",
        "answer_skill",
        "chapter_id",
        "topic",
        "subtopic",
        "stale_risk",
        "tags",
    ]
    with (output_dir / "questions.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(fields + ["options"])
        for question in questions:
            writer.writerow(
                [
                    question.get("id", ""),
                    question.get("question_type", ""),
                    question.get("question", ""),
                    question.get("answer", ""),
                    question.get("answer_text", ""),
                    question.get("answer_skill", ""),
                    question.get("chapter_id", ""),
                    question.get("topic", ""),
                    question.get("subtopic", ""),
                    question.get("stale_risk", ""),
                    ";".join(question.get("tags", [])),
                    " | ".join(question.get("options", [])),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize DrivingTestSubjectOne C1 科目一 questions."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--retrieved-at", default=date.today().isoformat())
    args = parser.parse_args()

    rows = json.loads(args.input.read_text(encoding="utf-8"))
    normalized, invalid, metadata = normalize_questions(
        rows, source_retrieved_at=args.retrieved_at
    )
    write_outputs(normalized, invalid, metadata, args.output_dir)
    print(f"wrote {len(normalized)} C1 subject-one questions to {args.output_dir}")
    if invalid:
        print(f"flagged {len(invalid)} invalid records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
