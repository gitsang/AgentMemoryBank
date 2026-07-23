# NodeBB 技术栈调研报告

> 仓库: https://github.com/NodeBB/NodeBB
> 调研版本: v4.14.1 (master 分支, 浅克隆于 2025-07-23)
> 调研方式: 克隆仓库源码, 分析 `install/package.json`、`src/`、构建配置、Dockerfile 等

## 一句话概览

NodeBB 是一个基于 **Node.js** 的现代论坛/BBS 软件,采用 **Express** 作为 Web 框架,服务端模板引擎为自研的 **Benchpress**,前端基于 **Bootstrap 5 + jQuery**,通过 **Socket.IO** 实现实时通信,支持 **Redis / MongoDB / PostgreSQL** 三种数据库,内置 **ActivityPub**(联邦宇宙)协议支持。

---

## 1. 运行时与语言

| 项目 | 技术 |
|------|------|
| 运行时 | Node.js **>= 22** (`engines.node`) |
| 语言 | JavaScript (CommonJS 为主, 配置文件用 ESM) |
| 入口 | `app.js` → `loader.js`(多进程 loader) → `src/start.js` |
| 进程模型 | 自带 `loader.js` 实现 cluster 多进程 + 守护进程化 (`daemon`) |

> 注意:NodeBB 采用 CLI 驱动的 setup,不通过标准 `npm start` 运行,而是 `./nodebb setup` / `./nodebb start`。

---

## 2. Web 框架与中间件

核心 Web 服务器为 **Express 4.x** (`src/webserver.js` 中 `const app = express()`),围绕它组装了一整套中间件生态:

- **express-session** — 会话管理
- **connect-mongo / connect-pg-simple / connect-redis** — 三种可切换的 session store
- **cookie-parser / body-parser** — 请求解析
- **connect-flash** — 闪存消息
- **express-useragent** — UA 解析
- **helmet** — 安全 HTTP 头
- **compression** — gzip 压缩
- **morgan** — HTTP 访问日志
- **serve-favicon** — favicon
- **multer** — 文件上传
- **csrf-sync** — CSRF 防护
- **@nodebb/spider-detector** — 爬虫识别(自研包)

---

## 3. 数据库层

NodeBB 通过 `src/database/` 下的抽象层支持三种数据库,可任选其一:

| 数据库 | 驱动 | 版本要求 |
|--------|------|----------|
| **Redis** | `redis` 5.x | >= 7.2(集群模式必需) |
| **MongoDB** | `mongodb` 7.x | >= 5 |
| **PostgreSQL** | `pg` 8.x + `pg-cursor` | — |

- `src/database/{mongo,postgres,redis}/` 各自实现底层适配
- 使用 **@socket.io/redis-adapter** 在多实例间同步 Socket.IO 事件(横向扩展)
- 缓存层使用 `@isaacs/ttlcache` + `lru-cache`

---

## 4. 实时通信

- **Socket.IO 4.x**(`socket.io` + `socket.io-client`)—— 核心实时能力,目录 `src/socket.io/`
- 用于即时消息、通知、在线状态、实时推帖等
- 多节点部署时通过 Redis adapter 桥接

---

## 5. 模板引擎与前端

### 服务端模板
- **BenchpressJS**(`benchpressjs`,自研)—— 高性能 JS 模板引擎,模板文件为 `.tpl`(见 `src/views/`)
- 与 Express 的 `app.render` 集成

### 前端 UI
- **Bootstrap 5.3** + **Bootswatch** —— 基础 UI 工具包(README 明确说明)
- **Popper.js** —— 定位
- **jQuery 3.7** —— DOM 操作(通过 `resolutions` 锁定全树版本)
- **jQuery UI** —— 部分交互
- 主题系统:内置多套主题包(`nodebb-theme-harmony` / `persona` / `lavender` / `peace`),默认 Harmony
- 样式:**Sass/SCSS**(`sass` + 可选 `sass-embedded`)+ **PostCSS**(`autoprefixer` / `postcss-clean`)+ **rtlcss**(RTL 支持)

### 前端功能库(精选)
- **Chart.js** — 图表
- **Cropper.js** — 图片裁剪
- **Sortable.js** — 拖拽排序
- **Ace editor**(`ace-builds`)— 代码编辑
- **Mousetrap** — 快捷键
- **TextComplete** — @提及自动补全
- **Tinycon / NProgress / timeago / Clipboard.js** — 各种 UX 增强

---

## 6. 构建工具链

- **Webpack 5**(`webpack` + `webpack-merge` + `minimizer-webpack-plugin`)—— 前端打包,配置见 `webpack.{common,dev,prod,installer}.js`
- **esbuild** —— 额外构建加速
- **Grunt**(`Gruntfile.js` + `grunt-contrib-watch`)—— 开发监听任务
- 产物输出到 `build/public/`,以 `.min.js` 命名

