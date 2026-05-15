# Bifrost 竞品专项分析：负载均衡算法与路由语义

这份报告只回答一个问题：**这些竞品到底用什么负载均衡算法，它们的“选路”规则是什么，和你要的高可用模型自动路由差在哪。**

重点不是“谁强谁弱”的口头判断，而是：

1. **算法名字是否明确写在官方文档里**
2. **算法的实际选择规则是否被解释清楚**
3. **算法是否和健康检查 / 摘除 / fallback / cooldown 联动**
4. **是否能表达你的目标场景**

你的目标场景再明确一下：

- `model = gpt-5.4`
- 同层两个 provider 做 **50/50 分流**
- 某 provider 出现 `Connection Refused`、`429` 之类错误时，**临时摘除**
- 摘除窗口可配置：5 分钟 / 1 小时 / 到第二天
- 第一层都失效后，切到 `provider3/gpt-5.4`
- 再失效后，切到 `provider4/gpt-5.3-codex`

---

## 一、先给结论

如果只看“**负载均衡算法本身**”而不是整个产品包装，当前最值得关注的 4 家是：

1. **Kong AI Gateway** — 算法最完整、语义最清晰
2. **LiteLLM** — 多策略路由最灵活，和 LLM gateway 场景贴合最好
3. **Portkey** — 加权负载均衡 + fallback 组合能力强，但算法种类较少
4. **Helicone** — 不是通用 LB 算法平台，更像“成本优先的自动 provider router”

如果把开源/自托管也纳进来：

5. **Ferro Labs AI Gateway** — 路由模式多，偏实用型
6. **Routerly** — 更像“多策略评分引擎”，不是传统 LB
7. **Olla** — 偏基础设施层，高性能，算法简单直接
8. **APISIX AI Gateway** — AI 层算法较少，但传统网关语义成熟

---

## 二、算法能力总表

| 产品 | Weighted | Sticky / Hash | Least Conn / Busy | Latency-Based | Cost-Based | Priority / Tier | Semantic / LLM-native | 健康摘除/熔断 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kong AI Gateway | ✅ | ✅ | ✅ | ✅ Peak EWMA | ✅ Lowest usage / cost | ✅ | ✅ semantic | ✅ 明确 |
| LiteLLM | ✅ | ⚠️ 非强项 | ✅ least-busy | ✅ latency-based | ✅ cost-based | ✅ order | ⚠️ custom | ✅ cooldown / health-check |
| Portkey | ✅ | ✅ sticky session | ❌ | ❌ | ⚠️ 通过权重表达成本偏置 | ✅ 通过 fallback 组合 | ✅ conditional routing | ⚠️ 有，但描述偏组合式 |
| Helicone | ⚠️ 有 equal-cost LB | ❌ | ❌ | ⚠️ 间接 latency/availability | ✅ cheapest-first | ✅ 手工 fallback chain | ❌ | ✅ 自动 failover |
| Ferro Labs | ✅ | ❌ | ❌ | ✅ least-latency | ✅ cost-optimized | ✅ fallback order | ✅ content-based | ✅ circuit breaker |
| Routerly | ⚠️ fairness policy | ❌ | ❌ | ✅ performance policy | ✅ cheapest policy | ⚠️ 排名式而非显式层级 | ✅ LLM policy | ✅ health policy |
| Olla | ✅（同优先级加权） | ❌ | ✅ | ❌ | ❌ | ✅ priority | ❌ | ✅ circuit breaker |
| APISIX | ✅ roundrobin | ✅ chash | ❌ | ❌ | ❌ | ✅ priority | ❌ | ✅ health checks + fallback |

---

## 三、逐家拆解：算法是什么，证据在哪里

## 1) Kong AI Gateway

### 官方明确列出的算法

Kong 官方文档对算法是写得最明确的一家，直接列出：

- **Round-robin (weighted)**
- **Consistent-hashing**
- **Least-connections**
- **Lowest-usage**
- **Lowest-latency**
- **Semantic**
- **Priority**

