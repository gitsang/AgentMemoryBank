# C1 / 小车科目一题库本地下载方案

## 已验证可下载：GitHub JSON

来源：`doupoa/DrivingTestSubjectOne`

- 仓库：https://github.com/doupoa/DrivingTestSubjectOne
- 数据直链：https://raw.githubusercontent.com/doupoa/DrivingTestSubjectOne/main/q.json
- 许可：仓库标注 MIT License
- README 标注：题库源为“banban驾道”，最后更新 `2022/07/17`
- 我已实际下载到 `/tmp/opencode/c1-kemu1-q.json` 并读取成功
- 实测数据：总计 `4378` 条，其中 `subject=1` 为 `2545` 条，`subject=4` 为 `1833` 条

下载原始 JSON：

```bash
curl -L -o c1-kemu1-q.json \
  https://raw.githubusercontent.com/doupoa/DrivingTestSubjectOne/main/q.json
```

过滤出科目一：

```bash
python3 - <<'PY'
import json

src = 'c1-kemu1-q.json'
dst = 'c1-kemu1-subject1.json'

data = json.load(open(src, encoding='utf-8'))
rows = [x for x in data if str(x.get('subject')) == '1']

json.dump(rows, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'wrote {len(rows)} questions to {dst}')
PY
```

转成 CSV，方便 Excel 打开：

```bash
python3 - <<'PY'
import csv
import json

data = json.load(open('c1-kemu1-subject1.json', encoding='utf-8'))

with open('c1-kemu1-subject1.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'question', 'A', 'B', 'C', 'D', 'answer', 'answerSkill', 'chapterId', 'style', 'type'])
    for x in data:
        opts = x.get('itemsDescArray') or []
        opts = (opts + ['', '', '', ''])[:4]
        w.writerow([
            x.get('id'),
            x.get('question'),
            *opts,
            x.get('answer'),
            x.get('answerSkill'),
            x.get('chapterId'),
            x.get('style'),
            x.get('type'),
        ])

print(f'wrote {len(data)} questions to c1-kemu1-subject1.csv')
PY
```

### 风险

- 不是官方题库。
- 最后更新为 2022 年，可能缺少 2025/2026 新规题。
- 原始 JSON 混合科目一和科目四，必须按 `subject=1` 过滤。
- 部分解析可能引用旧公安部令号，遇到扣分、年龄、换证、满分学习等题，建议用现行法规核对。

## 可导出但需要注册：极速数据 API

来源：https://www.jisuapi.com/api/driverexam/

- 格式：JSON API
- 参数支持：`type=C1`、`subject=1`、`pagesize=100`、`pagenum=1...`、`sort=normal`
- 页面示例返回 `total=950`
- 免费额度页面标注为 `100次/天`

调用形态：

```text
https://api.jisuapi.com/driverexam/query?appkey=你的appkey&type=C1&subject=1&pagesize=100&pagenum=1&sort=normal
```

适合：想要结构化 JSON、愿意注册 appkey、可以自己分页拉取的人。

风险：仍是第三方 API；“最新/公安部题库”的宣传不能当作官方背书，答案仍需用现行法规抽查。

## 可下载但不推荐优先用：文库/PDF/DOCX

例如：

- 原创力文档 `科目一考试题库(1073题完整版、含标准答案).docx`
- 原创力文档 `2026最新驾照C1证考试科目一题库及答案(包过版).pdf`
- CSDN、百度文库上的 `900题/1000题` PDF 或 DOC

问题：

- 多数需要登录、积分或 VIP。
- 来源链路不透明，题库可能拼接自旧版资料。
- 很多标题写“2026 最新”，正文仍可能引用旧规则。
- 不适合作为唯一题库，最多作为补充阅读。

## 推荐选择

如果只是想离线备份：

1. 先下载 GitHub JSON。
2. 过滤 `subject=1`，得到本地 JSON/CSV。
3. 刷题仍用驾考宝典/驾校一点通/元贝补最新题。
4. 扣分、年龄、换证、登记、满分学习题目，回到官方法规核对。

如果想要更像“C1 科目一接口库”：

1. 注册极速数据 appkey。
2. 按页拉取 `type=C1&subject=1`。
3. 保存为 JSON/CSV。
4. 抽样对照主流 App 和官方法规。
