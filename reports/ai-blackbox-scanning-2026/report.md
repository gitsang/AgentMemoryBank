# AI 黑盒扫描调研报告 (2026-05)

## 概述

本报告调研了当前 AI 在黑盒安全扫描（Web、固件、二进制）方向的工具、组织、论文和方法论。

**核心发现：**
- **商业化方向**：AI 辅助 DAST（动态应用安全测试），自主认证处理和漏洞验证
- **学术前沿**：LLM Agent + 记忆 + 工具调用 + 反馈循环
- **最佳黑盒方案**：观察 → 规划 → 验证 → 适应，而非静态载荷字典

---

## 一、Web 黑盒扫描

### 1.1 工具

| 工具 | 类型 | 组织 | AI 能力 | URL |
|---|---|---|---|---|
| **Burp AI / Burp Suite DAST** | 商业 | PortSwigger | AI 增强扫描、自主探索、AI 登录序列、请求/响应分析 | https://portswigger.net/burp/documentation/dast/user-guide/burp-ai |
| **Levo DAST Scanner** | 商业 | Levo.ai | AI 驱动认证发现、爬虫/扫描编排 | https://docs.levo.ai/dast |
| **Qualys WAS AI** | 商业 | Qualys | AI 剖析应用并选择最相关检测 | https://docs.qualys.com/en/was/latest/scans/ai_powered_scan_optimization.htm |
| **Veracode DAST** | 商业 | Veracode | AI 辅助登录和黑盒 DAST 工作流 | https://docs.veracode.com/r/DAST |
| **Sec1 DAST** | 商业 | Sec1 | Agentic AI 引擎、多 Agent 爬虫/攻击/验证 | https://sec1.io/products/dast/ |
| **Xalgorix** | 开源 | Xalgorix | 自主目标发现、工具编排、报告生成 | https://docs.xalgorix.com/ |
| **ShakerScan** | 开源 | andriyze | AI 门探测 chat/RAG/agent/MCP 接口 | https://github.com/andriyze/shakerscan |
| **KramScan** | 开源 | shaikhakramshakil | 多 LLM 分析、自主验证、SPA/浏览器测试 | https://github.com/shaikhakramshakil/kramscan |
| **AIPTX** | 开源 | aiptx | LLM 辅助扫描编排、DAST + 业务逻辑测试 | https://github.com/aiptx/aiptx |
| **SSSAI** | 开源 | vzeman | Agentic 扫描规划/执行、浏览器自动化 | https://github.com/vzeman/sssai |

### 1.2 组织

- **PortSwigger** — 最强主流 AI 辅助黑盒 Web 测试厂商
- **Levo.ai** — AI 驱动 DAST
- **Qualys** — AI 扫描优化
- **Veracode** — DAST + AI 认证
- **Sec1** — Agentic 自主 DAST

### 1.3 关键论文

| 论文 | 作者 | 会议 | 核心思想 | URL |
|---|---|---|---|---|
| **PENTESTGPT** | Deng et al. | arXiv 2023 | LLM 引导渗透测试助手，任务分解+工具使用 | https://arxiv.org/pdf/2308.06782 |
| **Getting pwn'd by AI** | Happe, Cito | ESEC/FSE 2023 | LLM 辅助测试规划+闭环反馈 | https://arxiv.org/pdf/2308.00121 |
| **Sqirl** | Al Wahaibi et al. | USENIX Security 2023 | RL 载荷生成+爬虫+数据库反馈 | https://www.usenix.org/system/files/usenixsecurity23-al-wahaibi.pdf |
| **LLM Agents can Autonomously Hack Websites** | Fang et al. | arXiv 2024 | 浏览器/工具 LLM Agent 链式多步 Web 漏洞利用 | https://arxiv.org/pdf/2402.06664v1 |
| **YURASCANNER** | Stafeev et al. | NDSS 2025 | 任务驱动 Web 应用扫描+XSS 引擎验证 | https://www.ndss-symposium.org/wp-content/uploads/2025-388-paper.pdf |
| **PENTESTGPT V2** | - | arXiv 2026 | 工具/技能层+任务难度评估+攻击树搜索 | https://arxiv.org/pdf/2602.17622 |
| **AWE** | - | arXiv 2026 | 记忆增强多 Agent Web 漏洞利用+确定性验证 | https://arxiv.org/pdf/2603.00960 |
| **Red-MIRROR** | - | arXiv 2026 | RAG+共享循环记忆+双阶段反思 | https://www.arxiv.org/pdf/2603.27127 |
| **Zelda** | Lee et al. | WWW 2026 | 闭环黑盒模糊测试+推断反馈信号 | https://yonghwi-kwon.github.io/data/zelda_www26.pdf |

