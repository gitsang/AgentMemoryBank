# LLM Gateway Load Balancing Algorithms and Routing Semantics Research Report

**Research Date:** 2026-04-15
**Scope:** Portkey, Helicone, Kong AI Gateway, OpenRouter, Cloudflare AI Gateway, Braintrust

---

## Executive Summary

This report provides evidence-rich documentation of load balancing algorithms and routing semantics across six major managed/commercial LLM gateways competing with Bifrost. Each section includes exact documented behavior, configuration examples, and algorithmic details sourced from official documentation.

---

## 1. PORTKEY

**Official Documentation:** https://docs.portkey.ai/docs/product/ai-gateway/load-balancing

### 1.1 Load Balancing Algorithm

**Algorithm Type:** Weighted probabilistic distribution with normalization

**Exact Behavior:**
1. **Define targets & weights** — Assign a `weight` to each target. Weights represent relative share of traffic.
2. **Weight normalization** — Portkey normalizes weights to sum to 100%. Example: weights 5, 3, 1 become 55%, 33%, 11%.
3. **Request distribution** — Each request routes to a target based on normalized probabilities.

**Configuration Parameters:**
- Default `weight`: `1`
- Minimum `weight`: `0` (stops traffic without removing from config)
- Unset weights default to `1`

**Example Configuration:**
```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@openai-prod", "weight": 0.7 },
    { "provider": "@azure-prod", "weight": 0.3 }
  ]
}
```

### 1.2 Sticky Load Balancing (Session Affinity)

**Algorithm:** Hash-based sticky sessions with TTL

**Configuration:**
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

**How It Works:**
1. **Identifier Generation**: When a request arrives, Portkey generates a hash from the specified `hash_fields` values
2. **Target Lookup**: The hash is used to look up the previously assigned target from cache
3. **Consistent Routing**: If a cached assignment exists and hasn't expired, the request goes to the same target
4. **New Assignment**: If no cached assignment exists, a new target is selected based on weights and cached for future requests

**Implementation Detail:** Sticky sessions use a two-tier cache system (in-memory + Redis) for fast lookups and persistence across gateway instances in distributed deployments.

### 1.3 Fallback Strategy

**Trigger:** By default, fallback triggers on any **non-2xx** status code

**Configuration:**
```json
{
  "strategy": { "mode": "fallback", "on_status_codes": [429, 503] },
  "targets": [
    { "provider": "@openai-prod" },
    { "provider": "@azure-prod" }
  ]
}
```

**Behavior:** Specify a prioritized list of providers/models. If the primary LLM fails, Portkey automatically falls back to the next in line.

### 1.4 Conditional Routing

**Algorithm:** Rule-based routing with MongoDB-like query operators

**Supported Operators:**
| Operator | Description |
|----------|-------------|
| `$eq` | Equals |
| `$ne` | Not equals |
| `$in` | In array |
| `$nin` | Not in array |
| `$regex` | Match the regex |
| `$gt` | Greater than |
| `$gte` | Greater than or equal to |
| `$lt` | Less than |
| `$lte` | Less than or equal to |
| `$and` | All conditions must be true |
| `$or` | At least one condition must be true |

**Example:**
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

### 1.5 Strategy Composition

Portkey supports **nested strategies** - any target in any strategy can itself contain another strategy:

| Outer Strategy | Inner Strategy | What it achieves |
|----------------|----------------|------------------|
| Conditional | Load Balancer | Route by model, then distribute within each model across providers |
| Load Balancer | Fallback | Each load-balanced slot has its own independent failover |
| Load Balancer | Conditional | Each distribution slot picks a model based on request metadata |

---

## 2. HELICONE AI GATEWAY

**Official Documentation:** https://docs.helicone.ai/gateway/provider-routing
**GitHub:** https://github.com/Helicone/ai-gateway

### 2.1 Smart Routing Algorithms

Helicone implements multiple routing strategies:

**1. Model-Based Latency Routing**
- Automatically selects the fastest model for the use case

**2. Provider Latency-Based P2C + PeakEWMA**
- Uses **Power of Two Choices (P2C)** algorithm combined with **Peak Exponentially Weighted Moving Average (PeakEWMA)**
- Identifies the optimal provider in real-time, avoiding slow or degraded services

**3. Weighted Distribution**
- Split traffic based on cost, performance, or reliability priorities

**4. Cost Optimization**
- Routes to cheapest available provider

