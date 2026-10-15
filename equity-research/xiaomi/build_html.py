#!/usr/bin/env python3
"""把教学切片的 Markdown 构建成可独立打开的 HTML。

设计语言复用 books/the-little-book-of-common-sense-investing/build_html.py：
同一套纸感配色、深色模式变量、CJK 字体栈与表格样式，保持仓库观感一致。

用法：
    python3 build_html.py [in.md] [out.html]

依赖：pandoc（用于 Markdown → HTML 片段）。不依赖任何 Python 第三方包。
"""
import html as html_mod
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IN = os.path.join(HERE, "teaching-slice-20261015.md")
DEFAULT_OUT = os.path.join(HERE, "teaching-slice.html")

CSS = """
:root {
  --bg: #f7f5f0;
  --paper: #fffdf8;
  --ink: #23201c;
  --muted: #6d6558;
  --rule: #ded6c8;
  --accent: #7a5c2e;
  --quote-bg: #f2ede3;
  --aside-bg: #f0ece2;
  --code-bg: #1f1d1a;
  --code-ink: #e9e3d6;
  --maxw: 54rem;
  --cjk: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun",
    ui-serif, Georgia, serif;
  --sans: "Noto Sans CJK SC", ui-sans-serif, system-ui, -apple-system, sans-serif;
  --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181a; --paper: #1e2023; --ink: #e6e2da; --muted: #9c958a;
    --rule: #33363a; --accent: #cbb083; --quote-bg: #24262a; --aside-bg: #24262a;
    --code-bg: #131416; --code-ink: #ddd7ca;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 400 17px/1.75 Georgia, "Times New Roman", var(--cjk);
}
.wrap { max-width: var(--maxw); margin: 0 auto; padding: 2.5rem 1.25rem 7rem; }

header.doc { padding: 3rem 0 2rem; border-bottom: 2px solid var(--rule); }
header.doc .kicker {
  font: 600 .7rem/1 var(--sans); letter-spacing: .18em; text-transform: uppercase;
  color: var(--accent); margin: 0 0 1rem;
}
header.doc h1 { font-size: clamp(1.6rem, 4.5vw, 2.3rem); line-height: 1.25; margin: 0 0 .8rem; }
header.doc .sub { color: var(--muted); font-size: .95rem; margin: 0 0 .35rem; }
header.doc .sub:last-child { margin-bottom: 0; }

nav.toc { margin: 2.2rem 0 3rem; padding: 1.4rem 1.7rem; background: var(--paper);
  border: 1px solid var(--rule); border-radius: .5rem; }
nav.toc h2 { font: 600 .72rem/1 var(--sans); letter-spacing: .16em; text-transform: uppercase;
  color: var(--accent); margin: 0 0 1rem; }
nav.toc ol { margin: 0; padding: 0; list-style: none; counter-reset: toc; }
nav.toc > ol > li { counter-increment: toc; margin: .5rem 0; }
nav.toc > ol > li > a::before {
  content: counter(toc); display: inline-block; min-width: 1.6rem;
  font: 600 .72rem/1 var(--sans); color: var(--accent); vertical-align: .1em;
}
nav.toc a { color: var(--ink); text-decoration: none; border-bottom: 1px solid transparent; }
nav.toc a:hover { border-bottom-color: var(--accent); }
nav.toc ol ol { margin: .3rem 0 .5rem 1.7rem; }
nav.toc ol ol li { margin: .22rem 0; }
nav.toc ol ol a { color: var(--muted); font-size: .92rem; }

section { scroll-margin-top: 1.5rem; }
h2 { font-size: clamp(1.3rem, 3.2vw, 1.65rem); line-height: 1.3;
  margin: 3.5rem 0 .9rem; padding-top: 1.5rem; border-top: 2px solid var(--rule); }
h2:first-of-type { margin-top: 1rem; }
h3 { font-size: 1.1rem; line-height: 1.4; margin: 2.2rem 0 .7rem; color: var(--accent); }
h4 { font-size: 1rem; margin: 1.6rem 0 .6rem; }

p { margin: 0 0 1.05rem; text-wrap: pretty; }
ul, ol { margin: 1rem 0 1.3rem; padding-left: 1.6rem; }
li { margin: .45rem 0; }
li > ul, li > ol { margin: .4rem 0 .5rem; }

blockquote {
  margin: 1.6rem 0; padding: 1.1rem 1.4rem; background: var(--quote-bg);
  border-left: 3px solid var(--accent); border-radius: 0 .35rem .35rem 0;
}
blockquote p { margin: 0 0 .75rem; }
blockquote p:last-child { margin-bottom: 0; }
blockquote strong { color: var(--accent); }

pre {
  margin: 1.4rem 0; padding: 1rem 1.15rem; background: var(--code-bg); color: var(--code-ink);
  border-radius: .45rem; overflow-x: auto;
  font: 400 .78rem/1.6 var(--mono); -webkit-overflow-scrolling: touch;
}
pre code { background: none; padding: 0; color: inherit; font-size: inherit; border: 0; }
code {
  font: 400 .86em/1.4 var(--mono); background: var(--aside-bg);
  padding: .12em .38em; border-radius: .25rem; border: 1px solid var(--rule);
}

.table-scroll { margin: 1.5rem 0; overflow-x: auto; -webkit-overflow-scrolling: touch;
  border: 1px solid var(--rule); border-radius: .45rem; background: var(--paper); }
table { border-collapse: collapse; width: 100%; table-layout: auto;
  font: 400 .82rem/1.5 var(--sans); }
th, td { padding: .5rem .72rem; border-bottom: 1px solid var(--rule); text-align: left;
  vertical-align: top; overflow-wrap: break-word; hyphens: none; text-wrap: pretty; }
th { background: var(--aside-bg); font-weight: 700; font-size: .78rem;
  white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
tbody tr:hover td { background: color-mix(in srgb, var(--accent) 5%, transparent); }
/* 代码标识（如 hk01810）不拆开换行 */
td code, th code { white-space: nowrap; }
/* 表内强调不换行，避免「**27.08 HKD**」被拆成两行 */
td strong { white-space: nowrap; }
/* 宽表（>=7 列）：字号与内边距收紧，表头允许换行 */
table.wide { font-size: .74rem; }
table.wide th, table.wide td { padding: .42rem .5rem; }
table.wide th { white-space: normal; }

hr { border: 0; border-top: 1px solid var(--rule); margin: 3rem 0; }

a { color: var(--accent); text-underline-offset: .18em; }
strong { font-weight: 700; }

.top-btn { position: fixed; right: 1rem; bottom: 1rem; z-index: 20;
  width: 2.5rem; height: 2.5rem; display: grid; place-items: center;
  background: var(--paper); color: var(--accent); border: 1px solid var(--rule);
  border-radius: 50%; text-decoration: none; font-size: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,.12); }
.top-btn:hover { color: var(--ink); }

footer.doc { margin-top: 4.5rem; padding-top: 1.5rem; border-top: 1px solid var(--rule);
  font-size: .82rem; line-height: 1.7; color: var(--muted); text-align: center; }

@media (max-width: 640px) {
  body { font-size: 16px; }
  .wrap { padding: 1.5rem .9rem 6rem; }
  th, td { padding: .45rem .6rem; font-size: .78rem; }
}
@media print {
  :root { --bg: #fff; --paper: #fff; --ink: #000; --rule: #bbb; --muted: #444; }
  .top-btn { display: none; }
  pre { background: #f4f4f4; color: #000; border: 1px solid #bbb; }
  h2 { break-before: page; }
  .table-scroll { overflow: visible; }
  table { font-size: 9pt; }
}
"""