### 1.4 方法论

- **RL 载荷生成**：基于响应反馈自适应攻击串（Sqirl, BertRLFuzzer）
- **LLM 漏洞 Agent**：LLM 作为规划者+操作者+验证者（PENTESTGPT, AutoPT）
- **多 Agent 编排**：专门角色提升长期攻击（planner/recon/exploit/validator/memory）
- **记忆/RAG/反思**：避免长 Web 工作流失状态
- **反馈驱动爬虫/模糊测试**：使用运行时信号而非源码
- **AI 辅助登录和认证**：商业扫描器常见功能

---

## 二、固件分析

### 2.1 工具

| 工具 | AI 角度 | 黑盒适用性 |
|---|---|---|
| **FACT** | 非 AI 原生；强自动化基线 | 强 |
| **Mango** | 算法数据流分析 | 强 |
| **LATTE** | LLM 选择污点源/汇和规则 | 强 |
| **FirmHive** | 递归委派+记忆的自主 LLM 固件分析 | 强 |
| **FORGE** | 推理-行动-观察循环的反馈驱动 LLM 执行 | 强 |
| **FirmAgent** | 模糊测试+LLM Agent 混合流水线 | 强 |
| **Wairz** | MCP 连接 Agent 工作流的 60+ 工具 | 强 |
| **FuzzForge AI** | Agentic 工具链的 AI 工作流编排 | 中强 |

### 2.2 组织

| 组织 | 焦点 |
|---|---|
| Fraunhofer FKIE / FACT 社区 | 黑盒固件分析自动化 |
| Arizona State University + UCSB | Mango / 可扩展污点发现 |
| Tsinghua + IIE CAS + Waterloo + Ant Group | LATTE / LLM 驱动污点分析 |
| Beijing Jiaotong University Security Lab | FORGE / 自主 LLM 二进制分析 |
| BJTU Security Lab (FirmHive) | 运行时增长多 Agent 固件分析 |

### 2.3 关键论文

| 年份 | 论文 | 会议 | 笔记 |
|---|---|---|---|
| 2024 | **Operation Mango** | USENIX Security 2024 | 可扩展黑盒二进制固件污点分析现代基线 |
| 2025 | **LLM-Powered Static Binary Taint Analysis** | ACM TOSEM 2025 | 首个清晰 LLM 驱动污点规则合成 |
| 2025 | **LLMs as Firmware Experts** | arXiv | 递归多 Agent 固件分析 |
| 2026 | **FORGE** | arXiv | 自适应推理循环+证据验证 |
| 2026 | **FirmAgent** | NDSS 2026 | 最佳黑盒+语义推理混合方案 |

### 2.4 方法论

- **LLM 辅助逆向工程**：LLM 读反编译输出、遍历固件树、推断源/汇
- **Agentic 多步分析**：递归 Agent、记忆、反馈循环持续探索
- **ML/LLM 驱动污点建模**：LLM 替代手写污点规则
- **模糊测试+LLM 混合**：模糊测试找输入点，LLM 重建路径和 PoC
- **工具编排黑盒流水线**：经典工具(binwalk/Ghidra/QEMU/AFL++)通过编排层暴露给 AI Agent

---

## 三、二进制分析

### 3.1 工具

