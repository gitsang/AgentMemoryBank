# LLM 网关负载均衡算法与路由语义研究报告

**研究日期：** 2026-04-15
**研究范围：** Portkey、Helicone、Kong AI Gateway、OpenRouter、Cloudflare AI Gateway、Braintrust

---

## 执行摘要

本报告提供了六个与 Bifrost 竞争的主要托管/商业 LLM 网关的负载均衡算法和路由语义的详细文档。每个章节均包含官方文档来源的确切行为描述、配置示例和算法细节。

---

## 1. PORTKEY

**官方文档：** https://docs.portkey.ai/docs/product/ai-gateway/load-balancing

### 1.1 负载均衡算法

**算法类型：** 加权概率分布与归一化

**具体行为：**
1. **定义目标与权重** — 为每个目标分配 `weight` 权重。权重代表流量相对份额。
2. **权重归一化** — Portkey 将权重归一化至总和为 100%。例如：权重 5、3、1 变为 55%、33%、11%。
3. **请求分发** — 每个请求根据归一化后的概率路由到目标。

**配置参数：**
- 默认 `weight`：`1`
- 最小 `weight`：`0`（停止流量但不从配置中移除）
- 未设置的权重默认为 `1`

**配置示例：**
```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@openai-prod", "weight": 0.7 },
    { "provider": "@azure-prod", "weight": 0.3 }
  ]
}
```

### 1.2 粘性负载均衡（会话亲和性）

**算法：** 基于哈希的粘性会话，带 TTL

**配置：**
```json
{
  "strategy": {
    "mode": "loadbalance",
    "sticky_session": {
      "hash_fields": ["metadata.user_id"],
      "ttl": 3600
    }
  },
  "targets": [
    { "provider": "@openai-prod", "weight": 0.5 },
    { "provider": "@anthropic-prod", "weight": 0.5 }
  ]
}
```

**工作原理：**
1. **标识符生成**：当请求到达时，Portkey 根据指定的 `hash_fields` 值生成哈希
2. **目标查找**：使用哈希从缓存中查找之前分配的目标
3. **一致性路由**：如果存在缓存的分配且未过期，则请求发送到相同目标
4. **新分配**：如果不存在缓存分配，则根据权重选择新目标并缓存以供将来使用

**实现细节：** 粘性会话使用两级缓存系统（内存 + Redis），用于快速查找和分布式部署中网关实例之间的持久化。

### 1.3 降级策略

**触发条件：** 默认情况下，降级在任何 **非 2xx** 状态码时触发

**配置：**
```json
{
  "strategy": { "mode": "fallback", "on_status_codes": [429, 503] },
  "targets": [
    { "provider": "@openai-prod" },
    { "provider": "@azure-prod" }
  ]
}
```

**行为：** 指定提供商/模型的优先级列表。如果主 LLM 失败，Portkey 自动降级到下一个候选。

### 1.4 条件路由

**算法：** 基于规则的路由，支持类 MongoDB 查询运算符

**支持的运算符：**
| 运算符 | 描述 |
|----------|-------------|
| `$eq` | 等于 |
| `$ne` | 不等于 |
| `$in` | 存在于数组 |
| `$nin` | 不存在于数组 |
| `$regex` | 正则匹配 |
| `$gt` | 大于 |
| `$gte` | 大于等于 |
| `$lt` | 小于 |
| `$lte` | 小于等于 |
| `$and` | 所有条件都为真 |
| `$or` | 至少一个条件为真 |

**示例：**
```json
{
  "strategy": {
    "mode": "conditional",
    "conditions": [
      { "query": { "metadata.user_plan": { "$eq": "paid" } }, "then": "finetuned-gpt4" }
    ],
    "default": "base-gpt4"
  },
  "targets": [
    { "name": "finetuned-gpt4", "provider": "@xx" },
    { "name": "base-gpt4", "provider": "@yy" }
  ]
}
```

### 1.5 策略组合

Portkey 支持 **嵌套策略** — 任何策略中的任何目标本身可以包含另一个策略：

| 外层策略 | 内层策略 | 实现效果 |
|----------------|----------------|------------------|
| 条件 | 负载均衡 | 按模型路由，然后在每个模型内跨提供商分发 |
| 负载均衡 | 降级 | 每个负载均衡槽位都有独立的故障转移 |
| 负载均衡 | 条件 | 每个分发槽位根据请求元数据选择模型 |

