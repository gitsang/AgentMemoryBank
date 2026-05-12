# C1 科目一学习系统实施计划

> **给 agentic worker 的要求：** 本计划获批后，执行阶段必须使用 `superpowers:subagent-driven-development` 子技能。

## 目标

基于 `doupoa/DrivingTestSubjectOne` 构建一个本地优先的 C1 科目一学习系统，并用现行官方法规做权威校验层。项目应产出五类可评审交付物：

1. 规范化后的本地 C1 科目一题库
2. 法规校验与过时风险审计报告
3. 完整电子知识手册，不做压缩版短指南
4. 交通标志、交警手势、仪表盘指示灯等图形题所需图片资产
5. 轻量本地学习工具：先做 CLI，再做静态 Docusaurus 练习页

本计划用于实施前评审。用户已经确认初始范围问题；但真正开始实现仍需用户明确批准。

## 用户已确认的规划决策

- 手册篇幅：不压缩，按原定扩展版电子手册规划，目标约 300-350 页。
- 配图策略：优先尝试从选定题库或来源材料中截取/提取图片；如果难度太高，再使用带来源标注的网络图片，或手绘/重绘示意图。
- 交付格式：只考虑电子版。手册内容用 Markdown/MDX 编写，再由 Docusaurus 生成 HTML；不要直接手写独立 HTML 手册，也不考虑打印版或 A5 骑马钉排版。
- 子项目根目录：所有新的数据、内容、工具、图片资产、报告和生成站点都放在 `c1-subject/` 下。已有 `reports/` 研究文件只作为历史输入保留。
- 题型：C1 科目一只有单选题和判断题。导入器只建模这两类；如果出现多答案记录，标记为无效或来源漂移。
- 题库来源标注：必须标注。所有生成的数据集和学习材料都要明确说明练习题来自第三方 `doupoa/DrivingTestSubjectOne` 仓库，除非后续替换为其他来源。
- 目标读者：同时服务“零基础/时间少”和“有驾驶经验/快速过关”两类学习者。学习计划和章节导读都要包含两条路线。

## 当前输入和已知事实

### 已创建的仓库内材料

- `reports/c1-subject1-question-bank-20260512/README.md` 记录了资料可靠性分层：官方法规用于权威核对，第三方题库用于练习。
- `reports/c1-subject1-question-bank-20260512/downloadable-sources.md` 记录了已验证的 `doupoa/DrivingTestSubjectOne` 下载流程。
- `reports/c1-subject1-question-bank-20260512/booklet-structure-design.md` 是规划团队产出的课程结构草稿。
- `docs/superpowers/plans/2026-05-12-local-study-question-bank.md` 是规划团队产出的工具子计划。

### 已验证的数据集概况

下载来源：

- URL: `https://raw.githubusercontent.com/doupoa/DrivingTestSubjectOne/main/q.json`
- 上游仓库标注许可：MIT
- 我们的报告记录的上游 README 最后更新时间：`2022/07/17`
- 原始记录数：`4378`
- `subject=1` 记录数：`2545`
- `subject=4` 记录数：`1833`

观察到的 `subject=1` 数据形态：

- `style=1`: `1758`
- `style=2`: `787`
- `type=3`: `1281`
- `type=1`: `1264`
- `chapterId` 分布：`1:1242`, `2:547`, `5:351`, `3:184`, `15:121`, `14:59`, `4:41`
- C1 科目一只有判断题和单选题；当前 `subject=1` 所有答案长度都是 `1`，如果导入时出现多答案记录，应标记为无效或来源漂移。

重要影响：课程草稿里提到了“多选题”和旧的“2 分”扣分档位。这些只能视为草稿风险，不能当作最终事实；实现时不要为 C1 科目一加入多选题支持，除非后续范围变化。当前记分规则必须按公安部令第 163 号核验，现行记分档位是 12/9/6/3/1。

## 权威来源模型

当答案、解析或口诀发生冲突时，按以下优先级处理：

1. 现行法律/行政法规
2. 现行公安部部门规章
3. 官方交通管理平台指引
4. 第三方题库文本
5. 学习口诀和生成解析

主要现行参考来源：

