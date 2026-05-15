# AI 网关智能路由设计方案（SLA 优先）

**日期**: 2026-04-22  
**目标**: 在不稳定、多约束、多账号、多供应商的 LLM 供给环境下，构建一个以 **SLA 保证** 为核心，同时兼顾 **低延迟、低成本、负载分散** 的 AI Gateway 路由系统。

---

## 一、结论先行

你对市场现状的判断基本是对的：**大多数 AI Gateway 的“路由”仍然停留在规则编排层**，能做 fallback、权重、条件判断，但很少真正把“供应能力、账号约束、实时健康、延迟波动、预算目标、降级目标”统一成一个调度问题。

现有产品的典型问题是：

1. **以 provider 为中心，而不是以实际可调度供给单元为中心**  
   现实里真正能接单的是“某个账号 + 某个 endpoint + 某组模型 + 某种额度/代理/协议能力”，不是抽象 provider。
2. **路由能力碎片化**  
   有的擅长 fallback，有的擅长 latency，有的擅长 cost，但很少能统一做多目标优化。
3. **规则树越写越复杂**  
   一旦加上多账号、订阅与按量混用、动态限额、429/503 退避、会话粘性、模型降级，传统规则树迅速失控。
4. **大多是“静态路由 + 被动故障切换”，不是“实时调度 + 主动 SLA 控制”**。

因此，你的产品应该把核心定义为：

> **不是做一个“支持很多规则的 AI 网关”，而是做一个“基于供需约束和实时状态的 LLM 调度系统”。**

这也是你的核心差异化方向。

---

## 二、竞品分析：当前产品做得好的地方与关键缺口

结合已有研究（Portkey、LiteLLM、Kong AI Gateway、OpenRouter、Cloudflare AI Gateway、Braintrust、Helicone、Ferro、Routerly 等），可以归纳为四类。

### 1. 规则/路由图型

代表：**Portkey、Cloudflare AI Gateway**

优点：
- 条件路由、加权路由、fallback 链、可视化编排都比较强
- 对业务规则表达友好
- 易于解释“为什么走了某条链路”

短板：
- 更像“流量编排引擎”，不是“实时调度器”
- 对账号级限额、实际供应饱和度、实时负载退避、容量预测支持不够强
- 多目标优化能力弱，通常需要手工配置权重

### 2. 工程型多策略路由器

代表：**LiteLLM、Kong AI Gateway、Ferro**

优点：
- 更接近传统高可用路由器
- 支持 health check、cooldown/circuit breaker、latency-aware、least-busy、cost-based 等
- 对 429 / timeout / 5xx 的处理语义更清晰

短板：
- 仍偏“请求来了，选一个后端”
- 对复杂供应结构（多 BaseURL、多账号、多代理、多协议能力）的数据建模不够深
- 很少把“订阅额度优先 + 按量兜底 + 模型降级 + 预算控制”统一进一个策略模型

### 3. 市场聚合/自动优选型

代表：**OpenRouter、Helicone**

优点：
- 默认体验好，上手快
- 成本优先或速度优先逻辑简单有效
- 适合“我不想自己维护 provider 池”的用户

短板：
- 灵活性有限
- 对 SLA 的可控性弱于自建路由层
- 不适合作为复杂 B2B 网关产品的底层能力模板

### 4. 智能评分 / 新路线型

代表：**Routerly**

优点：
- 开始把 routing 看成多维评分问题
- 比传统 weight/fallback 更接近你的方向

短板：
- 很多产品仍停留在“策略打分器”，没有形成强数据模型和完整的供应治理体系
- 对 quota / account / protocol / degradation 的工业级建模仍不够成熟

### 你的机会窗口

你的切入点不是“再做一个支持 fallback / 权重 / 条件的网关”，而是把下面四件事统一起来：

1. **账号级供给建模**
2. **实时可调度性判断**
3. **多目标路由评分**
4. **SLA 导向的分层降级与兜底**

---

## 三、当前产品的核心痛点

### 1. 路由对象建模错误

多数产品把 `provider` 或 `model` 当主维度。但你实际遇到的问题是：

