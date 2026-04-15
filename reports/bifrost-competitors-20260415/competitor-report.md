# Bifrost 竞品调研（聚焦高可用自动路由 + 遥测）

调研目标：寻找 `https://github.com/maximhq/bifrost` 的竞品，重点筛选两类能力：

1. **模型自动路由（高可用）**
   - 同一模型别名按权重分流，例如 `gpt-5.4 -> provider1/provider2 = 50/50`
   - 当某 provider 出现 `Connection Refused`、`429` 等错误时，自动摘除并在一段可配置时间后恢复
   - 当当前层全部失效时，继续 fallback 到下一个 provider / 下一个模型
2. **遥测数据**
   - 使用量、错误、缓存命中、价格/成本、延迟、请求日志

---

## 结论先看

如果把你的需求拆成“**高可用自动路由**”和“**内建遥测**”两条，当前更值得优先看的竞品是：

### 第一梯队（最贴近你的目标）

1. **LiteLLM**
   - 优势：路由/冷却/失败摘除能力成熟，生态最成熟，支持多 provider、多部署、权重、fallback、健康检查路由。
   - 短板：遥测更偏 Prometheus/Grafana 外接，缓存命中分析不如 Helicone/Portkey 那样开箱即用。

2. **Portkey AI Gateway**
   - 优势：权重负载均衡、fallback 链、嵌套路由、日志和分析能力强，内建成本/缓存/请求追踪更完整。
   - 短板：官方文档对“provider 摘除多久、是否是 circuit breaker 语义”描述不如 LiteLLM/Kong 明确。

3. **Helicone AI Gateway**
   - 优势：遥测能力非常强，成本、缓存命中、请求日志、错误、provider routing 都是第一类能力。
   - 短板：自动路由更偏“自动选最便宜 provider + fallback”，显式的权重分流能力不如 Portkey / LiteLLM / Kong 清晰。

4. **Kong AI Gateway**
   - 优势：企业级最强，明确支持负载均衡算法、fallback、health check、circuit breaker、OTel/Prometheus。
   - 短板：更重、更偏企业栈；很多高级能力在 Enterprise / AI Proxy Advanced。

### 第二梯队（值得关注，但更偏某个方向）

5. **Routerly**
   - 优势：自托管、内建 dashboard、成本与预算、健康策略、自动 failover，整体产品完整。
   - 短板：更偏“智能路由 + 健康优先”，对你要的“精确权重 + 明确摘除窗口”证据没 LiteLLM/Portkey 那么强。

6. **Ferro Labs AI Gateway**
   - 优势：Go 写的，性能强，支持 fallback、loadbalance、重试状态码过滤、Prometheus、dashboard、usage stats。
   - 短板：生态和成熟度还不如 LiteLLM/Kong。

7. **Olla**
   - 优势：高性能、健康检查、circuit breaker、自动 failover，很适合本地/自建推理节点。
   - 短板：更像“推理负载均衡层”，不是完整的成本/业务级 AI gateway 平台。

---

## 与你需求的贴合度对比

| 产品 | 权重分流 | 失败摘除/冷却 | 多级 fallback | 跨模型 fallback | 使用/错误遥测 | 缓存命中 | 成本/价格 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LiteLLM | ✅ | ✅ 很强 | ✅ | ✅ | ✅ | ⚠️ 偏外接 | ✅ |
| Portkey | ✅ | ⚠️ 有但文档不够细 | ✅ 很强 | ✅ | ✅ 很强 | ✅ | ✅ |
| Helicone | ⚠️ 未见强权重证据 | ✅ 自动 failover | ✅ | ✅ | ✅ 很强 | ✅ 很强 | ✅ 很强 |
| Kong AI Gateway | ✅ 很强 | ✅ 很强 | ✅ 很强 | ✅ | ⚠️ 偏外接 | ⚠️ 偏外接 | ⚠️ 偏外接 |
| Routerly | ⚠️ 更偏策略评分 | ✅ | ✅ | ✅ | ✅ | 未见强证据 | ✅ |
| Ferro Labs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Olla | ✅ | ✅ 很强 | ✅ | ⚠️ 有限 | ⚠️ 基础指标 | 未见强证据 | ⚠️ 弱 |

说明：
- `✅` = 官方文档或 README 有明确证据
- `⚠️` = 有能力迹象，但证据不够明确，或能力依赖外部系统

---

## 重点竞品详解

## 1) LiteLLM

- GitHub: https://github.com/BerriAI/litellm
- 定位：最成熟的开源 LLM Gateway / Proxy 之一

### 高可用自动路由

官方文档明确支持：

- **权重分流**：`weight` 字段可控制同一模型下多个 deployment 的流量比例。
- **部署优先级**：`order` 字段支持同模型的主备优先级；高优 deployment 失败后，自动尝试更低优先级 deployment。
- **冷却（cooldown）**：
  - 支持 `allowed_fails`
  - 支持 `cooldown_time`
  - 文档写明 429 / 401 / 404 / 408 等会触发 cooldown
