# 自托管与离线部署专项分析（聚焦免费、本地、无云依赖）

你的约束：
1. **免费**
2. **本地部署**
3. **不依赖云服务**

本报告把各家拆成四个维度：
1. 是否有 OSS self-hostable 版本
2. 是否必须连接厂商云端（license check / telemetry / billing）
3. 是否存在付费门槛（Enterprise-only 功能）
4. 是否能满足你场景的核心路由能力

---

## 一、结论先看（按你的约束排序）

### 第一梯队：真正免费、本地、完全离线

| 产品 | 开源? | 本地部署 | 强制云端? | 付费门槛 | 路由能力 | 备注 |
|---|---|---|---|---|---|---|
| LiteLLM | ✅ MIT | ✅ | ❌ 无 | ❌ 无 | ✅ 多策略路由 + cooldown + fallback | 最成熟、最贴合 LLM 工程场景 |
| Ferro Labs AI Gateway | ✅ Apache-2.0 | ✅ | ❌ 无 | ❌ 无 | ✅ 多路由策略 + circuit breaker + dashboard | Go 单二进制、性能强 |
| Routerly | ✅ AGPL-3.0 | ✅ | ❌ 无 | ❌ 无 | ✅ 多策略评分路由 + budget | 零依赖、纯 JSON 配置 |
| Olla | ✅ Apache-2.0 | ✅ | ❌ 无 | ❌ 无 | ✅ priority + round-robin + least-conn + circuit breaker | 偏自建推理节点池 |
| APISIX AI Gateway | ✅ Apache-2.0 | ✅ | ❌ 无 | ❌ 无 | ⚠️ roundrobin + chash + priority + health check | AI 层算法较少，但传统网关语义成熟 |
| Portkey AI Gateway（核心） | ✅ MIT | ✅ | ❌ 无 | ❌ 无 | ✅ loadbalance + fallback + conditional | 核心网关是 OSS；观测是 Enterprise |

### 第二梯队：可自托管，但部分能力需付费或受限

| 产品 | 开源? | 本地部署 | 强制云端? | 付费门槛 | 路由能力 | 备注 |
|---|---|---|---|---|---|---|
| Kong AI Gateway | ⚠️ OSS core, AI 功能商业 | ✅ OSS Gateway 可本地 | ❌ OSS 无强制 | ⚠️ AI Proxy/Cache/Prompt Guard = Konnect/Enterprise | ✅ 企业级算法菜单，但 AI 功能需要 license | 你要的 AI 负载均衡需付费 |
| Helicone Observability Platform | ✅ Apache-2.0 | ✅ Docker all-in-one | ❌ 无强制 | ❌ 无付费门槛 | ⚠️ 自托管版仅 OpenAI/Anthropic | 完整观测，但 provider 支持受限 |
| Helicone AI Gateway | ✅ Apache-2.0 | ✅ 单二进制 | ❌ 无强制 | ❌ 无付费门槛 | ✅ 多 provider 路由 + fallback | 无观测 dashboard；观测需连 Control Plane（可选） |

### 第三梯队：不满足你的约束（必须云端）

| 产品 | 开源? | 本地部署 | 强制云端? | 付费门槛 | 路由能力 | 备注 |
|---|---|---|---|---|---|---|
| Cloudflare AI Gateway | ❌ 闭源 | ❌ 云端托管 | ✅ 必须 | ⚠️ Core 免费，Logs 有限 | ✅ 缓存 / fallback / rate limit | 不符合"本地、不连云" |
| OpenRouter | ❌ 闭源 | ❌ 云端托管 | ✅ 必须 | ⚠️ Free 50 req/day | ✅ 多 provider 路由 | 不符合"本地、不连云" |
| Braintrust AI Gateway | ❌ 闭源 | ⚠️ 仅 Data Plane 可本地 | ⚠️ Control Plane 在云端 | ⚠️ Enterprise 才可自托管 Data Plane | ✅ 缓存 / 观测 / custom providers | 不符合"不连云" |

---

## 二、逐家拆解：证据在哪里

### 1) LiteLLM

**开源 & 本地**
- GitHub：https://github.com/BerriAI/litellm
- License：**MIT**
- README 明写：`Self-hosted. Enterprise-ready.`

