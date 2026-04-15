## Browser Automation

### Browser Tool Routing

Before using any browser tool, classify the task into one of these buckets and pick one primary tool first:

1. **Debugging / inspection** → `chrome-devtools`
2. **Deterministic automation / testing** → `Playwright`
3. **Lightweight browsing / quick web automation** → `agent-browser`
4. **Autonomous browsing / open-ended multi-step exploration** → `browser-use`

Prefer exactly one primary browser tool per task. Only switch tools when the current tool is clearly insufficient for the task.

Default preference in this repository:

- Prefer `chrome-devtools` for debugging, authenticated browsing, console/network inspection, performance analysis, and login-gated pages.
- Prefer `agent-browser` for search engines, news lookup, quick navigation, lightweight extraction, screenshots, downloads, and simple browser automation.
- Use `Playwright` only when the task is clearly test automation, deterministic replay, assertions, or cross-browser verification.
- Use `browser-use` only when the task is explicitly open-ended and agentic, such as autonomous multi-site research or workflows where the path is not known in advance.

Do not choose tools by vague preference like "best" or "most powerful". Route based on task type.

### chrome-devtools MCP

如果页面需要登录，请改用 chrome-devtools MCP 进行访问。

如果使用 chrome-devtools MCP 访问网页仍然需要登录，请立即停止等待用户完成登录。
在需要登录的情况下，禁止尝试使用其他的浏览器或工具进行访问（尤其禁止使用 playwright）。

Use `chrome-devtools` first when:

- The page requires login or should reuse an existing user session
- The task involves console errors, network requests, cookies, storage, or request inspection
- The task involves performance profiling, Lighthouse, or rendering/debugging issues
- The task is troubleshooting a real page rather than writing a reusable browser script

Avoid using `chrome-devtools` as the default tool for CI-style browser tests when debugging is not the main goal.

### Agent Browser

对于使用搜索引擎，新闻查找等可以使用 agent-browser

Use `agent-browser` for web automation. Run `agent-browser --help` for all commands.

Core workflow:

1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

Use `agent-browser` first when:

- The task is quick browser interaction in a CLI agent workflow
- The task is searching the web, reading pages, grabbing text, taking screenshots, or downloading files
- The task benefits from lower overhead and compact output rather than deep debugging

Avoid using `agent-browser` for login-gated tasks when `chrome-devtools` can attach to an authenticated session.

### Playwright

Use `Playwright` when:

- The task is end-to-end testing or deterministic browser automation
- The task needs assertions, repeatability, or CI-friendly workflows
- The task requires cross-browser verification

Avoid using `Playwright` for login-gated browsing in this repository unless the task is explicitly test-related and `chrome-devtools` is not the right fit.

### browser-use

Use `browser-use` only when:

- The task is explicitly open-ended, agentic, and multi-step
- The task requires autonomous exploration across pages or sites with an unclear path

Avoid using `browser-use` for simple click/fill/screenshot tasks or for work that can be completed deterministically with `agent-browser`, `chrome-devtools`, or `Playwright`.

### Tool Switching Guardrails

- Start with the routing rules above instead of trying multiple browser tools at once.
- Do not mix multiple browser tools in the same task unless the first tool clearly cannot satisfy the requirement.
- If you switch tools, explain why the previous tool was insufficient.
- For authenticated pages, stop after `chrome-devtools` if login is still required and wait for the user.

## Research

When Agent performs analysis and research tasks:

1. Create a new subdirectory in the `reports/` directory, using a descriptive task name or timestamp
2. Save all relevant outputs (reports, data, screenshots, etc.) to this subdirectory
3. Keep the report structure clear for easy future reference

## Memory

Read [MEMORY.md](./MEMORY.md)
