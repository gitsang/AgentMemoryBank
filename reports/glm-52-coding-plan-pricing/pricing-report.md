# GLM-5.2 Coding / Token 订阅套餐 — 跨平台定价与配额对比

> 抓取时间：2026-07-01 ｜ 时区 UTC+8 (Asia/Shanghai)
> 汇率假设：1 USD ≈ 7.2 CNY（2026 Q3 中间价参考，实际以结算为准）
> 所有 USD 数字均为按上述汇率折算后的"等价 API 价值"，并非平台实际计费货币。

---

## 0. 统一换算方法论（用户给定的混合口径）

**前设**

- 缓存命中率 = 90%
- 输入(含缓存读) : 输出 = 200 : 1
- 把"一次完整的 200:1 计算单元"定义为一个 unit：
  - 180 个 cache-read token
  - 20 个 fresh input token
  - 1 个 output token
  - unit 总长 = 201 tokens，其中 output = 1 token

**API 官方单价（per 1M tokens）**

| 平台 / 模型                                                   | 输入          | 缓存读         | 输出           | 备注         |
| ------------------------------------------------------------- | ------------- | -------------- | -------------- | ------------ |
| Zhipu 原厂 (BigModel / SiliconFlow / Z.ai 海外 / OpenCode Go) | $1.40 / ¥8    | $0.26 / ¥2     | $4.40 / ¥28    | 等价         |
| 阿里云百炼（cn-beijing，Zhipu 部署的 GLM-5.2）                | $1.333 / ¥9.6 | $0.333 / ¥2.40 | $4.667 / ¥33.6 | 缓存折扣 25% |

**Blend cost per unit（每单元等价 USD）**

- **Zhipu 原厂族**：`(180×0.26 + 20×1.40 + 1×4.40) / 1,000,000 = **$0.0000792 / unit**`
  - ↔ `$1 = 12,626 units = 2.538M mixed tokens` (= 12,626 output tokens)
  - ↔ `1M 混合 tokens = $0.394`
- **阿里云百炼 GLM-5.2**：`(180×0.333 + 20×1.333 + 1×4.667) / 1M = $0.0000913 / unit`
  - ↔ `$1 = 10,951 units = 2.20M mixed tokens`
  - ↔ `1M 混合 tokens = $0.456`

**杠杆 (Leverage)** =（月配额折算的等价 API 美元价值）/ 月费

---

## 1. 价格总表（按官费 + 月度等价）

| 平台                                | 套餐                                                 | 官方月费             | 官方月配额                                                      | 月配额 Token (混合)     | 月配额 USD      | 杠杆                                             | 备注                                                                       |
| ----------------------------------- | ---------------------------------------------------- | -------------------- | --------------------------------------------------------------- | ----------------------- | --------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| **智谱 BigModel** 国内              | Lite                                                 | ¥49/月 (¥34 包年)    | ~80 prompts / 5h，~400 / 周 → 1,600 prompts / 月                | 约 **259–518M** mixed   | $102–204        | **15–30×**                                       | GLM-5.2 高峰 3× / 非高峰 2× 抵扣（截至 9 月底促销：非高峰 1×）             |
|                                     | Pro                                                  | ¥149/月 (¥104 包年)  | ~400 prompts / 5h，~2,000 / 周 → 8,000 / 月                     | 约 **786M–1.58B**       | $310–621        | **15–30×**                                       | 同上                                                                       |
|                                     | Max                                                  | ¥469/月 (¥328 包年)  | ~1,600 prompts / 5h，~8,000 / 周 → 32,000 / 月                  | 约 **2.48–4.96B**       | $977–1,954      | **15–30×**                                       | 高峰优先资源保障                                                           |
| **Z.ai Coding Plan** (海外)         | Lite                                                 | $18/月 ($12.60 包年) | 同 BigModel：80 / 5h，400 / 周 → 1,600 / 月                     | 约 **686M–1.37B** mixed | $270–540        | **15–30×**                                       | 同上 3×/2× 倍率，9 月底前非高峰 1× 促销                                    |
|                                     | Pro                                                  | $72/月 ($50.40 包年) | 2,000 / 周 → 8,000 / 月                                         | 约 **2.74–5.48B**       | $1,080–2,160    | **15–30×**                                       |                                                                            |
|                                     | Max                                                  | $160/月 ($112 包年)  | 8,000 / 周 → 32,000 / 月                                        | 约 **6.09–12.2B**       | $2,400–4,800    | **15–30×**                                       |                                                                            |
| **OpenCode Go**                     | Go (单一套餐)                                        | $5 首月 → $10/月     | **$12 / 5h, $30 / 周, $60 / 月**（按官方 API 价折算后抵扣上限） | 约 **152M** mixed / 月  | **$60**         | **6×**（首月 12×）                               | GLM-5.2 单模型上限：880 req/5h，2,150/周，4,300/月；13 模型共用额度        |
| **阿里云百炼 Token Plan（团队版）** | 标准席                                               | ¥198/月              | 25,000 Credits / 月                                             | 约 **76M** mixed        | $34.7 (= ¥250)  | **1.26×**                                        | 仅华北2；团队管理、缓存 25% 折价；可加 5h 共享用量包 ¥5,000 / 625K Credits |
|                                     | 高级席                                               | ¥698/月              | 100,000 Credits / 月                                            | 约 **306M**             | $139 (= ¥1,000) | **1.43×**                                        |                                                                            |
|                                     | 尊享席                                               | ¥1,398/月            | 250,000 Credits / 月                                            | 约 **764M**             | $347 (= ¥2,500) | **1.79×**                                        |                                                                            |
|                                     | 共享用量包                                           | ¥5,000 / 个          | 625,000 Credits / 个                                            | 约 **1.91B**            | $868 (= ¥6,250) | **1.25×**                                        | 1 个月有效期，可叠加                                                       |
| **SiliconFlow (硅基流动)**          | (无 Coding/Token 套餐，仅 API 按量付费 + 新人赠额度) | ¥0/月（充值按需）    | 无月度配额                                                      | 按量                    | 按量            | 1× (主)；14 元新人赠额度 (= ~17.7M mixed tokens) | API 单价同 Zhipu：¥8 / ¥2 / ¥28；另提供预留实例 (¥486K–594K/月，企业级)    |

