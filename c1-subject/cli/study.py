#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Iterable


def load_questions(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def search_questions(questions: Iterable[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    needle = query.casefold()
    result = []
    for question in questions:
        haystack = " ".join([
            str(question.get("question", "")),
            " ".join(question.get("options", [])),
            str(question.get("answer_text", "")),
            str(question.get("answer_skill", "")),
            " ".join(question.get("tags", [])),
            str(question.get("topic", "")),
            str(question.get("subtopic", "")),
        ]).casefold()
        if needle in haystack:
            result.append(question)
    return result


def filter_questions(questions: Iterable[dict[str, Any]], tag: str | None = None, topic: str | None = None) -> list[dict[str, Any]]:
    result = []
    for question in questions:
        if tag and tag not in question.get("tags", []):
            continue
        if topic and topic != question.get("topic") and topic != question.get("subtopic"):
            continue
        result.append(question)
    return result


def _load_review(review_path: Path) -> list[dict[str, Any]]:
    if not review_path.exists():
        return []
    return json.loads(review_path.read_text(encoding="utf-8"))


def record_wrong_answer(review_path: Path, question: dict[str, Any], given_answer: str) -> None:
    review_path.parent.mkdir(parents=True, exist_ok=True)
    rows = _load_review(review_path)
    by_id = {row.get("id"): row for row in rows}
    entry = dict(question)
    entry["last_given_answer"] = given_answer
    by_id[question.get("id")] = entry
    review_path.write_text(json.dumps(list(by_id.values()), ensure_ascii=False, indent=2), encoding="utf-8")


def _ask(question: dict[str, Any]) -> str:
    print(f"\n[{question.get('id')}] {question.get('question')}")
    for index, option in enumerate(question.get("options", [])):
        print(f"  {chr(65 + index)}. {option}")
    return input("Your answer: ").strip().upper()


def run_quiz(questions: list[dict[str, Any]], review_path: Path, count: int | None = None) -> int:
    selected = questions[: count or len(questions)]
    correct = 0
    for question in selected:
        answer = _ask(question)
        expected = str(question.get("answer", "")).upper()
        if answer == expected:
            print("✓ Correct")
            correct += 1
        else:
            print(f"✗ Wrong. Correct: {expected} {question.get('answer_text', '')}")
            record_wrong_answer(review_path, question, answer)
        if question.get("answer_skill"):
            print(f"解析：{question['answer_skill']}")
    print(f"\nScore: {correct}/{len(selected)}")
    return correct


def main() -> int:
    parser = argparse.ArgumentParser(description="Local C1 科目一 practice tool.")
    parser.add_argument("command", choices=["quiz", "random", "review", "search"])
    parser.add_argument("file", type=Path)
    parser.add_argument("--count", type=int)
    parser.add_argument("--tag")
    parser.add_argument("--topic")
    parser.add_argument("--query")
    parser.add_argument("--review-file", type=Path, default=Path(".study-review.json"))
    args = parser.parse_args()

    questions = load_questions(args.file)
    questions = filter_questions(questions, tag=args.tag, topic=args.topic)

    if args.command == "search":
        if not args.query:
            parser.error("search requires --query")
        for question in search_questions(questions, args.query):
            print(f"{question.get('id')}	{question.get('question')}")
        return 0

    if args.command == "random":
        random.shuffle(questions)
        return 0 if run_quiz(questions, args.review_file, args.count) >= 0 else 1

    if args.command == "review":
        review_questions = _load_review(args.review_file)
        if not review_questions:
            print("No review questions yet.")
            return 0
        return 0 if run_quiz(review_questions, args.review_file, args.count) >= 0 else 1

    return 0 if run_quiz(questions, args.review_file, args.count) >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
