# `opencode-context-cache` 实现审查：是否适合 Bifrost 场景

目标：判断 `JackDrogon/opencode-context-cache` 是否适合你当前的 Bifrost 场景：

- OpenCode 作为客户端
- 上游是 Bifrost / OpenAI-compatible gateway
- 希望提升 prompt cache 命中
- 可能还想把同一会话稳定路由到同一 provider / deployment
- 同时保留加权分流、故障摘除、fallback

---

## 结论先看

**适合做“稳定会话键 + prompt cache key 对齐”的增强层，但不适合直接当成完整的 Bifrost sticky-session 方案。**

更具体地说：

- **适合**：当你的 Bifrost/上游网关会基于 `x-session-id` 或类似头做缓存键/会话归并/弱粘性路由时
- **不完全适合**：当你要的是严格的、可控的、按 OpenCode `sessionID` 保持语义一致的 sticky 路由
- **最大问题**：它默认发送的并不是原始 `OpenCode sessionID`，而是一个**派生出来的 SHA256 哈希键**，而且默认来源优先级里 `process.cwd()` 比 `sessionID` 更高

---

## 代码实际做了什么

源码文件：

- `plugins/opencode-context-cache.mjs`

核心逻辑分成三部分：

### 1. 先解析一个“稳定 cache/sticky key”

实现类：`CacheKeyResolver`

优先级是：

1. `OPENCODE_PROMPT_CACHE_KEY`
2. `OPENCODE_STICKY_SESSION_ID`
3. `user@host:<cwd>`
4. 现有 model headers (`x-session-id`, `conversation_id`, `session_id`)
5. OpenCode `sessionID`

这点非常关键：

**默认情况下，它更倾向于使用“用户+机器+工作目录”作为稳定身份，而不是 OpenCode 当前 sessionID。**

### 2. 对这个 key 做 SHA256

逻辑：

- 如果值已经像 64 位 hex sha256，就不再重复 hash
- 否则统一做 SHA256

结果：

- 上游看到的是哈希值，不是原始 sessionID

### 3. 同时写入 prompt cache key 和 session headers

实现类：`CacheKeyApplier`

它会：

- 设置 `output.options.promptCacheKey = <hashed>`
- 修改 `input.model.headers`：
  - `x-session-id = <hashed>`
  - `conversation_id = <hashed>`
  - `session_id = <hashed>`

也就是说：

**它把“缓存键”和“会话路由键”强绑定成同一个值。**

---

## 这对 Bifrost 场景意味着什么

## 适合的部分

### 1. 很适合解决“上游 session 标识不稳定导致 cache hit 差”

如果你的 Bifrost 或前置 relay 会：

- 看 `x-session-id`
- 看 `conversation_id`
- 或看 `promptCacheKey`

那么这个插件能把这些键稳定下来。

特别是它默认用 `user@host:<cwd>` 生成稳定身份，这意味着：

- 同一个项目目录反复发请求
- 即使 OpenCode 每次 sessionID 不同
- 上游仍然会看到同一个 hash key

这对 prompt cache 命中是非常有利的。

### 2. 对“缓存”和“弱粘性”是一致的

它把：

- `promptCacheKey`
- `x-session-id`
- `conversation_id`
- `session_id`

全部对齐到同一个值。

好处是：

- cache key 不会和 session routing key 打架
- 观测和缓存更容易关联

---

## 不适合的部分

### 1. 它默认不是“按 OpenCode sessionID 粘性”

你前面更关心的是：

- 一个 OpenCode 会话 / 子会话
- 稳定地落到某个 provider / deployment

但这个插件默认不是这样设计的。

它默认优先使用：

- `OPENCODE_PROMPT_CACHE_KEY`
- `OPENCODE_STICKY_SESSION_ID`
- `user@host:<cwd>`

只有前面都没有时，才退到 `input.sessionID`。

所以它更像：

**按“项目稳定身份”做统一 key**

而不是：

**按“当前 OpenCode 会话树”做 sticky affinity**

这两件事在你的场景里并不完全一样。

### 2. 它把 cache identity 和 routing identity 硬绑定了