- 《机动车驾驶证申领和使用规定》公安部令第 172 号，2025-01-01 施行：驾驶证申请资格、C1/C2 准驾范围、考试、换证、补证、实习期、审验等。
- 《道路交通安全违法行为记分管理办法》公安部令第 163 号，2022-04-01 施行：扣分题；现行档位为 12/9/6/3/1。
- 《机动车登记规定》公安部令第 164 号，2022-05-01 施行：登记、号牌、行驶证、转让、临牌、检验相关业务。
- 《中华人民共和国道路交通安全法》现行 2021 修正版：基本义务、处罚、酒驾/逃逸/无证责任、保险、执法等。
- 《中华人民共和国道路交通安全法实施条例》现行修订版：具体通行规则、速度、车道、超车、转弯、灯光、停车、高速公路行为等。

生成材料的引用格式目标：

```text
【公安部令第163号《道路交通安全违法行为记分管理办法》第8/9/10/11/12条，2022-04-01施行】
```

每个已核验知识块至少配一条引用。对于没有单一法条依据的安全操作类知识，标记为 `pedagogical/non-statutory`，并引用公安部令第 172 号中的科目一考试范围，不要硬造法规出处。

## 文件结构

创建独立的 `c1-subject/` 子项目。`c1-subject/` 本身就是 Docusaurus 项目根，因此手册源文件、生成 HTML、数据、图片资产、脚本、CLI 和本地报告都放在一起。新的实现产物不要放进顶层 `reports/`、`data/`、`content/`、`web/` 或 `cli/` 目录。

```text
c1-subject/
  README.md
  package.json
  docusaurus.config.ts
  sidebars.ts
  docs/
    handbook-outline.md
    chapter-00-exam-overview.md
    chapter-01-law-regulations.md
    chapter-02-traffic-signals.md
    chapter-03-safe-civilized-driving.md
    chapter-04-driving-operation-basics.md
    chapter-05-new-rules-local-notes.md
    study-plan.md
    appendices.md
  src/
    components/
    pages/
      index.tsx
      practice.tsx
  static/
    img/
      c1-subject/
  data/
    raw/
      driving-test-subject-one-q.json
    processed/
      questions.json
      questions.csv
      metadata.json
    audits/
      stale-risk-report.md
      law-source-registry.json
      topic-map.json
  assets/
    source-captures/
    web-sourced/
    hand-drawn/
    attribution.json
  scripts/
    import_questions.py
    audit_stale_risks.py
  cli/
    study.py
  reports/
    source-validation.md
    sample-audit-findings.md
  build/        # Docusaurus 生成目录，不手工编辑
```

最低可接受结构：

- `c1-subject/data/`：原始和处理后的题库数据
- `c1-subject/assets/`：来源截取、网络来源、重绘图片及其归因元数据
- `c1-subject/docs/`：Markdown/MDX 手册内容
- `c1-subject/`：Docusaurus 配置和生成 HTML 站点
- `c1-subject/src/pages/practice.tsx`：浏览器练习页
- `c1-subject/cli/study.py`：本地终端练习工具
- `c1-subject/reports/`：来源校验和审计结果

## 数据结构

每道题统一规范化为稳定的内部结构：

```json
{
  "id": "string",
  "source": "DrivingTestSubjectOne",
  "source_id": "string",
  "source_url": "string",
  "source_license": "string|null",
  "source_retrieved_at": "YYYY-MM-DD|null",
  "subject": "1",
  "chapter_id": "string",
  "question_type": "true_false|single_choice",
  "question": "string",
  "options": ["string"],
  "answer": "string",
  "answer_text": "string",
  "answer_skill": "string",
  "tags": ["string"],
  "topic": "string",
  "subtopic": "string",
  "vehicle_scope": "C1-general|all-motor-vehicles|special-vehicle|non-C1|unknown",
  "primary_source": "string|null",
  "article_refs": ["string"],
  "effective_date": "YYYY-MM-DD|null",
  "last_verified": "YYYY-MM-DD|null",
  "stale_risk": "low|medium|high|unknown",
  "validation_notes": "string"
}
```

第一轮实现必须填充：

- `id`
- `source_id`
- `subject`
- `chapter_id`
- `question_type`
- `question`
- `options`
- `answer`
- `answer_skill`
- `topic`
- `stale_risk`

可逐步补齐：

- `primary_source`
- `article_refs`
- `effective_date`
- `last_verified`
- `validation_notes`

## 主题路由规则

用这些规则把题目映射到权威来源和手册章节：

