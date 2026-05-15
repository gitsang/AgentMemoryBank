# oh-my-pi 项目介绍与 Claude Code / OpenCode 对比

**Research Date**: 2026-05-11  
**Object**: https://github.com/can1357/oh-my-pi  
**Question**: 介绍 oh-my-pi，并说明它相比 Claude Code 和 OpenCode 的优势、适用场景和劣势。

---

## Executive Summary

`oh-my-pi` 是一个面向终端的开源 AI coding agent，命令名是 `omp`，核心包是 `@oh-my-pi/pi-coding-agent`。它 fork 自 `badlogic/pi-mono`，但已经扩展成一个“重工具链、重兼容、重可定制”的工程代理平台：TypeScript/Bun 运行时，Rust N-API 提供 grep、shell、glob、文本处理、语法高亮等高性能原生能力；内置 LSP、Python/IPython、浏览器自动化、SSH、MCP、hooks、skills、自定义工具、自定义 slash command、session branching、memory、subagents 和本地统计。

相对 Claude Code，Pi 的核心优势不是“模型更强”，而是“工具和运行时更开放”：多模型/多订阅接入、读取其他工具配置、更多本地原生工具、Python kernel、Puppeteer browser、隔离 subagent、TypeScript 扩展点。相对 OpenCode，Pi 更像一个激进的 batteries-included agent lab；OpenCode 更简洁、产品化和权限模型更清晰。

建议把 Pi 用在：你同时使用多种 AI coding 工具、想复用 Claude/Codex/Gemini/OpenCode/Cursor 等配置；需要多 provider 降本或用本地模型；需要 Python/浏览器/SSH/LSP/subagent 隔离等高级工具；愿意接受较快迭代带来的复杂度。若你要的是稳定主力、企业权限治理、Claude 官方能力或低心智负担，优先 Claude Code 或 OpenCode。

---

## 1. 项目概况

- GitHub repo: `can1357/oh-my-pi`
- 描述: “AI Coding agent for the terminal — hash-anchored edits, optimized tool harness, LSP, Python, browser, subagents, and more”
- License: MIT
- 技术栈: TypeScript 为主，Rust 原生扩展，少量 Python/JS/CSS/HTML
- 包管理/运行时: Bun，`package.json` 要求 Bun `>=1.3.7`
- npm 包: `@oh-my-pi/pi-coding-agent`，命令入口 `omp`
- 最新核验版本: npm latest `14.9.3`，GitHub latest release `v14.9.3`
- GitHub API 核验时约 4.2k stars、388 forks、160 contributors、124 open issues

Monorepo 主要包：

| Package | 作用 |
|---|---|
| `@oh-my-pi/pi-ai` | 多 provider LLM client |
| `@oh-my-pi/pi-agent-core` | agent runtime、tool calling、state management |
| `@oh-my-pi/pi-coding-agent` | 主 CLI / TUI / SDK |
| `@oh-my-pi/pi-tui` | 终端 UI library |
| `@oh-my-pi/pi-natives` | Rust N-API 原生能力 |
| `@oh-my-pi/omp-stats` | 本地 AI 用量统计 dashboard |
| `@oh-my-pi/pi-utils` | 共享工具库 |
| `@oh-my-pi/swarm-extension` | swarm / 多 agent 编排扩展 |

---

## 2. 主要能力

### 2.1 终端 coding agent + TUI

Pi 与 Claude Code、OpenCode 一样，核心交互面是终端里的 agent。README 中列出大量 in-chat slash commands，例如 `/plan`、`/model`、`/extensions`、`/session`、`/tree`、`/branch`、`/fork`、`/compact`、`/handoff`、`/browser`、`/mcp`、`/memory`、`/background`、`/login` 等。

### 2.2 LSP 集成

Pi README 明确列出 11 类 LSP 操作：diagnostics、definition、type_definition、implementation、references、hover、symbols、rename、code_actions、status、reload。还支持 format-on-write、edit/write 后 diagnostics、workspace diagnostics、40+ language configs、项目本地 LSP server 发现。

### 2.3 Python / IPython kernel

Pi 的 `eval` Python backend 不是简单 `python -c`，而是通过 Jupyter Kernel Gateway 运行 Python cells；支持 persistent kernel、streaming stdout/stderr、rich output、Markdown/images/JSON tree、shared gateway、`.omp/modules/` 自定义模块。

### 2.4 Browser automation

Pi 内置 Puppeteer browser tool，并宣称有 14 个 stealth scripts；支持 navigate、click、type、fill、scroll、drag、screenshot、evaluate JS、extract readable content、accessibility snapshots、CSS/ARIA/text/xpath/pierce selectors、headless/visible 切换。

### 2.5 Subagent / task 系统

README 列出 6 个 bundled agents：explore、plan、designer、reviewer、task、quick_task。支持并行探索、实时 artifact streaming、`agent://<id>` 读取完整输出、background jobs、最高 100 并发、`/agents` dashboard、自定义 agents、per-agent model overrides。隔离后端包括 git worktrees、Unix fuse-overlay filesystems、Windows ProjFS，合并策略支持 patch 或 branch。