### 证据

官方文档 `Load balancing with AI Proxy Advanced` 明确说明：

- `Round-robin (weighted)`：按权重比例分发流量，且**不考虑 usage / latency / cache-hit ratio**
- `Consistent-hashing`：对 header 做 hash，相同值稳定落到同一个 target，用于 sticky session
- `Least-connections`：跟踪每个 backend 的 in-flight requests，把新请求送给“剩余容量最高”的 backend
- `Lowest-usage`：按 token 或 cost 之类的实际消耗来选最空闲/最便宜的 target
- `Lowest-latency`：明确写的是 **peak EWMA (Exponentially Weighted Moving Average)**
- `Semantic`：通过 embeddings + vector search 按语义相似度选模型
- `Priority`：**始终先用最高优先级组，整组不可用后再落到下一组**；组内再按 `weight` 分流

### 为什么这很重要

Kong 不是只有“支持很多算法”这么简单，而是它把 **算法层** 和 **故障层** 分开建模了：

- 算法决定“平时怎么选”
- `failover_criteria` 决定“什么错误算失败”
- `max_fails` / `fail_timeout` 决定“失败后摘除多久”

这很接近经典 API Gateway / service mesh 的路由语义。

### 对你场景的映射

你要的场景可以非常自然地表示成：

1. 第一层用 `Priority` group 1
2. group 1 内部用 `Round-robin (weighted)` 做 50/50
3. 当某 target 满足 `http_429`、`timeout`、`error` 等 `failover_criteria` 时 failover
4. 当目标达到 `max_fails` 后进入 circuit breaker，`fail_timeout` 后再探测恢复
5. group 1 全挂后，退到 group 2 / group 3

### 结论

**如果你最关注“负载均衡算法”本身，Kong 是当前文档最硬、语义最标准的一家。**

---

## 2) LiteLLM

### 官方明确列出的算法 / 策略

LiteLLM 官方不是用“LB algorithms”这个词，而是用 `routing strategies`，但实质上已经是算法层：

- `simple-shuffle`（默认）
- `least-busy`
- `latency-based-routing`
- `usage-based-routing`
- `cost-based-routing`
- `custom routing strategy`

另外它还有：

- `weight`
- `rpm/tpm`
- `order`
- `cooldown_time`
- `allowed_fails_policy`
- `background_health_checks`

### 证据

LiteLLM 官方路由文档明确写到：

- `simple-shuffle` 是默认并推荐用于生产的策略
- 如果设置 `weight`，就会按权重 pick deployment
- 如果设置 `rpm` / `tpm`，会做基于速率限制感知的选择
- `least-busy` 是按**当前 in-flight requests 最少**选 deployment
- `latency-based-routing` 会缓存和更新 deployment 的 response time，并支持：
  - `ttl`
  - `lowest_latency_buffer`
- `cost-based-routing` 会检查每个 deployment 对应模型的定价，选择最低成本

LiteLLM 还明确说明：

- `order=1` 失败后自动尝试 `order=2`
- `429`、401、404、408、失败率过高等情况会触发 cooldown
- cooldown 是**按 deployment 生效，不是按整个 model group 生效**
- 后台健康检查路由可以在用户请求打到坏节点之前先把它移出池子

### 这里真正厉害的地方

LiteLLM 的强点不是“某个单独算法比别人强”，而是它把这些东西拼成了一个比较完整的 LLM router：

- 平时：可以按权重 / 使用量 / 延迟 / 成本选
- 出错：deployment 级 cooldown
- 层级：`order` 实现优先级 fallback
- 主动：background health check 提前剔除坏节点

### 对你场景的映射

你的例子在 LiteLLM 里很像：

1. `model_name: gpt-5.4` 下挂多个 deployment
2. provider1 / provider2 各设 `weight: 1`
3. 某个 deployment 出现 `429` 或达到失败阈值后进入 cooldown
4. 同一 model group 内剩余健康 deployment 继续接流量
5. 若高优层失败，用 `order` 或 fallback 再跳到 provider3
6. 再失败后跳到更低层模型

