#!/usr/bin/env python3
"""把教学切片的 Markdown 构建成可独立打开的 HTML。

设计语言复用 books/the-little-book-of-common-sense-investing/build_html.py：
同一套纸感配色、深色模式变量、CJK 字体栈与表格样式，保持仓库观感一致。

用法：
    python3 build_html.py [in.md] [out.html]

依赖：pandoc（用于 Markdown → HTML 片段）。不依赖任何 Python 第三方包。
"""
import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IN = os.path.join(HERE, "teaching-slice-20261015.md")
DEFAULT_OUT = os.path.join(HERE, "teaching-slice.html")
DEFAULT_GLOSSARY = os.path.join(HERE, "glossary.json")

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

/* ---------- 术语高亮 + 点击弹窗 ---------- */
.term { font: inherit; color: inherit; background: none; border: 0; padding: 0;
  margin: 0; cursor: help; text-align: inherit;
  border-bottom: 1px dotted var(--accent); }
.term:hover, .term.is-open { color: var(--accent); border-bottom-style: solid; }
.glossary-pop { position: absolute; z-index: 40;
  width: min(23rem, calc(100vw - 24px));
  background: var(--paper); color: var(--ink);
  border: 1px solid var(--rule); border-radius: .5rem;
  padding: .8rem 1rem; box-shadow: 0 8px 28px rgba(0,0,0,.2);
  font-size: .85rem; line-height: 1.65; }
.glossary-pop .gp-en { font: 600 .7rem/1.3 var(--sans); letter-spacing: .05em;
  color: var(--muted); }
.glossary-pop .gp-zh { font-family: var(--cjk); font-size: 1.02rem; font-weight: 700;
  margin: .2rem 0 .5rem; color: var(--accent); }
.glossary-pop .gp-note { font-family: var(--cjk); text-wrap: pretty; }
.glossary-pop .gp-hint { margin-top: .55rem; padding-top: .45rem;
  border-top: 1px solid var(--rule); font: 400 .68rem/1.4 var(--sans);
  color: var(--muted); }

/* 页头提示条 */
.gl-hint { margin: 1.6rem 0 0; padding: .7rem .95rem; background: var(--aside-bg);
  border: 1px solid var(--rule); border-radius: .5rem;
  font: 400 .82rem/1.6 var(--sans); color: var(--muted); }
.gl-hint b { color: var(--accent); }
.gl-hint .gl-demo { border-bottom: 1px dotted var(--accent); color: var(--accent);
  cursor: help; }

/* ---------- 文末完整术语表 ---------- */
.glossary-appendix { margin: 3.5rem 0 0; padding: 1.1rem 1.4rem;
  background: var(--paper); border: 1px solid var(--rule); border-radius: .5rem; }
.glossary-appendix > summary { cursor: pointer; font: 600 .78rem/1.6 var(--sans);
  letter-spacing: .1em; text-transform: uppercase; color: var(--accent); }
.glossary-appendix .gl-cat { margin: 1.4rem 0 .5rem; font: 700 .82rem/1 var(--sans);
  color: var(--accent); }
.glossary-appendix dl { margin: 0; }
.gl-entry { margin: 0 0 .95rem; }
.gl-entry dt { font: 700 .88rem/1.5 var(--sans); }
.gl-entry dt .gl-zh { font-family: var(--cjk); font-weight: 700;
  color: var(--accent); margin-left: .5rem; }
