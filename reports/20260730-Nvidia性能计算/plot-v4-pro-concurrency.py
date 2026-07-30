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


def save_single(filename: str, plotter, concurrency: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.8), constrained_layout=True)
    plotter(ax, concurrency)
    ax.text(
        1.0,
        -0.15,
        "估算：90% prefix hit；HiCache 按独立 BF16 KV、L2 恢复 10.6 GB/请求、活跃批 H200/H20=36/208",
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