### 和 Kong 的核心区别

- Kong 更像“标准网关负载均衡器”
- LiteLLM 更像“专门为 LLM provider / deployment 写的多策略路由器”

### 结论

**如果你最关心的是“LLM 场景下的工程可操作性”，LiteLLM 很可能比 Kong 更贴近你的实际需求。**

---

## 3) Portkey

### 算法到底是什么

Portkey 的核心不是一大串不同算法，而是：

- `loadbalance`
- `fallback`
- `conditional`

也就是说，它更像一个**可组合路由图引擎**。

在 `loadbalance` 这层，官方给出的机制是非常明确的：

1. 每个 target 定义 `weight`
2. 权重做归一化
3. 每个请求按归一化概率分配给某个 target

这本质上是：

**加权概率分流（weighted probabilistic distribution）**

### 证据

官方文档 `Load Balancing` 明确写了：

- 权重会被归一化到 100%
- `weight: 0` 可以停流但不移除 target
- sticky load balancing 通过 `hash_fields` + `ttl` 进行一致性路由
- sticky session 使用两层缓存（内存 + Redis）

官方示例也很直接：

- provider 间 0.7 / 0.3 分流
- model 间 0.75 / 0.25 分流
- 同 provider 多 API keys 负载均衡
- old/new model 的渐进式迁移

### 这意味着什么

Portkey 的负载均衡不是：

- least connections
- latency aware
- peak EWMA
- cost aware runtime scoring

而是：

- **你先定义一张路由图**
- 某些边是 weighted load balancing
- 某些边是 fallback
- 某些边是 conditional match

### 对你场景的映射

Portkey 对你需求的适配非常强，但强点不在“算法种类”，而在“组合表达能力”：

1. 第一层 `loadbalance`：provider1/provider2 各 0.5
2. 第一层外包一层 `fallback`
3. 当整个第一层 cluster 不可用时，切到 provider3
4. 再切到 provider4/gpt-5.3-codex

### 它和 LiteLLM / Kong 的差异

- LiteLLM / Kong 更偏“多种 runtime selection algorithms”
- Portkey 更偏“组合式 traffic graph”

### 结论

**如果你要的是“明确、可配置、可视化的路由图”，Portkey 很强；如果你要比较丰富的负载均衡算法菜单，Portkey 不如 Kong / LiteLLM。**

---

## 4) Helicone

### 算法到底是什么

Helicone 不是典型的多算法负载均衡平台。

它官方文档写得很直白：

- 找到所有支持该模型的 provider
- **优先选最便宜的 provider**
- 如果价格一样，则在 equal-cost providers 之间做 load balancing
- 出错时即时 failover 到下一个 provider

### 证据

官方 `Provider Routing` 文档写明：

- `Selection: Routes to the cheapest provider first. Equal-cost providers are load balanced.`
- `Failover: Instantly tries the next provider on errors (rate limits, timeouts, server errors, etc.)`
- BYOK keys 优先，然后才用 Helicone managed keys

此外还有：

- 手工 fallback chain：`model: "gpt-4o-mini/azure,gpt-4o-mini/openai,gpt-4o-mini"`
- 失败触发错误：429 / 401 / 400 / 408 / 500+

### 这里要非常明确

Helicone 的默认路由逻辑不是你传统理解中的“负载均衡算法库”，而是：

**成本优先的自动 provider 路由器**

更像：

- 第一步：按成本排序
- 第二步：同价目标之间再做分摊
- 第三步：失败时继续下探

### 对你场景的适配程度

它能做：

- 自动跨 provider 路由
- 自动 failover
- 手工 provider chain

但如果你要的是：

- provider1/provider2 严格 50/50
- 明确 cooldown 1h / 5m / 24h
- circuit breaker state machine

Helicone 的文档证据明显不如 LiteLLM / Kong。

### 结论

**Helicone 更像“自动 provider optimizer”，不是“强算法型 LLM load balancer”。**

---

