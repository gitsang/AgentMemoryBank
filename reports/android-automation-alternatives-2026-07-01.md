# Android 连接 / 自动化 Agent 框架替代方案调研报告

> 生成日期：2026-07-01
> 目的：作为 paseo / sesori 的参考搜索补充，覆盖远程控制、设备连接、自动化测试、Agent 框架四个子领域

---

## 一、远程控制 & 屏幕镜像（Remote Control / Screen Mirroring）

### 1. scrcpy

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/Genymobile/scrcpy |
| **Stars** | **144,206** ⭐ |
| **Forks** | 13,298 |
| **语言** | C + Java |
| **License** | Apache-2.0 |
| **最后推送** | 2026-06-23 |
| **最新版本** | v4.0 (2026-05-12) |
| **核心维护者** | rom1v (Romain Vimont), Genymobile |
| **一句话定位** | 高性能 Android 设备屏幕镜像与控制工具，USB/WiFi 连接，无需 root，延迟 35-70ms，30-120fps |
| **连接方式** | USB ADB / TCP/IP (WiFi) |
| **定位差异** | 纯镜像与控制层工具，不含自动化测试或 Agent 能力，但可作为底层流媒体层被上层方案集成 |

---

## 二、设备集群管理（Device Farm Management）

### 2. STF (Smartphone Test Farm) / DeviceFarmer

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/DeviceFarmer/stf (活跃分支) / https://github.com/openstf/stf (原项目) |
| **Stars** | DeviceFarmer: **4,421** ⭐ / OpenSTF: **13,897** ⭐ (归档) |
| **Forks** | 606 / 2,973 |
| **语言** | JavaScript (Node.js) |
| **License** | Apache-2.0 |
| **最后推送** | 2026-03-01 |
| **最新版本** | v3.7.7 (2025-07-23) |
| **核心维护者** | DeviceFarmer 社区 (sorccu, gunta, koral-- 等) |
| **一句话定位** | 从浏览器远程调试和控制 Android 设备的 Web 应用，支持设备农场管理、多用户、设备预订、ADB 转发 |
| **连接方式** | ADB (USB) + WebRTC 流媒体 + 浏览器控制 |
| **定位差异** | 完整的设备农场管理系统，比 paseo/sesori 更底层——管理物理设备而非 agent 会话；OpenSTF 已停维，DeviceFarmer 是活跃社区 fork |

### 3. GADS

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/shamanec/GADS |
| **Stars** | **310** ⭐ |
| **Forks** | 62 |
| **语言** | Go |
| **License** | AGPL-3.0 |
| **最后推送** | 2026-06-29 |
| **最新版本** | v5.7.0 (2026-06-15) |
| **核心维护者** | shamanec |
| **一句话定位** | 自托管设备农场平台，支持 Android/iOS 远程控制 + Appium 测试执行 + Smart TV (Tizen/WebOS)，AWS Device Farm / Firebase Test Lab 的开源替代 |
| **连接方式** | ADB (USB/WiFi) + MJPEG/WebRTC 流 + Appium |
| **定位差异** | 轻量级 STF 替代，内置 Appium 集成、JWT 认证、设备分组管理 |

### 4. drizz-farm

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/parthadrizz/drizz-farm |
| **Stars** | 新项目（约 50+） |
| **语言** | Go + React |
| **License** | Apache-2.0 |
| **最后推送** | 2026 活跃 |
| **一句话定位** | 单二进制自托管 Android 模拟器/设备农场，零云依赖，支持 ADB root 访问、WebRTC H.264 流、声明式 session artifacts |
| **连接方式** | ADB + WebRTC / PNG WebSocket |
| **定位差异** | 极简安装（单个 Go 二进制），专注 Android 模拟器（boot-on-demand），对比 STF 不需要 RethinkDB/Node 8 等旧技术栈 |

---

## 三、自动化测试框架（Automation Testing Frameworks）

### 5. Appium

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/appium/appium |
| **Stars** | **21,635** ⭐ |
| **Forks** | 6,274 |
| **语言** | TypeScript |
| **License** | Apache-2.0 |
| **最后推送** | 2026-06-12 |
| **最新版本** | v3.5.2 (2026-06-18) |
| **核心维护者** | OpenJS Foundation + 社区 (appium org) |
| **一句话定位** | 跨平台 (iOS/Android/Windows/Mac) 自动化框架，基于 W3C WebDriver 协议，支持多种语言 (Python/Java/JS 等) |
| **连接方式** | ADB (通过 uiautomator2-driver / espresso-driver) + USB/WiFi + 云 |
| **定位差异** | 行业标准测试框架，非 agent 平台——专注于测试脚本执行而非 agent 编排；与 paseo/sesori 互补（Appium 可被 agent 调用执行自动化） |