> Zhipu 原厂族指：BigModel (国内官方)、Z.ai (海外官方)、SiliconFlow (经纬智谱授权直供)、OpenCode Go (转发)。四者 API 单价等价，但订阅套餐形式不同。

---

## 2. 各平台换算细则（"是怎么算的"全额展开）

### 2.1 智谱 BigModel (国内) — `docs.bigmodel.cn/cn/coding-plan/overview`

**输入**：

- 月费：Lite ¥49 / Pro ¥149 / Max ¥469（包年 7 折更低：¥34 / ¥104 / ¥328）
- 每月配额（prompts）：`400 / 周 × 4 ≈ 1,600（Lite）`、`8,000（Pro）`、`32,000（Max）`
- "1 prompt = 15–20 次模型调用"（官方）

**计算步骤**：

```
官方 leverage = 15–30 × 月费（"已计入周限额影响"，厂商声明）
→ Lite USD 值 = 15–30 × ¥49 / 7.2 = $102 – $204 / 月
→ Pro USD 值 = $310 – $621 / 月
→ Max USD 值 = $977 – $1,954 / 月

Token 换算（Zhipu 族 blend = $0.394 / M mixed）：
→ Lite Token = $102–204 / $0.394 × 1M = 259M – 518M mixed / 月
→ Pro Token = 786M – 1.58B / 月
→ Max Token = 2.48B – 4.96B / 月

杠杆（USD价值/月费）= 15–30×（厂商官方）
```

**倍率调整**：GLM-5.2 调用配额消耗系数 = 高峰(14–18 UTC+8) **3×**，非高峰（其它时段） **2×**；
限免促销至 2026-09 月底：**非高峰 1×**。这意味"高峰跑满"会把上面估算再打 1/3 折扣；"全非高峰跑"（促销期内）可拿到上限。

### 2.2 Z.ai Coding Plan (海外)

**输入**：

- 月费：Lite $18 / Pro $72 / Max $160（年付约 7 折）
- 同样的配额表（80 / 400 / 1600 prompts/5h，400 / 2,000 / 8,000 prompts/周）
- 同样的 15–30× 官方 leverage，以及同样的 3×/2× 高峰系数，9 月底前 1× 非高峰促销
- API 单价：GLM-5.2 输入 $1.40 / 已缓存 $0.26 / 输出 $4.40（per 1M）

**计算**：

```
USD 月值 = 15–30 × 月费本身（美元平台，无需汇率）:
Lite: $270 – $540
Pro:  $1,080 – $2,160
Max:  $2,400 – $4,800

Token（Zhipu 族 blend $0.394/M mixed）：
Lite: $270–540 / 0.394 = 686M – 1.37B / 月
Pro:  2.74B – 5.48B / 月
Max:  6.09B – 12.2B / 月

杠杆 15–30×（官方直接给）
```