def md_to_fragment(md_path: str) -> str:
    """用 pandoc 转换 Markdown → HTML 片段。"""
    try:
        out = subprocess.run(
            ["pandoc", "-f", "markdown+pipe_tables+raw_html", "-t", "html5",
             "--wrap=none", "--no-highlight", md_path],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        sys.exit("错误：未找到 pandoc。请安装后再运行（apt install pandoc）。")
    except subprocess.CalledProcessError as e:
        sys.exit(f"错误：pandoc 转换失败\n{e.stderr}")
    return out.stdout


def strip_colgroup(body: str) -> str:
    """去掉 pandoc 从 Markdown 分隔行推出来的固定列宽。

    那些宽度按源文里 ASCII 对齐字符数推算，对 CJK 混排常常分配失衡；
    交给浏览器的 table-layout:auto 按内容分配更耐看，也不会溢出。
    """
    return re.sub(r"<colgroup>.*?</colgroup>", "", body, flags=re.S)


def wrap_tables(body: str) -> str:
    """把每个 <table> 包进可横向滚动的容器，并给宽表打上 class。

    必须用正则匹配 <table ...>（pandoc 会给带列宽的表格加属性），
    否则精确字符串替换会漏掉部分表格、留下不配对的 </div>。
    列数 >= 7 的表格标为 wide，用更紧的字号与内边距，并允许表头换行。
    """
    def repl(m: re.Match) -> str:
        attrs, inner = m.group(1), m.group(2)
        ncol = len(re.findall(r"<col\b", inner))
        if ncol == 0:
            first_tr = re.search(r"<tr\b.*?</tr>", inner, re.S)
            ncol = len(re.findall(r"<t[hd]\b", first_tr.group(0))) if first_tr else 0
        cls = ' class="wide"' if ncol >= 7 else ""
        return f'<div class="table-scroll"><table{attrs}{cls}>{inner}</table></div>'

    return re.sub(r"<table\b([^>]*)>(.*?)</table>", repl, body, flags=re.S)


def build_toc(body: str) -> str:
    """从 h2/h3 生成两级目录。

    必须保证 <li> 内嵌 <ol> 时先闭 </ol> 再闭 </li>，
    否则会产生 “</li> 之前有未闭合 ['ol']” 这类非法嵌套。
    """
    entries = []
    for m in re.finditer(r'<h([23])(?:\s+id="([^"]*)")?[^>]*>(.*?)</h\1>', body, re.S):
        level, hid, text = m.group(1), m.group(2), m.group(3)
        if not hid or not re.search(r"[0-9A-Za-z\u4e00-\u9fff]", text):
            continue
        text = re.sub(r"<[^>]+>", "", text).strip()
        entries.append((int(level), hid, html_mod.escape(text)))
    if not entries:
        return ""

    # 若首个标题就是 h3，则降级为一级（避免 <ol> 直接嵌套 <ol>）
    if entries[0][0] == 3:
        entries = [(2, h, t) for _, h, t in entries]

    out = ['<nav class="toc" aria-label="目录"><h2>目录</h2><ol>']
    sub_open = False
    first = True
    for level, hid, text in entries:
        link = f'<a href="#{hid}">{text}</a>'
        if level == 2:
            if sub_open:
                out.append("</ol></li>")      # 先闭子 ol，再闭父 li
                sub_open = False
            elif not first:
                out.append("</li>")
            out.append(f"<li>{link}")
            first = False
        else:
            if not sub_open:
                out.append("<ol>")
                sub_open = True
            out.append(f"<li>{link}</li>")
    out.append("</ol></li>" if sub_open else "</li>")
    out.append("</ol></nav>")
    return "\n".join(out)


def main() -> None:
    md_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    if not os.path.exists(md_path):
        sys.exit(f"错误：输入文件不存在：{md_path}")

    raw = open(md_path, encoding="utf-8").read()

    title = "投资分析教学切片"
    m = re.search(r"^#\s+(.+)$", raw, re.M)
    if m:
        title = re.sub(r"[*`]", "", m.group(1)).strip()

    # 副标题：取正文顶部引用块里的前几行元信息
    subs = []
    for line in raw.splitlines()[:12]:
        s = line.strip()
        if s.startswith("> **") and any(k in s for k in ("撰写日期", "数据截止", "报告币种", "行业附录")):
            txt = re.sub(r"^>\s*", "", s)
            txt = txt.replace("**", "")
            txt = re.sub(r"`([^`]+)`", r"<code>\1</code>", txt)
            txt = txt.replace("｜", " · ")
            subs.append(f'<p class="sub">{txt}</p>')

    body = md_to_fragment(md_path)
    # 正文首个 h1 与页头重复，去掉（页头用 header.doc 渲染）
    body = re.sub(r"\A\s*<h1\b[^>]*>.*?</h1>\s*", "", body, count=1, flags=re.S)
    body = strip_colgroup(body)
    body = wrap_tables(body)
    toc = build_toc(body)

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_mod.escape(title)}</title>
<meta name="description" content="{html_mod.escape(title)} — 小米集团（1810.HK）反向 DCF 与情景估值教学">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="doc">
  <p class="kicker">Equity Research · Teaching Slice</p>
  <h1>{html_mod.escape(title)}</h1>
  {''.join(subs)}
