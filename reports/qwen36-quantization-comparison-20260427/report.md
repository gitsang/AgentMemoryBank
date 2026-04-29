# Qwen3.6 / Qwen3.5 系列主要量化方式对比

> 日期：2026-04-27  
> 说明：公开资料里 “Qwen3.6” 多数与 Qwen3.5/Qwen3.5-MoE 架构、社区衍生权重和 Qwen3 官方量化栈一起讨论。下面按当前可见主流方式整理；“Apex、Unsloth”更准确地说是量化策略/发行工具链，AWQ、GPTQ、GGUF K-quants、FP8/NVFP4/MXFP4、bitsandbytes NF4 等才是算法或格式层面的概念。

## 一句话选型

- **本地个人使用 / Ollama / LM Studio / llama.cpp**：优先 **GGUF**，通常从 `Q4_K_M / Q4_K_XL / IQ4_XS` 起步；显存紧张看 `IQ3_* / Q3_K_*`。
- **Qwen3.5/3.6 MoE 本地高质量压缩**：优先看 **Unsloth Dynamic GGUF** 或 **APEX GGUF**；它们都不是简单全层同位宽量化，而是根据张量敏感性做混合精度。
- **GPU 服务 / vLLM / SGLang 高吞吐**：优先 **AWQ INT4** 或 **FP8**；官方 Qwen benchmark 显示 SGLang 下 Qwen3 dense 模型 FP8/AWQ 通常明显快于 BF16。
- **GPU 服务且希望 GPTQ-Marlin 内核**：可选 **GPTQ INT4/INT8**，但 MoE 与不同框架兼容性要实测。
- **微调 / QLoRA**：优先 **Unsloth 4-bit safetensors / bitsandbytes NF4**；目标是省显存训练，不是最终生产推理格式。
- **超长上下文显存瓶颈**：关注 **KV cache 量化/压缩**，如 llama.cpp 的 KV quant、TurboQuant/quant.cpp；它和权重量化是两件事，可以叠加。

## 主流方式对比

| 方式 / 工具链 | 本质 | 核心目标 | 核心优势 | 局限 / 风险 | 典型场景 |
|---|---|---|---|---|---|
| **GGUF / llama.cpp K-quants** (`Q8_0`, `Q6_K`, `Q5_K_M`, `Q4_K_M`, `Q3_K_M`, `IQ*`) | 本地推理格式 + 多种权重量化类型 | 让大模型在 CPU、Apple Silicon、单卡/混合 RAM+VRAM 上跑起来 | 生态最广：llama.cpp、Ollama、LM Studio；可 CPU/GPU 混合；量化档位丰富 | 吞吐通常不如专用 GPU serving；不同上传者校准集差异很大 | 个人本地、低成本部署、边缘设备 |
| **Unsloth Dynamic 2.0 GGUF** | 基于 GGUF 的动态/混合精度量化发行 | 用更小文件尽量保持真实任务能力 | 针对 Qwen3/3.5 做大量 KLD/PPL 实验；强调 imatrix、长上下文、代码、工具调用校准；有 2/3/4/5/6/8-bit 多档 | 仍依赖 llama.cpp/GGUF 生态；低 bit 会有速度/质量取舍；官方指标也提示 PPL/KLD 不等于真实任务表现 | 本地高质量 GGUF，尤其 Qwen3/3.5 MoE |
| **APEX / apex-quant** | MoE-aware mixed precision GGUF 策略 | 针对 MoE，把专家层/共享专家/注意力等按敏感性分配不同精度 | 对 Qwen3.5-35B-A3B 这类 MoE 设计：边缘层高精度、中间层更激进压缩；用 stock llama.cpp，无需自定义内核 | 当前主要是社区方法；重点覆盖 MoE；跨模型泛化需要实测 | Qwen3.5/3.6 35B-A3B 等 MoE 的本地 GGUF 高质量压缩 |
| **AWQ / AutoAWQ** | Activation-aware weight-only INT4 | 面向推理的低比特 GPU 友好量化 | Qwen 文档推荐方向之一；vLLM/SGLang/Transformers 支持；AutoAWQ 宣称相对 FP16 约 3x 加速、3x 省内存；SGLang 可用 awq_marlin 后端 | 需要校准集；Qwen3.5 混合架构/MTP/视觉/线性注意力可能需要跳过或特殊处理；AutoAWQ 版本兼容要注意 | GPU serving、vLLM/SGLang、高吞吐 INT4 |
| **GPTQ / AutoGPTQ / GPTQModel** | 近似二阶信息的一次性权重量化，常见 INT4/INT8 | 在低比特下尽量降低权重量化误差，并利用 Marlin 等内核 | GPTQ-Marlin 在支持场景下吞吐好；Qwen 官方 benchmark 覆盖 GPTQ；部分 MTP 场景社区认为 GPTQ 比 AWQ 保留更好 | AutoGPTQ 维护状态与新模型支持需注意；官方 Qwen benchmark 提到 GPTQ-INT4 在 SGLang 的性能仍需改进，MoE 在 Transformers 下可能 kernel unsupported | GPU INT4/INT8 serving、需要 GPTQ-Marlin 的部署 |
| **FP8** | 8-bit 浮点权重/计算或压缩格式 | 在质量接近 BF16 的前提下降低显存、提高吞吐 | Qwen 官方 benchmark 显示 SGLang 下 Qwen3 dense/MoE FP8 通常速度优于 BF16，且显存更低；比 INT4 更稳健 | Transformers FP8 性能官方提示尚不理想；硬件/框架版本依赖强 | H100/H20/新 GPU 上的生产 serving、较保守压缩 |
| **NVFP4 / MXFP4 / FP4 via vLLM llm-compressor** | 4-bit 浮点/微缩放格式，常见 W4A16 | 面向新 GPU / serving 栈的更激进压缩 | vLLM llm-compressor 已有 Qwen3.5 示例；可保存 compressed-tensors；适合和 vLLM 生态衔接 | Qwen3.5 混合架构需跳过 visual、linear_attn、MTP 等模块；Unsloth 基准中 MXFP4 对部分张量并不总是优于 Q4_K | 新硬件实验、vLLM 生态、追求更低显存 |
| **bitsandbytes NF4 / Unsloth 4-bit safetensors** | 训练/QLoRA 常用 4-bit 加载格式 | 让微调/RL 在低显存上可行 | Unsloth 宣称 Qwen3 微调 2x faster、70% less VRAM、8x longer context；Qwen3 14B 可在 16GB T4 上 fine-tune | 主要服务训练/微调，不一定是最终推理最优格式；MoE 4-bit 导入/转换可能有额外限制 | LoRA/QLoRA、GRPO/RL 微调、低显存训练 |
| **INT8 / SmoothQuant / RTN / data-free quant** | 传统或通用 PTQ 方法 | 更稳妥降显存，或无需复杂校准 | INT8 通常质量损失小；SmoothQuant 对 W8A8 类推理友好；data-free AWQ 方便快速发布 | 压缩率不如 INT4/FP4；不同框架支持差异大 | 保守压缩、没有高质量校准集、企业兼容性优先 |
| **KV cache 量化/压缩** (`q8_0`, `q4_0`, TurboQuant, quant.cpp) | 推理时 KV 缓存压缩，不改或少改权重 | 超长上下文下降低运行时显存 | 可与权重量化叠加；对 128K/1M 上下文尤其关键；TurboQuant/quant.cpp 主打 4x+ KV 压缩 | 运行时/框架支持分裂；TurboQuant 等未必进入上游 llama.cpp/vLLM | 长上下文、多轮对话、RAG、Agent 记忆 |