## 5) Ferro Labs AI Gateway

### 官方列出的模式

Ferro README 和文档给出的 routing modes 有：

- `single`
- `fallback`
- `loadbalance`
- `conditional`
- `least-latency`
- `cost-optimized`
- `content-based`
- `ab-test`

### 证据

Ferro 明确给出：

- `loadbalance`：Weighted load balancing，例如 70/30
- `least-latency`：按 rolling latency 选最优 target
- `cost-optimized`：基于模型 catalog 的 pricing 数据估算成本后选最便宜目标
- `content-based`：按 prompt 的 regex / substring 做路由
- `fallback`：顺序尝试 targets，并支持 `on_status_codes: [429, 502, 503]`
- `circuit_breaker`：
  - `failure_threshold`
  - `success_threshold`
  - `timeout`

这说明 Ferro 的“负载均衡算法”其实和 Portkey 不同，它更像一组**明确互斥的 routing modes**。

### 和 LiteLLM 的区别

- LiteLLM 是一个单路由器 + 多策略选择框架
- Ferro 更像“多种模式切换器”

### 结论

**如果你喜欢 Go 实现，且希望算法比较直白、性能强、配置简单，Ferro 很值得看。**

---

## 6) Routerly

### 它不是传统 LB，而是多策略评分器

Routerly 最特别的一点是：它几乎不把自己描述成传统 load balancer，而是一个 **intelligent multi-policy routing engine**。

官方明确列出 9 个 policy：

- `llm`
- `cheapest`
- `health`
- `performance`
- `capability`
- `context`
- `budget-remaining`
- `rate-limit`
- `fairness`

### 证据

官方 README 写得很清楚：

- `Each request is scored against up to 9 pluggable routing policies, applied simultaneously and combined into a final ranking.`
- `fairness` policy：balances load across candidates
- `health`：deprioritizes models with recent errors
- `performance`：favors models with lower average latency
- `cheapest`：minimizes cost per token

### 这和传统负载均衡有本质区别

传统 LB 在问：

- 这次请求分给哪个节点？

Routerly 在问：

- 对这个具体请求，哪个候选模型综合得分最高？

所以它不是：

- weighted round robin
- least connections
- peak EWMA

而是：

- 多维评分 → 排名 → 选择

### 对你场景的适配度

它对“智能选模型”很强，但你要的“严格 50/50 + 明确摘除时间窗 + 分层 fallback”并不是它文档最强的表达方向。

### 结论

**Routerly 适合“智能路由”，不适合把它当成最标准的负载均衡器去比较。**

---

## 7) Olla

### 明确算法

Olla 文档非常清楚地列出：

- `priority`（默认）
- `round-robin`
- `least-connections`

### 证据

官方文档写到：

- Priority strategy：
  1. 先选最高 priority tier
  2. 同 tier 内使用 weighted random
  3. 更高 tier 挂掉后自动退到更低 tier
- 所有策略都遵守 endpoint health status
- circuit breaker 有 closed / open / half-open

同时还给出了不同健康状态的权重：

- Healthy = 1.0
- Busy = 0.3
- Warming = 0.1
- Unhealthy = 0.0

### 对你场景的意义

这意味着 Olla 更像：

- 基础设施层的负载均衡器
- 优先级 + 健康状态 + 自动 failover

但它没有 LiteLLM / Kong 那样丰富的高层模型路由语义。

### 结论

**如果你在做自建推理节点池，Olla 的算法足够好；如果你在做多 SaaS provider 的精细化 LLM gateway，它不如 LiteLLM / Kong。**

---

## 8) APISIX AI Gateway

### 官方明确能力

APISIX 的 `ai-proxy-multi` 目前文档明确的 balancer 算法是：

- `roundrobin`
- `chash`

另外还有：

- `priority`
- `fallback_strategy`
- `checks.active`

### 证据

官方文档直接写到：

- `balancer.algorithm: roundrobin, chash`
- `priority takes precedence over weight`
- `fallback_strategy` 可用：
  - `instance_health_and_rate_limiting`
  - `http_429`
  - `http_5xx`

