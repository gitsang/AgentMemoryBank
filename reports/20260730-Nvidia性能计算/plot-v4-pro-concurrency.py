#!/usr/bin/env python3
"""Plot the DeepSeek-V4-Pro concurrency estimates used in the capacity note."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager


OUT_DIR = Path(__file__).resolve().parent
COLORS = {"H200": "#2563EB", "H20": "#EA580C"}

# Assumptions from the capacity estimate.
PREFILL_SECONDS_PER_REQUEST = {"H200": 0.2406797684, "H20": 1.6091393977}
EFFECTIVE_BW_GBPS = {"H200": 16 * 4.8 * 0.60 * 1000, "H20": 32 * 4.8 * 0.60 * 1000}
EFFECTIVE_COMPUTE_TFLOPS = {"H200": 16 * 3958 * 0.35, "H20": 32 * 296 * 0.35}
WEIGHT_GB = 49.0
KV_GB_PER_REQUEST = 11.79648
DECODE_TFLOP_PER_REQUEST_STEP = 0.433
PREFILL_SLO_SECONDS = 300
DECODE_SLO_TPS = 25
SHARED_PREFIX_RESIDENT_LIMIT = {"H200": 355, "H20": 2076}
PREFILL_LIMIT = {"H200": 355, "H20": 186}
DECODE_LIMIT = {"H200": 152, "H20": 306}
JOINT_LIMIT = {name: min(PREFILL_LIMIT[name], DECODE_LIMIT[name]) for name in COLORS}

# HiCache scheduling model: independent 128k KV, request-level residency, L2 hits.
ACTIVE_BATCH_LIMIT = {"H200": 36, "H20": 208}
L2_RESTORE_BW_GBPS = {"H200": 600.0, "H20": 1200.0}
RESTORE_GB_PER_REQUEST = KV_GB_PER_REQUEST * 0.90
OUTPUT_TOKENS = 1000

# Context sweep model.
FIXED_CONCURRENCY = 100
CONTEXT_MIN_K = 8
CONTEXT_MAX_K = 372
CACHE_CONTEXT_TOKENS = 372000
CACHE_HIT_MIN_PERCENT = 0
CACHE_HIT_MAX_PERCENT = 100
ACTIVE_KV_POOL_GB = {
    cluster: ACTIVE_BATCH_LIMIT[cluster] * KV_GB_PER_REQUEST for cluster in COLORS
}
ACTIVE_PARAMETERS = 49e9
ATTENTION_WIDTH = 8192
ATTENTION_LAYERS = 80


def configure_style() -> None:
    noto_cjk = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if noto_cjk.exists():
        font_manager.fontManager.addfont(noto_cjk)
        family = font_manager.FontProperties(fname=noto_cjk).get_name()
    else:
        candidates = ["Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Micro Hei"]
        available = {font.name for font in font_manager.fontManager.ttflist}
        family = next((name for name in candidates if name in available), "DejaVu Sans")
    plt.rcParams.update(
        {
            "font.family": family,
            "axes.unicode_minus": False,
            "figure.dpi": 140,
            "savefig.dpi": 180,
            "axes.titleweight": "bold",
            "axes.edgecolor": "#94A3B8",
            "axes.labelcolor": "#334155",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "grid.color": "#CBD5E1",
            "grid.alpha": 0.55,
        }
    )


def decode_step_seconds(cluster: str, concurrency: np.ndarray) -> np.ndarray:
    bandwidth_time = (WEIGHT_GB + KV_GB_PER_REQUEST * concurrency) / EFFECTIVE_BW_GBPS[cluster]
    compute_time = DECODE_TFLOP_PER_REQUEST_STEP * concurrency / EFFECTIVE_COMPUTE_TFLOPS[cluster]
    return np.maximum(bandwidth_time, compute_time)


def hicache_batch_metrics(cluster: str, total_requests: int) -> tuple[float, float, float, float]:
    """Return average queue, restore+queue, service, and completion seconds."""
    remaining = total_requests
    elapsed = 0.0
    weighted_queue = 0.0
    weighted_ready = 0.0
    weighted_service = 0.0

    while remaining:
        batch = min(ACTIVE_BATCH_LIMIT[cluster], remaining)
        restore = batch * RESTORE_GB_PER_REQUEST / L2_RESTORE_BW_GBPS[cluster]
        service = OUTPUT_TOKENS * decode_step_seconds(cluster, np.array([batch]))[0]
        weighted_queue += batch * elapsed
        weighted_ready += batch * (elapsed + restore)
        weighted_service += batch * service
        elapsed += restore + service
        remaining -= batch

    average_queue = weighted_queue / total_requests
    average_ready = weighted_ready / total_requests
    average_service = weighted_service / total_requests
    return average_queue, average_ready, average_service, average_ready + average_service


def hicache_series(cluster: str, concurrency: np.ndarray) -> tuple[np.ndarray, ...]:
    rows = [hicache_batch_metrics(cluster, int(value)) for value in concurrency]
    return tuple(np.array(column) for column in zip(*rows))


def context_kv_gb(context_tokens: np.ndarray | float) -> np.ndarray | float:
    return KV_GB_PER_REQUEST * np.asarray(context_tokens) / 128000


def context_prefill_seconds(cluster: str, context_tokens: np.ndarray) -> np.ndarray:
    new_tokens = context_tokens * 0.10
    average_keys = context_tokens * 0.95
    linear_flops = 2 * ACTIVE_PARAMETERS * new_tokens
    attention_flops = 4 * new_tokens * average_keys * ATTENTION_WIDTH * ATTENTION_LAYERS
    effective_flops = EFFECTIVE_COMPUTE_TFLOPS[cluster] * 1e12
    return FIXED_CONCURRENCY * (linear_flops + attention_flops) / effective_flops


def context_decode_step_seconds(cluster: str, batch: int, context_tokens: float) -> float:
    kv_gb = float(context_kv_gb(context_tokens))
    bandwidth_time = (WEIGHT_GB + kv_gb * batch) / EFFECTIVE_BW_GBPS[cluster]
    attention_tflop = 4 * context_tokens * ATTENTION_WIDTH * ATTENTION_LAYERS / 1e12
    compute_tflop = (2 * ACTIVE_PARAMETERS / 1e12 + attention_tflop) * batch
    compute_time = compute_tflop / EFFECTIVE_COMPUTE_TFLOPS[cluster]
    return max(bandwidth_time, compute_time)


def context_active_batch(cluster: str, context_tokens: float) -> int:
    kv_gb = float(context_kv_gb(context_tokens))
    return min(FIXED_CONCURRENCY, max(1, int(ACTIVE_KV_POOL_GB[cluster] // kv_gb)))


def context_hicache_metrics(cluster: str, context_tokens: float) -> tuple[float, float, float, float]:
    remaining = FIXED_CONCURRENCY
    elapsed = 0.0
    weighted_queue = 0.0
    weighted_ready = 0.0
    weighted_service = 0.0
    max_batch = context_active_batch(cluster, context_tokens)
    restore_gb = float(context_kv_gb(context_tokens)) * 0.90

    while remaining:
        batch = min(max_batch, remaining)
        restore = batch * restore_gb / L2_RESTORE_BW_GBPS[cluster]
        service = OUTPUT_TOKENS * context_decode_step_seconds(cluster, batch, context_tokens)
        weighted_queue += batch * elapsed
        weighted_ready += batch * (elapsed + restore)
        weighted_service += batch * service
        elapsed += restore + service
        remaining -= batch

    average_queue = weighted_queue / FIXED_CONCURRENCY
    average_ready = weighted_ready / FIXED_CONCURRENCY
    average_service = weighted_service / FIXED_CONCURRENCY
    return average_queue, average_ready, average_service, average_ready + average_service


def context_hicache_series(cluster: str, context_tokens: np.ndarray) -> tuple[np.ndarray, ...]:
    rows = [context_hicache_metrics(cluster, float(value)) for value in context_tokens]
    return tuple(np.array(column) for column in zip(*rows))


def cache_prefill_seconds(cluster: str, hit_rates: np.ndarray) -> np.ndarray:
    new_tokens = CACHE_CONTEXT_TOKENS * (1 - hit_rates)
    average_keys = CACHE_CONTEXT_TOKENS * (1 + hit_rates) / 2
    linear_flops = 2 * ACTIVE_PARAMETERS * new_tokens
    attention_flops = 4 * new_tokens * average_keys * ATTENTION_WIDTH * ATTENTION_LAYERS
    effective_flops = EFFECTIVE_COMPUTE_TFLOPS[cluster] * 1e12
    return FIXED_CONCURRENCY * (linear_flops + attention_flops) / effective_flops


def cache_hicache_metrics(cluster: str, hit_rate: float) -> tuple[float, float, float, float]:
    remaining = FIXED_CONCURRENCY
    elapsed = 0.0
    weighted_queue = 0.0
    weighted_ready = 0.0
    weighted_service = 0.0
    max_batch = context_active_batch(cluster, CACHE_CONTEXT_TOKENS)
    restore_gb = float(context_kv_gb(CACHE_CONTEXT_TOKENS)) * hit_rate

    while remaining:
        batch = min(max_batch, remaining)
        restore = batch * restore_gb / L2_RESTORE_BW_GBPS[cluster]
        service = OUTPUT_TOKENS * context_decode_step_seconds(
            cluster, batch, CACHE_CONTEXT_TOKENS
        )
        weighted_queue += batch * elapsed
        weighted_ready += batch * (elapsed + restore)
        weighted_service += batch * service
        elapsed += restore + service
        remaining -= batch

    average_queue = weighted_queue / FIXED_CONCURRENCY
    average_ready = weighted_ready / FIXED_CONCURRENCY
    average_service = weighted_service / FIXED_CONCURRENCY
    return average_queue, average_ready, average_service, average_ready + average_service


def cache_hicache_series(cluster: str, hit_rates: np.ndarray) -> tuple[np.ndarray, ...]:
    rows = [cache_hicache_metrics(cluster, float(value)) for value in hit_rates]
    return tuple(np.array(column) for column in zip(*rows))


def style_axis(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=14, pad=12)
    ax.set_xlabel("并发请求数")
    ax.set_ylabel(ylabel)
    ax.grid(True, linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def add_legend(ax) -> None:
    ax.legend(frameon=False, ncol=2, loc="upper left")


def plot_prefill(ax, concurrency: np.ndarray) -> None:
    for cluster, color in COLORS.items():
        values = concurrency * PREFILL_SECONDS_PER_REQUEST[cluster]
        ax.plot(concurrency, values, color=color, linewidth=2.4, label=cluster)
        limit = PREFILL_LIMIT[cluster]
        ax.scatter(limit, limit * PREFILL_SECONDS_PER_REQUEST[cluster], color=color, s=38, zorder=4)
    ax.axhline(PREFILL_SLO_SECONDS, color="#B91C1C", linestyle="--", linewidth=1.5, label="5 分钟门槛")
    ax.axvline(PREFILL_LIMIT["H200"], color=COLORS["H200"], linestyle=":", alpha=0.75)
    ax.axvline(PREFILL_LIMIT["H20"], color=COLORS["H20"], linestyle=":", alpha=0.75)
    ax.text(190, 310, "H20 上限约 186", color=COLORS["H20"], fontsize=9)
    ax.text(350, 96, "H200 驻留上限约 355", color=COLORS["H200"], fontsize=9, ha="right")
    style_axis(ax, "Prefill：并发量与 TTFT", "Prefill 时间 / 秒")
    ax.set_xlim(1, 360)
    ax.set_ylim(0, 620)
    add_legend(ax)


def plot_decode(ax, concurrency: np.ndarray) -> None:
    for cluster, color in COLORS.items():
        tps = 1 / decode_step_seconds(cluster, concurrency)
        ax.plot(concurrency, tps, color=color, linewidth=2.4, label=cluster)
        limit = DECODE_LIMIT[cluster]
        limit_tps = 1 / decode_step_seconds(cluster, np.array([limit]))[0]
        ax.scatter(limit, limit_tps, color=color, s=38, zorder=4)
        ax.axvline(limit, color=color, linestyle=":", alpha=0.75)
    ax.axhline(DECODE_SLO_TPS, color="#B91C1C", linestyle="--", linewidth=1.5, label="25 tok/s 门槛")
    ax.text(148, 18, "H200 约 152", color=COLORS["H200"], fontsize=9, ha="right")
    ax.text(302, 31, "H20 约 306", color=COLORS["H20"], fontsize=9, ha="right")
    style_axis(ax, "Decode：并发量与单请求生成速度", "单请求速度 / tok/s（对数轴）")
    ax.set_yscale("log")
    ax.set_xlim(1, 360)
    ax.set_ylim(10, 1800)
    add_legend(ax)


def plot_recovery_queue(ax, concurrency: np.ndarray) -> None:
    for cluster, color in COLORS.items():
        queue, ready, _, _ = hicache_series(cluster, concurrency)
        ax.plot(concurrency, ready, color=color, linewidth=2.4, label=f"{cluster} 恢复+排队")
        ax.plot(concurrency, queue, color=color, linewidth=1.5, linestyle="--", alpha=0.65, label=f"{cluster} 仅排队")
        limit = ACTIVE_BATCH_LIMIT[cluster]
        ax.axvline(limit, color=color, linestyle=":", alpha=0.75)
    ax.text(39, 54, "H200 HBM 活跃批上限 36", color=COLORS["H200"], fontsize=9)
    ax.text(211, 7, "H20 HBM 活跃批上限 208", color=COLORS["H20"], fontsize=9)
    style_axis(ax, "HiCache：并发量与平均 Decode 恢复/排队时间", "请求开始 Decode 前的平均时间 / 秒")
    ax.set_xlim(1, 360)
    ax.set_ylim(0, 70)
    add_legend(ax)


def plot_total(ax, concurrency: np.ndarray) -> None:
    for cluster, color in COLORS.items():
        prefill = concurrency * PREFILL_SECONDS_PER_REQUEST[cluster]
        _, _, _, average_decode_completion = hicache_series(cluster, concurrency)
        total = prefill + average_decode_completion
        old_total = prefill + OUTPUT_TOKENS * decode_step_seconds(cluster, concurrency)
        ax.plot(concurrency, total, color=color, linewidth=2.4, label=f"{cluster}，含恢复/排队")
        ax.plot(concurrency, old_total, color=color, linewidth=1.4, linestyle="--", alpha=0.5, label=f"{cluster}，旧驻留模型")
        limit = JOINT_LIMIT[cluster]
        limit_total = total[limit - 1]
        ax.scatter(limit, limit_total, color=color, s=38, zorder=4)
        ax.axvline(limit, color=color, linestyle=":", alpha=0.75)
        ax.annotate(
            f"并发 {limit}\n平均约 {limit_total:.0f} 秒",
            xy=(limit, limit_total),
            xytext=(10, 14),
            textcoords="offset points",
            color=color,
            fontsize=9,
        )
    ax.axhline(PREFILL_SLO_SECONDS, color="#64748B", linestyle="--", linewidth=1.3, label="300 秒参考线")
    style_axis(ax, "端到端平均值：Prefill + HiCache 恢复/排队 + 输出 1,000 token", "平均总时长 / 秒")
    ax.set_xlim(1, 360)
    ax.set_ylim(0, 680)
    add_legend(ax)


def style_context_axis(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=14, pad=12)
    ax.set_xlabel("Context size / k tokens")
    ax.set_ylabel(ylabel)
    ax.set_xlim(CONTEXT_MIN_K, CONTEXT_MAX_K)
    ax.grid(True, linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def plot_context_prefill(ax, context_k: np.ndarray) -> None:
    tokens = context_k * 1000
    for cluster, color in COLORS.items():
        values = context_prefill_seconds(cluster, tokens)
        ax.plot(context_k, values, color=color, linewidth=2.4, label=cluster)
    ax.axhline(PREFILL_SLO_SECONDS, color="#B91C1C", linestyle="--", linewidth=1.5, label="5 分钟门槛")
    style_context_axis(ax, "固定并发 100：Context size 与 Prefill 时间", "Prefill 时间 / 秒")
    add_legend(ax)


def plot_context_decode(ax, context_k: np.ndarray) -> None:
    tokens = context_k * 1000
    for cluster, color in COLORS.items():
        batches = np.array([context_active_batch(cluster, value) for value in tokens])
        tps = np.array([
            1 / context_decode_step_seconds(cluster, int(batch), float(context))
            for batch, context in zip(batches, tokens)
        ])
        ax.plot(context_k, tps, color=color, linewidth=2.4, label=cluster)
        ax.text(context_k[-1] - 4, tps[-1] + 3, f"活跃批 {batches[-1]}", color=color, fontsize=9, ha="right")
    ax.axhline(DECODE_SLO_TPS, color="#B91C1C", linestyle="--", linewidth=1.5, label="25 tok/s 门槛")
    style_context_axis(ax, "固定逻辑并发 100：Context size 与活跃 Decode 速度", "活跃请求单请求速度 / tok/s")
    ax.set_ylim(0, 180)
    add_legend(ax)


def plot_context_recovery_queue(ax, context_k: np.ndarray) -> None:
    tokens = context_k * 1000
    for cluster, color in COLORS.items():
        queue, ready, _, _ = context_hicache_series(cluster, tokens)
        ax.plot(context_k, ready, color=color, linewidth=2.4, label=f"{cluster} 恢复+排队")
        ax.plot(context_k, queue, color=color, linewidth=1.5, linestyle="--", alpha=0.65, label=f"{cluster} 仅排队")
    style_context_axis(ax, "固定并发 100：Context size 与平均 Decode 恢复/排队", "请求开始 Decode 前的平均时间 / 秒")
    add_legend(ax)


def plot_context_total(ax, context_k: np.ndarray) -> None:
    tokens = context_k * 1000
    for cluster, color in COLORS.items():
        prefill = context_prefill_seconds(cluster, tokens)
        _, _, _, decode_completion = context_hicache_series(cluster, tokens)
        total = prefill + decode_completion
        ax.plot(context_k, total, color=color, linewidth=2.4, label=cluster)
        ax.scatter(context_k[-1], total[-1], color=color, s=38, zorder=4)
        ax.annotate(
            f"372k：约 {total[-1]:.0f} 秒",
            xy=(context_k[-1], total[-1]),
            xytext=(-8, 12),
            textcoords="offset points",
            color=color,
            fontsize=9,
            ha="right",
        )
    ax.axhline(PREFILL_SLO_SECONDS, color="#64748B", linestyle="--", linewidth=1.3, label="300 秒参考线")
    style_context_axis(ax, "固定并发 100：Prefill + HiCache 恢复/排队 + 输出 1,000 token", "平均总时长 / 秒")
    add_legend(ax)


def style_cache_axis(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", fontsize=14, pad=12)
    ax.set_xlabel("Cache hit rate / %")
    ax.set_ylabel(ylabel)
    ax.set_xlim(CACHE_HIT_MIN_PERCENT, CACHE_HIT_MAX_PERCENT)
    ax.grid(True, linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def plot_cache_prefill(ax, hit_percent: np.ndarray) -> None:
    hit_rates = hit_percent / 100
    for cluster, color in COLORS.items():
        ax.plot(
            hit_percent,
            cache_prefill_seconds(cluster, hit_rates),
            color=color,
            linewidth=2.4,
            label=cluster,
        )
    ax.axhline(PREFILL_SLO_SECONDS, color="#B91C1C", linestyle="--", linewidth=1.5, label="5 分钟门槛")
    style_cache_axis(ax, "固定并发 100、Context 372k：Cache hit rate 与 Prefill 时间", "Prefill 时间 / 秒")
    add_legend(ax)


def plot_cache_decode(ax, hit_percent: np.ndarray) -> None:
    for cluster, color in COLORS.items():
        batch = context_active_batch(cluster, CACHE_CONTEXT_TOKENS)
        tps = 1 / context_decode_step_seconds(cluster, batch, CACHE_CONTEXT_TOKENS)
        ax.plot(hit_percent, np.full_like(hit_percent, tps, dtype=float), color=color, linewidth=2.4, label=cluster)
        ax.text(98, tps + 3, f"活跃批 {batch}", color=color, fontsize=9, ha="right")
    ax.axhline(DECODE_SLO_TPS, color="#B91C1C", linestyle="--", linewidth=1.5, label="25 tok/s 门槛")
    style_cache_axis(ax, "固定并发 100、Context 372k：Cache hit rate 与活跃 Decode 速度", "活跃请求单请求速度 / tok/s")
    ax.set_ylim(0, 125)
    add_legend(ax)


def plot_cache_recovery_queue(ax, hit_percent: np.ndarray) -> None:
    hit_rates = hit_percent / 100
    for cluster, color in COLORS.items():
        queue, ready, _, _ = cache_hicache_series(cluster, hit_rates)
        ax.plot(hit_percent, ready, color=color, linewidth=2.4, label=f"{cluster} 恢复+排队")
        ax.plot(hit_percent, queue, color=color, linewidth=1.5, linestyle="--", alpha=0.65, label=f"{cluster} 仅排队")
    style_cache_axis(ax, "固定并发 100、Context 372k：Cache hit rate 与平均 Decode 恢复/排队", "请求开始 Decode 前的平均时间 / 秒")
    add_legend(ax)


def plot_cache_total(ax, hit_percent: np.ndarray) -> None:
    hit_rates = hit_percent / 100
    for cluster, color in COLORS.items():
        prefill = cache_prefill_seconds(cluster, hit_rates)
        _, _, _, decode_completion = cache_hicache_series(cluster, hit_rates)
        total = prefill + decode_completion
        ax.plot(hit_percent, total, color=color, linewidth=2.4, label=cluster)
        for index in (0, -1):
            ax.scatter(hit_percent[index], total[index], color=color, s=34, zorder=4)
        annotation_offset = (-8, 24) if cluster == "H200" else (-8, -20)
        ax.annotate(
            f"100%：约 {total[-1]:.0f} 秒",
            xy=(hit_percent[-1], total[-1]),
            xytext=annotation_offset,
            textcoords="offset points",
            color=color,
            fontsize=9,
            ha="right",
        )
    ax.axhline(PREFILL_SLO_SECONDS, color="#64748B", linestyle="--", linewidth=1.3, label="300 秒参考线")
    style_cache_axis(ax, "固定并发 100、Context 372k：Prefill + HiCache 恢复/排队 + 输出 1,000 token", "平均总时长 / 秒")
    add_legend(ax)


def save_single(filename: str, plotter, concurrency: np.ndarray, footer: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.8), constrained_layout=True)
    plotter(ax, concurrency)
    ax.text(
        1.0,
        -0.15,
        footer or "估算：90% prefix hit；HiCache 按独立 BF16 KV、L2 恢复 10.6 GB/请求、活跃批 H200/H20=36/208",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.5,
        color="#64748B",
        clip_on=False,
    )
    fig.savefig(OUT_DIR / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    configure_style()
    concurrency = np.arange(1, 361)

    save_single("v4-pro-prefill-concurrency.png", plot_prefill, concurrency)
    save_single("v4-pro-decode-concurrency.png", plot_decode, concurrency)
    save_single("v4-pro-decode-recovery-queue.png", plot_recovery_queue, concurrency)
    save_single("v4-pro-1k-total-concurrency.png", plot_total, concurrency)

    context_k = np.arange(CONTEXT_MIN_K, CONTEXT_MAX_K + 1)
    context_footer = "固定逻辑并发 100；90% prefix hit；独立 BF16 KV；L2 带宽 H200/H20=600/1200 GB/s；最大 372k"
    save_single("v4-pro-ctx-prefill-c100.png", plot_context_prefill, context_k, context_footer)
    save_single("v4-pro-ctx-decode-c100.png", plot_context_decode, context_k, context_footer)
    save_single("v4-pro-ctx-decode-recovery-queue-c100.png", plot_context_recovery_queue, context_k, context_footer)
    save_single("v4-pro-ctx-1k-total-c100.png", plot_context_total, context_k, context_footer)

    context_fig, context_axes = plt.subplots(4, 1, figsize=(10.5, 21), constrained_layout=True)
    plot_context_prefill(context_axes[0], context_k)
    plot_context_decode(context_axes[1], context_k)
    plot_context_recovery_queue(context_axes[2], context_k)
    plot_context_total(context_axes[3], context_k)
    context_fig.suptitle("DeepSeek-V4-Pro：固定并发 100 的 Context size 关系", fontsize=18, fontweight="bold")
    context_axes[-1].text(
        1.0, -0.15, context_footer, transform=context_axes[-1].transAxes,
        ha="right", va="top", fontsize=8, color="#64748B", clip_on=False,
    )
    context_fig.savefig(OUT_DIR / "v4-pro-ctx-overview-c100.png", bbox_inches="tight", facecolor="white")
    plt.close(context_fig)

    hit_percent = np.arange(CACHE_HIT_MIN_PERCENT, CACHE_HIT_MAX_PERCENT + 1)
    cache_footer = "固定逻辑并发 100；Context 372k；独立 BF16 KV；HiCache L2 带宽 H200/H20=600/1200 GB/s；输出 1k token"
    save_single("v4-pro-cache-prefill-c100-ctx372k.png", plot_cache_prefill, hit_percent, cache_footer)
    save_single("v4-pro-cache-decode-c100-ctx372k.png", plot_cache_decode, hit_percent, cache_footer)
    save_single("v4-pro-cache-decode-recovery-queue-c100-ctx372k.png", plot_cache_recovery_queue, hit_percent, cache_footer)
    save_single("v4-pro-cache-1k-total-c100-ctx372k.png", plot_cache_total, hit_percent, cache_footer)

    cache_fig, cache_axes = plt.subplots(4, 1, figsize=(10.5, 21), constrained_layout=True)
    plot_cache_prefill(cache_axes[0], hit_percent)
    plot_cache_decode(cache_axes[1], hit_percent)
    plot_cache_recovery_queue(cache_axes[2], hit_percent)
    plot_cache_total(cache_axes[3], hit_percent)
    cache_fig.suptitle("DeepSeek-V4-Pro：固定并发 100、Context 372k 的 Cache hit rate 关系", fontsize=18, fontweight="bold")
    cache_axes[-1].text(
        1.0, -0.15, cache_footer, transform=cache_axes[-1].transAxes,
        ha="right", va="top", fontsize=8, color="#64748B", clip_on=False,
    )
    cache_fig.savefig(OUT_DIR / "v4-pro-cache-overview-c100-ctx372k.png", bbox_inches="tight", facecolor="white")
    plt.close(cache_fig)

    fig, axes = plt.subplots(4, 1, figsize=(10.5, 21), constrained_layout=True)
    plot_prefill(axes[0], concurrency)
    plot_decode(axes[1], concurrency)
    plot_recovery_queue(axes[2], concurrency)
    plot_total(axes[3], concurrency)
    fig.suptitle("DeepSeek-V4-Pro：并发容量关系总览", fontsize=18, fontweight="bold")
    axes[-1].text(
        1.0,
        -0.15,
        "估算：90% prefix hit；计算效率 35%；HBM 带宽效率 60%；HiCache 独立 BF16 KV、L2 恢复；不含检索和网络固定开销",
        transform=axes[-1].transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#64748B",
        clip_on=False,
    )
    fig.savefig(OUT_DIR / "v4-pro-concurrency-overview.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
