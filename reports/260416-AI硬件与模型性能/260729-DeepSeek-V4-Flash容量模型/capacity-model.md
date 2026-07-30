# DeepSeek-V4-Flash 企业 Agent 推理容量模型

## 1. 文档目的

本文给出一个统一的容量计算方法，用于判断企业 Agent、知识问答和 RAG 场景中的主要瓶颈究竟来自：

- Prefill 算力；
- HBM 显存容量；
- HBM 显存带宽；
- DRAM / SSD Cache 恢复；
- Decode 吞吐；
- NVLink / PCIe / 网络通信；
- 排队和外部检索延迟。

核心原则是：**不能把在线会话数、HTTP 并发数、Prefill 并发数、Decode 并发数和 HBM 驻留会话数视为同一个“并发”指标。**

容量规划应基于实际未缓存 token、热 KV 工作集和输出 token 速率。

---

## 2. 统一判断公式

把每种资源的压力归一化到 `0-1`，最终取最大值：

\[
\boxed{
\rho = \max\left(
\rho_{\text{TTFT}},
\rho_{\text{HBM}},
\rho_{\text{Decode}},
\rho_{\text{Link}}
\right)
}
\]

判断建议：

| 总压力 `ρ` | 状态 | 工程含义 |
|---:|---|---|
| `< 0.60` | 余量充分 | 通常能承受一定突发流量 |
| `0.60-0.80` | 关注区 | P95 / P99 延迟开始敏感 |
| `0.80-1.00` | 临界区 | 容易因突发、淘汰或碎片触发 SLO 违约 |
| `> 1.00` | 超载 | 容量不足或无法满足目标 SLO |

最大的压力项就是当前主要瓶颈。

> 对严格 P99 SLO 的在线服务，不应把目标稳定利用率设置在 100%。通常应保留 20%-40% 的容量余量。

---

## 3. 请求级变量

对一个调度窗口中的每个请求 `i`，定义：

| 变量 | 含义 |
|---|---|
| `L_i` | 请求总上下文 token 数 |
| `H_i` | 成功复用的连续 prefix token 数 |
| `Δ_i = L_i - H_i` | 真正需要重新 Prefill 的 token 数 |
| `L_i^resident` | 当前驻留 HBM 的上下文 token 数 |
| `R_{i,t}` | 从 Cache 层级 `t` 恢复的 KV 字节数 |
| `O_i` | 预计生成的输出 token 数 |
| `A_i` | 请求是否处于活跃 Decode 状态 |

Cache 层级 `t` 通常包括：

- `HBM`：GPU 显存；
- `DRAM`：主机内存；
- `SSD`：本地或远端持久化缓存；
- `MISS`：没有可用 KV，需要重新 Prefill。

真正影响 Prefill 算力的不是总上下文：

\[
L_i
\]

而是未缓存后缀：

\[
\Delta_i = L_i - H_i
\]

一个调度窗口内的总未缓存输入为：

\[
\boxed{
N_{\text{new}} = \sum_{i \in B} \Delta_i
}
\]

这里的 `B` 是同一个调度窗口内真正进入 Prefill 的请求集合，不是所有在线会话。

---

## 4. TTFT 压力

### 4.1 Prefill 计算时间

一阶近似下，MoE 模型每个输入 token 的前向计算量为：

\[
F_{\text{token}} \approx 2P_{\text{active}}
\]

一个批次的 Prefill 计算时间为：

\[
\boxed{
T_{\text{prefill}}
=
\frac{
2P_{\text{active}}N_{\text{new}} + F_{\text{attention}}
}
{
\eta F_{\text{peak}}(1-u_D)
}
}
\]

变量说明：

| 变量 | 含义 |
|---|---|
| `P_active` | 每 token 激活参数量 |
| `F_attention` | CSA / HCA / MLA 等注意力额外计算量 |
| `F_peak` | GPU 集群理论峰值算力 |
| `η` | 模型、量化、内核、调度共同决定的有效效率 |
| `u_D` | 当前被 Decode 占用的计算 / 带宽比例 |

第一版估算可以忽略 `F_attention`，再使用真实压测数据修正 `η`。对于 H20 在线推理，建议初始使用 `η = 0.2-0.4`，不要直接使用 100% 峰值。

### 4.2 Cache 恢复时间

Cache 命中会减少 Prefill，但 DRAM 和 SSD 命中不等于零延迟：

