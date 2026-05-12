#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

STALE_PATTERNS = {
    "2分": "公安部令第163号",
    "记2": "公安部令第163号",
    "扣2": "公安部令第163号",
    "二分": "公安部令第163号",
    "两分": "公安部令第163号",
    "60周岁": "公安部令第172号",
    "年满60": "公安部令第172号",
    "60岁": "公安部令第172号",
    "满60": "公安部令第172号",
    "162号": "公安部令第172号",
    "公安部令第162号": "公安部令第172号",
    "139号": "公安部令第172号",
    "公安部令第139号": "公安部令第172号",
    "102号": "公安部令第164号",
    "公安部令第102号": "公安部令第164号",
    "91号": "现行法规源",
    "111号": "现行法规源",
    "123号": "公安部令第164号/第172号",
    "124号": "公安部令第164号",
    "回核发地": "公安部令第172号",
    "核发地车管所": "公安部令第172号",
    "驾驶证核发地": "公安部令第172号",
    "迁回": "公安部令第172号",
    "转入换证": "公安部令第172号",
    "旧规": "current-law manual review",
    "新规": "current-law manual review",
}
STALE_REGEX_PATTERNS = {
    "2分": re.compile(r"(?<![0-9])2分"),
    "记2": re.compile(r"(?<![0-9])记\s*2"),
    "扣2": re.compile(r"(?<![0-9])扣\s*2"),
}
SPECIAL_VEHICLE_TERMS = [
    "A1",
    "A2",
    "A3",
    "A证",
    "B1",
    "B2",
    "B证",
    "D证",
    "E证",
    "F证",
    "大型客车",
    "中型客车",
    "重型牵引挂车",
    "城市公交车",
    "牵引挂车",
    "大型货车",
    "营运客车",
    "旅游客运",
    "公路客运",
    "危化",
    "危险品",
    "危险物品运输车",
    "校车",
    "校车驾驶资格",
]


def _text(question: dict[str, Any]) -> str:
    return f"{question.get('question', '')} {question.get('answer_skill', '')} {' '.join(question.get('options', []))}"


def audit_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for question in questions:
        text = _text(question)
        matches = []
        for pattern in STALE_PATTERNS:
            regex = STALE_REGEX_PATTERNS.get(pattern)
            if (regex and regex.search(text)) or (not regex and pattern in text):
                matches.append(pattern)
        if matches:
            findings.append(
                {
                    "id": question.get("id", ""),
                    "severity": "high",
                    "category": "stale_phrase",
                    "matches": matches,
                    "question": question.get("question", ""),
                    "suggested_source": ", ".join(
                        dict.fromkeys(STALE_PATTERNS[match] for match in matches)
                    ),
                }
            )

        special_matches = [term for term in SPECIAL_VEHICLE_TERMS if term in text]
        if special_matches and question.get("vehicle_scope") == "C1-general":
            findings.append(
                {
                    "id": question.get("id", ""),
                    "severity": "medium",
                    "category": "possible_non_c1_scope",
                    "matches": special_matches,
                    "question": question.get("question", ""),
                    "suggested_source": "special-vehicle source or exclusion review",
                }
            )
    return findings


def validate_topic_sources(
    registry: dict[str, Any], topic_map: dict[str, Any]
) -> list[str]:
    source_ids = {source.get("id") for source in registry.get("sources", [])}
    missing: list[str] = []
    for topic, mapping in topic_map.items():
        primary_source = mapping.get("primary_source")
        if primary_source not in source_ids:
            missing.append(f"{topic}.primary_source: {primary_source}")
        for source_id in mapping.get("secondary_sources", []):
            if source_id not in source_ids:
                missing.append(f"{topic}.secondary_sources: {source_id}")
    return missing


def write_report(findings: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(finding["category"] for finding in findings)
    lines = [
        "# C1 科目一题库过时风险审计",
        "",
        "本报告基于第三方练习题库 `doupoa/DrivingTestSubjectOne` 的规范化结果生成。命中项不是自动判错，而是提示需要用现行法规复核。",
        "",
        "## 摘要",
        "",
        f"- 风险命中总数：{len(findings)}",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"- `{category}`：{count}")
    if not findings:
        lines.extend(["", "未发现配置范围内的高风险关键词。"])
    else:
        lines.extend(["", "## 命中明细", ""])
        for finding in findings:
            lines.extend(
                [
                    f"### {finding['id']}",
                    "",
                    f"- 严重级别：`{finding['severity']}`",
                    f"- 类别：`{finding['category']}`",
                    f"- 命中词：{', '.join(finding['matches'])}",
                    f"- 建议核对来源：{finding['suggested_source']}",
                    f"- 题干：{finding['question']}",
                    "",
                ]
            )
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit normalized C1 科目一 questions for stale-risk patterns."
    )
    parser.add_argument("questions", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    findings = audit_questions(questions)
    write_report(findings, args.output)
    print(f"wrote {len(findings)} stale-risk findings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
