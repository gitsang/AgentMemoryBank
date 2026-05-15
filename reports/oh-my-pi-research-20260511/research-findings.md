# oh-my-pi Research Findings

**Date**: 2026-05-11
**Repo**: https://github.com/can1357/oh-my-pi
**Latest release**: v14.9.3 (2026-05-10)
**License**: MIT

---

## 1. What It Is

- AI coding agent for the terminal — an agentic harness that wraps LLMs with tool-calling, file editing, and automation.
- Fork of `badlogic/pi-mono` (by @mariozechner, now `earendil-works/pi`).
- Described as: "⌥ AI Coding agent for the terminal — hash-anchored edits, optimized tool harness, LSP, Python, browser, subagents, and more"

## 2. Architecture & Components

**Monorepo** (TypeScript 85% + Rust 11% + Python 2.5%), runs on **Bun** runtime.

| Package | Purpose |
|---|---|
| `@oh-my-pi/pi-ai` | Multi-provider LLM client with streaming |
| `@oh-my-pi/pi-agent-core` | Agent runtime with tool calling + state management |
| `@oh-my-pi/pi-coding-agent` | Main CLI application (`omp` command) |
| `@oh-my-pi/pi-tui` | Terminal UI library (differential rendering) |
| `@oh-my-pi/pi-natives` | N-API bindings (Rust crate `pi-natives`) for grep, shell, image, text, syntax highlighting |
| `@oh-my-pi/omp-stats` | Local observability dashboard ("omp stats") |
| `@oh-my-pi/pi-utils` | Shared utilities (logging, streams, dirs/env/process helpers) |
| `@oh-my-pi/swarm-extension` | Swarm orchestration extension |

## 3. Stated Goals

- Minimal, opinionated harness for terminal-native AI coding (inherited from pi-mono philosophy: "if I don't need it, it won't be built")
- Hash-anchored file edits to prevent silent corruption on concurrent/parallel edits
- Maximum model/provider flexibility (not locked to any single LLM)
- Full tool harness without leaving the terminal — LSP, Python kernel, browser, git, etc.

## 4. Notable Features

### Core Differentiators
1. **Hash-anchored edits (Hashline)**: File read returns content+SHA hash; edit requires matching hash. Mismatch = abort before corruption. Enables safe concurrent edits from parallel subagents.
2. **Multi-provider support**: 50+ providers (Anthropic, OpenAI, Google, Mistral, OpenRouter, Groq, Ollama, xAI, Azure, Bedrock, HuggingFace, Together, LiteLLM, etc. etc.)
3. **Role-based model routing**: Route different task types (planning vs execution) to different models — expensive reasoning models for planning, cheap fast models for edits. Users report 40% API cost savings.
4. **LSP integration**: Agent queries Language Server Protocol daemon for go-to-definition, diagnostics, symbol resolution.
5. **Persistent IPython kernel**: Survives across agent turns. Variables/imports/state persist. Built-in helpers: `lines()`, `insert_at()`, `delete_lines()`, `delete_matching()`. Optional shared gateway across sessions.
6. **Session branching**: Checkpoint session state, branch, experiment, roll back.
7. **Agentic git commits**: Git tools at hunk level (`git-overview`, `git-file-diff`, `git-hunk`); splits unrelated changes into atomic commits; enforces conventional commits; optionally updates CHANGELOG.md.
8. **Subagents**: Spawn child agents for parallel subtasks, results merged back.
9. **Browser automation**: Puppeteer-based browser tool.
10. **Automatic context compaction**: Unlike Claude Code's manual `/compact`.
11. **Universal config discovery**: Reads config from 8 AI tools: Claude Code, Cursor, Windsurf, Gemini, Codex, Cline, GitHub Copilot, VS Code.

### Built-in Tools (from README)
bash, read, write, edit, grep, glob, LSP (go-to-def, diagnostics, symbols), ast_grep/ast_edit, browser (puppeteer), web_search (multi-provider), fetch, commit (agentic), eval (code execution), image (generation), IRC (subagent coordination), bg/bg_write (async jobs), memory (autonomous memory), permissions (gate), and more.

