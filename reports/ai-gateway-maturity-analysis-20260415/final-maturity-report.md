# AI Gateway 成熟度与推荐最终报告（免费、本地、离线）

你的约束：
1. **免费**
2. **本地部署**
3. **不依赖云服务**

这份报告直接回答你的核心问题：**哪些项目真正成熟，哪些是早期/hobby 风险。**

---

## 一、证据级成熟度分层

### 第一梯队：Enterprise Mature（可放心生产）

| 项目 | Stars | Contributors | Releases | License | 生产证据 |
|---|---|---|---|---|---|
| LiteLLM | 43,500+ | 400+ | 1,300+ | MIT | Netflix、Stripe、Google ADK、OpenHands |
| SGLang Model Gateway | 25,796 | 大型社区 | 活跃 | Apache 2.0 | 大规模生产部署、prefill/decode disaggregation |
| Apache APISIX | 16,500+ | 420+ | 65 | Apache 2.0 | NASA JPL、Tencent、Zoom、OPPO、Airwallex |
| OpenLLM | 12,273 | 100+ | 147 | Apache 2.0 | BentoML 生态、自托管推理主流 |
| Portkey OSS Gateway | 11,300+ | 100+ | 81 | MIT | 2T tokens/day、$180M annualized spend managed |

### 第二梯队：Growing/Pre-Enterprise（有潜力但偏新）

| 项目 | Stars | Contributors | Releases | License | 备注 |
|---|---|---|---|---|---|
| Bifrost | 3,704 | 活跃 | 1,436 | Apache 2.0 | Go、号称 50x faster than LiteLLM、单二进制 |
| llm-d | 2,986 | 活跃 | 多 | Apache 2.0 | Kubernetes-native、prefix-cache aware routing |
| vLLM Router | 2,000+ | 活跃 | 多 | Apache 2.0 | Rust、为 vLLM 大规模部署而生 |
| Envoy AI Gateway | 1,465 | 90+ | 20 | Apache 2.0 | CNCF、6 个月新、但 Envoy 底座很强 |
| AxonHub | 2,852 | 40+ | 108 | MIT | 新但活跃、TypeScript |
| OmniRoute | 1,723 | 50+ | 198 | MIT | 新但更新频繁 |

### 第三梯队：Early Stage（谨慎使用）

| 项目 | Stars | Contributors | Releases | License | 备注 |
|---|---|---|---|---|---|
| LLMGateway (theopenco) | 1,044 | 20 | 4 | AGPLv3 + Enterprise | AGPLv3 license、相对稳定 |
| AIProxy (labring) | 415 | 20 | 57 | MIT | Go 实现、中等成熟度 |
| Helicone AI Gateway | 565 | 小 | 多 | Apache 2.0 | Rust、简单部署、但 community 小 |
| Inference Gateway | 109 | 4 | 151 | MIT | Go、新但 releases 多 |
| Olla | 194 | 4 | 19 | Apache 2.0 | 偏本地推理节点池、早期项目 |

### 第四梯队：Hobby/Very Early（不建议生产）

| 项目 | Stars | Contributors | Releases | License | 备注 |
|---|---|---|---|---|---|
| Ferro Labs AI Gateway | 62 | 3 | 21 | Apache 2.0 | 2 个月新、bus factor 高风险 |
| Routerly | 31 | 1 | 1 | AGPL-3.0 | 单 contributor、AGPL license 限制、高风险 |

---

## 二、诚实判断：低 Star 项目到底靠谱吗

### Ferro Labs AI Gateway（61 stars）

**证据：**
- GitHub：https://github.com/ferro-labs/ai-gateway
- 创建时间：2026-02-25（约 2 个月）
- Contributors：3
- Releases：21
- License：Apache 2.0

**优点：**
- Go 单二进制、32MB 内存
- 自测 benchmark vs LiteLLM/Kong/Portkey
- MCP 支持、29 providers
- 文档写得认真