- 同一个 provider 下有多个账号
- 不同账号可用模型不同
- 不同账号配不同代理
- 同一个账号下可能有多个 BaseURL / 协议适配层
- 同一模型在不同 endpoint 上的 SLA、价格、额度、速率限制不同

因此，**真正的调度对象不应该是 provider，也不应该只是 model，而应该是“可供给单元（Supply Unit）”。**

### 2. 规则系统复杂度爆炸

一旦引入：

- 订阅账号优先
- 按量兜底
- 会话粘性
- 额度耗尽退避
- 并发过高降权
- provider 故障摘除
- 模型降级
- 语义化选模

传统 `if/else + weight + fallback` 的表达会很快失去可维护性。

### 3. 缺少“实时动态权重”

市面很多产品的 `weight` 本质仍是**静态配置**。但真实世界里权重应该被实时状态影响：

- 错误率升高
- P95 延迟升高
- 首 token 变慢
- token 配额趋近耗尽
- 并发接近上限
- 429 增多
- 某代理链路抖动

### 4. 缺少明确的 SLA 目标函数

产品会说“更便宜”“更快”“更稳”，但很少明确：

- 稳定的定义是什么？成功率？可用率？TTFT？P95？
- 成本和稳定冲突时谁优先？
- 哪些请求允许降级，哪些不允许？
- 什么时候从订阅切到按量？

这导致路由策略无法产品化，只能变成工程师调参。

---

## 四、产品定位：你应该做成什么

建议把产品定位定义为：

> **面向不稳定多源 LLM 供给的智能调度网关**  
> 不是规则代理，不是简单 proxy，而是一个以 SLA 为目标函数的供给编排与路由系统。

### 一句话价值主张

> 在不稳定的供应商和账号体系之上，提供稳定、快速、便宜、可控的统一 LLM 供应层。

### 核心优势主张

1. **以账号/供给单元为核心建模，而不是只按 provider 配置**
2. **路由是实时调度，不是静态规则树**
3. **统一处理 cost / quota / latency / health / fallback / degradation**
4. **把 SLA 做成产品能力，而不是运维经验**
5. **可解释：每一次路由都能说清楚为什么这么选**

---

## 五、关键设计思想：从“规则驱动”转向“供应关系驱动”

你的 thinking 里最重要的一点是对的：

> 先理清楚“谁提供什么，谁需求什么”，再决定路由和数据模型。

### 设计原则

#### 原则 1：供给实体必须足够细

一个 provider 不是一个可调度单元。真正可调度的是：

- 某个账号
- 在某个接入 endpoint / BaseURL 下
- 以某种协议适配（OpenAI / Anthropic / Ollama / llama.cpp / Bedrock-like）
- 暴露某组模型能力
- 受某组速率 / 并发 / token / 预算限制
- 走某条代理网络

#### 原则 2：路由对象是“供给候选池”，不是单个 provider

用户请求的是一种能力，例如：

- `chat.completion` with tool calling
- reasoning medium
- vision input
- 128k context
- structured output

系统先把请求映射成 **需求画像（Demand Profile）**，再与供给候选池匹配。

#### 原则 3：调度分两段

1. **硬筛选（Eligibility Filtering）**：不满足能力、协议、额度、预算、健康条件的直接淘汰
2. **软评分（Scoring & Ranking）**：在可用候选中，根据策略目标进行多目标排序

#### 原则 4：Fallback / 降级 / 退避是调度层能力，不是事后补丁

它们不是异常处理，而是路由主流程的一部分。

---

## 六、推荐的数据模型：以“账号优先”的供给分层

你提出“也许不是以 provider 为第一层，而是以账号为第一层”这个方向，我建议继续推进，并进一步抽象成下面 8 个核心实体。

### 1. Provider

表示供应商品牌或服务源，如 OpenAI、Anthropic、Azure OpenAI、OpenRouter、DeepSeek、Ollama Cluster。

**职责**：
- 品牌/生态信息
- 通用协议能力集合
- 默认价格目录引用
- 默认健康模型/错误语义映射

### 2. Account

表示某个 provider 下的具体供给身份。

例如：
- OpenAI paid account A
- OpenAI subscription account B
- Azure deployment account C
- OpenRouter team account D