| 工具 | 类型 | 功能 | 组织 |
|---|---|---|---|
| **RevEng.AI / reait** | 商业 | 二进制相似性搜索、stripped 符号恢复、AI 反编译 | RevEng.AI |
| **ReversingLabs Spectra** | 商业 | AI 驱动恶意软件/篡改/密钥/供应链风险分析 | ReversingLabs |
| **Innora-Sentinel** | 商业+OSS | 本地 LLM 驱动自主逆向+漏洞扫描 | Innora AI |
| **Kong** | OSS | Ghidra 上的 Agentic 逆向：反编译/重命名/重类型/去混淆 | Kong project |
| **OGhidra** | OSS | Ghidra LLM 编排，本地/云模型，恶意软件工作流 | LLNL |
| **GhidrAssist** | OSS | 语义图/RAG/agentic 模式的 LLM 辅助 RE | symgraph |
| **TetraMCP** | OSS | Ghidra MCP 服务器；AI 辅助重命名/解释 | kronflux |
| **ReSym** | OSS 研究 | 从 stripped 二进制恢复变量名/类型 | Purdue |
| **DeGPT** | OSS 研究 | LLM 反编译器输出优化 | CAS/UCAS |
| **VulBinLLM** | 研究原型 | LLM stripped 二进制漏洞检测 | UCLA+Cisco |
| **LibLMFuzz** | 研究原型 | LLM 闭源二进制库模糊驱动生成 | 独立研究 |

### 3.2 组织

| 组织 | 知名领域 |
|---|---|
| RevEng.AI (Binary AI Ltd.) | 商业二进制相似性/符号恢复/AI RE |
| ReversingLabs | 企业级供应链和恶意软件二进制分析 |
| Innora AI | AI 逆向引擎+漏洞发现 |
| Purdue University | ReSym；强二进制符号恢复 |
| UCLA + Cisco Research | VulBinLLM；LLM stripped 二进制漏洞检测 |
| CAS/UCAS/Ant Group/Tsinghua/Waterloo | LATTE；LLM 驱动二进制污点分析 |
| LLNL | OGhidra / Ghidra-LLM 工作流 |
| BJTU SecurityLab | FORGE；反馈驱动 LLM 二进制漏洞分析 |

### 3.3 关键论文

| 论文 | 会议 | 核心思想 |
|---|---|---|
| **LATTE** | TOSEM 2025 | LLM 引导提示序列+代码切片做二进制污点分析 |
| **DeGPT** | NDSS 2024 | 三角色 LLM 循环优化反编译器可读性 |
| **ReSym** | CCS 2024 | 微调 LLM+Prolog 聚合恢复变量名/类型 |
| **VulBinLLM** | arXiv 2025 | 反编译代码丰富+记忆/队列编排做漏洞检测 |
| **FORGE** | arXiv 2026 | 推理-行动-观察循环+动态 Agent 森林做长期二进制漏洞发现 |
| **LibLMFuzz** | arXiv 2025 | LLM 规划/生成/自修复 stripped 库模糊驱动 |

### 3.4 方法论

- **LLM 辅助反编译器精炼**：改进变量名/注释/结构（DeGPT, ReSym, OGhidra, Kong）
- **LLM 引导漏洞推理**：反编译代码+提示序列/思维链/记忆推断 CWE（LATTE, VulBinLLM）
- **Agentic 反馈循环**：模型检查工具输出、修订假设、递归（FORGE, Kong, GhidrAssist）
- **二进制相似性/嵌入恢复**：学习表示恢复符号或找相关函数（RevEng.AI, sentinel-reverse）
- **LLM 辅助模糊测试**：为黑盒二进制生成模糊驱动/输入/线束（LibLMFuzz）
- **图支撑上下文组装**：构建函数/模块知识图减少幻觉（GhidrAssist, TetraMCP）

---

## 四、领先组织和趋势

### 4.1 顶级研究组