### 2.2 Default Routing Behavior

**Routing Priority:**
1. Your provider keys (BYOK) if configured
2. Helicone's managed keys (credits) - automatic fallback at 0% markup

**Selection Logic:**
- Routes to the **cheapest provider first**
- Equal-cost providers are **load balanced**

**Failover Triggers:**
| Error | Description |
|-------|-------------|
| 429 | Rate limit errors |
| 401 | Authentication errors |
| 400 | Context length errors |
| 408 | Timeout errors |
| 500+ | Server errors |

### 2.3 Configuration Example (Self-Hosted)

```yaml
routers:
  production:
    load-balance:
      chat:
        strategy: latency  # Options: latency, weighted, custom
        models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-7-sonnet
    rate-limit:
      per-api-key:
        capacity: 1000
        refill-frequency: 1m  # 1000 requests per minute
```

### 2.4 Model Name Format Routing

**Automatic routing:** `model: "gpt-4o-mini"` (routes across all providers)
**Specific provider:** `model: "gpt-4o-mini/openai"`
**Custom deployment:** `model: "gpt-4o/azure/your-deployment-id"`
**Manual fallback chain:** `model: "gpt-4o-mini/azure,gpt-4o-mini/openai,gpt-4o-mini"`
**Exclude providers:** `model: "!openai,gpt-4o-mini"`

---

## 3. KONG AI GATEWAY

**Official Documentation:** https://developer.konghq.com/ai-gateway/load-balancing/

### 3.1 Load Balancing Algorithms

Kong AI Proxy Advanced plugin supports **7 distinct algorithms**:

#### 1. Round-robin (Weighted)
**Description:** Distributes requests across models based on assigned weights. If models `gpt-4`, `gpt-4o-mini`, and `gpt-3` have weights of `70`, `25`, and `5`, they receive approximately 70%, 25%, and 5% of traffic respectively.

**Characteristics:**
- Traffic is routed proportionally based on weights
- Requests follow a circular sequence adjusted by weight
- Does not account for cache-hit ratios, latency, or current load

#### 2. Consistent-hashing
**Description:** Routes requests based on a hash of a configurable header value. Requests with the same header value are routed to the same model.

**Configuration:** `hash_on_header` setting defines the header to hash. Default is `X-Kong-LLM-Request-ID`.

**Characteristics:**
- Effective with consistent keys like user IDs
- Requires diverse hash inputs for balanced distribution
- Useful for session persistence and cache-hit optimization

#### 3. Least-connections (v3.13+)
**Description:** Tracks the number of in-flight requests for each backend and routes new requests to the backend with the highest spare capacity.

**Characteristics:**
- Dynamically adapts to backend response times
- Routes away from slower backends as they accumulate open connections
- Does not account for cache-hit ratios

#### 4. Lowest-usage (v3.10+)
**Description:** Routes requests to models with the lowest measured resource usage.

**Configuration:** `tokens_count_strategy` parameter defines how usage is measured:
- `prompt_token_counts`
- `response_token_counts`
- `cost`

#### 5. Lowest-latency
**Description:** Routes requests to the model with the lowest observed latency.

**Configuration:** `latency_strategy` parameter:
- `tpot` (default): time-per-output-token
- `e2e`: end-to-end response time

**Algorithm Detail:** Uses **peak EWMA (Exponentially Weighted Moving Average)** to track latency from TCP connect through body response. Metrics decay over time.

**Traffic Distribution:**
- The fastest model gets a majority of traffic (~90-99%)
- Kong never sends 100% to a single target unless it's the only one available
- EWMA ensures all targets continue to receive a small amount of traffic for ongoing probing

#### 6. Semantic (v3.13+)
**Description:** Routes requests based on semantic similarity between the prompt and model descriptions.

**Implementation:**
- Embeddings generated using specified model (e.g., `text-embedding-3-small`)
- Similarity calculated using vector search
- Requires vector database (e.g., Redis)
- `distance_metric` and `threshold` settings control matching sensitivity

#### 7. Priority (v3.10+)
**Description:** Routes requests to models based on assigned priority groups.

**Behavior:**
- The balancer always selects from the highest-priority group first
- If all targets in that group are unavailable, it falls back to the next group
- Within each group, the `weight` parameter controls traffic distribution

**Use case:** Cost-aware routing and controlled failover

### 3.2 Retry and Fallback Configuration

