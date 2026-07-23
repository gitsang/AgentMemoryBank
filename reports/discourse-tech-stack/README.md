# Discourse 技术栈调研报告

> 仓库: https://github.com/discourse/discourse
> 调研版本: main 分支(浅克隆于 2025-07-23,对应 2026.7 开发周期)
> 调研方式: 克隆仓库源码,分析 `Gemfile`、`package.json`、`pnpm-workspace.yaml`、`config/`、`frontend/`、`plugins/` 等

## 一句话概览

Discourse 是一个基于 **Ruby on Rails 8** 的现代社区论坛平台,**后端 Rails + PostgreSQL + Redis/Sidekiq**,**前端是 Ember.js 6 单页应用(SPA)**,用 **Rolldown(Rust 打包器)** 构建,通过 **MessageBus** 实现实时通信,拥有 44 个内置插件的高度可扩展体系。比 NodeBB 现代、复杂得多。

---

## 1. 运行时与语言

| 项目 | 技术 |
|------|------|
| 后端语言 | **Ruby 3.4+**(`ruby "~> 3.4"`) |
| 前端语言 | **JavaScript + TypeScript**(Ember 用 Glint 做模板类型检查) |
| Web 框架 | **Ruby on Rails 8.0**(actionmailer/actionpack/activerecord/railties 均 `~> 8.0.0`) |
| 前端框架 | **Ember.js 6.10**(`ember-source ~6.10.0`)—— 真正的 SPA |
| 入口 | `config.ru`(Rack)→ Discourse::Application |

> 与 NodeBB 的关键差异:Discourse 前端是 **Ember SPA**(客户端路由 + 渲染),Rails 只提供 JSON API;NodeBB 则是 Express SSR + jQuery 增强。

---

## 2. 后端架构(Rails)

标准 Rails 全栈结构,`app/` 下:

| 目录 | 数量 | 说明 |
|------|------|------|
| `models/` | ~297 | ActiveRecord 模型 |
| `controllers/` | ~90 | 控制器(JSON API 为主) |
| `serializers/` | ~228 | `active_model_serializers` 0.8 序列化 JSON |
| `jobs/` | — | Sidekiq 异步任务(regular/onceoff/scheduled) |
| `services/` | — | 业务逻辑服务对象 |
| `views/` | — | 少量服务端渲染(邮件等) |

### 关键后端库

- **pg + mini_sql** —— PostgreSQL 高性能查询(`mini_sql` 是轻量 SQL 映射,比 ActiveRecord 快)
- **redis + redis-namespace** —— 缓存/队列
- **Sidekiq >= 7.3 + mini_scheduler** —— 后台任务调度
- **message_bus** —— 实时 Pub/Sub(自研,见下文)
- **rails_multisite** —— 多站点支持(一个代码库跑多个论坛)
- **bootsnap** —— Rails 启动加速
- **propshaft** —— 现代资源管道(Rails 7+ 默认,替代 Sprockets)
- **goldiloader** —— 自动消除 N+1 查询
- **oj** —— 高性能 JSON 序列化
- **nokogiri / loofah / sanitize** —— HTML 解析与净化
- **liquid / mustache** —— 模板(主题/邮件)
- **sassc-embedded** —— Sass 编译(dart-sass)
- **logster + lograge** —— 日志管理 UI + 结构化日志
- **rack-mini-profiler** —— 性能分析
- **faraday + faraday-retry** —— HTTP 客户端
- **web-push** —— Web Push 推送通知
- **aws-sdk-*** —— S3 存储 / SNS / MediaConvert / **Bedrock(AI)**
- **maxminddb** —— GeoIP
- **image_optim + fastimage** —— 图片优化

### 认证
- **OmniAuth** —— 多策略:`facebook` / `twitter` / `github` / `google-oauth2` / `oauth2` / `openid-connect`
- **rotp + rqrcode** —— TOTP 双因素
- **cbor + cose + sshkey** —— WebAuthn / 安全密钥支持

---

## 3. 数据库