**无强制云端**
- 无 license check
- 无 mandatory telemetry
- Prometheus 指标全部本地暴露

**无付费门槛**
- OSS 版包含：
  - 100+ provider 支持
  - Weighted routing / least-busy / latency-based / cost-based
  - `cooldown_time` / `allowed_fails_policy` / `background_health_checks`
  - `order` / fallback 跨 provider / 跨模型
  - 请求/成本/延迟统计（Prometheus）
- Enterprise 版主要是 SSO / audit logs / premium support

**路由能力（与你的场景）**
- `weight` 实现 50/50
- `cooldown_time` 实现摘除窗口
- `background_health_checks` 提前剔除坏节点
- `order` 实现多层 fallback
- `model_name` 别名机制支持跨模型路由

**结论**
- ✅ 完全符合你的三条约束
- ✅ 路由能力最贴近 LLM 工程场景

---

### 2) Ferro Labs AI Gateway

**开源 & 本地**
- GitHub：https://github.com/ferro-labs/ai-gateway
- License：**Apache-2.0**
- README 明写：`Single binary, zero dependencies, 32 MB base memory`

**无强制云端**
- Docker / 单二进制部署
- 无任何云端 endpoint 必填项
- 配置全本地 YAML / JSON

**无付费门槛**
- OSS 版包含：
  - 8 routing strategies：single, fallback, loadbalance, least-latency, cost-optimized, content-based, ab-test, conditional
  - circuit breaker：`failure_threshold`, `success_threshold`, `timeout`
  - 内建 dashboard
  - Prometheus `/metrics`
  - SQLite/PostgreSQL 持久化
- 文档中写明 `Managed cloud: Coming Soon`（目前没有收费版）

**路由能力**
- `loadbalance` 支持 weighted（例如 70/30）
- `fallback` 支持 `on_status_codes: [429, 502, 503]`
- `least-latency` / `cost-optimized`
- circuit breaker 实现临时摘除

**结论**
- ✅ 完全符合你的三条约束
- ✅ Go 单二进制，性能强，适合你偏轻量栈

---

### 3) Routerly

**开源 & 本地**
- GitHub：https://github.com/Inebrio/Routerly
- License：**AGPL-3.0**
- README 明写：`Self-hosted. Zero infrastructure. No database required.`

**无强制云端**
- 配置存本地 JSON（`~/.routerly/`）
- 无 external DB / Redis
- Docker 部署只需 `ROUTERLY_HOME=/data`

**无付费门槛**
- OSS 版包含：
  - 9 routing policies：llm, cheapest, health, performance, capability, context, budget-remaining, rate-limit, fairness
  - per-project token isolation
  - budget enforcement
  - 内建 Web dashboard
  - CLI
- README 写：`Free forever: self-hosted, AGPL-3.0, you pay only what your providers charge`

**路由能力**
- 不是传统加权负载均衡器，而是多策略评分引擎
- 每请求并行评分 → 合成排名 → 选最优
- `health` policy 会根据最近错误降权
- `budget-remaining` 会排除会超标模型

**结论**
- ✅ 完全符合你的三条约束
- ⚠️ 更偏"智能路由"，不是经典 LB 算法菜单

---

### 4) Olla

**开源 & 本地**
- GitHub：https://github.com/thushan/olla
- License：**Apache-2.0**
- 文档：`High-performance, low-overhead proxy and load balancer for LLM infrastructure`

**无强制云端**
- Docker / 本地二进制
- 无任何云端依赖

**无付费门槛**
- OSS 版包含：
  - priority-based routing（默认）
  - round-robin
  - least-connections
  - circuit breaker（closed/open/half-open）
  - health monitoring
  - 响应头：`X-Olla-Endpoint`, `X-Olla-Model`, `X-Olla-Response-Time`

**路由能力**
- 同 tier 内 weighted random
- tier 间按 priority fallback
- 健康状态影响权重（Healthy=1.0, Busy=0.3, Warming=0.1, Unhealthy=0.0）

**结论**
- ✅ 完全符合你的三条约束
- ⚠️ 更偏自建推理节点池（Ollama / vLLM / llama.cpp），不主打跨 SaaS provider 的 LLM gateway 平台

