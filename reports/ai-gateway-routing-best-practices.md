# Resilient AI Gateway Routing: Design Principles for Unreliable LLM Providers

**Research Date**: April 2026  
**Objective**: Distilled design principles, algorithms, and operational techniques for SLA-focused model routing across flaky providers

---

## Executive Summary

Building a resilient AI gateway for unreliable LLM providers requires a multi-layered approach combining intelligent routing, health monitoring, circuit breakers, and adaptive load balancing. This document synthesizes best practices from production systems including LiteLLM, Bifrost, Kong AI Gateway, and academic research on multi-armed bandits for LLM routing.

**Key Findings:**
- Production gateways achieve 60-85% cost reduction through intelligent routing
- EWMA-based latency scoring reduces P95/P99 latency by 40-70%
- Circuit breakers prevent cascading failures during provider degradation
- Multi-armed bandits enable dynamic cost-quality-latency optimization

---

## 1. Core Routing Strategies

### 1.1 Weighted Load Balancing

**Concept**: Distribute traffic across providers based on configurable weights that reflect capacity, cost, or reliability preferences.

**Implementation Pattern**:
```yaml
# LiteLLM-style configuration
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      weight: 0.7  # 70% traffic
  - model_name: gpt-4o
    litellm_params:
      model: anthropic/claude-3-opus
      weight: 0.3  # 30% traffic
```

**Key Considerations**:
- Weights normalize automatically to sum to 1.0
- Weighted routing integrates with automatic failover (providers sorted by weight become fallback chain)
- Use for: cost optimization, capacity-based distribution, A/B testing