---

## 7. 认证与安全

- **Passport**(`passport` + `passport-local` + `passport-http-bearer`)—— 认证框架,支持本地账号与 Bearer token(API)
- **bcryptjs** — 密码哈希(独立 worker 进程 `password_worker.js`)
- **jsonwebtoken (JWT)** — API 令牌
- **zxcvbn** — 密码强度评估
- **nodebb-plugin-2factor** — 双因素认证(内置插件)
- **sanitize-html** — HTML 净化
- **helmet / csrf-sync** — 安全防护
- **sharp** — 图片处理(防恶意图片)

---

## 8. 其他关键后端能力

| 能力 | 库 |
|------|----|
| 邮件 | `nodemailer` 9.x + 开发用 `smtp-server` |
| 任务调度 | `cron` + `cronstrue` |
| HTTP 客户端 | `undici` 8.x + `fetch-cookie` |
| CSV | `@json2csv/node` + `csv-parse` |
| 归档/压缩 | `archiver` |
| RSS | `rss` |
| Sitemap | `sitemap` |
| 国际化 i18n | Transifex(`.tx/`)+ 自研 translator |
| OG 图片生成 | `satori`(服务端生成社交分享图) |
| XML 处理 | `@xmldom/xmldom` + `xml` |
| 日志 | `winston` + `logrotate-stream` |
| **ActivityPub(联邦宇宙)** | `src/activitypub/` 自实现 —— 支持 Mastodon 等互联 |
| Web Push 推送 | `nodebb-plugin-web-push` |

---

## 9. 测试与代码质量

- **测试框架**:Mocha 11(`.mocharc.yml`)— `npm test`
- **覆盖率**:nyc 18 + coveralls
- **Lint**:ESLint 9(flat config `eslint.config.mjs`)+ `eslint-config-nodebb` + `@stylistic/eslint-plugin`
- **测试环境**:jsdom(浏览器模拟)
- **提交规范**:commitlint(Angular 规范,自定义 type-enum 含 `breaking`)+ Husky + lint-staged
- **依赖更新**:Renovate(`renovate.json`)
- **代码质量监控**:Code Climate(`.codeclimate.yml`)

---

## 10. DevOps / 部署

- **容器化**:Dockerfile(多阶段构建,`node:lts` → `node:lts-slim`),`tini` 作 init
- **Compose**:提供三套 —— `docker-compose.yml`(默认 Redis)、`docker-compose-redis.yml`、`docker-compose-pgsql.yml`
- **CI/CD**:GitHub Actions(`.github/workflows/test.yaml` 测试 + `docker.yml` 镜像构建)
- **反向代理**:官方推荐 nginx >= 1.3.13
- **默认端口**:4567

---

## 技术栈速查表

| 层 | 技术 |
|----|------|
| 运行时 | Node.js >= 22 |
| 语言 | JavaScript (CommonJS) |
| Web 框架 | Express 4 |
| 模板引擎 | BenchpressJS(自研) |
| 数据库 | Redis 7.2+ / MongoDB 5+ / PostgreSQL(三选一) |
| 实时通信 | Socket.IO 4 |
| 前端 UI | Bootstrap 5 + jQuery 3 + Bootswatch |
| 样式 | Sass/SCSS + PostCSS |
| 构建打包 | Webpack 5 + esbuild + Grunt |
| 认证 | Passport + JWT + bcrypt |
| 邮件 | Nodemailer |
| 联邦协议 | ActivityPub(自实现) |
| 测试 | Mocha + nyc + jsdom |
| Lint | ESLint 9 (flat config) |
| 容器 | Docker(多阶段) + docker-compose |
| CI | GitHub Actions |
| 许可证 | GPL-3.0 |

---

## 结论

NodeBB 是一个**技术栈相当传统且自包含**的 Node.js 全栈论坛项目:

1. **后端**走经典的 Express + 自研模板引擎 + Socket.IO 路线,没有引入 TypeScript、ORM 或现代元框架(如 NestJS),代码以 CommonJS 为主。
2. **数据库抽象**做得较好,Redis/Mongo/PG 三选一,且通过 Redis adapter 支持水平扩展。
3. **前端**依赖 jQuery + Bootstrap,而非 React/Vue 等 SPA 框架——属于服务端渲染 + 客户端增强的传统模式,Webpack 仅做打包压缩。
4. **亮点**是内置 **ActivityPub** 联邦协议支持(可与 Mastodon 等互通),以及较完善的插件/主题生态(核心功能大量以 `nodebb-plugin-*` / `nodebb-theme-*` 包形式存在)。
5. **工程化**成熟:ESLint flat config、commitlint、Husky、Renovate、GitHub Actions、多阶段 Docker 构建齐全。

适合需要**自托管、可联邦、传统论坛形态且需高度定制**的场景;若追求现代 SPA/SSR 架构则不是首选。
