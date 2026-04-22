# token 数对模型效果影响：统计数据、分析与论文

更新时间：2026-04-22

## 一、先说结论

“token 数”不是一个单一变量。至少要分成 4 类，否则很容易把不同现象混在一起：

1. **训练 token 数**：决定模型是否“吃够数据”。通常更多训练 token 会带来更好效果，但边际收益递减。
2. **输入 token 数 / 上下文长度**：不是越长越好。能“塞进去”不等于能“稳定用好”，长上下文常出现准确率、召回率下降。
3. **输出 token 数 / 推理 token 数**：在推理模型里，给模型更多“思考预算”通常能提升数学、代码、科学推理表现，但同样有成本与收益递减。
4. **思维链（CoT）长度**：并不是越长越好。已有研究显示常常呈现 **倒 U 型**：太短不够，太长反而拖累。

所以，如果问“token 变多会不会让模型更强”，最准确的回答是：

- **训练 token 变多**：大概率更强；
- **上下文 token 变多**：能力上限更高，但实际效果可能变差；
- **推理 token 变多**：复杂任务通常更强，但收益递减；
- **CoT token 变多**：超过最优点后反而变差。

---

## 二、最值得记住的统计数据

### 1）训练 token：更多数据通常比盲目堆参数更划算

#### Chinchilla scaling law（Hoffmann et al., 2022）

- 论文：*Training Compute-Optimal Large Language Models*
- 链接：https://arxiv.org/abs/2203.15556
- 核心结果：在固定训练算力下，**模型参数量和训练 token 数应该近似等比例扩张**。
- 论文摘要给出的直接证据：作者训练了 **400+** 个语言模型，规模覆盖 **7000 万到 160 亿参数**、数据覆盖 **50 亿到 5000 亿 token**。
- 代表性结论：Chinchilla 用与 Gopher 相同的训练算力，但采用 **70B 参数 + 4 倍训练数据**，在下游任务上显著优于 Gopher（280B）、GPT-3（175B）等。
- 论文摘要中明确给出：Chinchilla 在 **MMLU 达到 67.5%**，比 Gopher **高 7 个百分点以上**。

这篇论文带来的行业共识可以概括为：**很多大模型以前是“参数太大、数据太少”，处于 undertrained 状态。**

#### Beyond Chinchilla（Sardana et al., ICML 2024）

- 论文：*Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws*
- 链接：https://arxiv.org/abs/2401.00448
- 核心结果：如果把**推理成本**也算进去，最优策略往往不是 Chinchilla 那个点，而是 **smaller and longer**（更小的模型、更多训练 token）。
- 论文摘要直接给出的证据：作者训练了 **47 个模型**，发现质量可以随着 **tokens per parameter** 持续上升到非常高的范围，最高到 **10,000 tokens / parameter**。
- 论文摘要还指出：如果预期推理请求量足够大（例如 **~10 亿次请求**），那就应该训练得比 Chinchilla 更“小而久”。

这意味着从总拥有成本看，**训练阶段多吃 token**，可能比“训练一个更大的模型”更划算。

---

### 2）长上下文 token：标称窗口不等于有效窗口

#### RULER（Hsieh et al., COLM 2024）

- 论文：*RULER: What's the Real Context Size of Your Long-Context Language Models?*
- 链接：https://arxiv.org/abs/2404.06654
- 核心结果：传统 NIAH（needle in a haystack）只能测很浅层的检索能力，很多模型即使 NIAH 很强，**上下文一长，复杂任务照样明显下滑**。
- 论文摘要直接给出的关键统计：作者评测了 **17 个长上下文模型**、**13 个任务**。
- 摘要中最重要的一句：虽然这些模型都声称支持 **32K+** 上下文，但**只有一半**能在 **32K** 长度上维持“令人满意”的性能。

#### NoLiMa（Modarressi et al., ICML 2025）

- 论文：*NoLiMa: Long-Context Evaluation Beyond Literal Matching*
- 链接：https://arxiv.org/abs/2502.05167
- 核心结果：如果问题与答案不再是字面匹配，而要做更真实的语义定位，长上下文性能下降会更明显。
- 论文摘要直接给出的关键统计：评测 **13 个**号称支持 **128K 以上上下文**的模型。
- 在 **32K token** 时，**11 个模型**的性能都跌到了其短上下文强基线的 **50% 以下**。
- 即便是表现较好的 GPT-4o，也从 **99.3%** 降到 **69.7%**，下降 **29.6 个百分点**。

这组结果非常重要，因为它说明：

- “模型能处理 128K / 1M 上下文” ≠ “在这个长度上仍然高质量”；
- **检索任务**都已经会掉，更复杂的总结、规划、多步推理通常只会更难。

#### Anthropic 官方：context rot