| 题目主题 | 主要来源 | 手册位置 |
| --- | --- | --- |
| 扣分、满分学习、记分减免、代扣分 | 公安部令第163号 | 第1章 + 扣分专项 |
| 申领、准驾车型、年龄、考试、换证、补证、审验、注销、实习期 | 公安部令第172号 | 第1章 + 驾驶证/时间专项 |
| 登记、号牌、行驶证、临牌、变更、转让、抵押、注销、检验标志 | 公安部令第164号 | 第1章 + 机动车登记小节 |
| 通行规则、灯光、让行、超车、掉头、停车、高速、速度 | 道交法 + 实施条例 | 第3章 + 速度专项 |
| 交通信号、标志、标线、交警手势 | 实施条例 + 可用的国家标准 | 第2章 |
| 事故处理、逃逸、现场处置 | 道交法 + 实施条例 | 根据题目归入第1章或第3章 |
| 安全文明、操作常识、仪表 | 考试范围 + 教学性来源 | 第3章 / 第4章 |
| 客货运、危化品、校车、摩托车专用 | 专门法规来源或排除 | 附录或排除清单 |

## 实施阶段

### Phase 0：范围锁定

初始评审问题已经确认：

1. 做完整系统，不只做数据、手册或工具的单项子集。
2. 目标是约 300-350 页的扩展版电子手册；不先做短版。
3. 用 Markdown/MDX 作为内容源格式，用 Docusaurus 生成 HTML。
4. 所有新项目产物都放在 `c1-subject/` 独立子项目中。
5. 从一开始就纳入图形题规划，但图片获取要走可追踪的资产流程。
6. C1 科目一题型只建模判断题和单选题。
7. 继续把 `DrivingTestSubjectOne` 作为主要练习题库，接受其 2022 年后的新鲜度风险，但必须做来源标注和过时风险审计。
8. 同时服务两类学习者：零基础/时间少，以及有经验/快速过关。

退出标准：

- 上述范围决策已落实到数据、内容、资产、工具和文档任务中。
- 未来如果改变这些决策，必须先更新本计划，再继续实施。

### Phase 1：数据导入与规范化

1. 添加 `c1-subject/data/raw/`，存放下载的 `q.json`，并写明来源说明。
2. 写一个小型导入器，只保留 `subject=1`。
3. 规范化字段名和选项数组。
4. `question_type` 只映射为 `true_false` 或 `single_choice`；任何异常多答案记录写入审计输出，不作为正常 C1 题型支持。
5. 生成 `c1-subject/data/processed/questions.json`、`questions.csv` 和 `metadata.json`。
6. 记录按 subject、style、type、chapter、答案形态统计的数量。

验证：

- 原始记录数仍为 `4378`。
- 处理后的 C1 科目一记录数仍为 `2545`，除非来源数据变化。
- 处理结果中没有 `subject=4` 记录。
- 所有处理后记录都有 `id`、`question`、`answer` 和规范化后的 `options`。

人工 QA：

- 用文本查看器打开 CSV，确认中文、选项和答案可读。
- 用一个小型 driver 命令随机打印 5 道规范化题目。

### Phase 2：主题映射与过时风险审计

1. 创建 `c1-subject/data/audits/law-source-registry.json`，记录来源标题、发布机关、令号、施行日期、规范 URL、检索日期和备注。
2. 创建 `c1-subject/data/audits/topic-map.json`，记录主题路由规则和关键词模式。
3. 为每道题打上 `topic`、`subtopic` 和 `vehicle_scope`。
4. 执行过时风险检查：
   - `2分`
   - `60周岁`
   - 旧令号，如 `91`、`111`、`123`、`124`，以及已被更新内容覆盖的旧 `162` 号引用
   - `回核发地` 等旧式线下办理表述
   - C1 通用内容中混入 A/B/D/E/F 专用准驾车型
   - 扣分答案不符合现行 12/9/6/3/1 档位
5. 写出 `c1-subject/data/audits/stale-risk-report.md`，高风险问题排在前面。

验证：

- 每道题都有主题标签，或明确标为 `unknown`。
- 每个高风险命中项都包含命中词、题目 ID 和建议核对的权威来源。
- 过时风险报告要区分“需要按法规更新”和“可能是非 C1/特殊车辆题”。

人工 QA：

- 抽 10 道高风险题，从处理后的 JSON 追踪到审计报告。
- 抽 5 道低风险题，确认没有被过度标记。

### Phase 3：电子手册大纲清理