### 6. uiautomator2

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/openatx/uiautomator2 |
| **Stars** | **8,161** ⭐ |
| **Forks** | 1,572 |
| **语言** | Python |
| **License** | MIT |
| **最后推送** | 2026-06-17 |
| **最新版本** | v3.6.0 (2026-06-17) |
| **核心维护者** | codeskyblue (开放 ATX 社区) |
| **一句话定位** | 基于 Google UiAutomator 的 Python 封装，设备端 HTTP RPC 服务 + Python 客户端，毫秒级操作延迟 |
| **连接方式** | ADB + HTTP (WiFi) |
| **定位差异** | 比 Appium 更轻量的纯 Android 方案，Python 原生集成，响应速度极快（毫秒级），不适合跨平台；适合作为 agent 的底层控制层 |

### 7. Airtest

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/AirtestProject/Airtest |
| **Stars** | **9,410** ⭐ |
| **Forks** | 1,434 |
| **语言** | Python |
| **License** | Apache-2.0 |
| **最后推送** | 2026-03-23 |
| **核心维护者** | NetEase (网易) |
| **一句话定位** | 跨平台 UI 自动化框架，主打游戏测试，基于图像识别 + Poco UI 层次定位，支持 Android/iOS/Windows/Unity |
| **连接方式** | ADB + 图像识别 + Poco SDK |
| **定位差异** | 网易出品、图像识别为核心、游戏引擎自动化为特色（Unity3D/Cocos）；AirtestIDE 提供录放式 IDE |

### 8. Espresso (android/android-test)

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/android/android-test |
| **Stars** | **1,219** ⭐ |
| **Forks** | 340 |
| **语言** | Java |
| **License** | Apache-2.0 |
| **最后推送** | 2026-06-30 |
| **核心维护者** | Google |
| **一句话定位** | Google 官方 Android UI 测试框架，提供可靠的 UI 控件匹配和操作同步，白盒集成测试 |
| **连接方式** | 设备内运行（instrumentation test）+ ADB |
| **定位差异** | 仅限 Android、Java/Kotlin、白盒（需源码）；性能最优但灵活性最低，对比 paseo/sesori 完全不属同一层级 |

### 9. Calabash

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/calabash/calabash-android |
| **Stars** | **1,683** ⭐ |
| **Forks** | 607 |
| **语言** | Ruby |
| **License** | NOASSERTION (LGPL 衍生) |
| **最后推送** | 2024-08-08 |
| **核心维护者** | calabash 社区（已基本停维） |
| **一句话定位** | 基于 Cucumber 的 Android 行为驱动开发 (BDD) 自动化测试框架 |
| **连接方式** | ADB + instrumentation test |
| **定位差异** | BDD 风格、Ruby 语言、已基本停维——不建议新项目选用 |

### 10. Robotium

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/RobotiumTech/robotium |
| **Stars** | **2,854** ⭐ |
| **Forks** | 780 |
| **语言** | Java |
| **License** | Apache-2.0 |
| **最后推送** | 2021-09-28 |
| **核心维护者** | RobotiumTech（已停维） |
| **一句话定位** | 曾经的 Android UI 测试标杆框架，黑盒测试支持，已多年不更新 |
| **连接方式** | ADB + instrumentation test |
| **定位差异** | 历史项目，已不再活跃；不适合新项目 |

---

## 四、Monkey / 压力测试（Stress & Monkey Testing）

### 11. Maxim

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/zhangzhao4444/Maxim |
| **Stars** | **905** ⭐ |
| **Forks** | 281 |
| **语言** | Python + Java (framework.jar/monkey.jar) |
| **License** | 未声明 |
| **最后推送** | 2021-06-12 |
| **核心维护者** | zhangzhao4444 |
| **一句话定位** | 基于 UiAutomator 控件解析的高性能 Android Monkey，支持 DFS/Mix/Troy 三种遍历策略，每秒 10-15 Action |
| **连接方式** | ADB shell 直接执行 |
| **定位差异** | 纯压力/遍历测试工具，非连接或 agent 方案 |

### 12. Fastbot_Android (字节跳动)

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/bytedance/Fastbot_Android |
| **Stars** | **1,189** ⭐ |
| **Forks** | 262 |
| **语言** | C++ |
| **License** | 未声明 |
| **最后推送** | 2025-06-20 |
| **核心维护者** | 字节跳动 |
| **一句话定位** | 基于 GUI 转换模型的稳定性测试工具，模型化探索 APP 发现崩溃问题 |
| **连接方式** | ADB |
| **定位差异** | 模型驱动的遍历测试，比 Maxim 更智能，字节跳动内部使用 |