---

## 2. HELICONE AI GATEWAY

**官方文档：** https://docs.helicone.ai/gateway/provider-routing
**GitHub：** https://github.com/Helicone/ai-gateway

### 2.1 智能路由算法

Helicone 实现多种路由策略：

**1. 基于模型的延迟路由**
- 自动为用例选择最快的模型

**2. 提供商延迟 P2C + PeakEWMA**
- 使用 **二次幂选择（P2C）** 算法结合 **峰值指数加权移动平均（PeakEWMA）**
- 实时识别最佳提供商，避免缓慢或降级的服务

**3. 加权分发**
- 按成本、性能或可靠性优先级分流流量

**4. 成本优化**
- 路由到最便宜的可用提供商

### 2.2 默认路由行为

**路由优先级：**
1. 您的提供商密钥（BYOK）如果已配置
2. Helicone 托管密钥（积分）— 自动降级，0% 加价

**选择逻辑：**
- 首先路由到 **最便宜的提供商**
- 成本相同的提供商进行 **负载均衡**

**故障转移触发条件：**
| 错误 | 描述 |
|----|-------------|
| 429 | 速率限制错误 |
| 401 | 认证错误 |
| 400 | 上下文长度错误 |
| 408 | 超时错误 |
| 500+ | 服务器错误 |

### 2.3 配置示例（自托管）

```yaml
routers:
  production:
    load-balance:
      chat:
        strategy: latency  # 选项: latency, weighted, custom
        models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-7-sonnet
    rate-limit:
      per-api-key:
        capacity: 1000
        refill-frequency: 1m  # 每分钟 1000 次请求
```

### 2.4 模型名称格式路由

**自动路由：** `model: "gpt-4o-mini"`（跨所有提供商路由）
**指定提供商：** `model: "gpt-4o-mini/openai"`
**自定义部署：** `model: "gpt-4o/azure/your-deployment-id"`
**手动降级链：** `model: "gpt-4o-mini/azure,gpt-4o-mini/openai,gpt-4o-mini"`
**排除提供商：** `model: "!openai,gpt-4o-mini"`

---

## 3. KONG AI GATEWAY

**官方文档：** https://developer.konghq.com/ai-gateway/load-balancing/

### 3.1 负载均衡算法

Kong AI Proxy Advanced 插件支持 **7 种不同的算法**：

#### 1. 加权轮询
**描述：** 根据分配的权重在模型之间分发请求。如果模型 `gpt-4`、`gpt-4o-mini` 和 `gpt-3` 的权重分别为 `70`、`25` 和 `5`，则它们分别接收约 70%、25% 和 5% 的流量。

**特点：**
- 流量按权重比例路由
- 请求按权重调整的循环顺序执行
- 不考虑缓存命中率、延迟或当前负载

#### 2. 一致性哈希
**描述：** 根据可配置头部的哈希值路由请求。具有相同头部值的请求被路由到相同的模型。

**配置：** `hash_on_header` 设置定义要哈希的头部。默认为 `X-Kong-LLM-Request-ID`。

**特点：**
- 使用一致密钥（如用户 ID）时有效
- 需要多样化的哈希输入以实现均衡分布
- 用于会话持久化和缓存命中优化

#### 3. 最小连接数 (v3.13+)
**描述：** 跟踪每个后端的飞行中请求数量，并将新请求路由到容量最大的后端。

**特点：**
- 动态适应后端响应时间
- 路由避开累积开放连接的较慢后端
- 不考虑缓存命中率

#### 4. 最低使用率 (v3.10+)
**描述：** 将请求路由到测量资源使用率最低的模型。

**配置：** `tokens_count_strategy` 参数定义使用率的衡量方式：
- `prompt_token_counts`
- `response_token_counts`
- `cost`

#### 5. 最低延迟
**描述：** 将请求路由到观察延迟最低的模型。

**配置：** `latency_strategy` 参数：
- `tpot`（默认）：每输出令牌时间
- `e2e`：端到端响应时间

**算法细节：** 使用 **峰值 EWMA（指数加权移动平均）** 跟踪从 TCP 连接完成到响应体的延迟。指标随时间衰减。