## 关键差异：不要混淆 4 个维度

1. **量化对象**：权重量化（GGUF/AWQ/GPTQ/FP8/NVFP4） vs KV-cache 量化（长上下文运行时内存）。
2. **目标环境**：GGUF 偏本地和混合 RAM/VRAM；AWQ/GPTQ/FP8 偏 GPU serving；NF4/bnb 偏训练微调。
3. **算法 vs 工具链**：AWQ/GPTQ/NF4/FP8 是算法或数值格式；Unsloth/APEX/AutoAWQ/llm-compressor 是工具链或策略；Ollama/LM Studio/vLLM/SGLang 是运行时。
4. **Qwen3.5/3.6 架构敏感性**：MoE、Gated DeltaNet/SSM、MTP、视觉塔、attention 张量对低比特并不等价；好的量化通常会跳过或提高这些敏感模块的精度。

## 推荐档位

- **质量优先**：FP8、Q8_0、Q6_K、APEX Quality、Unsloth UD-Q6/Q8。
- **平衡优先**：AWQ INT4、GPTQ INT4、Q4_K_M、Unsloth UD-Q4_K_XL、APEX Balanced/Compact。
- **显存极限**：IQ3_XXS、Q3_K_M、UD-Q2_K_XL、APEX Mini；但建议按任务集实测。
- **微调**：Unsloth/bnb 4-bit；最终上线再转 GGUF/AWQ/GPTQ/FP8。

## 资料来源

- Qwen 官方 Speed Benchmark：`https://qwen.readthedocs.io/en/latest/getting_started/speed_benchmark.html`
- Qwen 官方 AWQ 文档：`https://qwen.readthedocs.io/en/latest/quantization/awq.html`
- Qwen 官方 GPTQ 文档：`https://qwen.readthedocs.io/en/latest/quantization/gptq.html`
- Qwen 官方 quantization benchmark：`https://qwen.readthedocs.io/en/latest/getting_started/quantization_benchmark.html`
- Unsloth Qwen3 run/fine-tune：`https://unsloth.ai/docs/models/tutorials/qwen3-how-to-run-and-fine-tune.md`
- Unsloth Qwen3.5 GGUF benchmark：`https://unsloth.ai/docs/models/qwen3.5/gguf-benchmarks`
- APEX quant GitHub：`https://github.com/mudler/apex-quant`
- APEX Qwen3.5 HF：`https://huggingface.co/mudler/Qwen3.5-35B-A3B-APEX-GGUF`
- vLLM llm-compressor Qwen3.5：`https://docs.vllm.ai/projects/llm-compressor/en/latest/key-models/qwen3.5/`
- TurboQuant Qwen3.6 HF：`https://huggingface.co/majentik/Qwen3.6-35B-A3B-TurboQuant`