### 13. DroidBot

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/honeynet/droidbot |
| **Stars** | **968** ⭐ |
| **Forks** | 259 |
| **语言** | Python + JavaScript |
| **License** | MIT |
| **最后推送** | 2024-08-16 |
| **核心维护者** | honeynet (yuanchun-li, yzygitzh) |
| **一句话定位** | 轻量级 Android 测试输入生成器，支持随机/脚本输入 + UI Transition Graph 生成，可集成 LLM (DroidBot-GPT) |
| **连接方式** | ADB + AccessibilityService |
| **定位差异** | 介于 monkey 和智能 agent 之间，支持 -humanoid 和 LLM 策略；DroidBot-GPT 分支直接提供 LLM agent 能力 |

---

## 五、底层 ADB 工具库（Low-level ADB Toolkits）

### 14. adbutils

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/openatx/adbutils |
| **Stars** | **1,060** ⭐ |
| **Forks** | 226 |
| **语言** | Python |
| **License** | MIT |
| **最后推送** | 2026-05-06 |
| **核心维护者** | codeskyblue (开放 ATX 社区) |
| **一句话定位** | 纯 Python ADB 库，对 Google ADB 服务的 Python 封装，uiautomator2 的底层依赖 |
| **连接方式** | ADB (USB/WiFi) |
| **定位差异** | 纯库/依赖层，非独立方案；适合作为 agent 框架的 ADB 通信层 |

### 15. AndroidViewClient

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/dtmilano/AndroidViewClient |
| **Stars** | **1,711** ⭐ |
| **Forks** | 343 |
| **语言** | Python |
| **License** | Apache-2.0 |
| **最后推送** | 2025-12-24 |
| **核心维护者** | dtmilano |
| **一句话定位** | Android ViewServer 和 ADB 的 Python 客户端库，提供 UI 控件层次分析和远程控制 |
| **连接方式** | ADB |
| **定位差异** | 较早的 Android 自动化 Python 库，功能全面但活跃度下降 |

### 16. ADBKeyBoard

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/senzhk/ADBKeyBoard |
| **Stars** | **1,812** ⭐ |
| **Forks** | 385 |
| **语言** | Java |
| **License** | GPL-2.0 |
| **最后推送** | 2026-01-10 |
| **核心维护者** | senzhk |
| **一句话定位** | Android 虚拟键盘，通过 ADB broadcast intent 发送 Unicode/非 ASCII 文本输入（解决 adb shell input 不支持中文问题） |
| **连接方式** | ADB broadcast intent |
| **定位差异** | 单一功能的辅助工具，解决中文/Unicode 输入问题，常被 uiautomator2/Appium 集成使用 |

---

## 六、新兴 Agent 驱动类（Agent-Driven / LLM-Powered）

### 17. ghost-in-the-droid/android-agent

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/ghost-in-the-droid/android-agent |
| **Stars** | **224** ⭐ |
| **Forks** | 23 |
| **语言** | Python (FastAPI) + Vue 3 前端 |
| **License** | MIT |
| **最后推送** | 2026-06-07 |
| **核心维护者** | ghost-in-the-droid |
| **一句话定位** | 开源 Android 设备自动化框架——50+ ADB 方法、MJPEG/WebRTC 实时流、Skill 系统、LLM 集成、Vue 仪表盘 |
| **连接方式** | ADB + MJPEG/WebRTC 流 + WebSocket |
| **定位差异** | 与 sesori 最接近的替代：提供了一个完整的设备自动化平台，含 Skill Creator（LLM 辅助创建操作技能）、Skill Miner（BFS 自动探索）、定时任务调度、多设备队列；但偏重设备控制而非 AI coding agent 连接 |

### 18. DroidBot-GPT / DroidBot-LLM

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/MobileLLM/DroidBot-GPT |
| **Stars** | **155** ⭐ |
| **Forks** | 19 |
| **语言** | Python |
| **License** | MIT |
| **最后推送** | 2024-01-17 |
| **核心维护者** | MobileLLM (yuanchun-li 等) |
| **一句话定位** | 基于 DroidBot + ChatGPT 的 Android UI Agent 框架，自然语言任务描述驱动 APP 自动操作 |
| **连接方式** | ADB + AccessibilityService + LLM API |
| **定位差异** | 最接近"Android agent"概念的项目：用自然语言描述任务，agent 自主执行；但基于学术研究项目 (DroidBot)，稳定性和维护度有限 |