**流量分发：**
- 最快的模型获得大部分流量（约 90-99%）
- Kong 永远不会 100% 发送到单个目标，除非它是唯一可用的
- EWMA 确保所有目标继续接收少量流量以持续探测

#### 6. 语义路由 (v3.13+)
**描述：** 根据提示词和模型描述之间的语义相似度路由请求。

**实现：**
- 使用指定模型生成嵌入（如 `text-embedding-3-small`）
- 使用向量搜索计算相似度
- 需要向量数据库（如 Redis）
- `distance_metric` 和 `threshold` 设置控制匹配灵敏度

#### 7. 优先级 (v3.10+)
**描述：** 根据分配的优先级组路由请求。

**行为：**
- 负载均衡器始终首先从最高优先级组中选择
- 如果该组中的所有目标都不可用，则降级到下一组
- 在每个组内，`weight` 参数控制流量分发

**用例：** 成本感知路由和受控故障转移

### 3.2 重试和降级配置

**配置参数：**
| 设置 | 描述 |
|--------|-------------|
| `retries` | 报告失败前重试失败请求的次数 |
| `failover_criteria` | 触发故障转移的失败条件（如 `http_429`、`http_500`、`error`、`timeout`） |
| `connect_timeout` | 建立 TCP 连接的最大时间 |
| `read_timeout` | 等待服务器响应的最大时间 |
| `write_timeout` | 发送请求负载的最大时间 |

**示例：**
```yaml
plugins:
  - name: ai-proxy-advanced
    config:
      balancer:
        algorithm: lowest-latency
        retries: 3
        failover_criteria:
          - error
          - timeout
          - http_429
          - http_503
```

### 3.3 健康检查和熔断器 (v3.13+)

**行为：**
- 如果不成功尝试次数达到 `config.balancer.max_fails`，负载均衡器停止向该目标发送请求
- 目标在 `config.balancer.fail_timeout` 期限后重新考虑
- 失败计数器跟踪总失败次数，而非连续失败次数
- 计数器仅在 `fail_timeout` 期限过去后收到成功请求时重置
- 如果所有目标同时变得不健康，请求失败并返回 `HTTP 500`

---

## 4. OPENROUTER

**官方文档：** https://openrouter.ai/docs/guides/routing/provider-selection

### 4.1 默认负载均衡策略

**算法：** 基于价格的负载均衡，使用平方反比加权

**具体步骤：**
1. 优先选择过去 30 秒内没有重大故障的提供商
2. 对于稳定的提供商，查看最低成本候选，并按 **价格的平方反比** 加权选择
3. 将剩余提供商用作降级候选

**数学公式：**
```
Weight = 1 / (price^2)
```

**示例：**
- 提供商 A 成本 $1/M tokens
- 提供商 B 成本 $2/M tokens  
- 提供商 C 成本 $3/M tokens

结果：提供商 A 被选中的可能性是提供商 C 的 **9 倍**，因为 (1 / 3² = 1/9)

### 4.2 提供商排序（显式优先级）

当设置 `sort` 或 `order` 时，负载均衡被禁用，提供商按顺序尝试。

**排序选项：**
- `"price"`：优先最低价格
- `"throughput"`：优先最高吞吐量
- `"latency"`：优先最低延迟

**快捷方式：**
- `:nitro` 后缀 = 按吞吐量排序（例如 `model: "llama-3.3-70b:nitro"`）
- `:floor` 后缀 = 按价格排序（例如 `model: "llama-3.3-70b:floor"`）

### 4.3 使用分区的高级排序

**配置：**
```typescript
provider: {
  sort: {
    by: 'throughput',
    partition: 'none'  // 'model'（默认）或 'none'
  }
}
```

**分区选项：**
- `partition: "model"`（默认）：在排序前按模型分组端点
- `partition: "none"`：移除分组，允许端点跨所有模型全局排序

### 4.4 性能阈值

**基于百分位的路由：**
OpenRouter 使用滚动 5 分钟窗口的百分位统计跟踪指标：
- **p50**（中位数）：50% 的请求表现更好
- **p75**：75% 的请求表现更好
- **p90**：90% 的请求表现更好
- **p99**：99% 的请求表现更好