- 文档：Claude Context Windows
- 链接：https://platform.claude.com/docs/en/build-with-claude/context-windows
- 官方原文明确写道：**“As token count grows, accuracy and recall degrade, a phenomenon known as context rot.”**
- 同页也给出当前窗口规模：部分 Claude 4.6/4.7 系列支持 **1M token context window**，其他一些模型为 **200K**。

这说明主流厂商自己也承认：**上下文增长会带来准确率和召回率下降。**

#### Google 官方 / Gemini 1.5

- 文档：Google Cloud Vertex AI Long Context
- 链接：https://cloud.google.com/vertex-ai/generative-ai/docs/long-context
- 技术报告链接：https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf
- Google 官方文档直接引用：Gemini 长上下文可实现 **near-perfect retrieval (>99%)**。
- 官方文档写明：Gemini 标配 **1M token context window**，Gemini 1.5 Pro 可达 **2M token**。
- 同页还给出多模态长上下文例子：
  - 音频 haystack 测试里，Gemini 1.5 Pro 为 **100%**，Flash 为 **98.7%**；
  - 1.5 Pro 可处理最高约 **19 小时音频**。

但 Google 自己也在文档里提醒：

- 单针检索高分，不代表多针、多任务场景同样稳定；
- 多个“needle”时，性能会显著波动。

所以更准确的解读是：**超长上下文在“单点检索”上可能很强，但这不等于真实复杂任务也几乎无损。**

#### Chroma 技术报告：context rot（非同行评审，但工程上很有参考价值）

- 报告：*Context Rot: How Increasing Input Tokens Impacts LLM Performance*
- 链接：https://trychroma.com/research/context-rot
- 性质：技术报告，不是正式学术论文。
- 关键统计：评测 **18 个模型**，包括 GPT-4.1、Claude 4、Gemini 2.5、Qwen3 等。
- 结论：**随着输入长度增加，模型表现持续下降**；且这种下降会被以下因素放大：
  - 问题与答案语义相似度更低；
  - 干扰项（distractors）变多；
  - haystack 本身结构更连贯时，模型有时反而更容易出错。

这份报告适合做工程侧证据，但引用时最好标注为“技术报告”。

---

### 3）推理 token / test-time compute：给模型更多“思考 token”通常能提升复杂任务表现

#### OpenAI 官方：Learning to reason with LLMs

- 官方页面：https://openai.com/index/learning-to-reason-with-llms/
- 核心结论：**o1 的表现会随着 train-time compute 和 test-time compute 同时平滑提升。**
- 官方原文关键信号：*“o1 performance smoothly improves with both train-time and test-time compute.”*
- 官方页面直接给出的 AIME 2024 数据：
  - **GPT-4o：12%**
  - **o1 单样本：74%**
  - **64 样本多数表决：83%**
  - **1000 样本重排：93%**

这组数据说明：**同一个基础模型/系统，如果允许更多测试时计算或更多采样，效果会继续上升。**

#### OpenAI reasoning docs

- 文档：https://developers.openai.com/api/docs/guides/reasoning
- 结论：reasoning 模型会消耗额外的 reasoning tokens，且可以调 `reasoning effort`。
- 这等于官方承认：**测试时 token 预算本身就是可调性能旋钮**。

#### Scaling LLM Test-Time Compute Optimally（Snell et al., 2024）

- 论文：*Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*
- 链接：https://arxiv.org/abs/2408.03314
- 核心观点：如果 test-time compute 分配得当，**小模型 + 更多测试时计算**，有时能优于大得多的模型。

#### s1: Simple Test-Time Scaling（Muennighoff et al., 2025）

- 论文：*s1: Simple Test-Time Scaling*
- 链接：https://arxiv.org/abs/2501.19393
- 关键结论：通过 budget forcing 等简单方法，**推理 token 预算增加**可以显著提高数学等任务表现。

这一类研究的共识是：

- 对困难任务，**测试时 token 不是浪费，而是另一条 scaling 轴**；
- 但它带来的是**时延、成本、吞吐**上的真实代价。

---

### 4）CoT token：更长不总是更好

#### When More is Less（Wu et al., 2025）

- 论文：*When More is Less: Understanding Chain-of-Thought Length in LLMs*
- 链接：https://arxiv.org/abs/2502.07266
- 核心结论：**CoT 长度和准确率之间常呈倒 U 型关系**。
- 论文结论摘要：
  - 最优 CoT 长度会随**任务难度上升而增加**；
  - 最优 CoT 长度会随**模型能力上升而下降**。

这意味着：

- 小模型在难题上，可能需要更长的显式思考；
- 强模型反而更倾向于用更短、更干净的思路解决同一问题；
- 盲目要求“多想一点、多写一点思维链”并不总会更好。

---

## 三、为什么会这样：一个更实用的分析框架

### 1. 训练 token 的作用，本质上是“让参数更充分被数据约束”