### 19. Mobile Device Farm MCP

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/MarcoCarnevali/mobile-device-farm-mcp |
| **Stars** | 约 100+ (新项目) |
| **语言** | TypeScript |
| **License** | MIT |
| **最后推送** | 2026 活跃 |
| **一句话定位** | 给 AI Agent (MCP 协议) 提供直接控制 Android/iOS 设备能力的 MCP 服务器——截图、UI 层次分析、点击、滑动、输入、性能采集 |
| **连接方式** | ADB + MCP 协议 |
| **定位差异** | 专为 AI Agent 生态设计（MCP 协议），让 Claude/Copilot 等直接操控手机；与 paseo/sesori 互补而非竞争 |

---

## 七、Google 官方 & 企业级框架

### 20. Mobly (Google)

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/google/mobly |
| **Stars** | **744** ⭐ |
| **Forks** | 215 |
| **语言** | Python |
| **License** | Apache-2.0 |
| **最后推送** | 2026-06-28 |
| **核心维护者** | Google |
| **一句话定位** | Google 开源的端到端测试框架，专注于复杂环境下的多设备协调测试（WiFi/BT/蜂窝等组合场景） |
| **连接方式** | ADB + 多设备协调 |
| **定位差异** | 多设备/多网络的 E2E 测试场景，非 UI 自动化框架；适合 IoT/连接类测试场景 |

### 21. SoloPi (支付宝/蚂蚁)

| 字段 | 内容 |
|------|------|
| **GitHub** | https://github.com/alipay/SoloPi |
| **Stars** | **6,180** ⭐ |
| **Forks** | 1,251 |
| **语言** | Java |
| **License** | Apache-2.0 |
| **最后推送** | 2024-07-11 |
| **最新版本** | v0.12.0 (2022-05) |
| **核心维护者** | 蚂蚁集团 (soloPi, ruoranw) |
| **一句话定位** | 支付宝开源的无线化、非侵入式 Android 专项测试工具：录制回放 + 性能测试 + 一机多控 |
| **连接方式** | ADB (USB TCP/IP) + AccessibilityService + CDP + 图像识别 |
| **定位差异** | 端上录制回放、不需 PC 即可回放；支持录制备份转 Appium/Macaca 脚本；一机多控（一台控制多台）；有 HarmonyOS 分支 |

---

## 八、结构化总表

| # | 项目 | Stars ⭐ | 类别 | 语言 | License | 最近更新 | 一句话定位 |
|---|------|---------|------|------|---------|---------|-----------|
| 1 | **scrcpy** | 144,206 | 屏幕镜像 | C+Java | Apache-2.0 | 2026-06 | 高性能 Android 屏幕镜像/控制，USB/WiFi，延迟 35ms |
| 2 | **OpenSTF / DeviceFarmer** | 13,897 / 4,421 | 设备农场 | JS (Node) | Apache-2.0 | 2026-03 | 浏览器远程设备调试/管理平台，多用户设备农场 |
| 3 | **Appium** | 21,635 | 自动化测试 | TS | Apache-2.0 | 2026-06 | 跨平台 WebDriver 自动化框架，iOS/Android/Windows |
| 4 | **uiautomator2** | 8,161 | 自动化测试 | Python | MIT | 2026-06 | 基于 UiAutomator 的 Python 封装，毫秒级操作 |
| 5 | **Airtest** | 9,410 | 自动化测试 | Python | Apache-2.0 | 2026-03 | 网易出品，图像识别 + 游戏引擎自动化框架 |
| 6 | **SoloPi** | 6,180 | 专项测试 | Java | Apache-2.0 | 2024-07 | 支付宝录制回放 + 性能测试 + 一机多控工具 |
| 7 | **Espresso** | 1,219 | 自动化测试 | Java | Apache-2.0 | 2026-06 | Google 官方 UI 测试框架，白盒集成测试 |
| 8 | **adbutils** | 1,060 | ADB 库 | Python | MIT | 2026-05 | 纯 Python ADB 封装库，uiautomator2 的底层依赖 |
| 9 | **AndroidViewClient** | 1,711 | ADB 库 | Python | Apache-2.0 | 2025-12 | ViewServer + ADB 的 Python 客户端库 |
| 10 | **Fastbot_Android** | 1,189 | Monkey | C++ | - | 2025-06 | 字节跳动模型化 GUI 遍历稳定性测试工具 |
| 11 | **DroidBot** | 968 | Monkey/Agent | Python | MIT | 2024-08 | 轻量级输入生成器 + UI Transition Graph，可集成 LLM |
| 12 | **Maxim** | 905 | Monkey | Python/Java | - | 2021-06 | 高性能 Android Monkey，DFS/Mix/Troy 遍历策略 |
| 13 | **Mobly** | 744 | E2E 框架 | Python | Apache-2.0 | 2026-06 | Google 多设备协调 E2E 测试框架 |
| 14 | **Calabash** | 1,683 | 自动化测试 | Ruby | - | 2024-08 | Cucumber BDD 风格 Android 测试（基本停维） |
| 15 | **Robotium** | 2,854 | 自动化测试 | Java | Apache-2.0 | 2021-09 | 曾经的 Android 测试标杆（已停维） |
| 16 | **ADBKeyBoard** | 1,812 | 辅助工具 | Java | GPL-2.0 | 2026-01 | ADB 广播输入法，解决 Unicode/中文输入 |
| 17 | **GADS** | 310 | 设备农场 | Go | AGPL-3.0 | 2026-06 | 自托管设备农场 + Appium 执行 + Smart TV |
| 18 | **android-agent (ghost)** | 224 | Agent 平台 | Python | MIT | 2026-06 | ADB 设备控制 + Skill 系统 + LLM + Vue 仪表盘 |
| 19 | **appium-device-farm** | 613 | 设备农场 | TS | Apache-2.0 | 2026-05 | Appium 2.0 插件，多设备并行 session 管理 |
| 20 | **DroidBot-GPT** | 155 | Agent | Python | MIT | 2024-01 | LLM agent 驱动 Android UI 自动化 |
| 21 | **drizz-farm** | ~50 | 设备农场 | Go+React | Apache-2.0 | 2026 | 单二进制 Android 模拟器农场，零云依赖 |
| 22 | **Mobile Device Farm MCP** | ~100 | Agent MCP | TS | MIT | 2026 | MCP 协议设备控制，让 AI 直接操控手机 |