**Configuration Parameters:**
| Setting | Description |
|---------|-------------|
| `retries` | How many times to retry a failed request before reporting failure |
| `failover_criteria` | Which failures trigger failover (e.g., `http_429`, `http_500`, `error`, `timeout`) |
| `connect_timeout` | Maximum time to establish TCP connection |
| `read_timeout` | Maximum time to wait for server response |
| `write_timeout` | Maximum time to send request payload |

**Example:**
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

### 3.3 Health Check and Circuit Breaker (v3.13+)

**Behavior:**
- If unsuccessful attempts reach `config.balancer.max_fails`, the load balancer stops sending requests to that target
- Target is reconsidered after `config.balancer.fail_timeout` period
- Failure counter tracks total failures, not consecutive failures
- Counter resets only when a successful request occurs after `fail_timeout` has elapsed since the last failed request
- If all targets become unhealthy simultaneously, requests fail with `HTTP 500`

---

## 4. OPENROUTER

**Official Documentation:** https://openrouter.ai/docs/guides/routing/provider-selection

### 4.1 Default Load Balancing Strategy

**Algorithm:** Price-based load balancing with inverse-square weighting

**Exact Steps:**
1. Prioritize providers that have not seen significant outages in the last 30 seconds
2. For stable providers, look at lowest-cost candidates and select one weighted by **inverse square of the price**
3. Use remaining providers as fallbacks

**Mathematical Formula:**
```
Weight = 1 / (price^2)
```

**Example:**
- Provider A costs $1/M tokens
- Provider B costs $2/M tokens  
- Provider C costs $3/M tokens

Result: Provider A is **9x more likely** to be selected than Provider C because (1 / 3² = 1/9)

### 4.2 Provider Sorting (Explicit Priority)

When `sort` or `order` is set, load balancing is disabled and providers are tried in order.

**Sort Options:**
- `"price"`: prioritize lowest price
- `"throughput"`: prioritize highest throughput
- `"latency"`: prioritize lowest latency

**Shortcuts:**
- `:nitro` suffix = sort by throughput (e.g., `model: "llama-3.3-70b:nitro"`)
- `:floor` suffix = sort by price (e.g., `model: "llama-3.3-70b:floor"`)

### 4.3 Advanced Sorting with Partition

**Configuration:**
```typescript
provider: {
  sort: {
    by: 'throughput',
    partition: 'none'  // 'model' (default) or 'none'
  }
}
```

**Partition Options:**
- `partition: "model"` (default): Groups endpoints by model before sorting
- `partition: "none"`: Removes grouping, allowing endpoints to be sorted globally across all models

### 4.4 Performance Thresholds

**Percentile-Based Routing:**
OpenRouter tracks metrics using percentile statistics over a rolling 5-minute window:
- **p50** (median): 50% of requests perform better
- **p75**: 75% of requests perform better
- **p90**: 90% of requests perform better
- **p99**: 99% of requests perform better

**Configuration:**
```typescript
provider: {
  preferredMinThroughput: {
    p90: 50  // Prefer providers with >50 tokens/sec for 90% of requests
  },
  preferredMaxLatency: {
    p90: 3   // Prefer providers with <3 second latency for 90% of requests
  }
}
```

**Behavior:** Endpoints not meeting thresholds are deprioritized (moved to fallback positions) rather than excluded entirely.

### 4.5 Model Fallbacks

**Configuration:**
```typescript
models: ['anthropic/claude-3.5-sonnet', 'gryphe/mythomax-l2-13b']
```

**Behavior:** Provide an array of model IDs in priority order. If the first model returns an error, OpenRouter automatically tries the next model in the list.

**Fallback Triggers:**
- Context length validation errors
- Moderation flags for filtered models
- Rate-limiting
- Downtime

### 4.6 Provider Routing Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `order` | string[] | - | List of provider slugs to try in order |
| `allow_fallbacks` | boolean | `true` | Whether to allow backup providers |
| `only` | string[] | - | List of provider slugs to allow |
| `ignore` | string[] | - | List of provider slugs to skip |
| `sort` | string/object | - | Sort providers by price, throughput, or latency |
| `max_price` | object | - | Maximum pricing for request |

---

## 5. CLOUDFLARE AI GATEWAY

**Official Documentation:** https://developers.cloudflare.com/ai-gateway/features/dynamic-routing

### 5.1 Dynamic Routing Architecture