.gl-entry dd { margin: .25rem 0 0; font-family: var(--cjk);
  font-size: .84rem; line-height: 1.7; color: var(--muted); text-wrap: pretty; }

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
  .term { border-bottom: 0; }
  .glossary-pop { display: none; }
  .glossary-appendix { break-before: page; }
  .glossary-appendix > summary { display: none; }
  .glossary-appendix details { display: block; }
}
"""


# 注意：必须是 raw string。JS 里的 \b（正则词边界）与 \u3400 这类序列
# 在普通 Python 字符串里会被吃掉（\b 变退格符、\u3400 变真 CJK 字符），
# 生成出来的 JS 会静默出错。
GLOSSARY_JS = r"""
(function () {
  var holder = document.getElementById('glossary-data');
  var main = document.querySelector('main');
  if (!holder || !main) return;

  var terms;
  try { terms = JSON.parse(holder.textContent).terms; } catch (e) { return; }
  if (!terms || !terms.length) return;

  var byId = {};
  terms.forEach(function (t) { byId[t.id] = t; });

  var CJK = /[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/;

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  // 每个术语一个正则：英文用词边界，中文按字面（\b 对 CJK 无效）。
  // 长词优先，避免「毛利率」被「毛利」先吃掉。
  var patterns = terms.map(function (t) {
    var forms = [t.en].concat(t.aliases || [])
      .filter(function (f) { return f && f.length; });
    var alts = forms.map(function (f) {
      var lit = escapeRe(f);
      return CJK.test(f) ? lit : '\\b' + lit + '\\b';
    });
    var weight = Math.max.apply(null, forms.map(function (f) { return f.length; }));
    return { id: t.id, weight: weight, re: new RegExp('(?:' + alts.join('|') + ')') };
  }).sort(function (a, b) { return b.weight - a.weight; });

  var SKIP = 'a,button,code,pre,sup,nav,header,footer,script,style,' +
             'h1,h2,h3,h4,h5,h6,.table-scroll th,.glossary-pop,.glossary-appendix,' +
             '.gl-hint';

  function eligible(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return false;
    var p = node.parentElement;
    return !!p && !p.closest(SKIP);
  }

  function firstMatchNode(root, re) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      if (eligible(node)) {
        re.lastIndex = 0;
        if (re.test(node.nodeValue)) return node;
      }
    }
    return null;
  }

  function wrap(node, re, id) {
    re.lastIndex = 0;
    var m = re.exec(node.nodeValue);
    if (!m) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'term';
    btn.setAttribute('data-term', id);
    btn.textContent = m[0];
    var parent = node.parentNode;
    parent.insertBefore(document.createTextNode(node.nodeValue.slice(0, m.index)), node);
    parent.insertBefore(btn, node);
    parent.insertBefore(document.createTextNode(node.nodeValue.slice(m.index + m[0].length)), node);
    parent.removeChild(node);
  }

  // 术语表里的 note 用 **x** 标重点；纯文本插入会把星号显示出来，
  // 所以按偶数段/奇数段切分，奇数段包成 <strong>。
  function richText(el, text) {
    String(text).split('**').forEach(function (seg, i) {
      if (!seg) return;
      if (i % 2 === 1) {
        var s = document.createElement('strong');
        s.textContent = seg;
        el.appendChild(s);
      } else {
        el.appendChild(document.createTextNode(seg));
      }
    });
    return el;
  }

  // 每个二级章节里，每个术语只标第一次出现——否则满页虚线，反而没人看。
  var used = {};
  Array.prototype.forEach.call(main.children, function (el) {
    if (el.tagName === 'H2') used = {};
    patterns.forEach(function (p) {
      if (used[p.id]) return;
      var node = firstMatchNode(el, p.re);
      if (!node) return;
      wrap(node, p.re, p.id);
      used[p.id] = true;
    });
  });

  var pop = document.createElement('div');
  pop.className = 'glossary-pop';
  pop.setAttribute('role', 'dialog');
  pop.hidden = true;
  document.body.appendChild(pop);
  var active = null;

  function close() {
    pop.hidden = true;
    if (active) active.classList.remove('is-open');
    active = null;
  }

  function open(btn) {
    var t = byId[btn.getAttribute('data-term')];
    if (!t) return;
    if (active === btn) { close(); return; }
    if (active) active.classList.remove('is-open');
    active = btn;
    btn.classList.add('is-open');

    pop.textContent = '';
    var elEn = document.createElement('div');
    elEn.className = 'gp-en';
    elEn.textContent = t.en;
    pop.appendChild(elEn);
    var elZh = document.createElement('div');
    elZh.className = 'gp-zh';
    elZh.textContent = t.zh;
    pop.appendChild(elZh);
    var elNote = document.createElement('div');
    elNote.className = 'gp-note';
    richText(elNote, t.note);
    pop.appendChild(elNote);
    var hint = document.createElement('div');
    hint.className = 'gp-hint';
    hint.textContent = '点击空白处或按 Esc 关闭';
    pop.appendChild(hint);

    pop.hidden = false;
    var r = btn.getBoundingClientRect();
    var maxLeft = window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 12;
    var top = r.bottom + window.scrollY + 8;
    // 下方空间不够就翻到上方
    if (r.bottom + pop.offsetHeight + 16 > window.innerHeight && r.top > pop.offsetHeight + 16) {
      top = r.top + window.scrollY - pop.offsetHeight - 8;
    }
    pop.style.top = top + 'px';
    pop.style.left = Math.max(12 + window.scrollX,
                              Math.min(r.left + window.scrollX, maxLeft)) + 'px';
  }

  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('.term');
    if (btn) { open(btn); return; }
    if (!pop.hidden && !pop.contains(ev.target)) close();
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') close();
  });

  window.addEventListener('resize', close);
  window.addEventListener('scroll', function () { if (!pop.hidden) close(); }, { passive: true });

  // 页头“术语表”链接：点一下直接展开文末的折叠区
  var link = document.getElementById('gl-open');
  var det = document.getElementById('glossary');
  if (link && det) link.addEventListener('click', function () { det.open = true; });
})();
"""


def load_glossary(path: str) -> list:
    """读取术语表；文件不存在或格式错就返回空列表（构建仍可继续）。"""
    if not path or not os.path.exists(path):
        return []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"警告：术语表读取失败（{e}），跳过术语功能", file=sys.stderr)
        return []
    return [t for t in data.get("terms", [])
            if t.get("en") and t.get("zh") and t.get("note")]


def md_bold(s: str) -> str:
    """把术语表 note 里的 **强调** 转成 <strong>（先转义，避免注入）。"""
    segs = html_mod.escape(s).split("**")
    return "".join(f"<strong>{x}</strong>" if i % 2 else x
                   for i, x in enumerate(segs))


def glossary_appendix(terms: list) -> str:
    """文末可折叠的完整术语表，按分类分组。"""
    if not terms:
        return ""
    order, groups = [], {}
    for t in terms:
        cat = t.get("cat", "其他")
        if cat not in groups:
            groups[cat] = []
            order.append(cat)
        groups[cat].append(t)

    parts = ['<details class="glossary-appendix" id="glossary">',
             f'<summary>术语表 · 共 {len(terms)} 条（点击展开）</summary>']
    for cat in order:
        parts.append(f'<div class="gl-cat">{html_mod.escape(cat)}</div><dl>')
        for t in groups[cat]:
            parts.append(
                f'<div class="gl-entry"><dt>{html_mod.escape(t["en"])}'
                f'<span class="gl-zh">{html_mod.escape(t["zh"])}</span></dt>'
                f'<dd>{md_bold(t["note"])}</dd></div>'
            )
        parts.append("</dl>")
    parts.append("</details>")
    return "\n".join(parts)


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
    ap = argparse.ArgumentParser()
    ap.add_argument("md", nargs="?", default=DEFAULT_IN, help="输入 Markdown")
    ap.add_argument("out", nargs="?", default=DEFAULT_OUT, help="输出 HTML")
    ap.add_argument("--glossary", default=DEFAULT_GLOSSARY,
                    help="术语表 JSON（默认同目录 glossary.json）")
    a = ap.parse_args()
    md_path, out_path = a.md, a.out
    if not os.path.exists(md_path):
        sys.exit(f"错误：输入文件不存在：{md_path}")

    terms = load_glossary(a.glossary)

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

    glossary_data = appendix = gl_hint = glossary_js = ""
    if terms:
        payload = json.dumps({"terms": terms}, ensure_ascii=False).replace("</", "<\\/")
        glossary_data = ('<script type="application/json" id="glossary-data">'
                         f'{payload}</script>')
        glossary_js = f"<script>{GLOSSARY_JS}</script>"
        appendix = glossary_appendix(terms)
        gl_hint = ('<p class="gl-hint">术语看不懂？'
                   '正文里带 <span class="gl-demo">虚线下划线</span> 的词'
                   '（例如 <span class="gl-demo">EV</span>、'
                   '<span class="gl-demo">YTD</span>、'
                   '<span class="gl-demo">反向 DCF</span>）'
                   '<b>点一下就会弹出解释</b>。'
                   f'完整 <a href="#glossary" id="gl-open">术语表（{len(terms)} 条）</a>在文末。</p>')

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
  {gl_hint}
</header>
{toc}
<main>
{body}
</main>
{appendix}
<footer class="doc">
  <p>本文件为投资分析方法教学材料，<strong>不是投资建议</strong>，不构成任何证券的买卖推荐。</p>
  <p>数据截止 2026-10-15 港股收盘 ｜ 由 <code>build_html.py</code> 从 Markdown 源稿生成</p>
</footer>
</div>
<a class="top-btn" href="#" aria-label="回到顶部" title="回到顶部">↑</a>
{glossary_data}
{glossary_js}
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
    if terms:
        print(f"  术语表 {len(terms)} 条（已内联；标注由页面 JS 在浏览器里完成）")


if __name__ == "__main__":
    main()
