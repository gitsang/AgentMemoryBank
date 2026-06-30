---
name: comfyui
description: 使用自然语言控制 ComfyUI 服务器生成图片和视频。支持文生图、图生图、工作流管理等功能。
---

# ComfyUI 技能

通过命令行控制远程 ComfyUI 服务器，生成图片、视频，管理工作流。

## 使用前提

### 必需依赖

1. **uv** - Python 包管理工具
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **comfy-cli** - ComfyUI 命令行工具
   ```bash
   uv tool install comfy-cli
   ```

### 初始化

首次使用前，运行初始化命令：

```
/comfyui init
```

初始化流程：
1. 检查 uv 和 comfy-cli 是否安装
2. 询问 ComfyUI 服务器地址
3. 测试连接
4. 获取可用模型列表
5. 写入配置文件
6. 确保 `.gitignore` 包含 `config.yml`（避免提交用户私密配置）

配置文件位置（按优先级读取）：
1. `./.agents/skills/comfyui/config.yml`（项目级，已被 .gitignore 忽略）
2. `~/.agents/skills/comfyui/config.yml`（全局级）

初始化时默认写入项目级配置。如果用户选择 `--global`，则写入全局级。

---

## 命令参考

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/comfyui init` | 初始化配置 | `/comfyui init` |
| `/comfyui status` | 查看服务器状态 | `/comfyui status` |
| `/comfyui model list` | 列出可用模型 | `/comfyui model list` |

### 生成命令

#### txt2img - 文生图

```
/comfyui txt2img <提示词> [选项]
```

示例：
```
/comfyui txt2img 一只猫坐在窗台上，阳光照射
/comfyui txt2img 赛博朋克城市 --batch 4 --width 1024 --height 768
/comfyui txt2img 动漫少女 --model Counterfeit-v2.5 --steps 30
```

#### img2img - 图生图

```
/comfyui img2img <提示词> --input <图片路径> [选项]
```

示例：
```
/comfyui img2img 油画风格 --input photo.jpg
/comfyui img2img 水彩画 --input ./images/drawing.png --strength 0.7
```

输入图片支持：
- 本地路径（自动上传到 ComfyUI）
- 远程文件名（已存在于 ComfyUI 服务器）

### 通用选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--batch N` | 生成数量 | 1 |
| `--model <name>` | 指定模型 | 配置文件中的默认值 |
| `--width N` | 宽度 | 512 |
| `--height N` | 高度 | 512 |
| `--steps N` | 步数 | 20 |
| `--cfg N` | CFG 缩放 | 7.0 |
| `--sampler <name>` | 采样器 | euler_a |
| `--seed N` | 随机种子 | -1（随机） |
| `--no-download` | 不下载结果 | - |
| `--async` | 异步模式，返回任务 ID | - |

### 工作流命令

#### 列出工作流

```
/comfyui workflow list
```

显示顺序：项目级 → 全局级 → 内置模板

#### 运行工作流

```
/comfyui workflow run <工作流名> [选项]
```

示例：
```
/comfyui workflow run my_flow --prompt "一只猫" --batch 4
```

#### 创建工作流

```
/comfyui workflow create <工作流名> [选项]
```

选项：
- `--global` - 创建到全局用户级
- `--from <模板名>` - 从模板创建

示例：
```
/comfyui workflow create my_batch_gen
/comfyui workflow create my_flow --global --from txt2img_basic
```

#### 编辑工作流

```
/comfyui workflow edit <工作流名>
```

#### 删除工作流

```
/comfyui workflow delete <工作流名>
```

---

## 配置说明

### 配置文件位置

按优先级读取：
1. `./.agents/skills/comfyui/config.yml`（项目级）
2. `~/.agents/skills/comfyui/config.yml`（全局级）

### 配置文件格式