**配置：**
```typescript
provider: {
  preferredMinThroughput: {
    p90: 50  // 优先 90% 请求超过 50 tokens/秒的提供商
  },
  preferredMaxLatency: {
    p90: 3   // 优先 90% 请求延迟低于 3 秒的提供商
  }
}
```

**行为：** 不满足阈值的端点会被降级（移动到降级位置），而非完全排除。

### 4.5 模型降级

**配置：**
```typescript
models: ['anthropic/claude-3.5-sonnet', 'gryphe/mythomax-l2-13b']
```

**行为：** 按优先级顺序提供模型 ID 列表。如果第一个模型返回错误，OpenRouter 自动尝试列表中的下一个模型。

**降级触发条件：**
- 上下文长度验证错误
- 过滤模型的审核标志
- 速率限制
- 停机时间

### 4.6 提供商路由字段

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `order` | string[] | - | 要按顺序尝试的提供商 slug 列表 |
| `allow_fallbacks` | boolean | `true` | 是否允许备用提供商 |
| `only` | string[] | - | 允许的提供商 slug 列表 |
| `ignore` | string[] | - | 跳过的提供商 slug 列表 |
| `sort` | string/object | - | 按价格、吞吐量或延迟排序提供商 |
| `max_price` | object | - | 请求的最大价格 |

---

## 5. CLOUDFLARE AI GATEWAY

**官方文档：** https://developers.cloudflare.com/ai-gateway/features/dynamic-routing

### 5.1 动态路由架构

Cloudflare 使用 **可视化流程路由系统**，支持 JSON 配置。

**核心概念：**
- **路由**：命名的版本化流程（如 `dynamic/support`）
- **节点**：开始、条件、百分比、模型、速率限制、预算限制、结束
- **元数据**：用于路由决策的任意键值上下文
- **版本**：每次更改都会产生新草稿，支持即时回滚

### 5.2 支持的节点类型

#### 条件元素（If/Else）
根据请求参数评估条件并相应路由。

**配置：**
```json
{
  "id": "<id>",
  "type": "conditional",
  "properties": {
    "condition": {
      "metadata.plan": { "$eq": "free" }
    }
  },
  "outputs": {
    "true": { "elementId": "<id>" },
    "false": { "elementId": "<id>" }
  }
}
```

#### 百分比分流
概率性地跨多个输出路由请求，用于 A/B 测试。

**配置：**
```json
{
  "id": "<id>",
  "type": "percentage",
  "outputs": {
    "10%": { "elementId": "<id>" },
    "50%": { "elementId": "<id>" },
    "else": { "elementId": "<id>" }
  }
}
```

#### 速率/预算限制
根据请求元数据应用限制，自动降级。

**配置：**
```json
{
  "id": "<id>",
  "type": "rate_limit",
  "properties": {
    "limitType": "count",
    "key": "metadata.user_id",
    "limit": 100,
    "interval": 3600,
    "technique": "sliding"
  },
  "outputs": {
    "success": { "elementId": "node_model_workers_ai" },
    "fallback": { "elementId": "node_model_openai_mini" }
  }
}
```

**限制类型：**
- `limitType`："count" 或 "cost"
- `technique`："sliding" 或 "fixed" 窗口

#### 模型节点
使用可配置的超时和重试设置执行推理。

**配置：**
```json
{
  "id": "<id>",
  "type": "model",
  "properties": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "timeout": 60000,
    "retries": 4
  },
  "outputs": {
    "success": { "elementId": "<id>" },
    "fallback": { "elementId": "<id>" }
  }
}
```

### 5.3 请求处理（旧版）

**请求重试：**
- 最多 5 次重试尝试
- 可配置退避策略："constant"、"linear" 或 "exponential"
- 可配置重试延迟（最大 5 秒）

**配置：**
```json
{
  "config": {
    "maxAttempts": 5,
    "retryDelay": 1000,
    "backoff": "exponential"
  }
}
```

### 5.4 响应头

动态路由返回：
- `cf-aig-model`：使用的模型
- `cf-aig-provider`：使用的提供商 slug

---

## 6. BRAINTRUST

**官方文档：** https://www.braintrust.dev/docs/deploy/gateway

### 6.1 负载均衡行为

**自动负载均衡：**
当多个 AI 提供商支持相同模型时，Braintrust **自动在所有可用提供商之间负载均衡** 请求。

**用例：** 解决每账户速率限制问题，并在某个提供商宕机时提供弹性。