- **健康检查驱动路由**：
  - `background_health_checks: true`
  - `enable_health_check_routing: true`
  - `allowed_fails_policy` 可对不同错误类型单独设阈值
  - `cooldown_time` 可配置

这意味着你要的模式基本可以表达成：

- `model_name: gpt-5.4` 下挂多个 deployment
- provider1/provider2 用 `weight: 1 / 1` 做 50/50
- `429` 或错误率超阈值时 deployment 进入 cooldown
- 所有同层 deployment 都不可用时，依靠 `order` / fallback 再跳到 provider3/provider4

### 遥测

- 有请求/延迟/失败/花费统计
- Prometheus 指标很多（token、cost、latency、failures）
- 但**缓存命中分析**和可视化更依赖 Prometheus/Grafana，而不是“开箱即用强 dashboard”

### 适合你的原因

- 如果你最看重**高可用路由控制力**，LiteLLM 是当前最像“工程化 Bifrost 替代品”的选项之一。

---

## 2) Portkey AI Gateway

- Docs: https://docs.portkey.ai/
- 定位：商用成熟度高，路由策略组合能力很强

### 高可用自动路由

官方文档明确支持：

- **loadbalance** 模式下 `weight`
- **fallback** 模式下按优先级链式切换
- 可设置 `on_status_codes: [429, 503]`
- 路由可以**嵌套组合**：
  - `conditional -> loadbalance`
  - `fallback -> loadbalance`
  - `fallback -> conditional`

这点非常适合你的场景，因为你要的是：

1. 同模型别名下先做 50/50 分流
2. 某 provider 出错时局部切换
3. 整个 cluster 不行时继续 fallback 到 provider3 / provider4

Portkey 的组合路由可以把这个逻辑表达得很自然。

### 遥测

- **内建日志与分析很强**
- 支持：
  - 请求日志
  - Trace ID 追踪 fallback 链
  - cost / latency / error 分析
  - cache hit / semantic cache hit / miss
  - Prometheus 指标

### 适合你的原因

- 如果你不只关心路由，还关心**把“路由发生了什么”看清楚**，Portkey 很有竞争力。

---

## 3) Helicone AI Gateway

- Docs: https://docs.helicone.ai/gateway/overview
- 定位：AI Gateway + Observability 平台

### 高可用自动路由

官方文档明确支持：

- 自动 provider routing
- cheapest-first 选择策略
- provider 出错时即时 failover
- 支持手工 fallback chain，例如：
  - `gpt-4o-mini/azure,gpt-4o-mini/openai,gpt-4o-mini`

支持的 failover 触发错误包括：

- `429`
- `401`
- `400`（上下文长度）
- `408`
- `500+`

### 遥测

这是 Helicone 的强项：

- usage analytics
- request logs
- latency
- token / cost accounting
- session 级成本归因
- caching 可视化
- `Helicone-Cache: HIT/MISS`

### 适合你的原因

- 如果你要的是“**网关 + 可观测性平台二合一**”，Helicone 很强。
- 如果你要非常明确的“50/50 + 冷却 1h + 明确 circuit breaker 状态机”，它不如 LiteLLM / Kong 那么硬核。

---

## 4) Kong AI Gateway

- Docs: https://docs.konghq.com/gateway/latest/ai-gateway/
- 插件: https://docs.konghq.com/plugins/ai-proxy-advanced
- 定位：企业级 API Gateway 扩展到 AI / MCP / A2A

### 高可用自动路由

Kong 的官方能力非常完整：

- 多种负载均衡算法：
  - weighted round-robin
  - least-connections
  - lowest-latency
  - lowest-usage
  - semantic
  - priority
- **retry and fallback**
- `failover_criteria` 可配置，支持把 `http_429`、`http_502` 之类纳入 failover 条件
- **circuit breaker**：
  - `max_fails`
  - `fail_timeout`

这和你说的“踢掉 provider 5 分钟 / 1 小时 / 到第二天”是同一类能力模型。

### 遥测

- OTel
- Prometheus
- audit log
- token / cost / latency metrics
- Konnect analytics

但很多可视化依赖 Kong 的 observability 套件，开箱即用程度不如 Portkey/Helicone。

### 适合你的原因

- 如果你偏**平台工程 / API Gateway 体系**，Kong 是很强的企业解。
- 如果你只是要一个轻量 LLM router，它可能偏重。

---

## 5) Routerly

- GitHub: https://github.com/Inebrio/Routerly
- 定位：自托管、零外部依赖、智能策略路由

### 高可用自动路由

官方证据：

- 9 种 routing policies
- `health` policy 会根据最近错误降低优先级
- provider fail 时自动 reroute
- 可跨多个 provider / 多个模型做自动选择

它更偏“**策略评分 + 自动选路**”，而不是你精确描述的“circuit breaker / cooldown 窗口可编排”。

### 遥测

- 内建 dashboard
- 实时 cost tracking
- call volume
- error rates
- per-model breakdown
- budget enforcement

### 结论

