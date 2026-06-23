# AI 网关接口转换调研报告

**调研日期**: 2026-06-22  
**调研目标**: 除了 AxonHub 之外，还有哪些 AI 网关支持 responses、messages、completions 三个接口的相互转换？

## 调研背景

当前 AI 领域存在三种主要的 API 接口格式：

1. **OpenAI Chat Completions** (`/v1/chat/completions`) - 最广泛使用的标准接口
2. **OpenAI Responses API** (`/v1/responses`) - 新一代代理式 AI 接口
3. **Anthropic Messages API** (`/v1/messages`) - Claude 的原生接口

用户希望找到支持这三种接口相互转换的 AI 网关，以便在不同格式之间无缝切换。

## 调研结果

经过全网调研，发现以下 AI 网关明确支持三种接口的相互转换：

### 1. Portkey AI Gateway

**支持状态**: ✅ 完全支持三种格式相互转换

**开源状态**: 
- **开源版本** (https://github.com/portkey-ai/gateway): 支持接口转换，但功能有限
- **企业版**: 完整功能，包括监控、密钥管理、安全合规等

**开源版本支持的功能**:
- ✅ 三种 API 格式转换：Chat Completions、Responses API、Messages API
- ✅ 自动重试和回退
- ✅ 负载均衡和条件路由
- ✅ Guardrails（防护栏）
- ✅ 多模态支持
- ✅ 轻量级（122kb），低延迟（<1ms）

**开源版本不支持的功能**（需要企业版）:
- ❌ 安全密钥管理（Secure Key Management）
- ❌ 语义缓存（Semantic Caching）
- ❌ 访问控制和入站规则（Access Control & Inbound Rules）
- ❌ PII 脱敏（PII Redaction）
- ❌ 合规性认证（SOC2, ISO, HIPAA, GDPR）
- ❌ 专业支持
- ❌ gRPC 支持

**文档链接**: https://docs.portkey.ai/docs/product/ai-gateway/universal-api

**使用示例**:
```bash
# 运行开源版本
npx @portkey-ai/gateway

# 使用 Chat Completions 格式调用 Anthropic 模型
curl -X POST http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-portkey-provider: anthropic" \
  -d '{"model": "claude-sonnet-4-5-20250514", "messages": [{"role": "user", "content": "Hello!"}]}'

# 使用 Responses API 格式调用 OpenAI 模型
curl -X POST http://localhost:8787/v1/responses \
  -H "Content-Type: application/json" \
  -H "x-portkey-provider: openai" \
  -d '{"model": "gpt-5.2", "input": "Explain quantum computing"}'

# 使用 Messages API 格式调用 Google 模型
curl -X POST http://localhost:8787/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-portkey-provider: google" \
  -d '{"model": "gemini-2.0-flash", "messages": [{"role": "user", "content": "Hello!"}]}'
```

**结论**: Portkey 开源版本的核心价值是**接口转换**，适合需要协议转换但不需要完整监控和安全管理的场景。

### 2. Cloudflare AI Gateway

**支持状态**: ✅ 完全支持三种格式相互转换

**关键特性**:
- 四个统一端点：`/ai/run`、`/ai/v1/chat/completions`、`/ai/v1/responses`、`/ai/v1/messages`
- 自动处理提供商之间的格式转换
- 内置日志、缓存、速率限制和防护栏
- 支持 OpenAI、Anthropic、Google 等主要提供商

**文档链接**: https://developers.cloudflare.com/ai-gateway/usage/rest-api/

**使用示例**:
```bash
# Chat Completions 格式
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions" \
  -H "Authorization: Bearer {CF_API_TOKEN}" \
  -d '{"model": "openai/gpt-5.2", "messages": [{"role": "user", "content": "Hello!"}]}'

# Responses API 格式
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/responses" \
  -H "Authorization: Bearer {CF_API_TOKEN}" \
  -d '{"model": "openai/gpt-4.1", "input": "Hello!"}'

# Messages API 格式
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/messages" \
  -H "Authorization: Bearer {CF_API_TOKEN}" \
  -d '{"model": "anthropic/claude-4-5-sonnet", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### 3. AISIX (API7 AI Gateway)

**支持状态**: ⚠️ 文档显示支持，但开源版本不包含此功能

**开源状态**: 
- **AISIX 开源版本** (Apache-2.0): 只支持 Chat Completions，**不支持**接口转换
- **AISIX Cloud / API7 Enterprise**: 支持完整接口转换功能（商业版本）

**关键发现**:
根据 GitHub 仓库 (https://github.com/api7/aisix)，开源版本的 Roadmap 显示：
- [ ] OpenAI Responses API
- [ ] Anthropic Messages API
- [ ] Google Gemini GenerateContent API

**这意味着开源版本目前只支持 Chat Completions，接口转换功能不在开源版本中。**

**文档网站功能**:
文档网站 (docs.api7.ai) 描述的接口转换功能很可能属于：
- API7 Enterprise 版本
- AISIX Cloud 托管服务
- 而非开源版本

**结论**: 如果需要开源的接口转换功能，AISIX 不是合适的选择。

### 4. Envoy AI Gateway

**支持状态**: ✅ 完全支持三种格式相互转换

**关键特性**:
- 支持 OpenAI 兼容 API 和 Anthropic 兼容 API
- 自动格式转换：Anthropic Messages ↔ OpenAI Chat Completions
- Responses API 支持，包括 Azure OpenAI 后端
- 提供商回退和负载均衡

**文档链接**: https://aigateway.envoyproxy.io/docs/capabilities/llm-integrations/supported-endpoints/

**支持端点**:
- `POST /v1/chat/completions` - 完全支持
- `POST /v1/responses` - 完全支持
- `POST /v1/messages` - 完全支持
- `POST /v1/completions` - 完全支持（传统端点）

### 5. Edgee AI Gateway

**支持状态**: ⚠️ 部分支持三种格式

**关键特性**:
- 支持两种 API 格式：OpenAI 格式（`/v1/chat/completions` 或 `/v1/responses`）和 Anthropic 格式（`/v1/messages`）
- 边缘原生 AI 网关，支持私有模型托管
- 自动模型选择和成本审计

**文档链接**: https://edgee.mintlify.app/api-reference

**限制**: 主要支持 OpenAI 和 Anthropic 格式，但 Responses API 和 Chat Completions 共享同一 OpenAI 格式。

## 对比表格

| AI 网关 | Chat Completions | Responses API | Messages API | 自动转换 | 开源状态 | 备注 |
|---------|------------------|---------------|--------------|----------|----------|------|
| **Portkey** | ✅ | ✅ | ✅ | ✅ | 核心开源（功能受限） | 开源版支持接口转换，但监控/密钥管理等需要企业版 |
| **Cloudflare AI Gateway** | ✅ | ✅ | ✅ | ✅ | 商业 | 统一端点，内置防护栏 |
| **Envoy AI Gateway** | ✅ | ✅ | ✅ | ✅ | **完全开源** | 完整功能开源，Envoy 代理基础 |
| **AIGateway (arcboxlabs)** | ✅ | ✅ | ⚠️ | ⚠️ | **开源** | 开源，专注于 Responses API 转换 |
| **AISIX (API7 AI Gateway)** | ✅ | ❌ (开源版) | ❌ (开源版) | ❌ (开源版) | 核心开源但功能受限 | 开源版只支持 Chat Completions |
| **Edgee AI Gateway** | ✅ | ✅ | ✅ | ⚠️ | 商业 | 边缘原生，部分转换支持 |
| **Gravitee** | ✅ | ✅ | ⚠️ | ⚠️ | 商业 | 需要确认 Messages 支持 |
| **Hadrian Gateway** | ✅ | ✅ | ⚠️ | ⚠️ | 实验性 | 实验性阶段 |

## 详细分析

### Portkey AI Gateway
**优势**:
- 最全面的三种格式支持
- 200+ 模型提供商支持
- 完善的文档和示例
- 提供统一的 SDK

**适用场景**:
- 需要在多种 API 格式之间切换的复杂应用
- 多提供商环境
- 需要高级路由和负载均衡

### Cloudflare AI Gateway
**优势**:
- 统一的 REST API 端点
- 内置安全功能（速率限制、防护栏）
- 全球边缘网络，低延迟
- 无需管理 API 密钥

**适用场景**:
- 已经使用 Cloudflare 生态系统
- 需要全球分布的 AI 网关
- 对安全性要求高

### API7 AI Gateway (APISIX)
**优势**:
- 基于成熟的 APISIX 网关
- 企业级功能（RBAC、监控、告警）
- 灵活的路由和转换规则
- 开源可自托管

**适用场景**:
- 企业级部署
- 需要高度定制化
- 已有 APISIX 基础设施

### Envoy AI Gateway
**优势**:
- 基于 Envoy 代理，性能优秀
- 开源社区活跃
- 与 Kubernetes 生态良好集成
- 支持多种云提供商

**适用场景**:
- Kubernetes 环境
- 需要高性能代理
- 云原生架构

## 转换能力详解

### 请求转换
所有支持的网关都能处理以下转换：

1. **Chat Completions → Messages**:
   - `messages` 数组转换为 Anthropic 格式
   - 系统消息提取为顶级 `system` 字段
   - 工具调用格式转换

2. **Messages → Chat Completions**:
   - Anthropic 消息格式转换为 OpenAI 格式
   - `system` 字段转换为系统消息
   - 工具使用格式转换

3. **Chat Completions → Responses**:
   - `messages` 转换为 `input` 数组
   - 系统消息转换为 `instructions`
   - 工具调用格式转换

4. **Responses → Chat Completions**:
   - `input` 数组转换为 `messages`
   - `instructions` 转换为系统消息
   - 输出项转换为助手消息

### 响应转换
- 流式和非流式响应支持
- 使用量统计转换
- 错误格式标准化
- 工具调用结果处理

## 推荐建议

### 开源方案（支持接口转换）

1. **Envoy AI Gateway** - 完全开源，功能完整 ✅
   - 支持三种格式转换
   - 包含监控、负载均衡、故障转移等完整功能
   - 适合需要生产级功能的场景

2. **Portkey 开源版本** - 核心开源，功能受限 ⚠️
   - 支持三种格式转换（核心功能）
   - 轻量级（122kb），低延迟（<1ms）
   - **缺少**：监控、密钥管理、安全合规等生产级功能
   - 适合只需要接口转换的轻量级场景

3. **AIGateway (arcboxlabs)** - 开源，专注 Responses API ⚠️
   - 主要支持 Responses API 转换
   - 功能相对单一

### 商业方案（功能完整）

1. **Portkey 企业版** - 最全面的三种格式支持
   - 包含完整的监控、密钥管理、安全合规功能
   - 适合企业级生产环境

2. **Cloudflare AI Gateway** - 统一端点，内置防护栏
   - 适合已经使用 Cloudflare 生态系统的用户

### 选择建议

| 场景 | 推荐方案 |
|------|----------|
| 只需要接口转换，轻量级 | Portkey 开源版本 |
| 需要完整功能的开源方案 | Envoy AI Gateway |
| 企业级生产环境 | Portkey 企业版或 Cloudflare AI Gateway |
| Kubernetes 环境 | Envoy AI Gateway |

## 注意事项

1. **功能完整性**: 不同网关对三种格式的支持程度可能不同
2. **性能影响**: 格式转换可能增加延迟
3. **提供商兼容性**: 某些转换可能不适用于所有提供商
4. **成本考虑**: 转换功能可能影响定价

## 结论

经过调研，发现除了 AxonHub 之外，确实有多个 AI 网关支持 responses、messages、completions 三个接口的相互转换。但需要注意：

### 关键发现

1. **Portkey 开源版本**：
   - ✅ 支持接口转换（核心功能）
   - ❌ 缺少监控、密钥管理、安全合规等生产级功能
   - 适合只需要接口转换的轻量级场景

2. **AISIX (API7 AI Gateway) 开源版本**：
   - ❌ **不支持接口转换功能**
   - 只支持 Chat Completions
   - 接口转换功能在商业版本中

3. **Envoy AI Gateway**：
   - ✅ 完全开源，功能完整
   - 支持三种格式转换
   - 包含监控、负载均衡、故障转移等完整功能

4. **商业方案**（Portkey 企业版、Cloudflare AI Gateway 等）：
   - ✅ 功能最全面
   - 包含完整的监控、安全、合规功能

### 选择建议

- **需要开源且功能完整**：选择 Envoy AI Gateway
- **只需要接口转换，轻量级**：选择 Portkey 开源版本
- **企业级生产环境**：选择 Portkey 企业版或 Cloudflare AI Gateway
- **避免**：AISIX 开源版本（不支持接口转换）

### 重要提醒

开源版本的功能通常有限，生产环境建议考虑商业方案以获得完整的监控、安全和合规功能。

---

**调研完成时间**: 2026-06-22  
**调研方法**: 全网搜索、官方文档分析、技术博客研究  
**数据来源**: 官方文档、GitHub 仓库、技术博客、API 文档