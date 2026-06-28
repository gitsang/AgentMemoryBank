# ComfyUI 技能设计文档

## 概述

为 OpenCode 创建一个 ComfyUI 技能，支持通过自然语言命令控制远程 ComfyUI 服务器进行图像/视频生成。

## 设计目标

1. **简洁优先** - Agent 直接调用 comfy-cli，仅在必要时使用脚本
2. **配置驱动** - 服务器地址、默认参数等通过配置文件管理
3. **工作流灵活** - 支持内置模板和用户自定义工作流
4. **渐进增强** - 首次使用引导初始化，后续直接使用

---

## 目录结构

```
.agents/skills/comfyui/
├── SKILL.md                    # 技能使用手册（中文）
├── config.yml                  # 配置文件（初始化时生成）
├── scripts/                    # 必要脚本
│   ├── upload_image.py        # 文件上传（img2img 需要）
│   └── fill_template.py       # 模板变量替换
├── templates/                  # 内置工作流模板（只读参考）
│   ├── txt2img_basic.json     # 基础文生图
│   ├── img2img_basic.json     # 基础图生图
│   └── batch_basic.json       # 批量生成
└── workflows/                  # 用户工作流目录
    └── *.json
```

---

## 配置管理

### 配置文件位置

按优先级读取：
1. `./.agents/skills/comfyui/config.yml`（项目级）
2. `~/.agents/skills/comfyui/config.yml`（全局级）

### 配置文件格式

```yaml
# ComfyUI 服务器配置
server:
  url: "http://dev.xm1.wg.c8g.top:8188"
  timeout: 300  # 秒

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

### 配置读取方式

- **Agent 读取**：仅用于检查配置是否存在
- **脚本读取**：所有实际执行场景，脚本内部自行读取配置

---

## 命令设计

### 命令列表

| 命令 | 用途 | 示例 |
|------|------|------|
| `/comfyui init` | 初始化配置 | `/comfyui init` |
| `/comfyui txt2img <prompt>` | 文生图 | `/comfyui txt2img 一只猫 --batch 4` |
| `/comfyui img2img <prompt>` | 图生图 | `/comfyui img2img 油画风格 --input photo.jpg` |
| `/comfyui workflow list` | 列出工作流 | `/comfyui workflow list` |
| `/comfyui workflow run <name>` | 运行工作流 | `/comfyui workflow run my_flow --prompt "猫"` |
| `/comfyui workflow create <name>` | 创建工作流 | `/comfyui workflow create batch_gen --global` |
| `/comfyui workflow edit <name>` | 编辑工作流 | `/comfyui workflow edit my_flow` |
| `/comfyui workflow delete <name>` | 删除工作流 | `/comfyui workflow delete old_flow` |
| `/comfyui model list` | 列出模型 | `/comfyui model list` |
| `/comfyui status` | 服务器状态 | `/comfyui status` |

### 通用选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--batch N` | 生成数量 | `--batch 4` |
| `--model <name>` | 指定模型 | `--model ChilloutMix` |
| `--width N` | 宽度 | `--width 1024` |
| `--height N` | 高度 | `--height 768` |
| `--steps N` | 步数 | `--steps 30` |
| `--seed N` | 随机种子 | `--seed 12345` |
| `--no-download` | 不下载结果 | `--no-download` |

### workflow create 选项

| 选项 | 说明 |
|------|------|
| `--global` | 创建到全局用户级 |
| `--from <source>` | 从模板创建 |

---

## 工作流管理

### 工作流存储位置

| 类型 | 路径 | 说明 |
|------|------|------|
| 内置模板 | `.agents/skills/comfyui/templates/*.json` | 随技能分发，只读参考 |
| 用户工作流（项目级） | `./.agents/skills/comfyui/workflows/*.json` | 可版本控制 |
| 用户工作流（全局级） | `~/.agents/skills/comfyui/workflows/*.json` | 跨项目共享 |

### 工作流查找顺序

1. 项目级 workflows/
2. 全局级 workflows/
3. 内置 templates/

### 工作流格式

使用 ComfyUI API 格式，支持占位符变量：

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

### 创建工作流

`workflow create` 支持：
1. 从模板创建 - `--from txt2img_basic`
2. 从远程导入 - 获取当前服务器工作流
3. 空白创建 - 创建最小可运行工作流

---

## 图片处理

### img2img 输入

支持两种输入方式：
- **本地路径**（`./photo.jpg`）→ 自动上传到 ComfyUI
- **远程文件名**（已存在于 ComfyUI）→ 直接使用

### 结果下载

| 选项 | 行为 |
|------|------|
| 自动下载（默认） | 生成后自动保存到 `output_dir` |
| 不下载 | `--no-download` 只返回文件名 |

### 图片预览

配置 `preview` 选项：
- `auto` - 自动检测：macOS 用 `open`，Linux 有 DISPLAY 用 `xdg-open`，否则 none
- `xdg-open` - Linux 打开
- `open` - macOS 打开
- `none` - 只打印文件路径

---

## 进度显示

### 默认模式（阻塞调用）

脚本内部轮询，完成后一次性返回结果：

```
⏳ 正在提交工作流...
⏳ 生成中... (预计 30 秒)
✅ 完成! 已保存到 ./comfyui-output/img_001.png
```

### 异步模式（可选）

使用 `--async` 参数返回任务 ID：

```bash
/comfyui txt2img 猫 --async
# 返回: task_id: abc123

/comfyui status abc123
# 返回: 生成中... 步数: 5/20
```

---

## 错误处理

| 场景 | 行为 |
|------|------|
| 服务器不可达 | 立即报错，提示检查地址和网络 |
| 模型不存在 | 报错，列出可用模型供选择 |
| 工作流格式错误 | 报错，显示 ComfyUI 返回的详细错误 |
| 生成超时 | 可配置超时时间（默认 300s） |
| VRAM 不足 | 报错，建议减小分辨率或 batch_size |

---

## 依赖管理

### 必需依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| comfy-cli | ComfyUI 命令行工具 | `uv tool install comfy-cli` |
| PyYAML | 配置文件解析 | 随 comfy-cli 安装 |

### 可选依赖

| 依赖 | 用途 |
|------|------|
| requests | 当 comfy-cli 无法实现时的降级方案 |

### 初始化流程

运行 `/comfyui init` 时：
1. 检查 uv 是否安装
2. 检查 comfy-cli 是否安装
3. 询问服务器地址
4. 测试连接
5. 获取可用模型列表
6. 写入配置文件

---

## Agent 使用流程

### 初始化

```
用户: /comfyui init
Agent: 
1. 检查配置是否存在
2. 如果不存在，引导用户输入服务器地址
3. 测试连接
4. 保存配置
```

### 生成图片

```
用户: /comfyui txt2img 一只猫坐在窗台 --batch 4
Agent:
1. 读取配置文件，获取默认参数
2. 合并用户参数（prompt, batch）
3. 加载模板或构建 comfy-cli 命令
4. 执行生成
5. 下载结果（如果 auto_download: true）
6. 预览（如果 preview: auto）
```

### 工作流管理

```
用户: /comfyui workflow list
Agent:
1. 读取配置，获取 workflows.search_path
2. 列出所有工作流文件
3. 按项目级/全局级分组显示
```

---

## 实现计划

### 第一版（MVP）

1. ✅ 设计文档
2. SKILL.md 使用手册
3. 配置文件模板
4. 必要脚本（upload_image.py, fill_template.py）
5. 内置工作流模板

### 后续迭代

- 更多工作流模板
- WebSocket 实时进度
- 批量任务管理
- 模型下载管理