如果参数很多、数据不够，模型就会 undertrained。Chinchilla 的核心贡献就是说明：在固定训练算力下，**继续喂数据**往往比继续盲目堆参数更有收益。

### 2. 长上下文变差，不是因为“放不下”，而是因为“注意力与检索更难了”

上下文越长，模型要做的事情至少更难了三层：

- 在更多 token 里定位相关信息；
- 排除相似但错误的干扰项；
- 把检索出来的信息用于推理，而不是只做表面匹配。

所以很多模型在单针检索上很强，但到真实问答、多跳推理、长对话记忆时就明显下滑。

### 3. test-time token 有效，是因为它给了模型额外搜索与纠错机会

更多 reasoning tokens、更多 samples、更多 reranking，本质上都在做一件事：**把一次前向输出，变成多步搜索/验证过程**。这解释了为什么数学、代码、科学题对 test-time compute 特别敏感。

### 4. CoT 过长会伤害效果，常见原因是“噪声、自我偏航、错误传播”

CoT 并不是越长越接近正确答案。它也可能：

- 引入无关中间步骤；
- 把早期错误不断放大；
- 让模型被自己生成的错误轨迹带偏。

这也是为什么最佳 CoT 长度会存在拐点。

---

## 四、对实际工作的启发

### 如果你在做模型训练 / 选型

- 不要只看参数量，要看**参数量 × 训练 token 是否匹配**。
- 若业务推理请求量很大，**更小模型 + 更多训练 token** 可能总成本更优。

### 如果你在做应用层 prompt / agent

- 不要把“更长上下文”当成免费午餐。
- 对 agent 来说，**精选上下文** 往往比“把所有东西都塞进去”更有效。
- 长上下文任务里，要特别警惕：
  - 相似干扰项；
  - 多轮历史里相近但过时的信息；
  - 结构过于复杂的大段原文。

### 如果你在做 reasoning 系统

- 对难题，给更多 test-time token 常常有效；
- 但应做**自适应分配**：简单题少想，难题多想；
- 不建议默认把所有请求都开到最高 reasoning budget。

---

## 五、建议引用的代表论文 / 报告清单

### 训练 token / scaling laws

1. Hoffmann et al., 2022, *Training Compute-Optimal Large Language Models*  
   https://arxiv.org/abs/2203.15556

2. Sardana et al., 2024, *Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws*  
   https://arxiv.org/abs/2401.00448

### 长上下文 / 输入 token 长度

3. Hsieh et al., 2024, *RULER: What's the Real Context Size of Your Long-Context Language Models?*  
   https://arxiv.org/abs/2404.06654

4. Modarressi et al., 2025, *NoLiMa: Long-Context Evaluation Beyond Literal Matching*  
   https://arxiv.org/abs/2502.05167

5. Levy et al., 2024, *Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models*  
   https://arxiv.org/abs/2402.14848

6. Wu et al., 2024/2025, *LongGenBench: Benchmarking Long-Form Generation in Long Contexts*  
   https://arxiv.org/abs/2409.02076

### test-time compute / reasoning token

7. OpenAI, 2024, *Learning to reason with LLMs*  
   https://openai.com/index/learning-to-reason-with-llms/

8. Snell et al., 2024, *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*  
   https://arxiv.org/abs/2408.03314

9. Muennighoff et al., 2025, *s1: Simple Test-Time Scaling*  
   https://arxiv.org/abs/2501.19393

### CoT 长度

10. Wu et al., 2025, *When More is Less: Understanding Chain-of-Thought Length in LLMs*  
    https://arxiv.org/abs/2502.07266

---

## 六、我建议你怎么引用这件事

如果你要对外讲得严谨，可以直接用下面这段表述：

> 现有研究表明，“token 数”对模型效果的影响并非单调一致，而取决于 token 所处阶段。训练 token 增加通常提升模型能力，代表性工作如 Chinchilla 证明在固定算力下模型规模与训练数据应近似等比例扩展；但输入 token / 上下文长度增加并不意味着效果稳定提升，RULER、NoLiMa 等研究显示，多数模型在更长上下文下会出现明显性能衰减；另一方面，测试时推理 token 的增加往往能显著改善复杂推理任务表现，如 OpenAI o1 与 test-time compute 相关结果所示；而对显式思维链而言，已有研究发现其长度与准确率常呈倒 U 型关系，并非越长越好。

---

## 七、一个最短版总结

- **训练 token**：通常越多越好，但边际收益递减；
- **上下文 token**：窗口越大不等于质量越稳，长上下文常有性能衰减；
- **推理 token**：更多 test-time compute 常能提升难题表现；
- **CoT token**：存在最优长度，过长可能变差。

换句话说，**token 不是“越多越强”，而是“要看是哪一种 token，以及它用在什么阶段”。**