---

### 5) APISIX AI Gateway

**开源 & 本地**
- GitHub：https://github.com/apache/apisix
- License：**Apache-2.0**
- README：`The Cloud-Native API Gateway and AI Gateway`

**无强制云端**
- OSS 版全部本地
- 无 license check / telemetry

**无付费门槛（对 OSS）**
- OSS 版包含：
  - `ai-proxy` / `ai-proxy-multi` plugin
  - `balancer.algorithm`: roundrobin, chash
  - `priority`（优先级优先于 weight）
  - `fallback_strategy`
  - `checks.active`（健康检查）
- AI 功能（prompt guard / semantic cache / rate limiting advanced）**也属于 OSS**，无付费门槛

**路由能力**
- `roundrobin`：加权轮询
- `chash`：一致性哈希（sticky session）
- `priority`：层级 fallback
- `fallback_strategy` 可设 `http_429`, `http_5xx`, `instance_health_and_rate_limiting`

**结论**
- ✅ 完全符合你的三条约束
- ⚠️ AI 层算法菜单不如 Kong / LiteLLM / Ferro 那样丰富，但传统网关语义非常稳

---

### 6) Portkey AI Gateway（核心）

**开源 & 本地**
- GitHub：https://github.com/Portkey-AI/gateway
- License：**MIT**
- 文档：`npx @portkey-ai/gateway` 或 Docker

**无强制云端（对 OSS 核心网关）**
- OSS 核心网关完全本地
- 不依赖 Portkey cloud
- 你可以只用 OSS gateway，不连任何 Portkey 服务

**付费门槛（观测层）**
- OSS 核心网关包含：
  - 250+ provider 支持
  - automatic fallbacks & retries
  - load balancing
  - conditional routing
  - request timeouts
  - multi-modal support
  - Gateway 2.0 新增：circuit breakers, semantic cache, budget limits, MCP Registry
- **观测层（dashboard / logs / traces / analytics）是 Enterprise/Managed 版功能**
- Enterprise 版才是"日志/分析/SSO/RBAC/合规"

**路由能力**
- `loadbalance`：加权概率分流（weight 归一化）
- `fallback`：fallback chain
- `conditional`：条件路由
- `sticky session`：`hash_fields` + TTL

**结论**
- ✅ 核心网关完全符合你的三条约束
- ⚠️ 若你需要内建观测 dashboard，需 Enterprise（否则自己接 Prometheus/Grafana）

---

### 7) Kong AI Gateway

**开源 & 本地（对 OSS core）**
- GitHub：https://github.com/Kong/kong
- License：**Apache-2.0**
- Kong Gateway OSS 可本地部署，无强制云端

**付费门槛（AI 功能）**
- Kong Gateway OSS 免费
- **Kong AI Gateway 的 AI 插件（AI Proxy, AI Prompt Guard, AI Semantic Cache, AI Rate Limiting Advanced, PII sanitization, token-based cost tracking）需要 Konnect 或 Enterprise license**
- 若你要"AI 负载均衡 / AI 缓存 / AI Guardrails"，需付费

**路由能力（若付费）**
- weighted round-robin
- consistent-hashing
- least-connections
- lowest-usage
- lowest-latency（peak EWMA）
- semantic routing
- priority
- circuit breaker：`max_fails`, `fail_timeout`

**结论**
- ⚠️ OSS Gateway 可本地，但 AI 负载均衡能力需付费
- 不符合你的"免费"约束（若你要 AI 功能）

---

### 8) Helicone（两个产品）

**A. Helicone Observability Platform**

**开源 & 本地**
- GitHub：https://github.com/Helicone/helicone
- License：**Apache-2.0**
- Docker all-in-one：`helicone/helicone-all-in-one:latest`

**无强制云端**
- Docker 部署完全本地（PostgreSQL, ClickHouse, MinIO, Jawn, Web）
- 无 mandatory telemetry / billing connection
- 官方博客写：`Keep your LLM data entirely within your infrastructure`

**无付费门槛**
- 自托管版免费，无请求限制
- 所有核心观测功能可用（日志、分析、dashboard、prompt management）

