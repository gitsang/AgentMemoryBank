from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator


ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / ".translation-cache-zh.json"

PLACEHOLDER = "__KEEP_{:04d}__"

SKIP_DIRS = {".git", ".translation-venv"}

PROTECTED_FRONT_MATTER_KEYS = {
    "obsidianUIMode",
    "cssclasses",
    "tags",
}

GLOSSARY = {
    "DnD 5e SRD in Markdown": "Markdown 格式的 DnD 5e SRD",
    "Source: SRD / Basic Rules": "来源：SRD / 基础规则",
    "SRD / Basic Rules": "SRD / 基础规则",
    "Ability Scores": "属性值",
    "Ability Score": "属性值",
    "Casting time": "施法时间",
    "Casting Time": "施法时间",
    "Components": "法术成分",
    "Duration": "持续时间",
    "Range": "距离",
    "Classes": "职业",
    "Type": "类型",
    "Size": "体型",
    "Speed": "速度",
    "Traits": "特质",
    "At Higher Levels.": "升环施法。",
    "See also": "另见",
    "Source": "来源",
    "Action": "动作",
    "Bonus Action": "附赠动作",
    "Reaction": "反应",
    "Free": "自由",
    "Instantaneous": "瞬发",
    "Medium": "中型",
    "Small": "小型",
    "Large": "大型",
    "Tiny": "超小型",
    "Huge": "巨型",
    "Gargantuan": "超巨型",
    "race": "种族",
    "spell": "法术",
    "item": "物品",
    "feat": "专长",
    "background": "背景",
    "class": "职业",
    "Strength": "力量",
    "Dexterity": "敏捷",
    "Constitution": "体质",
    "Intelligence": "智力",
    "Wisdom": "感知",
    "Charisma": "魅力",
    "Athletics": "运动",
    "Acrobatics": "体操",
    "History": "历史",
    "Common": "通用语",
    "Dwarvish": "矮人语",
}


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def should_translate(text: str) -> bool:
    if not text.strip():
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    stripped = text.strip()
    if stripped.startswith(("http://", "https://")):
        return False
    if (
        re.fullmatch(r"[A-Za-z0-9_./#%:+\-\s]+", stripped)
        and "/" in stripped
        and len(stripped.split()) <= 2
    ):
        return False
    return True