- 很像 Bifrost 的“智能控制面”方向。
- 如果你接受更策略化、而不是非常硬的故障摘除状态机，值得看。

---

## 6) Ferro Labs AI Gateway

- GitHub: https://github.com/ferro-labs/ai-gateway
- 定位：Go 写的高性能 AI Gateway

### 高可用自动路由

官方证据：

- 8 种 routing strategies
- fallback / load balance / least latency / cost-optimized
- 可针对状态码配置 retry，比如 `429, 502, 503`
- weighted load balancing 示例明确存在

### 遥测

- Prometheus `/metrics`
- `/health` provider status
- usage stats
- request logs
- built-in dashboard
- SQLite/PostgreSQL 持久化

### 结论

- 如果你想要 **Go + 高性能 + 比 LiteLLM 更轻** 的实现，Ferro 值得认真看。

---

## 7) Olla

- Docs: https://thushan.github.io/olla/
- 定位：高性能 LLM proxy / load balancer，偏自建推理基础设施

### 高可用自动路由

- round-robin / least-connections / priority
- circuit breaker
- health monitoring
- automatic failover

### 遥测

- metrics
- tracing
- response headers（endpoint/model/response-time）

### 结论

- 如果你的核心是“**本地推理 / vLLM / Ollama / 自建节点池**”，Olla 很好。
- 如果你要的是“跨 SaaS provider 的完整成本治理平台”，它不是第一选择。

---

## 哪些最适合你当前的需求

### 如果你最在意“和你描述的故障切换逻辑最像”

优先顺序建议：

1. **LiteLLM**
2. **Kong AI Gateway**
3. **Portkey**
4. **Ferro Labs**

原因：

- 都能明确表达同模型多 deployment / 多 provider 路由
- 都有较强的 fallback / health / retry 概念
- LiteLLM / Kong 对 cooldown / failover 条件的描述最硬

### 如果你最在意“遥测一体化，最好开箱就能看”

优先顺序建议：

1. **Helicone**
2. **Portkey**
3. **Routerly**
4. **LiteLLM**

原因：

- Helicone / Portkey 在 usage / cost / cache / request trace 上最完整
- LiteLLM 强在路由和生态，但可观测性更偏外接 Prometheus 栈

### 如果你要“综合平衡”

我会给出这个 shortlist：

1. **LiteLLM** — 最像工程型替代品
2. **Portkey** — 路由 + 遥测最平衡
3. **Helicone** — 遥测最强
4. **Kong AI Gateway** — 企业级最强但偏重
5. **Routerly** — 新但方向很像 Bifrost

---

## 对你的两个需求的直接判断

### 需求 1：模型自动路由（高可用）

你给的例子：

- `model: gpt-5.4`
- provider1/provider2 50/50
- provider1 出现 `Connection Refuse` 或 `429` -> 摘除 5 分钟 / 1 小时 / 到次日
- provider1/provider2 同时失效 -> 用 provider3
- 再失效 -> provider4/gpt-5.3-codex

**最像这个模型的产品：**

- **LiteLLM**
- **Kong AI Gateway**
- **Portkey**

其中：

- **LiteLLM**：最容易靠 deployment + weight + cooldown + health_check_routing 拼出来
- **Kong**：最标准的 gateway/circuit-breaker 语义
- **Portkey**：最容易把“多层路由图”表达清楚

### 需求 2：遥测数据（usage / errors / cache hit / price）

**最强：**

- **Helicone**
- **Portkey**

**次强但偏平台工程化：**

- **LiteLLM**
- **Kong**

---

## 最终建议

如果你问我“该先试哪 3 个”，我建议：

1. **LiteLLM** — 验证高可用自动路由模型
2. **Portkey** — 验证复杂路由 + 遥测一体化
3. **Helicone** — 验证 observability 深度

如果你更偏企业网关体系，再加：

4. **Kong AI Gateway**

如果你更偏自托管且喜欢新产品路线，再加：

5. **Routerly**

---

## 主要来源

- Bifrost: https://github.com/maximhq/bifrost
- LiteLLM routing: https://docs.litellm.ai/docs/routing
- LiteLLM health check routing: https://docs.litellm.ai/docs/proxy/health_check_routing
- Portkey load balancing: https://docs.portkey.ai/docs/product/ai-gateway/load-balancing
- Portkey fallbacks: https://docs.portkey.ai/docs/product/ai-gateway/fallbacks
- Helicone gateway overview: https://docs.helicone.ai/gateway/overview
- Helicone provider routing: https://docs.helicone.ai/gateway/provider-routing
- Helicone cost tracking: https://docs.helicone.ai/guides/cookbooks/cost-tracking
- Kong AI Gateway: https://docs.konghq.com/gateway/latest/ai-gateway/
- Kong AI Proxy Advanced: https://docs.konghq.com/plugins/ai-proxy-advanced
- Routerly: https://github.com/Inebrio/Routerly
- Ferro Labs AI Gateway: https://github.com/ferro-labs/ai-gateway
- Olla: https://thushan.github.io/olla/
