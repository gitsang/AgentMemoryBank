# MrFlow (Multi-Resolution Flow Matching) — Research Report

**Date**: 2026-07-08
**Paper**: arXiv 2607.01642 — "Multi-Resolution Flow Matching: Training-Free Diffusion Acceleration via Staged Sampling"

---

## Overview

MrFlow is a **training-free** staged sampling method for accelerating pretrained flow-matching text-to-image diffusion models. It achieves up to **10× end-to-end speedup** standalone, and up to **25×** when combined with timestep-distilled models like Pi-Flow.

### Pipeline (4 stages)

1. **Low-resolution generation** — 12/20 steps at 512×512 latent (4× cheaper per step)
2. **Pixel-space super-resolution** — VAE decode → Real-ESRGAN x2 upscale in pixel space (avoids latent grid artifacts)
3. **Low-strength noise injection** — σ=0.10–0.20 noise re-added before high-res refine
4. **High-resolution refinement** — 1-step denoising at 1024×1024

---

## Repositories

### 1. Official Implementation (Primary)

| Field | Value |
|-------|-------|
| **URL** | https://github.com/Xingyu-Zheng/MrFlow |
| **Stars** | 231 |
| **Forks** | 16 |
| **License** | Apache-2.0 |
| **Language** | Python (100%) |
| **Status** | Active (20 commits, Jul 2026) |

**Contents:**
- Root scripts: `flux1_mrflow.py`, `qwen_image_mrflow.py`, `mrflow_utils.py`
- `examples/` — FLUX.1-dev, Qwen-Image, FLUX.2 Klein, Z-Image-Turbo, Pi-Flow combos
- `ComfyUI-MrFlow/` — ComfyUI custom node extension
- `community/` — Community contributions area

**Supported backbones:**
- FLUX.1-dev (8.25× speedup with 12+1)
- Qwen-Image (10.3× speedup with 12+1)
- FLUX.2 Klein Base 9B (8.79×)
- Z-Image-Turbo (21.0× with 8+1)
- Qwen-Image + Pi-Flow (up to 25× with 4+1)

### 2. Community Port — RealRebelAI/Rebels_MrFlow

| Field | Value |
|-------|-------|
| **URL** | https://github.com/RealRebelAI/Rebels_MrFlow |
| **Stars** | 29 |
| **Forks** | 3 |
| **Description** | ComfyUI custom node port for Z-Image Turbo and Krea-2 MrFlow |

Provides preset nodes: `ZIT Mr. Flow Preset`, `Krea-2 Mr. Flow Preset`, `Mr. Flow Upscale + Encode`, and refine nodes. Includes presets for `9plus1 (paper)` and `base_12plus1` / `turbo_8plus1`.

### 3. HuggingFace Resources

| Resource | URL |
|----------|-----|
| **Model card** | https://huggingface.co/Xingyu-Zheng/MrFlow |
| **HF Space (demo)** | https://huggingface.co/spaces/Xingyu-Zheng/mrflow-fast-diffusion |
| **HF Daily Paper** | https://huggingface.co/papers/2607.01642 |

### 4. Related Repositories (Flow Matching ecosystem)

| Repo | URL | Description |
|------|-----|-------------|
| facebookresearch/flow_matching | https://github.com/facebookresearch/flow_matching | Official PyTorch flow matching library (continuous + discrete) |
| VinAIResearch/LFM | https://github.com/VinAIResearch/LFM | Latent Flow Matching (pioneer in latent-space FM) |
| black-forest-labs/Self-Flow | https://github.com/black-forest-labs/Self-Flow | [ICML'26] Self-Supervised Flow Matching |
| jy0205/Pyramid-Flow | https://github.com/jy0205/Pyramid-Flow | Autoregressive video generation via flow matching |

---

## Paper Details

- **Title**: Multi-Resolution Flow Matching: Training-Free Diffusion Acceleration via Staged Sampling
- **Authors**: Xingyu Zheng, Xianglong Liu, Yifu Ding, Weilun Feng, Junqing Lin, Jinyang Guo, Haotong Qin
- **arXiv**: https://arxiv.org/abs/2607.01642
- **Published**: July 2026
- **Method**: MrFlow — training-free multi-resolution acceleration strategy

### Key Results

| Setting | Backbone | Speedup | Quality |
|---------|----------|---------|---------|
| 12+1 (aggressive) | Qwen-Image | 10.3× | OneIG within 1% of native |
| 20+1 (quality) | Qwen-Image | ~6× | Higher quality |
| 12+1 | FLUX.1-dev | 8.25× | GenEval 0.63 |
| 12+1 | FLUX.2 Klein 9B | 8.79× | — |
| 8+1 | Z-Image-Turbo | 21.0× | — |
| 4+1 + Pi-Flow | Qwen-Image | 25× | GenEval 0.85 (vs 0.86 native) |

---

## Installation & Quick Start

```bash
# Dependencies
pip install torch diffusers transformers

# Real-ESRGAN for pixel-space SR
# Code: https://github.com/ai-forever/Real-ESRGAN
# Weights: https://huggingface.co/ai-forever/Real-ESRGAN

# Run MrFlow
python flux1_mrflow.py    # or qwen_image_mrflow.py
```

Edit checkpoint paths in the script:
```python
MODEL = "/path/to/Qwen-Image"
REALESRGAN_X2 = "/path/to/RealESRGAN_x2.pth"
```

### ComfyUI Plugin
Symlink `ComfyUI-MrFlow/` into `ComfyUI/custom_nodes/`, restart, load workflow JSON.

---

## Key Design Insight

The core innovation is doing super-resolution in **pixel space** (not latent space), which avoids the grid artifacts that plague latent-space upsampling methods (LSSGen, RALU, SPEED, etc.). The low-strength noise injection (σ=0.10–0.15) enables high-frequency resampling while preserving low-frequency structure — backed by frequency-domain analysis showing low-frequency noise is irreversible while high-frequency noise is correctable.

---

## Community & News

- **Hugging Face Trending Papers** (July 2026)
- **DEV.to article**: https://dev.to/breachprotocol/a-training-free-trick-makes-ai-image-generation-up-to-10x-faster-1256
- **Japanese summary**: https://ai-papers.net/mrflow-multi-resolution-flow-matching-flux-25x-speedup
- Active Discussions on GitHub repo
- Community experimental ports in `community/experimental/`

---

## Citation

```bibtex
@misc{zheng2026multiresolutionflowmatchingtrainingfree,
  title={Multi-Resolution Flow Matching: Training-Free Diffusion Acceleration via Staged Sampling},
  author={Xingyu Zheng and Xianglong Liu and Yifu Ding and Weilun Feng and Junqing Lin and Jinyang Guo and Haotong Qin},
  year={2026},
  eprint={2607.01642},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2607.01642},
}
```
