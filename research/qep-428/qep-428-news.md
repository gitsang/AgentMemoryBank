# QGIS 全面禁止 AI 生成代码贡献，违者回滚并封禁

（2026年10月13日）开源地理信息系统项目 QGIS 于10月7日投票通过 [QEP-428 提案](https://github.com/qgis/QGIS-Enhancement-Proposals/pull/387)，禁止一切经 LLM、AI 或 agent 工作流辅助的代码贡献进入主仓库。项目方事后发现某项贡献使用了 AI，将回滚代码并对贡献者的提交权利作出制裁，最重可永久封禁。此前 Linux 内核只是以非正式警告劝阻 AI 补丁，QGIS 是第一个把 AI 禁令写成正式项目政策的主流开源项目。

![QEP-428 禁令条文（PR #387 diff：绿色为新增的禁令两句话，红色为被删除的 QEP-408 原政策）](qep428-evidence.png)

## 一、禁令写了什么

QEP-428 的政策正文只有两句话："qgis/qgis 仓库不允许任何 LLM、AI 或 agent 辅助的代码贡献。若我们事后发现你的贡献使用了 AI、LLM 或任何基于 agent 的工作流，你将面临代码回滚和贡献者权利制裁。" 按维护者在讨论中的解释，禁令覆盖范围不止代码，还包括 issue、文档、PR 描述以及 GitHub 上的全部书面交流。

禁令的执行依赖贡献者自觉。QGIS 项目指导委员会主席 Tim Sutton 被问到如何核查时回答："合规标准就是'你是否凭良心亲手写了这段代码'，我们没有能力窥探你的电脑。"

## 二、为什么要全面禁止

推动禁令的核心开发者 Nyall Dawson 在提案讨论中说，项目此前实行的 [QEP-408 政策](https://github.com/qgis/QGIS-Enhancement-Proposals/blob/master/qep-408-ai-tool-policy.md)要求"人工把关"并用 Assisted-by 标签声明 AI 参与，但这个流程在现实中从未真正发生。约 50 个 PR 打过 "AI Assisted" 标签，其中约 40 个被关闭，还有不打标签的提交漏网。指导委员会成员 Julien Cabieces 描述了维护者的处境："外部贡献者的 AI 使用给维护者压上了巨大且难以承受的负担，而他们在 LLM 时代之前就已经够忙了。AI 流量远超人类评审能认真消化的上限。" Dawson 说，项目因此至少失去了一位极高价值的贡献者。

## 三、事件时间线

事情始于9月16日。Dawson 当天在 [QGIS 开发者邮件列表](https://lists.osgeo.org/pipermail/qgis-developer/2026-September/068576.html)提出两项行动：对所有形式的 LLM 贡献实施立即、全面的暂停；并要求新贡献者先"验明正身"，包括先向 QGIS 项目捐款再提交代码。9月23日，Sutton 代表指导委员会表态支持立法，但要求走既定的 QEP 提案流程。QEP-428 于9月24日提交，10月7日以四票赞成通过，其中包括 Even Rouault、Alexander Bruy、Signedav 和 Elpaso。

## 四、争议在哪里

开发者 Kannes 指出，"assisted"和"used"这两个词太宽，会连带禁止用 AI 做代码评审、安全审计、阅读陌生代码库这类正当用法。Dawson 承认有这个风险："我们清楚这可能把孩子和洗澡水一起倒掉，但这个孩子可能本来就是死胎。" 自己提交过 AI 辅助修复的贡献者 Amalvir 反而支持禁令："这样做打破了评审者和贡献者之间的信任契约。要向这样的大项目贡献代码，前提是你知道自己在干什么。"

## 五、修正提案已在路上

禁令公布两天后即出现修正提案。10月9日，Martin Dobias 与 3nids 提出 [QEP 429](https://github.com/qgis/QGIS-Enhancement-Proposals/pull/388)，主张给有良好记录的资深贡献者开 AI 使用例外，新贡献者则继续关门。该提案在 GitHub 上收获 9 个赞同、5 个反对。核心开发者 Even Rouault 评论说，这份提案"不如改名叫'成分不明的毒品只允许成年人使用'"。他本人在 QEP-428 投票期间已进入罢工状态。

按 Dawson 的说法，QEP-428 是"先把门关死、之后逐案放开"的起点。IDE 代码补全、翻译辅助等具体豁免场景，项目计划在下一次用户大会上讨论。QEP 429 目前仍在讨论中，尚未投票。

---

**来源**

- QEP-428 提案与讨论（PR #387）：https://github.com/qgis/QGIS-Enhancement-Proposals/pull/387
- QEP 429 修正提案（PR #388）：https://github.com/qgis/QGIS-Enhancement-Proposals/pull/388
- QEP-408 原 AI 工具政策：https://github.com/qgis/QGIS-Enhancement-Proposals/blob/master/qep-408-ai-tool-policy.md
- 开发者邮件列表讨论（2026-09）：https://lists.osgeo.org/pipermail/qgis-developer/2026-September/068576.html
- 媒体报道（LavX News）：https://news.lavx.hu/article/qgis-bans-ai-generated-contributions-after-maintainer-burnout