```yaml
# ComfyUI 服务器配置
server:
  url: "http://your-server:8188"
  timeout: 300  # 超时时间（秒）

# 默认生成参数
defaults:
  checkpoint: null  # null 表示自动检测第一个可用模型
  width: 512
  height: 512
  steps: 20
  cfg: 7.0
  sampler: "euler_a"
  negative_prompt: "lowres, bad anatomy, worst quality, low quality"

# 输出配置
output:
  dir: "./comfyui-output"
  auto_download: true
  preview: "auto"  # auto | xdg-open | open | none

# 工作流配置
workflows:
  search_path:
    - "./.agents/skills/comfyui/workflows"  # 项目级
    - "~/.agents/skills/comfyui/workflows"  # 全局级
```

---

## 工作流管理

### 工作流格式

使用 ComfyUI API 格式（JSON），支持占位符变量：

```json
{
  "3": {
    "inputs": {
      "seed": "{{seed}}",
      "steps": "{{steps}}",
      "cfg": "{{cfg}}",
      "sampler_name": "{{sampler}}"
    }
  },
  "6": {
    "inputs": {
      "text": "{{prompt}}"
    }
  }
}
```

### 支持的占位符

| 占位符 | 替换为 |
|--------|--------|
| `{{prompt}}` | 用户输入的正向提示词 |
| `{{negative_prompt}}` | 负向提示词 |
| `{{width}}` | 宽度 |
| `{{height}}` | 高度 |
| `{{batch_size}}` | 批量数 |
| `{{steps}}` | 步数 |
| `{{cfg}}` | CFG 缩放 |
| `{{sampler}}` | 采样器 |
| `{{seed}}` | 随机种子 |
| `{{model}}` | 模型名 |

### 工作流存储位置

| 类型 | 路径 | 说明 |
|------|------|------|
| 内置模板 | `.agents/skills/comfyui/templates/` | 只读参考 |
| 项目级 | `./.agents/skills/comfyui/workflows/` | 可版本控制 |
| 全局级 | `~/.agents/skills/comfyui/workflows/` | 跨项目共享 |

---

## Agent 执行流程

### 初始化检查

每次执行命令前：
1. 检查配置文件是否存在
2. 如果不存在，提示用户运行 `/comfyui init`

### 生成图片

```
用户: /comfyui txt2img 一只猫 --batch 4
Agent:
1. 读取配置文件
2. 合并参数：用户参数 + 默认参数
3. 构建 comfy-cli 命令
4. 执行生成
5. 下载结果（如果 auto_download: true）
6. 预览图片（根据 preview 配置）
```

### 图片预览

`output.preview` 配置控制生成完成后如何打开图片：

| 值 | 行为 |
|------|------|
| `feh` | 用 `feh <path>` 打开（推荐 Linux + X11 环境） |
| `xdg-open` | 用系统默认程序打开 |
| `open` | macOS 默认程序 |
| `auto` | 自动检测：优先 feh，其次 xdg-open |
| `none` | 不预览 |

Agent 在下载图片后，根据该配置执行预览命令，例如：
```bash
feh ./comfyui-output/flux_cat.png
```

如果需要查看已有图片内容（用于判断生成效果、调整提示词），也可主动调用 `feh` 打开本地图片，或调用 multimodal-looker 读取图片描述。

### comfy-cli 命令构建

#### txt2img 示例

```bash
# 基础命令
comfy run txt2img_basic.json \
  --server http://your-server:8188 \
  --output ./comfyui-output

# 带参数
comfy run txt2img_basic.json \
  --server http://your-server:8188 \
  --output ./comfyui-output \
  -- --prompt "一只猫" --batch_size 4
```

#### img2img 示例

```bash
# 先上传图片
python scripts/upload_image.py photo.jpg

# 再运行工作流
comfy run img2img_basic.json \
  --server http://your-server:8188 \
  --output ./comfyui-output
```

---

## 进度显示

### 默认模式（阻塞）

```
⏳ 正在提交工作流...
⏳ 生成中... (预计 30 秒)
✅ 完成! 已保存到 ./comfyui-output/img_001.png
```

### 异步模式（--async）

```
/comfyui txt2img 猫 --async
# 返回: task_id: abc123

/comfyui status abc123
# 返回: 生成中... 步数: 5/20
```