\[
\boxed{
T_{\text{restore}}
=
\sum_t
(1-\theta_t)
\frac{
\sum_i R_{i,t}
}
{BW_t}
}
\]

| 变量 | 含义 |
|---|---|
| `BW_t` | Cache 层级的实际有效带宽 |
| `θ_t` | Cache 恢复与 GPU 计算的重叠比例，范围 `0-1` |

- `θ_t = 0`：完全不能重叠，恢复时间全部进入 TTFT；
- `θ_t = 1`：恢复完全隐藏在计算后面；
- HBM 命中通常不需要跨设备恢复；
- SSD 应使用真实随机 I/O 和碎片化读取带宽，不能直接套用顺序读取峰值。

### 4.3 端到端 TTFT

\[
\boxed{
T_{\text{TTFT}}
=
T_{\text{retrieval}}
+T_{\text{rerank}}
+T_{\text{queue}}
+T_{\text{restore}}
+T_{\text{prefill}}
+T_{\text{framework}}
}
\]

归一化 TTFT 压力：

\[
\boxed{
\rho_{\text{TTFT}}
=
\frac{T_{\text{TTFT}}}{T_{\text{SLO}}}
}
\]

如果 `ρ_TTFT > 1`，即使显存仍有大量余量，也无法满足 TTFT SLO。

---

## 5. HBM 容量压力

总 HBM 占用可以写成：

\[
M_{\text{total}}
=
M_{\text{weights}}
+M_{\text{runtime}}
+M_{\text{KV}}
\]

KV 占用为：

\[
M_{\text{KV}}
=
K
\left(
\sum_i L_i^{\text{resident}}
-L_{\text{shared}}
\right)
\]

因此：

\[
\boxed{
\rho_{\text{HBM}}
=
\frac{
M_{\text{weights}}
+M_{\text{runtime}}
+K\left(\sum_i L_i^{\text{resident}}-L_{\text{shared}}\right)
}
{M_{\text{HBM}}}
}
\]

变量说明：

| 变量 | 含义 |
|---|---|
| `K` | 每 token KV 字节数 |
| `L_resident` | 实际驻留 HBM 的热上下文 |
| `L_shared` | Radix / Prefix Cache 真正共享掉的 token |
| `M_runtime` | CUDA Graph、激活、工作区、碎片和框架预留 |

已经 offload 到 DRAM / SSD 的会话不计入 HBM KV，但重新激活时必须计入 `T_restore`。

---

## 6. Decode 与通信压力

Decode 的瓶颈会随 batch size 改变：

- 小 batch 通常更偏 HBM 带宽瓶颈；
- batch 增大后权重复用增加，可能转为 Tensor 算力瓶颈；
- MoE 模型还可能先撞到专家路由和 All-to-All 通信瓶颈。

Decode 压力建议使用真实 benchmark：

\[
\boxed{
\rho_{\text{Decode}}
=
\max\left(
\frac{\lambda_{\text{out}}}{\mu_{\text{decode}}},
\frac{B_{\text{decode}}}{BW_{\text{HBM}}},
\frac{B_{\text{MoE}}}{BW_{\text{NVLink}}}
\right)
}
\]

| 变量 | 含义 |
|---|---|
| `λ_out` | 业务要求的输出 token/s |
| `μ_decode` | 目标模型、上下文、batch 下的实测输出 token/s |
| `B_decode` | Decode 所需 HBM 读取字节/s |
| `B_MoE` | 专家并行通信字节/s |

其他链路压力可以表示为：

\[
\boxed{
\rho_{\text{Link}}
=
\max_t
\frac{B_t}{BW_t}
}
\]

---

## 7. 4×H20 + DeepSeek-V4-Flash 代入公式

### 7.1 硬件和模型假设

| 项目 | 数值 |
|---|---:|
| GPU 数量 | 4× NVIDIA H20 |
| 单卡 HBM | 141GB |
| 总 HBM | 564GB |
| 单卡 FP8 峰值 | 296 TFLOPS |
| 集群 FP8 峰值 | 1.184 PFLOPS |
| 模型总参数 | 284B |
| 每 token 激活参数 | 13B |
| Hopper FP8 权重估算 | 约 284GB |
| 最大上下文 | 1,048,576 tokens |
| TTFT SLO | 10s |

4×H20 无法部署 BF16 权重：

\[
284B \times 2\text{ bytes} \approx 568GB
\]