### 6.2 提供商选择覆盖

**基于头部的路由：**
使用 `x-bt-endpoint-name` 头部将请求路由到特定的提供商凭证。

**示例：**
```bash
curl -X POST "https://api.braintrust.dev/v1/proxy/chat/completions" \
  -H "Authorization: Bearer $BRAINTRUST_API_KEY" \
  -H "Content-Type: application/json" \
  -H "x-bt-endpoint-name: OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**验证：** 检查响应头 `x-bt-used-endpoint` 以确认处理请求的提供商。

### 6.3 网关功能

**缓存：**
- 网关自动缓存结果
- 三种模式：`auto`（默认）、`always`、``never`
- 在 `auto` 模式下，如果请求设置了 `temperature=0` 或 `seed` 参数，则会被缓存
- 默认 TTL：1 周（最大 604800 秒）
- 缓存加密：AES-GCM，密钥从用户 API 密钥派生

**支持的缓存路径：**
- `/auto`
- `/embeddings`
- `/chat/completions`
- `/completions`
- `/moderations`

**响应头：**
- `x-bt-cached`：`HIT` 或 `MISS`
- `x-bt-used-endpoint`：使用的配置提供商端点
- `x-bt-span-id`：日志记录的 span ID（启用跟踪时）

### 6.4 配置头部

| 头部 | 值 | 描述 |
|--------|--------|-------------|
| `x-bt-use-cache` | `auto`、`always`、`never` | 控制缓存行为 |
| `x-bt-cache-ttl` | 秒数（最大 604800） | 设置缓存 TTL |
| `x-bt-endpoint-name` | 端点名称 | 使用特定配置的端点 |
| `x-bt-project-id` | 项目 ID | 使用项目级 AI 提供商凭证 |
| `x-bt-org-name` | 组织名称 | 为多组织用户指定组织 |

---

## 综合对比

| 网关 | 加权路由 | 基于延迟 | 基于成本 | 粘性会话 | 熔断器 | 语义路由 |
|---------|-----------------|---------------|------------|-----------------|-----------------|------------------|
| **Portkey** | ✅ 概率性 | ❌ | ❌ | ✅ 基于哈希 | ❌ | ❌ |
| **Helicone** | ✅ | ✅ P2C+PeakEWMA | ✅ 最便宜优先 | ❌ | ❌ | ❌ |
| **Kong** | ✅ 轮询 | ✅ 峰值 EWMA | ✅ 最低使用率 | ✅ 一致性哈希 | ✅ | ✅ |
| **OpenRouter** | ✅ 平方反比 | ✅ | ✅ 默认 | ❌ | ❌ | ❌ |
| **Cloudflare** | ✅ 百分比分流 | ❌ | ✅ 预算限制 | ❌ | ❌ | ❌ |
| **Braintrust** | ✅ 自动 | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 参考来源

1. Portkey Load Balancing: https://docs.portkey.ai/docs/product/ai-gateway/load-balancing
2. Portkey Fallbacks: https://docs.portkey.ai/docs/product/ai-gateway/fallbacks
3. Portkey Conditional Routing: https://docs.portkey.ai/docs/product/ai-gateway/conditional-routing
4. Helicone Provider Routing: https://docs.helicone.ai/gateway/provider-routing
5. Helicone GitHub: https://github.com/Helicone/ai-gateway
6. Kong AI Gateway Load Balancing: https://developer.konghq.com/ai-gateway/load-balancing/
7. Kong AI Proxy Advanced Reference: https://developer.konghq.com/plugins/ai-proxy-advanced/reference/
8. OpenRouter Provider Selection: https://openrouter.ai/docs/guides/routing/provider-selection
9. OpenRouter Model Fallbacks: https://openrouter.ai/docs/guides/routing/model-fallbacks
10. Cloudflare Dynamic Routing: https://developers.cloudflare.com/ai-gateway/features/dynamic-routing
11. Cloudflare JSON Configuration: https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/json-configuration
12. Braintrust Gateway: https://www.braintrust.dev/docs/deploy/gateway
13. Braintrust Provider Routing: https://www.braintrust.dev/docs/kb/route-requests-to-specific-ai-providers

---

*报告生成日期：2026-04-15。所有信息均来源于该日期的官方文档。*