</header>
{toc}
<main>
{body}
</main>
<footer class="doc">
  <p>本文件为投资分析方法教学材料，<strong>不是投资建议</strong>，不构成任何证券的买卖推荐。</p>
  <p>数据截止 2026-10-15 港股收盘 ｜ 由 <code>build_html.py</code> 从 Markdown 源稿生成</p>
</footer>
</div>
<a class="top-btn" href="#" aria-label="回到顶部" title="回到顶部">↑</a>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    size = os.path.getsize(out_path)
    n_tbl = len(re.findall(r"<table\b", doc))
    n_wrap = len(re.findall(r'<div class="table-scroll">', doc))
    n_pre = len(re.findall(r"<pre\b", doc))
    n_div_o, n_div_c = len(re.findall(r"<div\b", doc)), len(re.findall(r"</div>", doc))
    assert n_tbl == n_wrap, f"有 {n_tbl} 张表但只包了 {n_wrap} 个滚动容器"
    assert n_div_o == n_div_c, f"<div> 不配对：{n_div_o} 开 / {n_div_c} 闭"
    print(f"已生成 {out_path}")
    print(f"  {size:,} 字节 | {len(body.splitlines()):,} 行 HTML | {n_tbl} 张表 | "
          f"{n_pre} 个代码块 | 目录 {toc.count('<li>')} 项 | div 配对 {n_div_o}/{n_div_c} ✓")


if __name__ == "__main__":
    main()
