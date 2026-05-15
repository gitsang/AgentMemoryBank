# OpenCode 粘性会话插件搜索笔记

## 已确认事实

- OpenCode SDK 支持 `config.headers`，可以给请求附加自定义请求头。
- OpenCode 插件 API 支持 `chat.headers` 钩子，且输入里包含 `sessionID`。
- 这意味着技术上完全可以实现“按 OpenCode sessionID 注入自定义 header，再让上游网关做 sticky routing”。

## 最终结论

有，已经找到一个明确命中的开源插件：

- `JackDrogon/opencode-context-cache`
- GitHub: `https://github.com/JackDrogon/opencode-context-cache`

它的 README 明确写着：

- `Enhanced prompt cache and sticky session management plugin for OpenCode.`
- 会同时写入：
  - `output.options.promptCacheKey`
  - model session headers: `x-session-id`, `conversation_id`, `session_id`

README 还明确说明其工作方式：

1. 计算稳定的 cache/sticky key
2. 设置 `output.options.promptCacheKey = <hashed>`
3. 把相同的值写入请求头：
   - `x-session-id`
   - `conversation_id`
   - `session_id`

这已经不是“能不能做”的层面，而是一个现成的、专门为 OpenCode + relay/gateway 场景写的插件。

## 额外确认到的事实

- OpenCode 官方插件文档示例里明确展示了通过插件扩展行为，并且配置示例里出现了社区插件名 `opencode-helicone-session`，说明 npm/plugin 生态是存在的。
- OpenCode 社区/核心也在推进原生 session header：
  - issue `#12930` 提议发送 `X-Session-ID` / `X-Parent-Session-ID`
  - PR `#12932` 说明过这套 header 方案
  - 该 PR 页面后续还提到更晚的实现方向，如 `x-session-affinity`

## 结论修正

- 不是“没人做过”
- 而是“现成插件不多，但已经至少有一个非常贴题的实现”
- 当前最贴近你需求、证据最明确的现成开源插件，就是 `opencode-context-cache`