def protect(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def keep(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return PLACEHOLDER.format(len(protected) - 1)

    patterns = [
        r"`[^`]*`",
        r"https?://[^\s)]+",
        r"\[[^\]]*\]\([^)]*\)",
        r"\[\[[^\]]+\]\]",
        r"\{#[^}]+\}",
        r"\b\d+d\d+(?:\s*[+\-]\s*\d+)?\b",
        r"\b\d+(?:\.\d+)?\s*(?:ft\.|feet|mile|miles|lb\.|pounds|gp|sp|cp|pp|d(?:ay|ays)?|hour|hours|minute|minutes)\b",
        r"\b[A-Z]?[VSMD]\b",
    ]
    for pattern in patterns:
        text = re.sub(pattern, keep, text)
    return text, protected


def restore(text: str, protected: list[str]) -> str:
    for idx, value in enumerate(protected):
        text = text.replace(PLACEHOLDER.format(idx), value)
    return text


def translate_text(
    text: str, translator: GoogleTranslator, cache: dict[str, str]
) -> str:
    if not should_translate(text):
        return text
    if text in GLOSSARY:
        return GLOSSARY[text]
    if text in cache:
        return cache[text]

    protected_text, protected = protect(text)
    stripped = protected_text.strip()
    if not should_translate(stripped):
        return text

    prefix = protected_text[: len(protected_text) - len(protected_text.lstrip())]
    suffix = protected_text[len(protected_text.rstrip()) :]
    body = protected_text.strip()

    if body in GLOSSARY:
        translated = GLOSSARY[body]
    else:
        for attempt in range(5):
            try:
                translated = translator.translate(body)
                break
            except Exception as exc:  # noqa: BLE001 - retry transient translation errors
                if attempt == 4:
                    raise RuntimeError(f"failed to translate: {text!r}") from exc
                time.sleep(1.5 * (attempt + 1))
    translated = restore(prefix + translated + suffix, protected)
    translated = translated.replace("＃", "#")
    cache[text] = translated
    return translated


def translate_link_text(
    segment: str, translator: GoogleTranslator, cache: dict[str, str]
) -> str:
    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2)
        return f"[{translate_text(label, translator, cache)}]({target})"

    return re.sub(r"\[([^\]]+)\]\(([^)]*)\)", replace, segment)


def translate_inline(
    line: str, translator: GoogleTranslator, cache: dict[str, str]
) -> str:
    if not should_translate(line):
        return line

    newline = "\n" if line.endswith("\n") else ""
    core = line[:-1] if newline else line

    # Preserve Markdown table separators and pure front matter/list metadata lines.
    if re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", core):
        return line

    heading = re.match(r"^(\s{0,3}#{1,6}\s+)(.*)$", core)
    if heading:
        return (
            heading.group(1)
            + translate_link_text(
                translate_text(heading.group(2), translator, cache), translator, cache
            )
            + newline
        )

    source = re.match(r"^(\s*[*_]Source:\s*)(.*?)([*_]*\s*)$", core)
    if source:
        return (
            source.group(1).replace("Source", "来源")
            + translate_text(source.group(2), translator, cache)
            + source.group(3)
            + newline
        )

    bold_field = re.match(r"^(\s*[-*]?\s*\*\*)([^*]+?)(\*\*\s*:?\s*)(.*)$", core)
    if bold_field:
        field = translate_text(bold_field.group(2).rstrip(":"), translator, cache)
        rest = translate_link_text(
            translate_text(bold_field.group(4), translator, cache), translator, cache
        )
        return f"{bold_field.group(1)}{field}{bold_field.group(3)}{rest}{newline}"

    table_line = core.strip().startswith("|") and "|" in core.strip()[1:]
    if table_line:
        cells = core.split("|")
        translated_cells = [
            translate_link_text(
                translate_text(cell, translator, cache), translator, cache
            )
            for cell in cells
        ]
        return "|".join(translated_cells) + newline

    list_item = re.match(r"^(\s*(?:[-*+] |\d+\. ))(.*)$", core)
    if list_item:
        return (
            list_item.group(1)
            + translate_link_text(
                translate_text(list_item.group(2), translator, cache), translator, cache
            )
            + newline
        )

    return (
        translate_link_text(translate_text(core, translator, cache), translator, cache)
        + newline
    )


def translate_front_matter_line(
    line: str, in_alias_list: bool, translator: GoogleTranslator, cache: dict[str, str]
) -> tuple[str, bool]:
    stripped = line.strip()
    if not stripped:
        return line, in_alias_list
    key_match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$", line)
    if key_match:
        key = key_match.group(1)
        value = key_match.group(2)
        if key in PROTECTED_FRONT_MATTER_KEYS:
            return line, key == "aliases" and not value.strip()
        if key == "aliases":
            translated = re.sub(
                r'"([^"]+)"',
                lambda m: '"' + translate_text(m.group(1), translator, cache) + '"',
                value,
            )
            return f"{key}:{translated}", not value.strip()
        return line, False
    if in_alias_list and stripped.startswith("-"):
        return re.sub(
            r'"([^"]+)"',
            lambda m: '"' + translate_text(m.group(1), translator, cache) + '"',
            line,
        ), True
    return line, in_alias_list


def translate_file(
    path: Path, translator: GoogleTranslator, cache: dict[str, str]
) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    out: list[str] = []
    in_code = False
    in_front = False
    in_alias_list = False

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx == 0 and stripped == "---":
            in_front = True
            out.append(line)
            continue
        if in_front:
            if stripped == "---":
                in_front = False
                in_alias_list = False
                out.append(line)
                continue
            translated_line, in_alias_list = translate_front_matter_line(
                line, in_alias_list, translator, cache
            )
            out.append(translated_line)
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or stripped.startswith("<!--"):
            out.append(line)
            continue
        out.append(translate_inline(line, translator, cache))

    translated = "".join(out)
    if translated != original:
        path.write_text(translated, encoding="utf-8")
        return True
    return False


def markdown_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    translator = GoogleTranslator(source="en", target="zh-CN")
    cache = load_cache()
    files = markdown_files()
    if limit:
        files = files[:limit]

    changed = 0
    for idx, path in enumerate(files, start=1):
        rel = path.relative_to(ROOT)
        if translate_file(path, translator, cache):
            changed += 1
        if idx % 25 == 0:
            save_cache(cache)
        print(f"[{idx}/{len(files)}] {rel}")
    save_cache(cache)
    print(f"changed={changed} cache_entries={len(cache)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