**这是你的一层核心实体。**

**原因**：
- 额度属于账号
- API key 属于账号
- 账单类型属于账号
- 限额和风控一般也是账号级
- 同 provider 不同账号常常表现完全不同

### 3. Credential

表示账号下的具体凭证集合。

一个 account 可以有多个 API key。不同 key：
- 速率限制可能不同
- 权限可能不同
- 风控状态可能不同
- 可能绑定不同代理

### 4. Endpoint

表示实际接入地址与协议适配层。

字段建议：
- `base_url`
- `protocol_type`（openai-compatible / anthropic-compatible / ollama / llama.cpp / custom）
- `region`
- `proxy_ref`
- `transport_config`

一个 account 可以挂多个 endpoint。

### 5. Supply Unit（核心调度实体）

这是最关键的抽象。  
它表示：

> **一个 credential 在某个 endpoint 上，以某种协议，能够提供某组模型/能力，并受一组限制约束的最小可调度供给单元。**

可理解成：

`SupplyUnit = Account + Credential + Endpoint + Capability Slice + Constraint Slice`

系统真正路由到的是它，而不是 provider/account 本身。

### 6. Model Offering

表示某个 Supply Unit 能提供的模型映射：

- 原始模型名
- 网关标准模型名（canonical model）
- 能力标签（vision / tool-use / reasoning / json / long-context）
- 上下文长度
- 支持接口（responses / messages / chat/completions）
- 价格信息（若有）

### 7. Constraint Policy

约束模型，建议至少覆盖：

- RPM
- TPM
- 并发数
- 日/小时/月 quota
- 成本预算
- 最大请求大小
- 最大上下文长度
- 风控冻结
- 维护时间窗

### 8. Routing Policy / Template

不是直接绑定 provider，而是绑定到：

- 业务租户
- 路由组
- canonical model alias
- 请求场景 / SLA profile

---

## 七、推荐的层级关系

建议采用如下关系：

```text
Provider
  └── Account
        └── Credential (1..n)
              └── Endpoint Binding (1..n)
                    └── Supply Unit (1..n)
                          └── Model Offering (1..n)
```

这样设计的好处：

1. **账号、凭证、endpoint、模型能力可以独立变化**
2. **支持一个账号多个 BaseURL / 多协议接入**
3. **支持不同 key 走不同代理**
4. **支持同模型由多个 Supply Unit 供给**
5. **路由器只看 Supply Unit，不需要理解复杂上游结构**

---

## 八、架构设计：从入口到调度再到执行

建议架构分为 7 层。

### 1. API Ingress / Protocol Normalization

职责：
- 接收 `/responses`、`/messages`、`/chat/completions` 等入口
- 统一为内部请求结构
- 标准化 streaming / tool-calling / multimodal 请求

输出：**Normalized Request**

### 2. Demand Profiler（需求画像层）

职责：
- 从请求中提取能力需求和路由上下文

输出字段建议：
- canonical model alias
- request type（chat / response / embeddings / image / rerank）
- required capabilities
- tenant / project / user / session
- latency sensitivity
- budget sensitivity
- downgrade allowance
- sticky key
- semantic class（可选）

### 3. Supply Registry（供给注册表）

职责：
- 存储全量 Supply Unit
- 暴露“当前有哪些可用供给单元”
- 维护静态配置 + 动态状态

### 4. State & Telemetry Engine（实时状态引擎）

职责：
- 聚合每个 Supply Unit 的：
  - success rate
  - 429 rate
  - timeout rate
  - p50/p95 latency
  - TTFT
  - in-flight requests
  - RPM/TPM usage
  - quota remaining
  - breaker state

这是路由“大脑”的实时输入层。

### 5. Eligibility Filter（硬筛选层）

先排除不可能候选：

- 不支持所需协议
- 不支持所需模型/能力
- quota 不足
- 并发已满
- breaker = open
- 显式维护中
- 不满足租户策略

### 6. Routing Engine（核心评分层）

对剩余候选进行打分、排序、采样。

### 7. Execution & Recovery Layer（执行与恢复层）

职责：
- 实际发起请求
- 判断是否 retry / failover / degrade
- 更新状态
- 记录解释日志