---

## 错误处理

| 场景 | 错误信息 | 解决方案 |
|------|----------|----------|
| 配置不存在 | `❌ 未找到配置文件，请先运行 /comfyui init` | 运行 init |
| 服务器不可达 | `❌ 无法连接到 ComfyUI 服务器` | 检查地址和网络 |
| 模型不存在 | `❌ 模型 xxx 不存在` | 运行 model list 查看可用模型 |
| 超时 | `❌ 生成超时（超过 300 秒）` | 增加 timeout 配置或减少 steps |
| VRAM 不足 | `❌ 显存不足` | 减小分辨率或 batch_size |

---

## 模型与工作流说明

### Flux 模型

使用 Flux 工作流时需要准备以下模型：

| 组件 | 节点 | 模型示例 | 存放路径 |
|------|------|----------|----------|
| UNET | `UnetLoaderGGUF` | `flux1-dev-Q4_K_S.gguf` | `models/unet/` 或 `models/diffusion_models/` |
| CLIP-L | `DualCLIPLoader` | `clip_l.safetensors` | `models/text_encoders/` 或 `models/clip/` |
| T5-XXL | `DualCLIPLoader` | `t5xxl_fp16.safetensors` | `models/text_encoders/` 或 `models/clip/` |
| VAE | `VAELoader` | `ae.safetensors` | `models/vae/` |

Flux 工作流要点：
- 使用 `DualCLIPLoader`（type=`flux`）同时加载 CLIP-L + T5-XXL
- 使用 `CLIPTextEncodeFlux` 编码提示词，`guidance` 默认 3.5
- KSampler 的 `cfg` 必须固定为 1.0
- negative 输入必须使用 `ConditioningZeroOut`，不能复用 positive

### 中文提示词

Flux 的 T5-XXL/CLIP-L 对中文理解较弱，中文提示词容易产生偏离主题的随机图像。**使用 Flux 工作流时，如果用户用中文描述，请先将提示词翻译成英文，再填入 `{{prompt}}`。**

示例：
- 用户：`/comfyui txt2img 一只猫坐在窗台上`
- 实际填入：`a cute fluffy cat sitting on a sunny windowsill, photorealistic, high detail`

SD 1.5 / SDXL 模型对中文支持相对较好，可保留中文或按需翻译。

---

## 常见问题

### Q: 如何查看服务器有哪些模型？

```
/comfyui model list
```

### Q: 如何使用特定模型？

```
/comfyui txt2img 猫 --model ChilloutMix-Ni-pruned-fp32.safetensors
```

### Q: 如何批量生成？

```
/comfyui txt2img 猫 --batch 4
```

### Q: 生成的图片保存在哪里？

默认保存在 `./comfyui-output/` 目录，可在配置文件中修改 `output.dir`。

### Q: 如何不下载生成结果？

```
/comfyui txt2img 猫 --no-download
```

### Q: 如何创建自定义工作流？

1. 从模板创建：
   ```
   /comfyui workflow create my_flow --from txt2img_basic
   ```

2. 编辑工作流：
   ```
   /comfyui workflow edit my_flow
   ```

3. 使用工作流：
   ```
   /comfyui workflow run my_flow --prompt "猫"
   ```

---

## 技术细节

### 依赖检测

Agent 执行命令前检测：
1. 配置文件是否存在
2. comfy-cli 是否可用（`which comfy`）
3. 服务器是否可达（`curl /system_stats`）

### 降级策略

- comfy-cli 不可用 → 使用 curl 直接调用 API
- WebSocket 不可用 → 使用轮询模式

### 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/upload_image.py` | 上传本地图片到 ComfyUI |
| `scripts/fill_template.py` | 替换工作流模板中的占位符 |

---

## 相关资源

- [ComfyUI 官方文档](https://docs.comfy.org/)
- [comfy-cli GitHub](https://github.com/Comfy-Org/comfy-cli)
- [ComfyUI API 文档](https://docs.comfy.org/development/comfyui-server/api-examples)
