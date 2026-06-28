#!/usr/bin/env python3
"""替换工作流模板中的占位符变量"""

import sys
import argparse
import json
from pathlib import Path


def fill_template(template_path: str, variables: dict) -> dict:
    """读取模板并替换占位符"""
    with open(template_path, "r") as f:
        content = f.read()

    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        content = content.replace(placeholder, str(value))

    return json.loads(content)


def main():
    parser = argparse.ArgumentParser(description="替换工作流模板占位符")
    parser.add_argument("template", help="模板文件路径")
    parser.add_argument("--var", action="append", help="变量 key=value")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    variables = {}
    if args.var:
        for item in args.var:
            key, value = item.split("=", 1)
            variables[key] = value

    try:
        result = fill_template(args.template, variables)
        output = json.dumps(result, indent=2)

        if args.output:
            Path(args.output).write_text(output)
        else:
            print(output)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