**风险：**
- **61 stars**：极低采纳量
- **3 contributors**：bus factor 极高（一个作者退出就没人维护）
- **2 个月新**：无生产部署证据
- **self-reported benchmarks**：不是独立第三方验证

**结论：**
- 适合：你愿意当早期用户、愿意自己维护、你偏 Go栈
- 不适合：你要稳定生产、不想承担"作者不再维护"风险

---

### Routerly（31 stars）

**证据：**
- GitHub：https://github.com/Inebrio/Routerly
- 创建时间：2026-02-27（约 2 个月）
- Contributors：1（单人项目）
- Releases：1
- License：AGPL-3.0

**优点：**
- LLM-native routing（独特）
- Native Anthropic API 支持
- 零依赖、JSON 配置

**风险：**
- **31 stars**：几乎无采纳
- **1 contributor**：极端 bus factor
- **AGPL-3.0**：对企业有 license 限制
- **1 release**：非常早期
- README 对比表是作者自写的营销话

**结论：**
- 高风险 hobby 项目，不建议生产
- 若你要尝鲜，需接受 AGPL-3.0 和单人维护风险

---

### Olla（192 stars）

**证据：**
- GitHub：https://github.com/thushan/olla
- 创建时间：2025-05-23（约 11 个月）
- Contributors：4
- Releases：19
- License：Apache 2.0

**优点：**
- 偏本地推理节点池（Ollama/vLLM/llama.cpp）
- 高性能、sub-millisecond latency
- circuit breaker + health check

**风险：**
- **192 stars**：小众采纳
- **4 contributors**：小团队
- 定位是"LiteLLM 的补充"，不是独立替代

**结论：**
- 适合你偏自建推理节点池的场景
- 若你要跨 SaaS provider 的 LLM gateway，它不如 LiteLLM/SGLang

---

## 三、新发现的高 Star 成熟项目

### SGLang Model Gateway（25,796 stars）

**GitHub**：https://github.com/sgl-project/sglang
**License**：Apache 2.0
**Language**：Rust/Python

**核心能力：**
- 大规模 LLM 部署的 model-routing gateway
- Cache-aware load balancing、fault tolerance
- Kubernetes-native service discovery
- Prefill/decode disaggregation
- MCP tooling support
- 高吞吐、低延迟（行业级 benchmark）

**是否满足你的场景：**
- ✅ 免费、本地、离线
- ✅ 多 provider 路由 + fallback
- ✅ production evidence（大规模部署）
- ⚠️ 更偏"推理基础设施层"，不是纯 SaaS provider gateway

---

### Bifrost（3,704 stars）

**GitHub**：https://github.com/maximhq/bifrost
**License**：Apache 2.0
**Language**：Go

**核心能力：**
- 单二进制、零配置启动
- 50x faster than LiteLLM（self-reported：11 µs overhead at 5k RPS）
- Adaptive load balancer + cluster mode
- 1000+ models、多 provider
- MCP integration
- SSO、Prometheus、distributed tracing

**是否满足你的场景：**
- ✅ 免费、本地、离线
- ✅ Go 单二进制、高性能
- ✅ 多 provider + fallback + caching
- ⚠️ 3,704 stars（成长期），无大规模企业背书证据

---

### OpenLLM（12,273 stars）

**GitHub**：https://github.com/bentoml/OpenLLM
**License**：Apache 2.0
**Language**：Python

**核心能力：**
- 自托管任意开源 LLM（Llama、Mistral、Qwen、DeepSeek）
- OpenAI-compatible API
- vLLM inference backend
- Docker + Kubernetes
- 内建 chat UI

**是否满足你的场景：**
- ✅ 免费、本地、离线
- ✅ 自托管推理主流方案
- ⚠️ 更偏"自托管推理层"，不是跨 SaaS provider 的 API gateway

---

### vLLM Router（2,000+ stars）

**GitHub**：https://github.com/vllm-project/router
**License**：Apache 2.0
**Language**：Rust

**核心能力：**
- 为 vLLM 大规模部署而生的高性能 router
- 多种 load balancing algorithms（cache-aware、power of two、consistent hashing、round robin）
- Prefill/decode disaggregation
- Health monitoring + fault tolerance