---

## 九、类别关系总览

```
                    ┌── Agent 编排平台 ── paseo, sesori
                    │
                    ├── Agent 设备控制 ── android-agent, DroidBot-GPT, Mobile Device Farm MCP
                    │
Android 方案 ────── ├── 设备农场管理 ── STF/DeviceFarmer, GADS, drizz-farm, appium-device-farm
                    │
                    ├── 自动化测试 ── Appium, uiautomator2, Airtest, Espresso
                    │
                    ├── 压力/遍历测试 ── Maxim, Fastbot, DroidBot
                    │
                    ├── 远程镜像控制 ── scrcpy
                    │
                    ├── 专项/辅助工具 ── SoloPi, ADBKeyBoard
                    │
                    └── 底层 ADB 库 ── adbutils, AndroidViewClient
```

---

## 十、与 paseo / sesori 的差异定位要点

1. **paseo** (9.5k ⭐, AGPL-3.0) 定位为"agent orchestration daemon"——连接 Claude Code/Codex/OpenCode 等多个 AI coding agent，提供统一桌面+移动界面。**不直接管理 Android 设备**，而是管理 AI agent 的编排和通信。

2. **sesori** (闭源/私有) 定位为"mobile cockpit for AI coding agents"——将手机变成 AI 编程 agent (OpenCode/Claude Code) 的遥控器。**不直接自动化 Android 应用**，而是让开发者从手机控制 coding agent。

3. **双方的共同假设**：你已经有了一台运行 AI coding agent 的电脑（Mac/Linux）。它们解决的是"如何从手机远程操控 agent"的问题，而非"如何自动化控制 Android 设备"。

4. **本报告覆盖的方案中，与 paseo/sesori 最接近的竞品**：
   - **android-agent (ghost)**：同样提供设备控制 + LLM 集成 + Web 仪表盘，但侧重 ADB 设备自动化而非 AI coding agent 编排
   - **Mobile Device Farm MCP**：同样通过 agent 控制设备，但使用 MCP 协议对接 AI agent
   - **DroidBot-GPT**：同样用 LLM 驱动设备操作，但更偏测试场景

5. **本报告中可与 paseo/sesori 互补的方案**：
   - **Appium / uiautomator2**：可作为 AI agent 的执行引擎——agent 通过 Appium 控制手机
   - **STF / GADS**：提供物理设备管理和远程 ADB 连接，为 agent 提供设备接入层
   - **scrcpy**：提供实时屏幕流，可被 agent 用于视觉观察

---

## 附：信息来源

所有数据均通过 GitHub API 和网页搜索采集于 2026-07-01。Star 数与活跃度可能随项目更新而变化。