1. 把 `reports/c1-subject1-question-bank-20260512/booklet-structure-design.md` 当作草稿，不当作最终来源。
2. 创建 `c1-subject/docs/handbook-outline.md`，修正现行法规假设，并以约 300-350 页为目标。
3. 删除或标记尚未证实的说法：
   - 明确 C1 科目一只有判断题和单选题；任何多选题表述都按草稿错误或来源漂移处理。
   - 用现行 12/9/6/3/1 记分结构替换旧的 12/6/3/2/1。
   - 避免“2545 题全部当前有效”这类说法。
4. 保留有用的手册组织方式，但按电子阅读场景扩展，不受打印排版限制：
   - 第0章：考试概况与学习路线
   - 第1章：法规、驾驶证、记分、处罚、事故处理、机动车登记
   - 第2章：交通信号、标志、标线、交警手势
   - 第3章：安全文明驾驶
   - 第4章：机动车驾驶操作基础
   - 第5章：新规与地方规则说明
   - 附录：口诀、关键词索引、易混淆概念、法规索引
5. 每个章节都要设计两类学习路线：
   - 零基础/时间少：白话解释、每日最低动作、哪些内容必须掌握/哪些可以先略读
   - 有经验/快速过关：易错陷阱、对比表、快速诊断题
6. 每个章节都要定义：
   - 对应题目范围
   - 权威来源
   - 常见陷阱
   - 代表题例
   - 核验状态

验证：

- 大纲只使用现行记分档位。
- 每章都说明自己是法规支撑型内容，还是教学性内容。
- 不承诺尚未获得的图片资产。

人工 QA：

- 对照审计报告阅读第1章大纲，确认高风险法规主题都有明确核验位置。

### Phase 4：图片资产流程

所有图片都必须走可追踪的资产流程。

优先级：

1. 题库/来源截取：截取或提取选定练习来源中已有的图片，记录来源 URL、截取日期、题目 ID，以及是否仅限内部学习使用。
2. 官方标准作为重绘依据：道路交通标志以 GB 5768.2-2022、道路交通标线以 GB 5768.3-2025、事故管理区标志以 GB 5768.9-2025 等现行标准为依据。若许可不清晰，优先重绘/矢量重构，不直接嵌入扫描版标准图。
3. 可合法复用的网络来源：只有在许可或使用条款足够清楚、适合本地教育材料时才使用，并记录精确 URL、许可和检索日期。
4. 手绘/重绘示意图：当来源许可不清晰或提取成本太高时，用作交通标志、交警手势、场景图和简化仪表指示灯的优先后备方案。

实施任务：

1. 创建 `c1-subject/assets/attribution.json`。
2. 定义图片元数据字段：`asset_id`、`kind`、`source_type`、`source_url`、`license_or_terms`、`retrieved_at`、`related_question_ids`、`redrawn_from_standard`、`internal_study_only`、`notes`。
3. 记录标准来源：标题、标准号、发布/实施年份、访问入口，以及资产是复用、重绘还是新画。
4. 在手册中创建图片资产清单，覆盖交通标志、手势、标线、仪表指示灯和场景示意图。
5. 第一里程碑只处理首个内容切片需要的图片；不要因为完整图片覆盖而阻塞数据和 CLI 工作。

验证：

- 每张非手绘图片都有来源 URL、检索日期和许可/条款说明。
- 每张基于标准的图片都标注为参考标准重绘/重构，不是扫描复制。
- 每张手绘/重绘图片都标注为学习用重绘，不是从官方或商业来源直接复制。
- 没有 `asset_id` 和归因记录的图片不得嵌入。
- 避免使用付费题库站、VIP PDF、无许可说明的随机搜索图片、OEM 仪表盘手册图片，除非权限清晰。

人工 QA：

- 打开一个包含图片的手册章节，并追踪到 `c1-subject/assets/attribution.json`。
- 确认手册中的图片署名简短但充分，例如：`Source: GB 5768.2-2022 reference; redrawn for study`，或 `Screenshot from DrivingTestSubjectOne-derived practice source; study reference only`。

### Phase 5：第一个内容切片

先做一个纵向切片，不要一开始就生成整本手册。

1. 选择 `第1章 / 违法记分制度` 作为第一个切片。
2. 从处理后的数据中提取相关题目。
3. 按公安部令第 163 号核验记分框架。
4. 写一个完整知识块，包含：
   - 概念解释
   - 现行规则表
   - 来自题库的例题
   - “为什么错误答案容易被选中”的说明
   - 引用
