# 苹果 A19 系列 CPU vs Intel CPU 性能对比

> 研究日期：2026-07
> 数据来源：Geekbench 6 官方榜单（browser.geekbench.com）、Nanoreview、Tom's Hardware、Tom's Guide
> 全部为实测数据（A19 系列随 iPhone 17 于 2025 年秋季发布，已有实测）。

## 一、A19 系列 CPU 规格

A19 系列全部 6 核（2 性能核 Everest @ 4.26 GHz + 4 能效核 Sawtooth @ 2.6 GHz），3nm（TSMC N3P）：

| 型号 | 机型 | L2 缓存 | 系统缓存 | 内存 |
|---|---|---|---|---|
| **A19 Pro** | iPhone 17 Pro / Pro Max | 16MB+6MB | 32MB | 12GB LPDDR5X-9600 |
| A19 Pro（降配） | iPhone Air | 16MB+6MB | 32MB | 12GB LPDDR5X-9600 |
| A19 | iPhone 17 | 8MB+4MB | 12MB | 12GB LPDDR5X-8533 |
| A19（入门） | iPhone 17e | 8MB+4MB | 12MB | 8GB LPDDR5X-8533 |

> A19 与 A19 Pro 的 CPU 核心/频率相同，差异主要在缓存、GPU、NPU 和内存带宽。

## 二、Geekbench 6 实测跑分对比

### 单核性能（Single-Core）

| 芯片 | Geekbench 6 单核 | 核心数 | 功耗 | 备注 |
|---|---|---|---|---|
| **Apple A19 Pro** | **~3,770–3,786** | 6 | ~3–8W | iPhone 17 Pro 实测 |
| **Apple A19** | **~3,607–3,608** | 6 | ~3–8W | iPhone 17 实测 |
| Apple A18 Pro（上代） | ~3,444 | 6 | ~3–8W | 参考 |
| Intel Core Ultra 9 285K（桌面旗舰） | ~3,195–3,379 | 24 | 125W | Intel 桌面单核王 |
| Intel Core Ultra 9 285HX（移动旗舰） | ~3,088–3,124 | 24 | 45–160W | Intel 移动单核王 |
| Intel Core Ultra 7 265K | ~3,062 | 20 | 125W | 桌面 |
| Intel Core i9-14900K（上代桌面旗舰） | ~3,063 | 24 | 125W | |
| Intel Core Ultra 9 275HX | ~2,798–2,799 | 24 | 45–160W | 移动 |
| Intel Core Ultra 9 285H | ~2,598–2,665 | 16 | 28–45W | 移动 |
| Intel Core Ultra 7 255H | ~2,489 | 16 | 28W | 移动 |
| Intel Core Ultra 5 225H | ~2,386 | 14 | 28W | 移动 |

**结论（单核）：A19 和 A19 Pro 的单核均超过目前所有 Intel 桌面/移动 CPU。**
- A19 Pro（~3,770）比 Intel 最强单核 285K（~3,195–3,379）高约 **12%–18%**
- A19（~3,607）比 285K 高约 **7%–13%**
- 功耗仅为 Intel 桌面的 **1/15–1/25**

### 多核性能（Multi-Core）

| 芯片 | Geekbench 6 多核 | 核心数 | 功耗 | 备注 |
|---|---|---|---|---|
| **Apple A19 Pro** | **~9,807–9,839** | 6 | ~3–8W | |
| **Apple A19** | **~9,246–9,247** | 6 | ~3–8W | |
| Intel Core Ultra 9 285K | ~22,472–23,095 | 24 | 125W | |
| Intel Core Ultra 9 285HX | ~21,043–22,215 | 24 | 45–160W | |
| Intel Core Ultra 7 265K | ~20,500–20,503 | 20 | 125W | |
| Intel Core Ultra 9 275HX | ~17,784–17,788 | 24 | 45–160W | |
| Intel Core Ultra 9 285H | ~14,707–15,330 | 16 | 28–45W | |
| Intel Core Ultra 7 255H | ~13,114 | 16 | 28W | |
| Intel Core Ultra 5 225H | ~11,579 | 14 | 28W | ← A19 多核最接近的 Intel 型号 |

**结论（多核）：受限于 6 核，A19/A19 Pro 多核 ~9,200–9,800，无法追平 Intel 20+ 核旗舰（2 万+），差距约 2 倍。**
- A19 Pro 多核最接近 Intel **Core Ultra 5 225H**（14 核，~11,579），但仍低约 15%–18%
- A19 多核同样接近 225H，低约 20%
- 但功耗仅为 225H（28W）的 **1/4–1/6**

## 三、综合结论

### A19 / A19 Pro 相当于哪款 Intel CPU？

| 维度 | 对标 Intel CPU | 说明 |
|---|---|---|
| **单核性能** | **超过 Intel 全线**（含桌面旗舰 Core Ultra 9 285K） | A19 Pro 领先 12%–18%，A19 领先 7%–13% |
| **多核性能** | **略低于 Intel Core Ultra 5 225H**（中端移动 14 核） | A19 Pro ~9,800 vs 225H ~11,579，差距 15%–18% |
| **能效（Per Watt）** | **远超 Intel 全线** | ~5W vs 28–125W，每瓦性能约 Intel 的 10–25 倍 |

### 关键解读

1. **单核已是手机 SoC 反超 x86 的延续**：A19 系列单核全面超过 Intel 桌面旗舰，这是自 A17 Pro 起延续的趋势。相比上代 A18 Pro（~3,444），A19 Pro 单核提升约 9%–10%，多核提升约 13%–15%。

2. **多核天花板由核心数决定**：6 核 vs Intel 14–24 核，多核差距是物理结构性的。桌面/工作站重负载（编译、渲染、视频转码）Intel 仍占优。

3. **能效碾压是手机芯片的核心价值**：A19 Pro 在 ~5W 达到 Intel 125W 芯片的单核水平，每瓦性能约 15–25 倍。这是 3nm + ARM + 苹果自研核心的成果。

4. **A19 vs A19 Pro 的 CPU 差异很小**：两者 CPU 核心和频率完全相同，主要差在缓存（L2/SLC）和内存带宽。单核差距约 4%，多核约 6%。买 Pro 主要是为 GPU/NPU/相机，而非 CPU。

5. **数据为实测**：与 A20 Pro（预测值）不同，A19 系列已有大量 Geekbench 实测样本，数据可靠。

## 四、与前序报告的关系

| 报告 | 芯片 | 单核 | 多核 | 数据状态 |
|---|---|---|---|---|
| 本报告 | A19 / A19 Pro | ~3,607 / ~3,770 | ~9,246 / ~9,807 | ✅ 实测 |
| A20 Pro 报告 | A20 Pro | ~4,200（预测） | ~10,000+（预测） | ⚠️ 预测（未发布） |

A20 Pro 相比 A19 Pro 预计单核再提升约 11%（2nm 工艺红利），多核提升约 2%–5%。

## 五、数据来源

- Geekbench Browser 官方榜单：iPhone 17 Pro / iPhone 17 / iPhone 16 实测
- Nanoreview: A19 Pro vs A19 vs A17 Pro
- Tom's Hardware: A19 Pro beats Ryzen 9 9950X single-thread（含 A19/A18 Pro/A17 Pro 对比表）
- Tom's Guide: iPhone 17 Pro benchmarks
- Nanoreview / Geekbench: Intel Core Ultra 9 285K / 285HX / 285H / 265K 等