这已经超过 564GB 总 HBM，且尚未包含 KV、激活和运行时。因此本文的“满参数版”指完整 284B 参数的 Hopper FP8 checkpoint，不是 BF16，也不是蒸馏或裁剪版本。

### 7.2 Prefill 简化公式

4×H20 理论输入 token 吞吐上限：

\[
\frac{1.184\times10^{15}}{2\times13\times10^9}
\approx 45,538\text{ tokens/s}
\]

因此：

\[
\boxed{
T_{\text{prefill}}
\approx
\frac{
N_{\text{new}}
}
{
45,538\eta(1-u_D)
}
}
\]

反推允许的未缓存 token：

\[
\boxed{
N_{\text{new,max}}
=
45,538\eta(1-u_D)T_{\text{GPU-budget}}
}
\]

其中：

\[
T_{\text{GPU-budget}}
=
T_{\text{SLO}}
-T_{\text{retrieval}}
-T_{\text{rerank}}
-T_{\text{queue}}
-T_{\text{restore}}
-T_{\text{framework}}
\]

### 7.3 HBM 简化公式

DeepSeek-V4-Flash BF16 KV 的一阶估算为：

\[
K\approx 6,881\text{ bytes/token}
\]

假设：

- 总 HBM：564GB；
- 静态显存利用率：85%；
- FP8 权重：284GB；
- 运行时额外预留：约 15.4GB；
- 最终留给 KV：约 180GB。

则 BF16 KV 热 token 上限：

\[
\boxed{
N_{\text{hot,max}}
=
\frac{180\times10^9}{6,881}
\approx26.2M\text{ tokens}
}
\]

对应压力：

\[
\boxed{
\rho_{\text{HBM}}
\approx
\frac{N_{\text{hot}}}{26.2M}
}
\]

若使用优化 FP8 / FP4 KV，容量可近似翻倍：

\[
N_{\text{hot,max}}\approx52.3M\text{ tokens}
\]

实际值必须以目标推理引擎的 KV allocator 和模型启动日志为准。

---

## 8. 完整计算示例

假设一个知识问答调度窗口中：

- 10 个逻辑会话提交请求；
- 每个请求总上下文 128K；
- 95% prefix token 命中；
- 每个请求实际新增约 6.4K token；
- 有效算力效率 `η = 0.30`；
- Decode 占用 `u_D = 0.25`；
- TTFT 目标为 10s；
- 检索、排队、框架等共消耗 3s；
- 留给 GPU 的时间为 7s。

总未缓存输入：

\[
N_{\text{new}}=10\times6.4K=64K
\]

Prefill 时间：

\[
T_{\text{prefill}}
=
\frac{64,000}
{45,538\times0.30\times0.75}
\approx6.25s
\]

端到端 TTFT：

\[
T_{\text{TTFT}}
\approx3+6.25=9.25s
\]

TTFT 压力：

\[
\rho_{\text{TTFT}}=9.25/10=0.925
\]

如果 10 个会话都将 128K KV 驻留 HBM：

\[
N_{\text{hot}}=10\times128K=1.28M
\]

HBM 压力：

\[
\rho_{\text{HBM}}
=1.28M/26.2M
\approx0.049
\]

最终：

\[
\rho=\max(0.925,0.049,\rho_{\text{Decode}},\rho_{\text{Link}})
\]

如果 Decode 和通信压力都低于 0.925，则该工作负载明显属于 **Prefill / TTFT 算力瓶颈**，而不是显存瓶颈。

---

## 9. Excel / 表格版公式

可以直接在容量评估表中使用：

```text
NewTokens = SUM(总上下文Token - 命中PrefixToken)

GpuTimeBudget =
    TTFT_SLO
  - RetrievalTime
  - RerankTime
  - QueueTime
  - RestoreTime
  - FrameworkTime

PrefillTime =
    NewTokens
  / (45538 * EffectiveEfficiency * (1 - DecodeUtilization))

RestoreTime =
    DramRestoreBytes / EffectivePcieBandwidth
  + SsdRestoreBytes / EffectiveSsdBandwidth

TtftPressure =
    (RetrievalTime
     + RerankTime
     + QueueTime
     + RestoreTime
     + PrefillTime
     + FrameworkTime)
  / TtftSlo

HbmPressure =
    (WeightBytes
     + RuntimeBytes
     + ResidentKvBytes
     - SharedKvBytes)
  / TotalHbmBytes

DecodePressure =
    RequiredOutputTokensPerSecond
  / MeasuredDecodeTokensPerSecond

TotalPressure =
    MAX(TtftPressure, HbmPressure, DecodePressure, LinkPressure)
```