Cloudflare uses a **visual flow-based routing system** with JSON configuration support.

**Core Concepts:**
- **Route**: A named, versioned flow (e.g., `dynamic/support`)
- **Nodes**: Start, Conditional, Percentage, Model, Rate Limit, Budget Limit, End
- **Metadata**: Arbitrary key-value context for routing decisions
- **Versions**: Each change produces a new draft with instant rollback

### 5.2 Supported Node Types

#### Conditional Element (If/Else)
Evaluates conditions based on request parameters and routes accordingly.

**Configuration:**
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

#### Percentage Split
Routes requests probabilistically across multiple outputs for A/B testing.

**Configuration:**
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

#### Rate/Budget Limit
Apply limits based on request metadata with automatic fallback.

**Configuration:**
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

**Limit Types:**
- `limitType`: "count" or "cost"
- `technique`: "sliding" or "fixed" window

#### Model Node
Executes inference with configurable timeout and retry settings.

**Configuration:**
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

### 5.3 Request Handling (Legacy)

**Request Retries:**
- Maximum of 5 retry attempts
- Configurable backoff: "constant", "linear", or "exponential"
- Configurable retry delay (max 5 seconds)

**Configuration:**
```json
{
  "config": {
    "maxAttempts": 5,
    "retryDelay": 1000,
    "backoff": "exponential"
  }
}
```

### 5.4 Response Headers

Dynamic routes return:
- `cf-aig-model`: The model used
- `cf-aig-provider`: The slug of provider used

---

## 6. BRAINTRUST

**Official Documentation:** https://www.braintrust.dev/docs/deploy/gateway

### 6.1 Load Balancing Behavior

**Automatic Load Balancing:**
When multiple AI providers support the same model, Braintrust **automatically load balances** requests across all available providers.

**Use Case:** Working around per-account rate limits and providing resiliency if one provider is down.

### 6.2 Provider Selection Override

**Header-Based Routing:**
Use the `x-bt-endpoint-name` header to route requests to a specific provider credential.

**Example:**
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

**Verification:** Check the `x-bt-used-endpoint` response header to confirm which provider handled the request.

### 6.3 Gateway Features

**Caching:**
- Gateway automatically caches results
- Three modes: `auto` (default), `always`, `never`
- In `auto` mode, requests are cached if they have `temperature=0` or `seed` parameter set
- Default TTL: 1 week (max 604800 seconds)
- Cache encryption: AES-GCM with key derived from user's API key

**Supported Cache Paths:**
- `/auto`
- `/embeddings`
- `/chat/completions`
- `/completions`
- `/moderations`

**Response Headers:**
- `x-bt-cached`: `HIT` or `MISS`
- `x-bt-used-endpoint`: The configured provider endpoint used
- `x-bt-span-id`: ID of the logged span (when tracing enabled)

### 6.4 Configuration Headers

| Header | Values | Description |
|--------|--------|-------------|
| `x-bt-use-cache` | `auto`, `always`, `never` | Control caching behavior |
| `x-bt-cache-ttl` | Seconds (max 604800) | Set cache TTL |
| `x-bt-endpoint-name` | Endpoint name | Use specific configured endpoint |
| `x-bt-project-id` | Project ID | Use project-level AI provider credentials |
| `x-bt-org-name` | Organization name | Specify organization for multi-org users |

---

## Comparative Summary

| Gateway | Weighted Routing | Latency-Based | Cost-Based | Sticky Sessions | Circuit Breaker | Semantic Routing |
|---------|-----------------|---------------|------------|-----------------|-----------------|------------------|
| **Portkey** | ✅ Probabilistic | ❌ | ❌ | ✅ Hash-based | ❌ | ❌ |
| **Helicone** | ✅ | ✅ P2C+PeakEWMA | ✅ Cheapest-first | ❌ | ❌ | ❌ |
| **Kong** | ✅ Round-robin | ✅ Peak EWMA | ✅ Lowest-usage | ✅ Consistent-hash | ✅ | ✅ |
| **OpenRouter** | ✅ Inverse-square | ✅ | ✅ Default | ❌ | ❌ | ❌ |
| **Cloudflare** | ✅ Percentage split | ❌ | ✅ Budget limits | ❌ | ❌ | ❌ |
| **Braintrust** | ✅ Automatic | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Sources

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

*Report generated on 2026-04-15. All information sourced from official documentation as of that date.*