- **Project Glasswing / Anthropic** — 大规模 AI 漏洞发现和代码扫描；扫描 1000+ OSS 项目，发现 10k+ 高/严重漏洞
- **TitanCA (SMU + GovTech Singapore)** — LLM Agent 漏洞发现流水线；分析 127k+ GitHub 仓库，发现 203 零日，产出 118 CVE
- **RESIST (Linköping Univ.)** — 网络弹性 AI 国家中心
- **AI Security Initiative (UC Berkeley CLTC)** — AI 风险/安全标准和治理研究
- **AIS2 Lab (Lingnan University)** — AI+系统安全实验室

### 4.2 领先公司

- **Protect AI** — 端到端 AI 安全平台；484 万+ 模型版本扫描，2520 CVE 记录
- **HiddenLayer** — AI 发现/供应链安全/攻击模拟/运行时安全
- **Anthropic** — Project Glasswing 和 Claude Security beta
- **AISLE** — AI 原生 SAST；声称 30+ 关键项目数百 CVE
- **Repello AI** — Agentic AI 自主红队
- **RAXE** — 运行时 AI 安全平台
- **Pinata** — AI 生成代码安全扫描

### 4.3 关键会议

| 会议 | 特点 |
|---|---|
| **IEEE S&P** | 首选 venue；明确包含 ML 攻击/防御 |
| **USENIX Security** | 系统安全 venue |
| **ACM CCS** | 顶 venue；有 ML/安全和提示注入/后门指导 |
| **NDSS** | 强系统/网络安全 venue |
| **Black Hat / DEF CON** | 实践 venue，AI 攻防工具快速出现 |

### 4.4 开源项目

- **FuzzingBrain** — LLM 驱动漏洞检测/修补；DARPA AIxCC 决赛系统
- **Clearwing (Lazarus AI)** — 自主漏洞扫描器/源码猎手
- **pentest-ai** — Agentic 渗透测试 CLI/MCP，200+ 工具
- **NeuroSploit** — AI 自主渗透测试平台
- **WRAITH** — RL 驱动渗透测试框架
- **FuzzForge AI** — MCP 模糊测试/攻击安全工作流编排

### 4.5 趋势

1. **从模式匹配到 Agentic 推理**：多步 LLM 工作流替代简单 SAST 规则
2. **接地/知识引导检测**：图、检索和程序分析与 LLM 融合
3. **漏洞确认而非仅检测**：PoC 生成和验证成为标准
4. **运行时 AI Agent 安全**：提示注入、工具滥用和行为监控成为一等产品
5. **LLM 安全基准+披露政策**：主要 venue 现在要求明确 LLM 使用披露
6. **持续 OSS 规模扫描**：Glasswing 和 TitanCA 在互联网规模扫描
7. **工具融合**：安全扫描器变得 MCP/Agent 友好并集成 CI/CD

---

## 五、总结

### 技术演进路径

```
2023: RL 载荷生成 + LLM 辅助规划
      ↓
2024: LLM Agent + 工具调用 + 反馈循环
      ↓
2025: 多 Agent 编排 + 记忆/RAG + 污点分析
      ↓
2026: Agentic 自主扫描 + 模糊测试混合 + PoC 生成验证
```

### 最佳实践组合

1. **Web**：浏览器支持的 Agent + 针对性漏洞验证（Burp AI, YURASCANNER, AWE）
2. **固件**：黑盒提取 + 指纹 + CVE 关联 + 模糊/仿真 + LLM 引导验证（FirmAgent）
3. **二进制**：LLM + 真实二进制工具（反编译器/调试器/模糊器）而非"仅 LLM"分析

### 关键洞察

- **商业化**：AI 辅助 DAST 成为主流，重点在自主认证和漏洞验证
- **学术**：LLM Agent + 记忆 + 工具调用 + 反馈循环是前沿
- **开源**：MCP/Agent 架构成为安全工具集成新范式
- **效果**：最佳黑盒结果来自"观察→规划→验证→适应"系统，而非静态规则

---

报告生成时间：2026-05-29
数据来源：Web 搜索、学术论文、开源项目、厂商文档