### Extensibility
- Custom slash commands, themes, skills, hooks, custom tools
- Compatible with Claude Code directories (`~/.claude/commands/`)
- Extensions in TypeScript (self-modifying harness)

## 5. Install / Run Surface

```bash
# npm global
npm install -g @oh-my-pi/pi-coding-agent
omp

# bunx (no install)
bunx @oh-my-pi/pi-coding-agent

# Pre-built binary (macOS ARM64)
# Download from GitHub Releases
```

**Provisioning**: BYOK (bring your own API key) — multi-provider config via settings file.

## 6. Maturity Signals

| Signal | Value |
|---|---|
| Stars | ~4,207 |
| Forks | 388 |
| Contributors | 160+ |
| Releases | 361 (very rapid iteration) |
| Latest release | v14.9.3 (2026-05-10) — yesterday |
| First release | ~2025-12-31 (repo created) |
| Activity | Very active: daily releases, CI, changelog with breaking changes |
| Open issues | 124 |
| License | MIT |
| Community | Discord server linked in README |
| CI | GitHub Actions |
| Origin | Fork of pi-mono (badlogic/pi-mono → earendil-works/pi), which has broader maturity |

**Honest caveats** (from multiple sources):
- Newer project, smaller community than Aider/Claude Code
- Rapid releases mean breaking changes are common (CHANGELOG has "Breaking Changes" sections)
- Minimal permission model by default ("YOLO mode" — runs everything without asking)
- Documentation is extensive but less polished than Claude Code's official docs

## 7. Key Comparisons

### vs Claude Code
| Dimension | oh-my-pi | Claude Code |
|---|---|---|
| License | Open source (MIT) | Proprietary |
| Model support | 50+ providers | Anthropic only |
| Hash-anchored edits | Yes | No (line-based) |
| LSP integration | Built-in | No |
| IPython kernel | Built-in | No |
| Session branching | Built-in | No |
| Agentic commits | Split-aware | Basic |
| Context compaction | Automatic | Manual (`/compact`) |
| Permission model | YOLO (opt-in gate) | 5 sandbox modes |
| IDE integration | Terminal only | VS Code, JetBrains |
| Permission sandbox | Opt-in extension | Built-in |
| Provider support | Anthropic + 50+ | Anthropic only |
| Terminal Bench 2.0 | N/A | #40 · 58.0% |
| Subagents | Yes | Yes (beta) |
| SDK | Yes | No |

### vs OpenCode
| Dimension | oh-my-pi | OpenCode |
|---|---|---|
| License | MIT | Open source |
| Runtime | Bun | Node.js |
| Hash-anchored edits | Yes | No (line-based) |
| Multi-provider | 50+ providers | Multi-provider |
| IPython kernel | Built-in | No |
| LSP | Built-in | Via config |
| Context compaction | Automatic | Manual |

## 8. Source URLs

- **GitHub repo**: https://github.com/can1357/oh-my-pi
- **README**: https://github.com/can1357/oh-my-pi/blob/main/README.md
- **Changelog**: https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/CHANGELOG.md
- **AGENTS.md (dev docs)**: https://github.com/can1357/oh-my-pi/blob/main/AGENTS.md
- **npm package**: https://www.npmjs.com/package/@oh-my-pi/pi-coding-agent
- **Releases**: https://github.com/can1357/oh-my-pi/releases
- **Original (pi-mono)**: https://github.com/earendil-works/pi
- **Discord**: https://discord.gg/4NMW9cdXZa (from README badge)
- **Comparison page (disler/pi-vs-claude-code)**: https://github.com/disler/pi-vs-claude-code/blob/main/COMPARISON.md
- **Comparison article (bswen)**: https://docs.bswen.com/blog/2026-04-20-oh-my-pi-vs-claude-code/
- **xdadevelopers "ditched Claude Code/OpenCode for Pi"**: https://www.xda-developers.com/replaced-claude-code-and-opencode-with-pi/
- **Terminal Trove comparison**: https://terminaltrove.com/compare/ai-coding-agents/claude-code-vs-pi/
- **dudarik.com article**: https://dudarik.com/en/blog/oh-my-pi/

---

*Research compiled 2026-05-11 from GitHub API, README, changelog, npm registry, and published comparisons.*