**是否满足你的场景：**
- ✅ 免费、本地、离线
- ✅ 高性能 Rust 实现
- ⚠️ 针对 vLLM backend，不是通用 SaaS provider gateway

---

### llm-d（2,986 stars）

**GitHub**：https://github.com/llm-d/llm-d
**License**：Apache 2.0
**Language**：Go

**核心能力：**
- Kubernetes-native distributed inference
- Prefix-cache aware routing
- Kubernetes Gateway API-based load balancer
- Disaggregated serving（prefill/decode separation）
- Hierarchical KV offloading
- Cache-aware LoRA routing

**是否满足你的场景：**
- ✅ 免费、本地、离线
- ✅ Kubernetes-native
- ⚠️ 需要 Kubernetes 1.29+，偏企业级分布式部署

---

## 四、最终推荐（按成熟度 + 你的约束）

### 如果你最在意"稳 + 成熟 + 生产证据"

**首选（Enterprise Mature）：**
1. **LiteLLM**（43,500+ stars、Netflix/Stripe 在用）
2. **SGLang Model Gateway**（25,796 stars、大规模生产）
3. **Apache APISIX**（16,500+ stars、NASA/Tencent/Zoom）
4. **OpenLLM**（12,273 stars、BentoML 生态）
5. **Portkey OSS Gateway**（11,300+ stars、2T tokens/day）

---

### 如果你最在意"高性能 + Go栈 + 轻量"

**可选（Growing/High-Performance）：**
1. **Bifrost**（3,704 stars、Go、11 µs overhead）
2. **vLLM Router**（2,000+ stars、Rust、为 vLLM 大规模）
3. **llm-d**（2,986 stars、Go、Kubernetes-native）
4. **Envoy AI Gateway**（1,465 stars、CNCF、Envoy 底座）

---

### 如果你接受"新但活跃"的风险

**可选（Growing）：**
1. **AxonHub**（2,852 stars、TypeScript）
2. **OmniRoute**（1,723 stars、新但 198 releases）

---

### 不建议生产（Very Early/Hobby）

- **Ferro Labs AI Gateway**（62 stars、3 contributors、2 个月新）
- **Routerly**（31 stars、1 contributor、AGPL-3.0）

---

## 五、直接回答你的问题

> "这几个项目的 star 都好少啊，靠谱吗？"

**诚实回答：**

- **Ferro Labs（61 stars）、Routerly（31 stars）**：高风险早期项目，不建议生产。
- **Olla（192 stars）**：偏本地推理节点池，早期项目，但有 niche 价值。
- **真正成熟的项目**：LiteLLM（43k+）、SGLang（25k+）、APISIX（16k+）、OpenLLM（12k+）、Portkey OSS（11k+）。

你的质疑是对的。低 star 项目 bus factor 高、无生产证据、self-reported benchmarks。若你要稳，优先 LiteLLM / SGLang / APISIX / OpenLLM / Portkey OSS。

---

## 六、主要来源

- LiteLLM GitHub: https://github.com/BerriAI/litellm
- SGLang GitHub: https://github.com/sgl-project/sglang
- Bifrost GitHub: https://github.com/maximhq/bifrost
- OpenLLM GitHub: https://github.com/bentoml/OpenLLM
- vLLM Router GitHub: https://github.com/vllm-project/router
- llm-d GitHub: https://github.com/llm-d/llm-d
- Apache APISIX GitHub: https://github.com/apache/apisix
- Envoy AI Gateway GitHub: https://github.com/envoyproxy/ai-gateway
- Portkey OSS Gateway GitHub: https://github.com/Portkey-AI/gateway
- AxonHub GitHub: https://github.com/looplj/axonhub
- OmniRoute GitHub: https://github.com/diegosouzapw/omniroute
- Ferro Labs GitHub: https://github.com/ferro-labs/ai-gateway
- Routerly GitHub: https://github.com/Inebrio/Routerly
- Olla GitHub: https://github.com/thushan/olla