4×H20 + V4-Flash 的快捷形式：

```text
PrefillTimeSeconds =
    NewTokens / (45538 * Efficiency * (1 - DecodeUtilization))

HbmPressureBf16Kv =
    HotResidentTokens / 26157924

TotalPressure =
    MAX(TtftPressure, HbmPressureBf16Kv, DecodePressure, LinkPressure)
```

---

## 10. 必须采集的线上指标

仅有 `prompt_tokens` 和总请求并发不足以完成容量规划。至少需要记录：

| 指标 | 用途 |
|---|---|
| `prompt_tokens_total` | 请求总输入长度 |
| `prefill_tokens_uncached` | 真正需要计算的新 token |
| `prefix_hit_tokens_hbm` | HBM 命中 token |
| `prefix_hit_tokens_dram` | DRAM 命中 token |
| `prefix_hit_tokens_ssd` | SSD 命中 token |
| `kv_restore_bytes_by_tier` | 分层恢复流量 |
| `kv_restore_latency_by_tier` | 分层恢复延迟 |
| `concurrent_prefills` | 实际 Prefill 并发，而非在线会话数 |
| `concurrent_decodes` | 实际 Decode 并发 |
| `resident_kv_tokens` | HBM 热 KV 工作集 |
| `shared_prefix_tokens` | 真正被共享的 KV |
| `cache_eviction_tokens` | Cache 淘汰规模 |
| `output_tokens` | 输出及 Thinking token 长度 |
| `ttft_queue_ms` | 排队耗时 |
| `ttft_retrieval_ms` | 检索和 Rerank 耗时 |
| `ttft_prefill_ms` | GPU Prefill 耗时 |
| `tpot_ms` / `itl_ms` | Decode 体验 |
| `nvlink_bytes_per_second` | MoE / TP 通信压力 |

容量规划应关注 P95 / P99 分布，特别是：

\[
P99\left(\sum_i\Delta_i\right)
\]

即一个调度窗口内同时出现的未缓存 token 总量，而不是日均 cache 命中率。

---

## 11. 使用边界与注意事项

1. 该公式是资源容量模型，不是对具体推理引擎的周期级仿真。
2. `η` 必须通过真实模型、量化、TP / EP 配置和请求分布压测获得。
3. Attention、MoE 路由、CUDA Graph、采样和通信开销会被吸收到 `η` 或独立修正项中。
4. Prefix Cache 通常要求 token 前缀完全一致，语义相似不等于 KV 命中。
5. 文档 KV 不能默认在任意位置拼接；位置编码和前序上下文可能使其失效。
6. DRAM / SSD 命中只省计算，不保证低 TTFT；必须计算恢复字节和有效带宽。
7. 平均命中率无法代表突发行为，应使用调度窗口内的 P95 / P99 未缓存 token。
8. 当资源利用率接近 100% 时，排队延迟会非线性增长，因此生产目标应保持在 `ρ < 0.6-0.8`。
9. 如果采用 Prefill / Decode 分离，必须额外计算 KV 传输、路由和双份模型权重成本。
10. 本文中的 KV 字节数和 FP8 权重大小是容量规划估算，最终应以目标 runtime 启动日志和显存快照校准。

---

## 12. 配套瓶颈图

![4×H20 部署 DeepSeek-V4-Flash 的算力墙与显存墙](../../../artifacts/deepseek_v4_flash_4xh20_bottleneck.png)

图中：

- 绿色线：20% 有效效率下的 TTFT 算力墙；
- 蓝色线：40% 有效效率下的 TTFT 算力墙；
- 蓝色虚线：100% 理论峰值上限；
- 红色线：保守 BF16 KV 显存墙；
- 红色虚线：优化 FP8 / FP4 KV 显存墙。

该图是“同一个调度窗口内同时进入 Prefill”的压力图，不应把纵轴直接理解为全部在线会话数。

---

## 13. 参考资料

- 用户提供的 NVIDIA H20 / H200 / B200 性能规格表。
- DeepSeek-V4 Technical Report: <https://arxiv.org/abs/2606.19348>
- DeepSeek-V4-Flash config: <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json>
- vLLM DeepSeek-V4 serving notes: <https://vllm.ai/blog/2026-04-24-deepseek-v4>