---

## 九、核心路由模型：推荐使用“硬约束 + 多目标评分 + 分层回退”

这是整套方案最核心的部分。

### 阶段 A：硬约束筛选

输入：Demand Profile + candidate Supply Units

过滤条件：

1. **协议兼容性**：是否支持请求入口语义
2. **能力兼容性**：是否支持所需模型能力/上下文/工具调用
3. **租户策略**：是否允许该 tenant 使用
4. **额度兼容性**：RPM / TPM / quota / budget 是否足够
5. **状态兼容性**：是否健康、是否处于 breaker-open / maintenance

这一步的目标不是“选最好”，而是“剔除不能选的”。

### 阶段 B：多目标评分

对可用候选计算统一分值：

```text
FinalScore =
  W_availability * AvailabilityScore
  + W_latency * LatencyScore
  + W_cost * CostScore
  + W_quota * QuotaScore
  + W_load * LoadScore
  + W_stickiness * StickyScore
  + W_semantic * SemanticScore
  + W_priority * BusinessPriorityScore
```

#### 各分值建议

**1. AvailabilityScore**
- 成功率 EWMA
- breaker 状态
- 最近 429 / 5xx / timeout 比率
- 是否刚从 open 恢复到 half-open

**2. LatencyScore**
- TTFT EWMA
- E2E latency EWMA
- P95 惩罚项

**3. CostScore**
- 每 token 成本
- 订阅账号额外加成
- 按量账号成本惩罚

**4. QuotaScore**
- 剩余额度越高越好
- 越接近 quota exhaustion，分数越低

**5. LoadScore**
- in-flight / max_concurrency
- 当前 rpm/tpm 占上限比值

**6. StickyScore**
- 若该 session 已绑定某供给单元，则给它加分
- 用于提升上下文稳定性/缓存命中

**7. SemanticScore**
- 若启用语义化路由，根据任务类型与模型能力匹配打分

**8. BusinessPriorityScore**
- 订阅优先
- 指定区域优先
- 指定 provider blacklist/whitelist

### 阶段 C：选择方式

不建议永远选 Top-1。建议：

1. **Top-K 采样**：从前 K 个候选中按分值归一化采样  
   避免流量过度集中到一个节点。
2. **温和探索**：保留少量试探流量给次优节点  
   避免冷启动节点永远没有样本。
3. **Sticky override**：会话型流量优先保持粘性

---

## 十、四类路由模板设计

你已经给出四个模板，我建议把它们都实现成同一评分引擎的不同参数集，而不是四套不同代码路径。

### 1. Cost Based

目标：**尽可能便宜，优先消耗订阅供给。**

权重倾向：
- `W_cost` 高
- `W_quota` 中高
- `W_latency` 中
- `W_availability` 必须仍然高于最低阈值

行为：
- 订阅账号优先
- 同订阅账号中优先剩余额度多、负载低者
- 订阅池整体不可用或接近耗尽时，fallback 到按量账号

适用场景：
- 批处理
- 内部工具
- 对速度没那么敏感的请求

### 2. Quota Based

目标：**尽可能分散订阅账号消耗，避免单账号提前打爆。**

权重倾向：
- `W_quota` 最高
- `W_load` 高
- `W_cost` 中
- `W_latency` 中低

行为：
- 优先路由到 quota usage ratio 更低的账号
- 接近阈值的账号自动降权
- 让所有订阅账号平滑消耗

适用场景：
- 多订阅账户池
- 目标是把总可用时间拉长而不是榨干个别账号

### 3. Latency Based

目标：**尽可能快，优先 TTFT 与 P95。**

权重倾向：
- `W_latency` 最高
- `W_availability` 高
- `W_load` 高
- `W_cost` 低至中

行为：
- 使用 TTFT/E2E 的 EWMA
- 慢节点快速降权
- 保留极小探针流量继续观察其它候选

适用场景：
- 用户交互式 chat
- 编码助手
- 高 SLA 面向终端用户的业务请求

### 4. All-in-One（全都要）

目标：**在成本、稳定性、延迟、配额分散之间找 Pareto 最优。**

