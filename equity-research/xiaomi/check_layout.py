#!/usr/bin/env python3
"""检查生成的 HTML 是否有布局问题（表格横向溢出、代码块溢出、页码高度）。

用无头 Chrome 加载页面、跑一段测量脚本，再把结果读回来。
不依赖任何 Python 第三方包（只用标准库 + chromium）。

用法：
    python3 check_layout.py [html] [--width 1200]
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

PROBE = """
<script>
window.addEventListener('load', function(){
  var out = [];
  var scrollers = document.querySelectorAll('.table-scroll');
  scrollers.forEach(function(w, i){
    var t = w.querySelector('table');
    if (!t) return;
    var over = t.scrollWidth - w.clientWidth;
    var cols = t.querySelectorAll('thead th').length || (t.rows[0] ? t.rows[0].cells.length : 0);
    if (over > 2) {
      var heads = Array.prototype.map.call(
        t.querySelectorAll('thead th'), function(x){ return x.textContent.trim(); }
      ).join('|');
      out.push('TABLE_OVERFLOW idx=' + i + ' over=' + over + 'px cols=' + cols + ' heads=' + heads);
    }
  });
  out.push('TABLES_TOTAL=' + scrollers.length);
  var pres = document.querySelectorAll('pre');
  pres.forEach(function(p, i){
    var over = p.scrollWidth - p.clientWidth;
    if (over > 2) out.push('PRE_OVERFLOW idx=' + i + ' over=' + over + 'px');
  });
  out.push('PRE_TOTAL=' + pres.length);
  out.push('PAGE_HEIGHT=' + document.documentElement.scrollHeight);
  out.push('BODY_WIDTH=' + document.body.clientWidth);
  document.title = 'PROBE::' + out.join(' ;; ');
});
</script>
"""


def chrome_probe(html_path: str, width: int) -> str:
    html = open(html_path, encoding="utf-8").read()
    probe_file = os.path.join(tempfile.gettempdir(), "layout_probe.html")
    with open(probe_file, "w", encoding="utf-8") as f:
        f.write(html.replace("</body>", PROBE + "</body>"))
    cmd = [
        "google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
        "--virtual-time-budget=5000", f"--window-size={width},1000",
        "--dump-dom", f"file://{probe_file}",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except FileNotFoundError:
        sys.exit("错误：未找到 google-chrome。")
    m = re.search(r"PROBE::(.*?)</title>", res.stdout, re.S)
    if not m:
        sys.exit("错误：探针未返回结果（页面可能未加载完成）。")
    return m.group(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", nargs="?", default="teaching-slice.html")
    ap.add_argument("--width", type=int, default=1200)
    a = ap.parse_args()
    if not os.path.exists(a.html):
        sys.exit(f"错误：找不到 {a.html}")

    raw = chrome_probe(a.html, a.width)
    items = [x.strip() for x in raw.split(";;") if x.strip()]

    problems = [x for x in items if "OVERFLOW" in x]
    info = {k: v for k, v in (x.split("=", 1) for x in items if "=" in x and "OVERFLOW" not in x)}

    print(f"视口宽度 {a.width}px ｜ 页面高度 {info.get('PAGE_HEIGHT', '?')}px")
    print(f"表格 {info.get('TABLES_TOTAL', '?')} 张 ｜ 代码块 {info.get('PRE_TOTAL', '?')} 个")
    print()
    if problems:
        print(f"⚠ 发现 {len(problems)} 处横向溢出：")
        for p in problems:
            print("   " + p)
        sys.exit(1)
    print("✅ 无横向溢出")


if __name__ == "__main__":
    main()