5. 添加一个短自测小节，使用真实规范化题目。

验证：

- 所有引用的记分档位都符合 12/9/6/3/1。
- 对于法规型题目，答案解析不能只依赖第三方 `answerSkill`。
- 每个例题都能追踪到 `source_id`。

人工 QA：

- 学习者不打开原始 JSON，也能读完该切片并答对 5 道相关练习题。

### Phase 6：CLI 学习工具

以现有工具子计划为输入，但第一版 CLI 要保持很小。

命令：

```text
python3 c1-subject/cli/study.py quiz c1-subject/data/processed/questions.json
python3 c1-subject/cli/study.py random c1-subject/data/processed/questions.json --count 20 --tag 扣分
python3 c1-subject/cli/study.py review c1-subject/data/processed/questions.json
python3 c1-subject/cli/study.py search c1-subject/data/processed/questions.json --query 扣分
```

最低行为：

1. 加载规范化 JSON。
2. 逐题运行 quiz 模式。
3. 接收用户答案输入。
4. 显示正确答案和现有 `answer_skill`。
5. 把错题持久化到 `.study-review.json`。
6. 复习错题。
7. 随机打乱题目顺序。
8. 按标签/主题过滤。
9. 按题干、选项、解析和标签搜索。

验证：

- JSON 能加载处理后的输出。
- Quiz 能接受正确和错误答案。
- 错题会写入复习文件。
- Review 模式能读取复习文件。
- Random 模式多次运行顺序不同。
- Search 能返回匹配题目 ID。

人工 QA：

- 在终端运行 5 题 quiz。
- 故意答错 1 题。
- 运行 review 模式，确认错题出现。
- 输入一次非法答案，确认 CLI 不会破坏状态文件。

### Phase 7：Docusaurus 手册站点与练习页

等 CLI 证明数据结构可用后再构建。手册源文件放在 `c1-subject/docs/`，使用 Markdown/MDX 编写；Docusaurus 把最终 HTML 生成到 `c1-subject/build/`。不要手工编辑生成的 HTML。

最低行为：

1. 在 `c1-subject/` 初始化/配置 Docusaurus。
2. 手册章节使用 `.md` 或 `.mdx` 文件，放在 `c1-subject/docs/`。
3. 站点公开图片放在 `c1-subject/static/img/c1-subject/`，从 `c1-subject/assets/` 中复制或优化得到。
4. 配置 `c1-subject/sidebars.ts`，组织手册章节和学习计划文档。
5. 只有 MDX 需要交互时，才在 `c1-subject/src/components/` 中添加可复用 React 组件。
6. 在 `c1-subject/src/pages/practice.tsx` 添加自定义 React 练习页。
7. 练习页在本地开发或构建时导入/读取 `c1-subject/data/processed/questions.json`。
8. 用 `localStorage` 保存错题和进度。
9. 按主题/标签/文本搜索过滤。

验证：

- Docusaurus dev server 能渲染手册文档。
- 在 `c1-subject/` 中运行 `npm run build`，能在 `c1-subject/build/` 中生成静态 HTML。
- 修改 Markdown/MDX 后，渲染出的 HTML 会更新，无需编辑生成文件。
- 练习页能显示题目、选项、答案揭示和解析。
- 错题重载后仍保留。
- 正常流程中浏览器控制台无错误。

人工 QA：

- 从 `c1-subject/` 本地运行 Docusaurus 站点。
- 打开手册路由，确认 Markdown 章节正确渲染。
- 打开 `/practice`，必要时加载/导入 `questions.json`，完成 3 道题。
- 刷新页面，确认错题状态保留。

### Phase 8：学习计划与练习计划

创建 `c1-subject/docs/study-plan.md`，包含三条路线：

1. 7 天冲刺：适合已有基本驾驶概念的人。
2. 14 天标准：默认推荐路线。
3. 30 天稳扎稳打：适合零基础学习者。

每条路线都要包含两种人群覆盖层：

- 零基础/时间少：每天概念更少、例子更多，明确“必须掌握”和“可以先略读”。
- 有经验/快速过关：先做诊断题，提供跳读路径、陷阱表和弱项专项练习。

每条路线都要写明：

- 每日阅读目标
- 每日刷题目标
- 错题复习目标
- 阶段检查分数线
- 什么时候从章节练习切换到模拟练习

建议阈值：