### 2.6 Universal Config Discovery

这是 Pi 最突出的定位之一：它能发现多种 AI coding 工具的配置和能力。README 称支持 Claude Code、Cursor、Windsurf、Gemini、Codex、Cline、GitHub Copilot、VS Code，发现 MCP servers、rules、skills、hooks、tools、slash commands、prompts、context files，并保留 provider attribution，可通过 `/extensions` 查看和禁用。

源码中也能看到多个 provider discovery module，例如 `claude`、`claude-plugins`、`codex`、`cursor`、`gemini`、`opencode`、`github`、`vscode`、`windsurf`、`agents-md` 等。

### 2.7 扩展点

Pi 支持：

- Skills: `.omp/skills/*/SKILL.md`，也读取 `.claude/skills`、`.codex/skills`、OpenCode skills 等；docs 显示 provider priority 中 native `.omp` 最高，其次 Claude，再到 Claude plugins / agents / Codex，OpenCode 为较低优先级。
- Hooks: TypeScript modules，位于 `~/.omp/agent/hooks` 或 `.omp/hooks`，可订阅 lifecycle events，能弹 UI confirm、block tool call、inject message。
- Custom tools: `.omp/tools/*/index.ts` 或 `~/.omp/agent/tools/*/index.ts`。
- Custom slash commands: `.omp/commands/*/index.ts` 或兼容 Claude Code command 目录。
- MCP: 可管理 MCP servers。

---

## 3. 相比 Claude Code 的优势

1. **更开放的模型和 provider 路线**  
   Claude Code 最强绑定 Anthropic/Claude 生态，虽然也有 MCP、SDK、hooks、subagents、plugins，但模型主线仍是 Claude。Pi 的 README 列出 Anthropic、ChatGPT Plus/Pro、GitHub Copilot、Google Cloud Code Assist、Cursor、Kimi、Perplexity、Ollama、LM Studio、vLLM、LiteLLM、Cloudflare/Vercel AI Gateway 等多种接入。这对降本、国内网络、私有模型、本地模型更友好。

2. **跨工具配置聚合**  
   Pi 可以把 Claude Code、Codex、Gemini、OpenCode、Cursor、Windsurf、Cline、Copilot 等工具的 instructions、skills、hooks、MCP、commands 统一发现。这适合“配置资产很多，想一个 agent 全部继承”的用户。Claude Code 主要围绕 `.claude`/CLAUDE.md/Claude plugins 生态。

3. **内置工具更激进**  
   Python kernel、Puppeteer stealth browser、SSH persistent connections、native grep/shell/text/glob、高级 LSP、hash-anchored edits，这些组合使 Pi 更像本地 agent 操作系统。Claude Code 的工具体系更稳、更官方，但默认工具面相对收敛。

4. **subagent 隔离方式更工程化**  
   Pi 明确支持 isolated task 跑在 worktree、fuse-overlay、ProjFS，并用 patch/branch merge 回收变更。Claude Code 也有 subagents、background、agent teams，但“文件系统隔离 + merge strategy”不是它最核心的公开产品卖点。

5. **可 hack 性更高**  
   Pi 是完整开源 monorepo，TypeScript/Rust 代码可改；hooks/custom tools/custom commands 都是 TypeScript。Claude Code repo 公开，但主要是官方产品分发，不是同等意义上的“你 fork 后深改 agent runtime”。

---

## 4. 相比 OpenCode 的优势

1. **配置兼容面更宽**  
   OpenCode 本身也支持 agents、commands、plugins、skills、tools、themes、MCP、AGENTS.md，并能读部分 Claude Code 资源；但 Pi 的目标更像“统一发现所有 AI coding 工具配置”，README 明确列出 8 类工具生态。

2. **工具箱更满**  
   OpenCode 的优势是简洁、TUI/desktop/IDE extension、权限和 agent 配置清晰。Pi 则把 Python kernel、browser stealth、SSH、hashline edit、LSP、native engine、stats、memory、subagent isolation 这类能力打包进一个平台，适合复杂自动化。

3. **多 provider / 订阅复用更激进**  
   Pi 明确支持 Claude Pro/Max、ChatGPT Plus/Pro、Copilot、Cursor、Gemini CLI、Antigravity、Kimi、Perplexity、本地推理、各类 gateway。OpenCode 也可配置多 provider，但 Pi 在 README 中把“订阅/OAuth/provider 复用”放得更中心。

4. **研究型/实验型能力更多**  
   TTSR（Time Traveling Streamed Rules）、autonomous memory、review tool with structured findings、swarm extension、persistent Python gateway、stealth browser，都是偏实验和高级 agent workflow 的特性。

---

## 5. 什么情况下建议使用 Pi

建议使用 Pi，如果你符合以下任一情况：