### 2.3 OpenCode Go — `opencode.ai/docs/go`

**输入**：

- 月费：首月 $5、之后 $10/月
- 配额以"美元抵扣上限"表述（不再换算 prompt 数）：
  - 每 5 小时上限 $12 等价使用
  - 每周上限 $30 等价使用
  - 每月上限 $60 等价使用
- 13 个模型共用同一个 $60 / 月池（包括 GLM-5.2 / GLM-5.1 / Kimi / Qwen3.7 / MiniMax / DeepSeek 等）
- GLM-5.2 单模型请求硬上限：880 req / 5h · 2,150 req / 周 · 4,300 req / 月
- 内部 API 单价（公开）：GLM-5.2 input $1.40 / cache $0.26 / output $4.40（与 Zhipu 直接对齐）

**计算**：

```
月 USD 值 = $60（官方明确披露，按 API 等价计算）
Token        = $60 / $0.394 × 1M = 152M mixed / 月
杠杆         = $60 / $10 = 6×（首月 $60 / $5 = 12×）

如全跑 GLM-5.2 单模型，受 4,300 req/月硬约束：
 单请求平均: $60 / 4,300 = $0.014 = ~17.7K mixed tokens / req
```

**特点**：是 5 个平台里**最透明、口径最一致**的——它直接把月配额写成"值 $60 的 API 调用"，省去了 prompt↔credit 的换算歧义。

### 2.4 阿里云百炼 Token Plan（团队版）— `help.aliyun.com/zh/model-studio/token-plan-overview`

**输入**：

- 月费 + 月度 Credits：标准席 ¥198 / 25,000 Credits，高级席 ¥698 / 100,000 Credits，尊享席 ¥1,398 / 250,000 Credits
- 可加购共享用量包 ¥5,000 / 625,000 Credits（1 个月有效期）
- 仅华北2（北京）地域
- GLM-5.2 调用单价（cn-beijing 标准按量）：输入 ¥9.6/M，输出 ¥33.6/M，缓存读 25% 折价 = ¥2.40/M

**Credits 换算**：
官方示例：qwen3.6-plus 单次 8,349 input tokens → 1.67 Credits，反推 1 Credit = ¥0.01 标准按量计费价值。
→ 也就是 Token Plan 把 GLM-5.2 的"标准 API 价格"以 1 Credit = ¥0.01 折算成 Credits：

- GLM-5.2 输入 = 960 Credits/M，缓存 240 Credits/M，输出 3,360 Credits/M

**计算（per unit, blend cost in Credits）**：

```
Cost/unit = (180×240 + 20×960 + 1×3,360) / 1,000,000 = 0.06576 Credits / unit
→ 1 Credit = 15.21 units = 3,057 mixed tokens
→ 25,000 Credits = 76.4M mixed tokens
→ 100,000 Credits = 305.7M mixed tokens
→ 250,000 Credits = 764.3M mixed tokens
→ 625,000 Credits = 1.911B mixed tokens

USD 等价（直接按 ¥0.01/Credit → USD @ 7.2 = $0.001389/Credit）:
 25K Credits = $34.7 (= ¥250)
 100K Credits = $139 (= ¥1,000)
 250K Credits = $347 (= ¥2,500)
 625K Credits = $868 (= ¥6,250)

杠杆 = 等价 API 价值 / 月费:
 标准 ¥250/¥198 = 1.26×
 高级 ¥1,000/¥698 = 1.43×
 尊享 ¥2,500/¥1,398 = 1.79×
 共享包 ¥6,250/¥5,000 = 1.25×
```

**特点**：Credits 即可直接换算为按量 API 的 ¥，**最直白、最低杠杆**。

> 价值不在数量，而是：仅华北2团队管理后台 + 不排队 + 不进训练 + 兼容 Cursor/OpenClaw/Claude Code/Anthropic 协议。

### 2.5 SiliconFlow — `siliconflow.cn/pricing`

**SiliconFlow 没有 Coding/Token 月度订阅套餐**，仅提供：

- **按量 API**：GLM-5.2 输入 ¥8/M (≤32K) → 长上下文阶梯到 ¥28/M（>`32k`档），缓存 ¥2/M，输出 ¥28/M
  - 国际平台美元价等价：$1.40 / $0.26 / $4.40（per 1M tokens）
- **新用户赠额度**：14 元 / $1 USD 信用（约等于 17.7M mixed tokens 的免费试用额度）
- **预留实例**（企业级）：~¥486K–594K / 组 / 月（DEEPSEEK / GLM 等），按组独占算力；折合单价 ¥2.08–6.875 / M tokens，仅在高 QPS 场景划算