建议逻辑：
- Availability 是硬门槛，不参与妥协
- 在健康候选中，对 cost / latency / quota / load 做加权评分
- 对接近阈值的 quota 和 load 增加非线性惩罚

适用场景：
- 默认路由模板
- 平台级通用模式

---

## 十一、退避、熔断、Fallback、降级策略设计

### 1. 退避（Backoff）

建议按错误类型分层处理：

- `429`：优先视为容量问题，快速降权 + 短期退避
- `5xx / timeout / connection refused`：视为健康问题，进入 breaker 计数
- `4xx capability mismatch`：不重试，直接切换兼容候选或降级

退避建议：
- 指数退避 + jitter
- 对 supply unit 本地生效，而不是影响整个 provider 品牌

### 2. 熔断（Circuit Breaker）

建议使用三态：
- `closed`
- `open`
- `half-open`

建议触发因素：
- 连续失败阈值
- 最近窗口错误率
- 连续 429 比例过高
- 连续 timeout

恢复策略：
- open 到期后进入 half-open
- 只放极少探针流量
- 成功后逐步恢复权重，而不是一步恢复

### 3. Fallback

建议分 3 层：

1. **同模型，同层候选切换**  
   例如同为 `gpt-4o` 的不同账号/endpoint
2. **同能力，不同 provider 切换**  
   例如从 OpenAI `gpt-4o` 切到 Azure `gpt-4o`
3. **模型能力降级**  
   例如从 Sonnet / GPT-4 级切到 mini 级

### 4. 降级（Degradation）

不建议把降级写成“最后兜底的 if/else”。建议把它产品化：

- 定义 canonical model family
- 定义 degrade chain
- 定义哪些请求允许 degrade
- 定义 degrade 后要不要告知上层

示例：

```text
claude-sonnet-class
  -> claude-haiku-class
  -> gpt-4o-mini-class
```

---

## 十二、粘性会话与语义路由该怎么做

### 1. 粘性会话

建议支持，但不是默认强绑定。

适用场景：
- 多轮对话
- prefix cache / KV cache 可复用
- 用户体验更需要连续性

机制建议：
- 基于 `session_id` / `conversation_id` 做 consistent hash
- 设置 TTL
- 当原目标明显不健康时允许打破粘性

### 2. 语义化路由

建议作为增强层，而不是核心第一阶段。

原因：
- 你的产品第一优先级是 SLA，不是 prompt classifier
- 语义路由的收益要建立在稳定供给调度之上

推荐落地方式：
- 先支持轻量 task tags（code / reasoning / cheap / vision / long-context）
- 后续再增加 embedding / classifier 驱动的 semantic routing

---

## 十三、调度引擎建议：先做可解释评分，再考虑 Bandit

从产品节奏上，不建议一开始就上多臂老虎机或强化学习。

### Phase 1：可解释评分引擎

优点：
- 易于调试
- 易于产品化
- 易于让客户理解“为什么这样选”

### Phase 2：自适应动态调权

在评分引擎基础上加入：
- EWMA latency
- EWMA health
- quota depletion penalty
- dynamic weight decay

### Phase 3：探索式智能调度

后续再引入：
- contextual bandit
- budget-paced optimization
- reward based on success × latency × cost × user satisfaction

建议顺序是：

> 先把工业级调度和可解释性做好，再引入学习式优化。

---

## 十四、产品架构建议：控制面 + 数据面分离

### 控制面

负责：
- 供给配置管理
- canonical model / degrade chain 管理
- routing template 管理
- quota / budget / policy 配置
- 可视化路由解释

### 数据面

负责：
- 高性能转发
- 流式代理
- 请求生命周期管理
- 实时状态更新
- breaker / retry / fallback 执行

这样做的好处：
- 配置变更与转发性能解耦
- 后续可做多节点水平扩展
- 有利于把“策略”和“执行”拆开

---

## 十五、可观测性：这是产品核心，不是附属功能

你的产品如果要卖“稳定”，那就必须能解释稳定性。

建议每次路由都记录：

- 请求画像
- 候选池规模
- 被过滤原因
- 每个候选的评分明细
- 最终选中的候选
- 是否发生 retry / fallback / degradation
- 请求最终结果
- cost / tokens / latency / TTFT