1. **你是多工具用户**：同时用 Claude Code、OpenCode、Codex、Gemini、Cursor、Windsurf、Copilot，希望复用已有配置、skills、rules、MCP、commands。
2. **你想降低模型成本或绕开单 provider 依赖**：希望把主模型、plan 模型、smol/explore 模型分开，用 Copilot/ChatGPT/Cursor/Claude/本地模型/API gateway 混搭。
3. **你需要复杂本地工具链**：任务经常涉及 Python 数据分析、网页自动化、SSH 到远端、LSP rename/diagnostics、代码库大规模检索。
4. **你要并行 agent 工作流**：希望 subagents 在 worktree/overlay 里隔离探索或修改，再合并 patch/branch。
5. **你愿意调试和定制 agent 本身**：愿意读源码、写 TypeScript hooks/tools/commands，接受快速迭代和破边界实验。
6. **你做 agent/tooling 研究**：Pi 是一个很好的“AI coding agent 工程实验场”，比闭源或强产品化工具更容易观察和改造。

---

## 6. Pi 的劣势和风险

1. **复杂度高，心智负担大**  
   Pi 几乎把所有高级能力都塞进来：多 provider、universal discovery、hooks、skills、tools、browser、Python、SSH、LSP、memory、task isolation。能力强，但出问题时排查面很大。

2. **成熟度不如 Claude Code 官方主线**  
   Claude Code 是 Anthropic 官方产品，文档、企业治理、权限、托管策略、模型适配、支持路径更明确。Pi 虽然更新快、contributors 多，但 open issues 也不少，且功能扩张很快。

3. **权限/安全模型不如 OpenCode 清晰简洁**  
   OpenCode 文档中的 permission 模型非常直接：allow/ask/deny，可按 bash/edit/read/grep/task/skill/lsp/webfetch 等细粒度配置。Pi 有 hooks 可以 block，也有权限/审批相关逻辑，但整体因为扩展点和外部配置自动发现更多，安全审计复杂度更高。

4. **Bun + Rust N-API + Puppeteer + Jupyter Gateway 依赖链更重**  
   OpenCode 是 Go 单二进制路线；Claude Code 官方安装路径也更标准。Pi 虽有预构建 binary 和 installer，但若使用完整能力，环境依赖明显更重。

5. **兼容发现可能带来“上下文污染”**  
   Universal config discovery 很强，但也可能把多个工具的 rules、skills、hooks、commands 一起加载，导致上下文过量、行为冲突、优先级难理解。README 也建议用 `/extensions` 检查 provider assets。

6. **不一定适合作为团队默认工具**  
   如果团队目标是低维护、权限边界明确、统一文档和稳定 onboarding，OpenCode 或 Claude Code 更稳。Pi 更适合高级用户、平台工程师、agent 爱好者先试点。

---

## 7. 简明选择建议

| 场景 | 推荐 |
|---|---|
| 只想要最强 Claude 官方 coding 体验 | Claude Code |
| 企业/团队要稳定、权限清晰、配置可控、UI 简洁 | OpenCode |
| 多模型、多订阅、本地模型、gateway 混用 | Pi |
| 想复用 Claude/Codex/Gemini/OpenCode/Cursor 等配置 | Pi |
| 需要 Python kernel、browser automation、SSH、LSP、isolated subagents | Pi |
| 不想折腾依赖和配置 | Claude Code 或 OpenCode |
| 想研究/改造 AI coding agent runtime | Pi |

---

## Sources Checked

- GitHub repo: https://github.com/can1357/oh-my-pi
- GitHub API: https://api.github.com/repos/can1357/oh-my-pi
- Latest release API: https://api.github.com/repos/can1357/oh-my-pi/releases/latest
- npm latest metadata: https://registry.npmjs.org/@oh-my-pi%2Fpi-coding-agent/latest
- Local clone inspected at `/tmp/opencode/oh-my-pi`
- Key local files inspected:
  - `README.md`
  - `AGENTS.md`
  - `package.json`
  - `packages/coding-agent/DEVELOPMENT.md`
  - `docs/skills.md`
  - `docs/python-repl.md`
  - `docs/tools/edit.md`
  - `packages/coding-agent/src/discovery/*`
  - `packages/coding-agent/src/task/worktree.ts`
  - `packages/coding-agent/src/hashline/*`
  - `packages/coding-agent/src/tools/browser/*`
- Claude Code docs/API checked:
  - https://docs.claude.com/en/docs/claude-code/cli-usage
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/hooks-guide
  - https://docs.anthropic.com/en/docs/claude-code/permissions
  - https://code.claude.com/docs/en/features-overview
  - https://api.github.com/repos/anthropics/claude-code
  - https://api.github.com/repos/anthropics/claude-code/releases/latest
- OpenCode docs/API checked:
  - https://opencode.ai/docs/
  - https://opencode.ai/docs/tui/
  - https://opencode.ai/docs/permissions/
  - https://opencode.ai/docs/agents/
  - https://opencode.ai/docs/cli
  - https://opencode.ai/docs/config/
  - https://api.github.com/repos/anomalyco/opencode
  - https://api.github.com/repos/anomalyco/opencode/releases/latest