- 章节练习：达到 90%+ 再进入下一章
- 混合随机练习：达到 92%+ 再进入纯模拟阶段
- 考前准备充分：多次 100 题模拟稳定在 95%+，且记分/法规/过时风险主题稳定

验证：

- 学习计划引用真实存在的内容章节和 CLI/浏览器工具命令。
- 除非明确标为“后续阶段”，否则每天任务不能要求尚未生成的内容。

人工 QA：

- 按当前纵向切片执行 Day 1 指令，确认所有引用文件和命令存在。

### Phase 9：文档与交接

1. 更新 `c1-subject/README.md`，写明项目入口。
2. 链接来源报告和处理后数据位置。
3. 清楚说明来源新鲜度风险。
4. 在 README、元数据、生成手册引言和工具 UI/help 文本中，明确第三方题库来源归因。
5. 记录如何重新运行导入和审计。
6. 记录如何使用 CLI 和Docusaurus 练习页。
7. 添加“非官方题库”免责声明。

验证：

- 新用户只看 README，就能完成导入、quiz 和打开Docusaurus 练习页。
- README 中所有路径都存在。
- README 中所有命令都至少手工执行过一次。

人工 QA：

- 只从 README 出发，完成一次 quiz 会话。

## 非目标

- 不声称拿到了完整的公安部/12123 官方可下载题库。
- 不复制商业 App 的题目解析，也不在未审查来源/授权/归因的情况下复制受保护的交通标志图片。
- 不做打印优先或 A5 骑马钉布局；目标是 Docusaurus 生成的电子 HTML/PDF 导出。
- 不把手册直接写成独立 HTML；Markdown/MDX 是内容源，Docusaurus 负责生成 HTML。
- 不构建账户、同步、后端服务或云存储。
- 第一版不做复杂的间隔重复算法。
- 不把 A/B/D/E/F 专用规则或营运运输规则当作 C1 通用内容讲，除非明确标注。
- 不发布未经现行法规核验的 2022 时代记分或年龄规则。

## 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 上游题库较旧 | 答案或解析可能过时 | 内容写作前先做过时风险审计 |
| 第三方题库不是官方来源 | 不能宣传为官方题库 | 使用“练习题库”表述，并单独引用官方法规 |
| 手册草稿存在旧假设 | 学习者混淆 | 只把草稿当作规划输入，在 `content/` 中修正 |
| 法规引用工作量大 | 内容生成速度慢 | 先做一个纵向切片，再按主题扩展 |
| 图形题图片资产需求大 | Docusaurus 练习页/手册进度受影响 | 使用可追踪资产流程：来源截取优先，带归因网络来源其次，手绘/重绘兜底 |
| CLI 和 Docusaurus 练习页逻辑重复 | 维护成本上升 | 保持数据结构简单；共享数据结构即可，不提前抽复杂前后端架构 |

## 已确认的评审决策

- 手册篇幅：扩展版约 300-350 页，不先做压缩版。
- 配图策略：题库/来源截取优先；如果提取不现实，再使用带归因的网络图片或手绘/重绘图。
- 格式：只做电子版；用 Markdown/MDX 编写，用 Docusaurus 生成 HTML，不直接手写手册 HTML。
- 子项目根目录：所有新产物都放在 `c1-subject/`。
- 题型：C1 科目一只有判断题和单选题。
- 题目来源归因：所有面向用户的材料和元数据都必须标注。
- 目标读者：同时服务零基础/时间少和有经验/快速过关两类学习者。

## 建议的第一个获批里程碑

如果没有新的修改，先只实施 Milestone 1：

1. 把 `DrivingTestSubjectOne` 规范化为 `c1-subject/data/processed/questions.json`
2. 生成 `metadata.json` 和 `questions.csv`
3. 在 `c1-subject/data/audits/` 下创建来源登记表和过时风险审计脚本/报告
4. 在 `c1-subject/` 下创建/配置 Docusaurus 项目
5. 把手册大纲修正为 `c1-subject/docs/handbook-outline.md`，并包含两类学习路线
6. 如果首个内容切片需要图片，创建第一条图片归因清单记录
7. 构建最小 CLI quiz/review/search 流程
8. 手工 QA：5 题终端 quiz、1 条过时风险追踪、1 次 Docusaurus Markdown 渲染、1 条来源归因追踪

这个里程碑会先产出一个可用的本地练习闭环，以及一套可信的手册基础，而不是过早生成几百页内容。