**限制**
- 自托管版只支持 OpenAI 和 Anthropic（文档：`Other providers (Vertex AI, AWS Bedrock, Azure OpenAI) are not supported in the self-hosted version`）

**结论**
- ✅ 完全符合你的三条约束（若你只用 OpenAI/Anthropic）
- ⚠️ 若你需要 100+ providers，自托管版不支持

**B. Helicone AI Gateway**

**开源 & 本地**
- GitHub：https://github.com/Helicone/ai-gateway
- License：**Apache-2.0**
- 单二进制：`npx @helicone/ai-gateway@latest`

**无强制云端**
- 可完全离线运行
- `.env.template` 中 `HELICONE_CONTROL_PLANE_API_KEY` 是**可选**（只在需要观测时才填）

**无付费门槛**
- OSS 版免费
- 支持多 provider 路由 + fallback

**限制**
- 无观测 dashboard（除非你连 Control Plane，那是可选）
- 若你要观测，需要额外部署 Helicone Observability Platform 或用云端

**结论**
- ✅ AI Gateway 部分完全符合你的三条约束
- ⚠️ 无观测 dashboard，除非你愿意自托管 Helicone Observability Platform（后者 provider 支持有限）

---

## 三、关键判断：Helicone 是否"必须连云"

你的怀疑：
> "我发现 helicone 似乎即使本地部署了也还是需要连接到云服务，也还需要付费"

**证据结论**

- **Helicone Observability Platform（自托管）**：
  - Docker all-in-one 完全本地
  - 无 mandatory cloud connection
  - 无 subscription requirement
  - **但** provider 支持受限（仅 OpenAI/Anthropic）

- **Helicone AI Gateway（自托管）**：
  - 完全离线可运行
  - `HELICONE_CONTROL_PLANE_API_KEY` 是可选（只在需要观测时才填）
  - 若你只要路由，不需要云端

**你可能的混淆点**
- Helicone 官网 Quick Start（云端版）需要 `HELICONE_API_KEY`，那是云端托管版
- 自托管版不需要 Helicone 云端 API key，只用自己的 DB / S3 / ClickHouse

**结论**
- ✅ Helicone 自托管版**确实可以离线**
- ⚠️ 但若你要多 provider 支持 + 观测 dashboard，需要同时部署 AI Gateway + Observability Platform，后者 provider 支持有限

---

## 四、最终推荐（按你的约束排序）

### 如果你优先"免费 + 本地 + 离线 + 负载均衡算法丰富"

**首选**
- LiteLLM
- Ferro Labs AI Gateway

**次选**
- Routerly（若你接受智能评分路由）
- APISIX AI Gateway（若你接受传统网关 AI 扩展）

### 如果你同时需要"观测 dashboard"

**首选**
- Ferro Labs AI Gateway（内建 dashboard + Prometheus + SQLite/PostgreSQL）
- LiteLLM + Prometheus + Grafana（你需要自己接栈）

**次选**
- Routerly（内建 dashboard）
- Helicone Observability Platform（若你只用 OpenAI/Anthropic）

### 如果你需要"多 provider 支持 + 观测"

**首选**
- LiteLLM + Prometheus
- Ferro Labs AI Gateway（dashboard + 多 provider）

**次选**
- Routerly（dashboard + 多 provider）

---

## 五、主要来源

- LiteLLM GitHub: https://github.com/BerriAI/litellm
- LiteLLM docs: https://docs.litellm.ai/docs/routing
- Ferro Labs GitHub: https://github.com/ferro-labs/ai-gateway
- Routerly GitHub: https://github.com/Inebrio/Routerly
- Olla docs: https://thushan.github.io/olla/
- APISIX docs: https://apisix.apache.org/docs/apisix/plugins/ai-proxy-multi
- Portkey GitHub: https://github.com/Portkey-AI/gateway
- Portkey docs: https://docs.portkey.ai/docs/product/ai-gateway/load-balancing
- Kong docs: https://docs.konghq.com/plugins/ai-proxy-advanced
- Kong GitHub: https://github.com/Kong/kong
- Helicone GitHub (Observability): https://github.com/Helicone/helicone
- Helicone GitHub (AI Gateway): https://github.com/Helicone/ai-gateway
- Helicone docs: https://docs.helicone.ai/getting-started/self-host/docker