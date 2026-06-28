#!/usr/bin/env python3
"""上传本地图片到 ComfyUI 服务器"""

import sys
import argparse
import requests
from pathlib import Path


def upload_image(server_url: str, image_path: str) -> str:
    """上传图片到 ComfyUI，返回服务器上的文件名"""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")

    url = f"{server_url.rstrip('/')}/upload/image"

    with open(path, "rb") as f:
        files = {"image": (path.name, f, "image/png")}
        data = {"overwrite": "true"}
        response = requests.post(url, files=files, data=data)

    response.raise_for_status()
    result = response.json()

    return result.get("name", path.name)


def main():
    parser = argparse.ArgumentParser(description="上传图片到 ComfyUI")
    parser.add_argument("image", help="本地图片路径")
    parser.add_argument("--server", required=True, help="ComfyUI 服务器地址")

    args = parser.parse_args()

    try:
        filename = upload_image(args.server, args.image)
        print(filename)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