**Evidence**: [LLM Gateway routing implementation](https://llmgateway.io/blog/how-we-handle-llm-provider-failover) uses weighted scoring with uptime (50%), throughput (20%), price (20%), latency (10%)

### 1.2 Latency-Based Routing with EWMA

**Concept**: Use Exponentially Weighted Moving Average (EWMA) to track provider latency and route to the fastest healthy provider.

**EWMA Formula**:
```
score = health / (1 + latency_penalty)
where latency_penalty = request_latency * (1 + pending_requests * 0.1)
```

**Key Parameters** (from Envoy/AgentGateway):
- `decay_time`: 10s (default) - how quickly older samples lose influence
- `aggregation_interval`: 100ms - measurement collection frequency
- `default_rtt`: 10ms - baseline for new providers
- `alpha`: 0.3 - weight given to recent observations

**Power of Two Choices (P2C) Algorithm**:
1. Select two random providers from available pool
2. Score each based on health (EWMA), latency (EWMA), pending requests
3. Route to provider with better score

**Evidence**: [Solo.io AgentGateway](https://docs.solo.io/agentgateway/2.3.x/llm/load-balancing/) implements P2C with EWMA scoring, achieving adaptive routing without manual configuration

### 1.3 Health-Aware Routing

**Health Score Calculation**:
```
health_score = EWMA(success_rate)  # 1.0 for success, 0.0 for failure
```

**Eviction Policy**:
- Providers with consecutive failures enter "cooldown"
- 429 (rate limit) errors trigger immediate cooldown
- Non-429 errors degrade health score but don't evict immediately

**Evidence**: [VoidLLM](https://voidllm.ai/blog/load-balancing-failover-llm-providers) implements per-deployment circuit breakers with configurable failure thresholds

---

## 2. Resilience Patterns

### 2.1 Circuit Breaker Pattern

**States**:
- **CLOSED**: Normal operation, all requests pass through
- **OPEN**: Provider unhealthy, requests fast-fail immediately (0ms)
- **HALF-OPEN**: After cooldown, probe requests test recovery

**Configuration** (from LiteLLM/Bifrost):
```python
allowed_fails: 5          # Failures before cooldown
cooldown_time: 60s        # Time before half-open
failure_threshold: 0.95   # Uptime threshold for routing decisions
```

**Critical Insight**: Circuit breakers prevent "slow Redis" problems—when a dependency is degraded but not completely down, circuit breakers cut off traffic before threadpool exhaustion occurs.

**Evidence**: [LiteLLM Redis Circuit Breaker](https://docs.litellm.ai/blog/redis-circuit-breaker) demonstrates 0ms fast-fail vs 20-30s timeout per operation

### 2.2 Retry Strategies

**Exponential Backoff with Jitter**:
```python
delay = min(base_delay * (2 ** attempt), max_delay)
jitter = delay * random.uniform(0, jitter_factor)  # typically 0.25
wait_time = delay + jitter
```

**Retry Configuration**:
- Base delay: 1-2 seconds
- Max delay: 60 seconds
- Max retries: 3-5
- Jitter factor: 0.1-0.25 (prevents thundering herd)

**Retryable Status Codes**:
- 429: Rate limit exceeded
- 500, 502, 503, 504: Server errors
- 529: Overloaded (provider-specific)

**Non-Retryable**:
- 400: Bad request
- 401, 403: Authentication failures
- 413: Context window exceeded (use fallback instead)

**Evidence**: [Orq.ai retry documentation](https://docs.orq.ai/docs/proxy/retries) provides production-tested retry configuration

### 2.3 Fallback Chains

**Priority-Based Failover**:
```yaml
router_settings:
  fallbacks:
    - gpt-4o:
      - claude-3-opus
      - gpt-4o-mini  # graceful degradation
```

**Fallback Triggers**:
1. Connection errors
2. 5xx responses
3. Timeouts
4. Circuit breaker open
5. Rate limit (429) after retries exhausted

**Evidence**: [Bifrost request flow](https://docs.getbifrost.ai/architecture/core/request-flow) shows provider selection → health check → circuit breaker → fallback logic

---

## 3. Quota and Rate Limit Management

### 3.1 Token Bucket Algorithm

**Concept**: Track both requests per minute (RPM) and tokens per minute (TPM) because LLM costs scale with tokens, not requests.

**Implementation**:
```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.now()
    
    def consume(self, tokens):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

**Multi-Dimensional Limits**:
- Global server rate limit
- Per-virtual-key limits
- Per-user limits
- Per-team limits
- Per-model limits

**Evidence**: [LiteLLM architecture](https://docs.litellm.ai/docs/proxy/architecture) shows MaxParallelRequestsHandler checking RPM/TPM at multiple scopes

### 3.2 Dynamic Quota Allocation

**Priority Reservation**:
```yaml
priority_reservation:
  "prod": 0.9    # 90% reserved for production
  "dev": 0.1     # 10% reserved for development
saturation_threshold: 0.50  # Strict priority above 50% capacity
```

**Behavior**:
- Below saturation: generous mode allows priority borrowing
- Above saturation: strict mode enforces normalized priority limits

**Evidence**: [LiteLLM dynamic rate limiting](https://docs.litellm.ai/docs/proxy/dynamic_rate_limit) implements priority-based quota allocation

### 3.3 Adaptive Rate Control

**Proactive Throttling**:
```python
if rate_limited:
    current_rpm = max(1.0, current_rpm * 0.8)  # Reduce by 20%
```

**Evidence**: [Gemini API rate limiting guide](https://gemilab.net/en/articles/gemini-api/gemini-api-rate-limiting-quota-management-production-guide) recommends adaptive rate control to prevent hitting limits

---

## 4. Advanced Routing Techniques

### 4.1 Semantic Routing

**Concept**: Route requests to models based on prompt content and required capabilities.

**Implementation Approaches**:

1. **Task Classification** (vLLM Semantic Router):
   - Classify prompts into categories: math, code, creative, general
   - Route to specialized models (e.g., DeepSeek for math)
   - Inject domain-specific system prompts

2. **Complexity-Based Routing**:
   - Simple tasks → cheaper models (GPT-4o-mini, Claude Haiku)
   - Complex tasks → frontier models (GPT-4o, Claude Opus)
   - Classification cost: ~$0.001/request, ~430ms latency

3. **Confidence-Based Escalation**:
   - Try cheap model first
   - Score response confidence
   - Escalate to expensive model if confidence < threshold

**Evidence**: [vLLM Semantic Router](https://vllm-semantic-router.com/) implements BERT-based classification with 3x P90 latency improvement

### 4.2 Multi-Armed Bandits for LLM Selection

**Concept**: Formulate model selection as a contextual multi-armed bandit problem to balance exploration (trying new models) with exploitation (using known good models).

**Algorithms**:

1. **LinUCB** (Linear Upper Confidence Bound):
   - Assumes linear relationship between context and reward
   - Fast, works well with query embeddings
   - ~5ms routing overhead

2. **NeuralUCB**:
   - Non-linear reward function
   - Better for complex query-to-model mappings
   - Higher computational cost but better quality-cost tradeoffs

3. **ParetoBandit**:
   - Enforces dollar-denominated per-request budgets
   - Online primal-dual budget pacer
   - Hot-swap registry for runtime model onboarding
   - 9.8ms end-to-end routing latency on CPU

**Key Features**:
- Budget-aware routing with hard/soft/adaptive modes
- Geometric forgetting for rapid adaptation to price/quality shifts
- Runtime model registration without retraining

**Evidence**: [ParetoBandit paper](https://paretobandit.github.io/ParetoBandit/) demonstrates 0.4% budget compliance across 7 budget ceilings

### 4.3 Sticky Sessions

**Concept**: Route requests from the same session/conversation to the same provider to maximize KV-cache hit rates.

**Implementation**:
- Consistent hashing on session ID or user ID
- Header-based routing: `X-Session-ID` → hash → provider
- TTL-based expiration (default 1 hour)

**Benefits**:
- Maximizes prefix caching (vLLM, SGLang)
- Reduces Time-To-First-Token (TTFT)
- 57x faster first token response in some deployments

**Evidence**: [TrueFoundry sticky routing](https://docs.truefoundry.com/docs/sticky-routing) implements consistent hash-based session pinning

---

## 5. Cost-Latency-Reliability Tradeoffs

### 5.1 Model Tier Strategy

**Three-Tier Architecture**:

| Tier | Models | Use Case | Latency Target | Cost |
|------|--------|----------|----------------|------|
| Nano | GPT-4o-mini, Claude Haiku, Gemini Flash | Simple tasks, classification | <300ms TTFT | $0.30-1/M |
| Mid | GPT-4o, Claude Sonnet, Gemini Pro | General reasoning | <2s TTFT | $3-15/M |
| Frontier | GPT-4o, Claude Opus, Gemini Ultra | Complex analysis, coding | Flexible | $15-75/M |

**Target Distribution**:
- Nano: ~30% of traffic
- Mid: ~50% of traffic
- Frontier: ~20% of traffic (should not exceed)

**Evidence**: [AI Model Routing 2026](https://www.learnaiforge.com/articles/ai-model-routing-2026) documents 60-85% cost reduction with proper tiering

### 5.2 Latency Optimization

**Techniques**:

1. **Semantic Caching**:
   - Two-level lookup: exact hash → semantic similarity
   - Similarity threshold: 0.92 (typical)
   - Cache hit saves 100% of LLM cost and latency
   - 15-30% typical cache hit rate

2. **Prefix Caching** (vLLM/SGLang):
   - Route conversations with shared history to same worker
   - Reuse KV-cache from previous turns
   - Requires sticky session routing

3. **Streaming First**:
   - Always use streaming for user-facing requests
   - Time-To-First-Token (TTFT) matters more than total time
   - Users perceive delays >300ms

**Evidence**: [Semantic caching guide](https://dev.to/pranay_batta/semantic-caching-in-a-production-llm-gateway-three-design-decisions-that-mattered-2pgj) shows dual-layer approach (exact → semantic)

### 5.3 Cost Control Mechanisms

**Budget Enforcement**:
- Per-request cost ceilings
- Per-user daily/monthly budgets
- Per-team spending limits
- Automatic model downgrade when budget exhausted

**Cost Attribution**:
- Track spend per request, per user, per team
- Real-time cost estimation before request
- Alert at 80% and 90% of budget

**Batch API**:
- 50% cost discount for non-real-time workloads
- Results within 24 hours
- Free cost reduction for background processing

**Evidence**: [Morph LLM cost optimization](https://morphllm.com/llm-cost-optimization) documents 5 levers for 70-85% cost reduction

---

## 6. Operational Best Practices

### 6.1 Health Monitoring

**Metrics to Track**:
- Provider uptime (success rate over 5-minute window)
- P50/P95/P99 latency per provider
- Error rate by status code
- Rate limit hit frequency
- Cost per 1K requests

**Alert Thresholds**:
- Uptime <95%: Page on-call
- P95 latency >2x baseline: Investigate
- Error rate >1%: Check provider status

### 6.2 Observability

**Required Telemetry**:
- Request ID for end-to-end tracing
- Routing decision logs (why was this provider chosen?)
- Cache hit/miss rates
- Circuit breaker state changes
- Cost attribution per request

**Evidence**: [Bifrost architecture](https://github.com/maximhq/bifrost) includes telemetry plugin for monitoring

### 6.3 Deployment Patterns

**Multi-Region Failover**:
- Deploy gateways in multiple regions
- Route to nearest healthy provider
- Automatic regional failover

**Sidecar Architecture** (LiteLLM):
- Python control plane: routing logic, validation
- Sidecar data plane: request forwarding, connection pooling
- Achieves sub-millisecond overhead

**Evidence**: [LiteLLM sub-millisecond overhead](https://docs.litellm.ai/blog/sub-millisecond-proxy-overhead) describes sidecar architecture

---

## 7. Implementation Checklist

### Minimum Viable Gateway
- [ ] Weighted load balancing across 2+ providers
- [ ] Circuit breaker with 5-failure threshold
- [ ] Exponential backoff with jitter (3 retries)
- [ ] Health checks every 30 seconds
- [ ] Basic request logging

### Production-Ready Gateway
- [ ] EWMA-based latency scoring
- [ ] Token bucket rate limiting (RPM + TPM)
- [ ] Semantic caching layer
- [ ] Multi-tier model routing
- [ ] Per-user/team budgets
- [ ] Comprehensive observability (metrics, tracing)
- [ ] Multi-region deployment

### Advanced Gateway
- [ ] Multi-armed bandit routing
- [ ] Semantic routing by task type
- [ ] Sticky session support
- [ ] KV-cache aware routing
- [ ] Dynamic quota allocation
- [ ] Automatic cost optimization

---

## 8. References

### Open Source Implementations

1. **LiteLLM** (Python)
   - GitHub: https://github.com/BerriAI/litellm
   - Features: Multi-provider routing, fallbacks, rate limiting, budgets
   - Architecture: [ARCHITECTURE.md](https://github.com/BerriAI/litellm/blob/main/ARCHITECTURE.md)

2. **Bifrost** (Go)
   - GitHub: https://github.com/maximhq/bifrost
   - Features: 50x faster than LiteLLM, <100µs overhead, semantic caching
   - Docs: https://docs.getbifrost.ai/

3. **vLLM Semantic Router**
   - GitHub: https://github.com/vllm-project/semantic-router
   - Features: BERT-based classification, semantic caching, PII detection

4. **ParetoBandit**
   - GitHub: https://github.com/paretobandit/paretobandit
   - Features: Budget-aware contextual bandits for LLM routing

### Academic Papers

1. **Preference-Conditioned Dynamic Routing** (2025)
   - arXiv:2502.02743
   - Multi-armed bandit formulation with user preference capture

2. **MixLLM: Dynamic Contextual Bandit Routing** (2025)
   - arXiv:2502.18482
   - LinUCB-based routing with latency constraints

3. **ParetoBandit: Budget-Paced Adaptive Routing** (2026)
   - arXiv:2604.00136
   - Online primal-dual budget control with runtime model onboarding

### Documentation

1. **Envoy Peak EWMA Load Balancer**
   - https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/contrib/load_balancing_policies/peak_ewma/peak_ewma.html

2. **Kong AI Gateway Load Balancing**
   - https://developer.konghq.com/ai-gateway/load-balancing/

3. **Solo.io AgentGateway**
   - https://docs.solo.io/agentgateway/2.3.x/llm/load-balancing/

4. **Microsoft GenAI Gateway Playbook**
   - https://learn.microsoft.com/en-us/ai/playbook/solutions/generative-ai/genai-gateway/key-considerations

---

## 9. Summary

Building a resilient AI gateway requires:

1. **Layered Resilience**: Combine retries, fallbacks, and circuit breakers
2. **Intelligent Routing**: Use EWMA scoring and multi-armed bandits for dynamic optimization
3. **Quota Awareness**: Implement token bucket rate limiting with priority reservation
4. **Cost Optimization**: Deploy semantic caching and model tiering
5. **Observability**: Track routing decisions, health metrics, and cost attribution

The most successful production systems (Bifrost, LiteLLM, Kong AI Gateway) share common patterns: health-aware routing, automatic failover, and comprehensive observability. Start with weighted routing and circuit breakers, then add EWMA scoring and semantic caching as scale demands.

**Key Takeaway**: Resilience is not a feature—it's an emergent property of proper layering. Each layer (retry → fallback → circuit breaker) handles a different failure mode, and together they create systems that degrade gracefully rather than failing catastrophically.