**对比口径**：因为没有月度订阅所以"杠杆 = 1×"。一般放在表里只作 API 单价参照与新人额度参照。

---

## 3. 横向比较要点

1. **Zhipu 原厂的订阅套餐（BigModel/Z.ai）官方声称 15–30× 杠杆** —— 远高于阿里云 Token Plan 的 1.25–1.79×。原因：智谱的 Clients 计费口径是 prompt × calls × per-call token budget（每次调用含大上下文缓存读），而阿里云 Credits 与按量 API 价 1:1。两个口径无法直接比较，但**实际能省下的美元**以智谱更高。
2. **OpenCode Go $10 / $60 的 6× 杠杆**，比 Zhipu 原厂的"官方声明"更"诚实"——它直接按 API 价值算配额，因而是最稳的横向基准。
3. **配额真实可用量的最大变量 = 高峰/非高峰系数**：
   - 智谱族（BigModel/Z.ai）：3× 高峰 / 2× 非高峰 → 实际 prompts 数打 1/3 ~ 1/2 折
   - OpenCode Go：纯美元抵扣，不乘系数（GLM-5.2 单模型仅受 4,300 req/月硬约束）
   - 阿里云：1× 计费，无时段倍率
4. **OpenCode Go** 性价比上限最低（约 $60 API 价值 / 月），但**单价最便宜**（$5 试错），并包含 GLM-5.2/Kimi/Qwen3.7/DeepSeek 等 13 个模型，**适合"试用 + 多模型对照"场景**；Z.ai/BigModel Max 适合"单一 GLM 重度 Agent 跑批 24h"场景（20× Lite 配额）。
5. **阿里云 Token Plan**最大价值在团队管理后台和合规审计——若团队需多席位共享并管理预算，是唯一现成方案；纯粹算账不划算。
6. **SiliconFlow**：API 价与 Zhipu 原厂一致，且**新人 14 元** = ~17.7M mixed tokens 免费，可用作"无月费试水"的极简入口；长期重度使用没有套餐概念，按量付费吃满额度。

---

## 4. 数据来源

| 平台                         | 官方文档                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| 智谱 BigModel 工具套餐概览   | https://docs.bigmodel.cn/cn/coding-plan/overview                                           |
| 智谱 BigModel FAQ            | https://docs.bigmodel.cn/cn/coding-plan/faq                                                |
| 智谱 BigModel 速率限制       | https://docs.bigmodel.cn/cn/api/rate-limit                                                 |
| 智谱 上下文缓存              | https://docs.bigmodel.cn/cn/guide/capabilities/cache                                       |
| Z.ai Coding Plan 详情        | https://z.ai/subscribe · https://docs.z.ai/devpack/overview                                |
| Z.ai 定价                    | https://docs.z.ai/guides/overview/pricing                                                  |
| Z.ai Coding Plan FAQ         | https://docs.z.ai/devpack/faq                                                              |
| Z.ai 旧套餐迁移公告          | https://docs.z.ai/devpack/transition                                                       |
| OpenCode Go                  | https://opencode.ai/go · https://opencode.ai/docs/go/                                      |
| OpenCode Go 模型与单价       | https://opencode.ai/data/zhipuai/glm-5.2                                                   |
| 阿里云百炼 Token Plan 团队版 | https://help.aliyun.com/zh/model-studio/token-plan-overview                                |
| 阿里云百炼 GLM 系列调用      | https://help.aliyun.com/zh/model-studio/glm                                                |
| 阿里云百炼 模型调用价格      | https://help.aliyun.com/zh/model-studio/model-pricing                                      |
| 阿里云百炼 上下文缓存        | https://help.aliyun.com/zh/model-studio/context-cache                                      |
| 阿里云百炼 GLM-5.2 上线公告  | https://developer.aliyun.com/article/1742456                                               |
| SiliconFlow 价格页           | https://siliconflow.cn/pricing · https://cloud-rd.siliconflow.cn/pricing                   |
| SiliconFlow GLM-5.2 模型页   | https://www.siliconflow.com/zh/models/glm-5-2                                              |
| 智谱标准定价核实(博客)       | https://www.cnblogs.com/AlayaNeW/articles/20726255 (输入¥8/输出¥28/缓存¥2)                 |
| 第三方聚合定价参考           | https://www.aipricing.guru/z-ai-subscription-pricing/ · https://codingplan.org/plans/zhipu |