在某些 Bifrost 场景里，你可能想分开：

- 缓存键：尽量稳定、尽量复用
- 路由键：按 session / user / thread 粘性

但这个插件把两者绑死：

- `promptCacheKey == x-session-id == conversation_id == session_id == hashedKey`

问题是：

- 你可能希望多个 session 共用缓存
- 但不希望它们被 sticky 到同一个 provider

这个插件做不到分离。

### 3. 它不知道 Bifrost 的 provider 健康状态 / 加权策略

它只是发 header 和 cache key，不参与：

- 50/50 分流
- provider cooldown
- circuit breaker
- fallback 到 provider3/provider4

所以它不能保证：

- sticky 不会破坏你的负载均衡目标
- sticky 和 fallback 会正确协同

这些必须由 Bifrost 网关侧自己定义规则。

### 4. 哈希后的 key 可能不符合某些网关的特定 affinity 语义

优点是隐私更好。

但风险是：

- 如果你希望上游按“原始 sessionID”排查问题，日志不直观
- 如果你的网关想区分 parent/child session，这个插件没有发送 `x-parent-session-id`
- 如果你希望兼容某些 provider 特定 header 语义，这里只是统一覆盖成 hash 值

---

## 对你当前 Bifrost 场景的判断

### 什么时候“可以直接用”

可以直接用，当且仅当你想要的是：

- **提高 prompt cache 命中率**
- 同时给 Bifrost 一个**稳定、匿名化的 session key**
- 并且你接受“以项目目录为默认稳定身份”

这种情况下它很合适，尤其适合：

- 长上下文重复请求
- 多次迭代同一代码仓库
- 上游网关支持按 `x-session-id` / `session_id` 做 cache 或弱粘性

### 什么时候“不建议直接用”

不建议直接用，如果你要的是：

- **严格按 OpenCode sessionID 粘性**
- 区分主会话和子 agent 会话
- 保留 `x-parent-session-id`
- 把 cache key 和 sticky routing key 分离
- 精细控制 sticky 只影响路由，不影响缓存

在这些情况下，这个插件的默认设计会偏离你的目标。

---

## 我对它的总体评价

### 优点

- 实现很小，逻辑清晰
- 没有 provider-specific 分支，迁移简单
- 对 relay/gateway 场景很友好
- 对缓存命中提升非常合理
- 用 `chat.params` 修改 `output.options.promptCacheKey` + model headers，路径实用

### 缺点

- 命名上叫 sticky session，但更准确说是 **stable cache/session identity plugin**
- 默认 identity 来源更偏“项目级稳定键”，而不是“会话级 sticky 键”
- 不支持 `x-parent-session-id`
- 把缓存键和路由键强耦合
- 没有针对 Bifrost 的 header 协议做专门适配

---

## 最终建议

### 建议 1：如果你主要追求 cache hit

**可以直接试这个插件。**

因为它最擅长的就是这个。

### 建议 2：如果你主要追求 Bifrost 粘性路由

**不建议原样直接上。**

更好的做法是基于它改一个 Bifrost 版：

- `promptCacheKey` 继续保留稳定 hash 逻辑
- sticky routing header 单独发：
  - `x-session-id = input.sessionID` 或你指定的稳定键
  - `x-parent-session-id = parent session`（若可得）
  - 或 `x-session-affinity = <stable-affinity-key>`

也就是把：

- **缓存身份**
- **路由粘性身份**

拆成两个概念。

### 建议 3：你当前最合理的落地方式

如果是 Bifrost，我建议做一个很小的定制版插件：

1. 继续借用它的 key precedence / hash 思路
2. 但不要把所有 header 都写成同一个 hashed 值
3. 至少拆成：
   - `promptCacheKey`：稳定 hash
   - `x-session-id`：OpenCode sessionID 或自定义 affinity key
   - `x-parent-session-id`：若可得则传

---

## 审查结论（一句话）

`opencode-context-cache` **适合拿来做 Bifrost 场景的基础模板，但不适合直接当最终版 sticky-session 方案**；它更偏“稳定缓存身份插件”，而不是“严格会话粘性路由插件”。