建议提供 4 个关键视图：

1. **供给池健康看板**
2. **路由解释看板**
3. **账号/额度消耗看板**
4. **SLA 看板（成功率/TTFT/P95/降级率）**

---

## 十六、你产品的核心优势应该怎么讲

### 1. 从“供应商路由”升级为“供给调度”

别人是在 provider 之间切换；你是在**账号、凭证、endpoint、模型能力、约束条件**构成的供给池里做实时调度。

### 2. 从“静态权重”升级为“实时动态权重”

你的权重不是配置值，而是实时状态函数。

### 3. 从“fallback 补丁”升级为“分层恢复系统”

retry、backoff、breaker、fallback、degradation 统一纳入主流程。

### 4. 从“规则树”升级为“目标函数”

支持 cost、quota、latency、balanced 四类模板，本质上是同一个评分引擎的不同目标函数。

### 5. 从“看日志排查”升级为“可解释路由”

每个请求都能解释：为什么不用 A，用了 B；为什么从订阅切到按量；为什么降级。

---

## 十七、建议的 MVP 范围

第一阶段不要做全量“最智能”。建议先把最有价值、最能体现差异化的部分做出来。

### MVP 必做

1. Supply Unit 数据模型
2. canonical model alias + capability tags
3. Eligibility Filter
4. 可解释评分路由
5. 四类 routing templates
6. breaker / retry / fallback / degrade
7. quota-aware + concurrency-aware 降权
8. 路由解释日志

### 第二阶段再做

1. 语义路由
2. sticky session + cache aware routing
3. 多区域感知
4. 自适应权重学习
5. 预算 pacing / bandit routing

---

## 十八、最终建议：你的产品该如何定义“核心路线”

如果只保留一句话，我建议是：

> **用供给建模 + 实时状态 + 多目标评分，把 AI Gateway 从“规则代理”做成“LLM 供给调度系统”。**

更具体一点：

- **数据模型上**：以 `Account / Supply Unit` 为核心，而不是只以 provider 为核心
- **策略模型上**：以 `硬约束筛选 + 多目标评分 + 分层回退` 为核心
- **产品定义上**：以 `SLA 保证` 为首要卖点，成本和速度是目标函数中的优化维度
- **落地顺序上**：先做可解释、可控、能上线的调度引擎，再做 bandit/semantic 等增强项

这条路线比“继续堆规则”更有机会形成真正的产品壁垒。

---

## 十九、参考依据（本次方案综合使用）

### 仓库内已有研究

- `reports/llm-gateway-routing-research/llm-gateway-load-balancing-research.md`
- `reports/bifrost-competitors-20260415/competitor-report.md`
- `reports/bifrost-competitors-20260415/load-balancing-algorithms-report.md`
- `reports/ai-gateway-maturity-analysis-20260415/final-maturity-report.md`
- `reports/ai-gateway-routing-best-practices.md`

### 重点外部文档（来自已有研究汇总）

- Portkey Load Balancing / Fallbacks / Conditional Routing
- LiteLLM Routing / Reliability / Health Check Routing
- Kong AI Gateway Load Balancing / AI Proxy Advanced
- OpenRouter Provider Selection / Model Fallbacks
- Cloudflare AI Gateway Dynamic Routing
- Braintrust Gateway
- Envoy Peak EWMA
- Solo.io AgentGateway LLM Load Balancing
- ParetoBandit / MixLLM / Preference-Conditioned Dynamic Routing

---

## 二十、下一步建议

如果你下一步要继续推进，我建议顺序是：

1. 先把 **实体模型 + 状态模型 + 评分模型** 固化成技术设计文档
2. 再定义 **Routing Template DSL / 配置结构**
3. 再拆 **控制面 / 数据面 / 存储 / 状态同步 / Telemetry** 的实现计划
4. 最后再补 **语义路由 / 学习式调权**

如果需要，我下一轮可以直接继续产出：

1. **实体 ER / 数据库 Schema 草案**
2. **Routing Engine 评分公式与状态机设计**
3. **MVP 技术架构图与模块拆分**
4. **产品 PRD / 对外定位文案**