### 结论

APISIX 的 AI routing 更像是在传统 API Gateway 负载均衡能力上，给 AI 增加 provider/fallback/health 语义。

不是算法最多，但语义很稳。

---

## 四、把“算法”和“高可用”分开看

这是最容易混淆的点。

很多产品会把下面这些混在一起宣传：

- 负载均衡算法
- fallback
- retry
- health check
- circuit breaker
- semantic routing

但它们不是一回事。

### 真正的“负载均衡算法”

- weighted round robin / weighted random
- consistent hashing / sticky session
- least connections / least busy
- lowest latency / EWMA
- lowest usage / least tokens / least cost

### 真正的“高可用机制”

- health checks
- cooldown
- circuit breaker
- retry
- fallback chain

### 真正的“智能路由机制”

- semantic routing
- LLM-native routing
- content-based routing
- conditional routing

**Kong** 是三类都做得比较全的。  
**LiteLLM** 在“算法 + 高可用”上很平衡。  
**Portkey** 更强在“组合式高可用路由图”。  
**Helicone** 更强在“成本优先自动选 provider”。  
**Routerly** 更强在“智能评分路由”。

---

## 五、按你的场景做匹配

## 你要的是：50/50 + 摘除 + 多层 fallback

### 最贴近的前三名

#### 1. LiteLLM

因为它能把这些元素都比较自然地表达出来：

- `weight` 实现 50/50
- `cooldown_time` + `allowed_fails_policy` 实现摘除
- `background_health_checks` 实现主动剔除
- `order` / fallback 实现多层路由

#### 2. Kong AI Gateway

因为它在算法和高可用机制的边界最清楚：

- group 内 weighted
- group 间 priority
- error 条件明确
- breaker 参数明确

#### 3. Portkey

因为它虽然算法种类少，但特别擅长表达这种多层 routing graph：

- 第一层 loadbalance
- 外层 fallback
- 失败条件按状态码触发

### 次一级候选

#### Ferro Labs

算法和 breaker 也够用，但生态成熟度还不如前三。

#### Helicone

如果你愿意接受“最便宜优先”而不是“严格 50/50”，它会很好。

#### Routerly

如果你要“智能选模型”而不是“传统 LB”，它更值得看。

---

## 六、最重要的最终判断

如果你的问题是：

> “我最关心负载均衡算法，这一点谁最值得认真看？”

我的最终排序是：

### 按算法完整度排序

1. **Kong AI Gateway**
2. **LiteLLM**
3. **Ferro Labs AI Gateway**
4. **Olla**
5. **APISIX**

### 按“最适合你的 LLM provider 高可用场景”排序

1. **LiteLLM**
2. **Kong AI Gateway**
3. **Portkey**
4. **Ferro Labs AI Gateway**
5. **Helicone**

### 按“智能路由而不是传统负载均衡”排序

1. **Routerly**
2. **Kong semantic routing**
3. **Ferro content-based**

---

## 七、核心来源

- LiteLLM routing: https://docs.litellm.ai/docs/routing
- LiteLLM health check routing: https://docs.litellm.ai/docs/proxy/health_check_routing
- Portkey load balancing: https://docs.portkey.ai/docs/product/ai-gateway/load-balancing
- Portkey fallbacks: https://docs.portkey.ai/docs/product/ai-gateway/fallbacks
- Helicone provider routing: https://docs.helicone.ai/gateway/provider-routing
- Kong load balancing: https://developer.konghq.com/ai-gateway/load-balancing/
- Kong AI Proxy Advanced: https://docs.konghq.com/plugins/ai-proxy-advanced
- Ferro Labs AI Gateway: https://github.com/ferro-labs/ai-gateway
- Routerly: https://github.com/Inebrio/Routerly
- Olla overview / load balancing / health checking: https://thushan.github.io/olla/
- APISIX ai-proxy-multi: https://apisix.apache.org/docs/apisix/plugins/ai-proxy-multi/