- **PostgreSQL 15+**(唯一支持的主数据库,见 `config/database.yml`:`adapter: postgresql`)
- Redis 7+(缓存 + Sidekiq 队列 + MessageBus)
- **不支持 MongoDB / MySQL**(MySQL 仅用于从其他论坛**导入**数据,`IMPORT=1` 时启用 `mysql2`)
- 数据库迁移:ActiveRecord migrations + 自研 `discourse-seed-fu` 种子数据
- 有完整的 **migrations/** 子项目(从 phpBB/vBulletin/XenForo 等导入)

---

## 4. 实时通信 —— MessageBus

与 NodeBB 用 Socket.IO 不同,Discourse 用自研的 **MessageBus**:

- 基于 **HTTP 长轮询(long-polling)** 的 Pub/Sub 库(`message_bus` gem + `message-bus-client` npm)
- 通过 Redis 在多实例间共享状态
- 用于:实时新帖推送、通知、在线状态、聊天(chat 插件)、存在感(discourse-presence)
- 优势:无需 WebSocket 特殊配置,穿透反向代理/CDN 更简单

---

## 5. 前端架构(Ember.js SPA)

这是 Discourse 与 NodeBB 最大的架构差异——**完整的客户端 SPA**。

### 框架与构建
- **Ember.js 6.10** —— 组件用 `.gjs` / `.gts`(Glimmer 组件 + TypeScript)
- **Rolldown** —— 基于 **Rust** 的新一代打包器(`rolldown.config.mjs`,很前沿,替代传统 ember-cli/webpack)
- **Embroider** —— Ember 现代构建工具链(`@embroider/compat`)
- **Glint**(`@glint/ember-tsc`)—— Ember 模板的 TypeScript 类型检查
- **pnpm workspace** —— monorepo(前端拆分为 discourse / discourse-i18n / pretty-text / discourse-markdown-it 等子包)

### 前端关键库
| 库 | 用途 |
|----|------|
| **ProseMirror** | 富文本/Markdown 编辑器(发帖 composer) |
| **CodeMirror 6** | 代码编辑 |
| **highlight.js** | 代码高亮 |
| **Chart.js** | 图表/统计 |
| **FullCalendar** | 日历(配合 discourse-calendar 插件) |
| **PhotoSwipe** | 图片灯箱浏览 |
| **Ace editor** | 代码编辑(管理后台) |
| **moment + moment-timezone** | 时间处理 |
| **@discourse/resize** 等 | 客户端图片格式转换(heic/jpeg/webp/jxl/gif/png) |
| **rete** | 可视化流程图(discourse-workflows) |
| **immer** | 不可变状态 |
| **morphlex** | DOM morphing(局部更新) |

### 样式
- **SCSS**(Sass)+ **BEM** 命名规范(见 AI-AGENTS.md)
- **stylelint** + **postcss**
- 主题系统可热切换

---

## 6. 插件与主题体系

Discourse 的核心可扩展性来源,**44 个内置插件**作为 pnpm workspace 成员:

- 每个插件是完整的 **Rails Engine + Ember 前端**(含 `plugin.rb`、`app/`、`db/`、`spec/`、`package.json`、`tsconfig.json`)
- 可独立类型检查(tsconfig references)
- 代表性插件:
  - **discourse-ai** —— AI 能力(配合 `aws-sdk-bedrockruntime` + `tokenizers` + `tiktoken_ruby`)
  - **chat** —— 实时聊天
  - **discourse-data-explorer** —— SQL 查询分析工具
  - **discourse-gamification** —— 游戏化
  - **discourse-subscriptions** —— 订阅(Stripe)
  - **discourse-solved** —— 标记已解决
  - **discourse-reactions** —— 反应表情
  - **discourse-calendar / discourse-presence** —— 日历/在线状态
- 主题:`themes/horizon`(新默认主题)

---

## 7. 测试

### 后端(Ruby)
- **RSpec + rspec-rails** —— 主测试框架
- **Fabrication** —— 测试工厂
- **shoulda-matchers / rspec-html-matchers** —— 匹配器
- **Capybara + Playwright**(`capybara-playwright-driver`)—— 系统测试(浏览器)
- **parallel_tests** —— 并行测试加速
- **test-prof** —— 测试性能分析
- **webmock** —— HTTP 桩
- **rswag-specs** —— OpenAPI/Swagger 文档测试
- **simplecov** —— 覆盖率
- `.rspec_parallel` 配置并行

### 前端(JavaScript)
- **QUnit** —— Ember 测试框架(`bin/qunit`)
- **@ember/test-helpers + @ember/test-waiters**
- **ember-exam** —— 并行测试
- Playwright(端到端)

### 冒烟测试
- `test/smoke-test.mjs`

---

## 8. 工程化与代码质量

- **RuboCop**(`rubocop-discourse`)+ **Syntax Tree** —— Ruby 代码风格/格式化
- **ESLint 10 + Prettier + stylelint** —— 前端 lint
- **TypeScript 5.9 + Glint** —— 前端类型安全
- **lefthook**(`lefthook.yml`)—— Git hooks(替代 Husky)
- **lint-to-the-future** —— 渐进式 lint 改进追踪
- **licensee** —— 许可证合规检查
- **annotaterb** —— 模型注解
- **Dependabot** —— 依赖更新(bundler + pnpm)
- **ruby-lsp + ruby-lsp-rails + ruby-lsp-rspec** —— LSP 语言服务

---

## 9. DevOps / 部署

| 项目 | 技术 |
|------|------|
| Web 服务器 | **Pitchfork**(Rack 服务器,Rack < 3,替代了 Unicorn)|
| 容器化 | Docker —— `.devcontainer/`(VS Code 推荐)+ `bin/docker/` 开发脚本 |
| CI/CD | **GitHub Actions**(18 个 workflow:tests / linting / release / migration-tests / licenses 等)|
| 反向代理 | 官方推荐 nginx(`config/nginx.sample.conf`)|
| 多版本管理 | `versions.json` —— 月度发布 + ESR 长期支持版 |
| 日志轮转 | logrotate(`config/logrotate.conf`)|

> 官方最低要求:Ruby 3.4+ / PostgreSQL 15 / Redis 7

---

## 技术栈速查表

| 层 | 技术 |
|----|------|
| 后端语言 | Ruby 3.4 |
| 后端框架 | Rails 8.0 |
| 数据库 | PostgreSQL 15+(独占) |
| 缓存/队列 | Redis 7 + Sidekiq |
| 实时通信 | MessageBus(HTTP 长轮询,自研)|
| 前端框架 | Ember.js 6.10(SPA)+ Glimmer 组件 |
| 前端语言 | JavaScript + TypeScript(Glint 类型检查)|
| 前端打包 | Rolldown(Rust)+ Embroider |
| 包管理 | pnpm 10 workspace(monorepo)/ bundler(Ruby)|
| 富文本编辑 | ProseMirror + CodeMirror |
| 认证 | OmniAuth(多 OAuth)+ WebAuthn + TOTP |
| API 序列化 | active_model_serializers 0.8 |
| 多站点 | rails_multisite |
| 存储 | AWS S3(可选)|
| AI | discourse-ai 插件 + Bedrock + tokenizers |
| 后端测试 | RSpec + Capybara/Playwright + Fabrication |
| 前端测试 | QUnit + ember-exam |
| Lint | RuboCop + ESLint + stylelint + Glint |
| Git hooks | lefthook |
| Web 服务器 | Pitchfork |
| 容器 | Docker(devcontainer)|
| CI | GitHub Actions |
| 许可证 | GPL-2.0 |

---

## Discourse vs NodeBB 对比

| 维度 | Discourse | NodeBB |
|------|-----------|--------|
| 后端语言 | Ruby(Rails 8)| JavaScript(Express 4)|
| 数据库 | PostgreSQL 独占 | Redis / MongoDB / PG 三选一 |
| 前端架构 | **Ember.js SPA**(客户端渲染)| jQuery + SSR(服务端渲染)|
| 实时通信 | MessageBus(HTTP 长轮询)| Socket.IO(WebSocket)|
| 前端打包 | Rolldown(Rust,极新)| Webpack 5 |
| 类型系统 | TypeScript + Glint(前端)| 无(纯 JS)|
| 模板 | Ember Glimmer(.gjs)| BenchpressJS(.tpl,自研 SSR)|
| 后台任务 | Sidekiq(Redis)| cron + workerpool |
| 插件 | Rails Engine(44 个内置)| npm 包形式 |
| 复杂度 | 高(~297 模型,~228 序列化器)| 中等 |
| 部署 | Docker / Pitchfork | Docker / node cluster |
| AI 能力 | 内置 discourse-ai 插件 | 无 |
| 联邦协议 | 无(原生)| ActivityPub(内置)|

---

## 结论

Discourse 是一个**架构成熟、工程化极高、技术选型偏前沿**的大型开源社区平台:

1. **后端**走 Rails 8 + PostgreSQL 经典稳健路线,但用了大量高性能优化(`mini_sql`、`oj`、`goldiloader`、`bootsnap`),并用 Sidekiq + Redis 处理异步。
2. **前端**是真正的 **Ember.js SPA**,且采用了非常前沿的 **Rolldown(Rust 打包器)** 和 **Glint 模板类型检查**,工程化程度远超 NodeBB。
3. **实时通信**用自研的 MessageBus(HTTP 长轮询)而非 WebSocket,换取部署简单性(穿透 CDN/代理),这是其十年架构演进的特色选择。
4. **插件体系**极其完善——每个插件是完整的 Rails Engine + Ember 前端 + 独立测试 + 类型检查,44 个内置插件覆盖 AI、聊天、订阅、游戏化等。
5. **AI 原生支持**是一大亮点(discourse-ai 插件 + Bedrock 集成 + tokenizer),顺应了当前趋势。

总体而言,Discourse 是**比 NodeBB 重得多、现代化程度高得多**的项目,适合需要**功能完备、可大规模部署、长期维护**的严肃社区场景;代价是部署和二次开发的门槛更高(Ruby + Ember + PostgreSQL 缺一不可)。NodeBB 则更轻、更灵活、技术栈更单一(全 JS)。
