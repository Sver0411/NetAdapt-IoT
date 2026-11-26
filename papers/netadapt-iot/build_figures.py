#!/usr/bin/env python3
"""Generate native 7.16-in IEEE print-ready vector PDF (+PNG) figures and Graphical Abstract."""
from collections import defaultdict
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT_P2 = ROOT / "output/phase2_validation"
OUT_C11 = ROOT / "output/phase2_c11"
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FIG_DIR = OUT_P2 / "figures"
REPORT_FIG_DIR.mkdir(parents=True, exist_ok=True)

IEEE_W = 7.16

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
        "mathtext.fontset": "stix",
        "font.size": 8.0,
        "axes.titlesize": 8.2,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.3,
        "ytick.labelsize": 7.3,
        "legend.fontsize": 7.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.65,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.45,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

STYLES = {
    "fud_ada":         dict(color="#004488", marker="o", ls="-",  lw=1.7, ms=4.5, label="FUD-Ada (Ours)", zorder=7),
    "fud_ada_no_debt": dict(color="#6699cc", marker="P", ls="--", lw=1.1, ms=3.8, label="FUD-Ada-NoDebt", zorder=5),
    "fud":             dict(color="#228833", marker="s", ls="-",  lw=1.3, ms=4.0, label="FUD-Quad", zorder=6),
    "aoi_gain":        dict(color="#aa3377", marker="D", ls="-.", lw=1.2, ms=3.7, label="AoI-Gain", zorder=5),
    "edf":             dict(color="#cc3311", marker="^", ls="--", lw=1.2, ms=4.0, label="EDF", zorder=5),
    "maxweight":       dict(color="#ee7733", marker="v", ls=":",  lw=1.1, ms=3.9, label="MaxWeight", zorder=4),
    "pf":              dict(color="#8855aa", marker="X", ls="-.", lw=1.1, ms=3.8, label="PF", zorder=4),
    "fifo":            dict(color="#666666", marker="*", ls=":",  lw=1.1, ms=4.5, label="FIFO", zorder=3),
}


def _load_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save_both(fig, stem: str) -> None:
    fig.savefig(FIG_DIR / f"{stem}.pdf")
    fig.savefig(REPORT_FIG_DIR / f"{stem}.png", dpi=200)
    plt.close(fig)


def _cluster_ci(rows: list[dict], filter_fn, key_fn, metric: str, n_boot: int = 2000):
    rng = np.random.default_rng(20261126)
    buckets: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if filter_fn(r) and r[metric] not in ("", None):
            buckets[key_fn(r)][r["cluster_id"]].append(float(r[metric]))
    out = {}
    for k, by_cl in buckets.items():
        vals = np.array([np.mean(v) for v in by_cl.values()], dtype=float)
        m = float(vals.mean())
        idx = rng.integers(0, len(vals), size=(n_boot, len(vals)))
        lo, hi = np.percentile(vals[idx].mean(axis=1), [2.5, 97.5])
        out[k] = (m, max(0.0, m - float(lo)), max(0.0, float(hi) - m))
    return out


def build_fig02_pareto(summary: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(IEEE_W, 2.55))
    pols_plot = ["fifo", "rr", "wrr", "edf", "priority", "pf", "aoi_gain", "debt", "fud", "fud_ada_no_debt", "fud_ada"]
    extra_styles = {
        "rr":       dict(color="#999999", marker="<", ms=4.5, label="RR"),
        "wrr":      dict(color="#888888", marker=">", ms=4.5, label="WRR"),
        "priority": dict(color="#bb8833", marker="h", ms=4.5, label="Priority"),
        "debt":     dict(color="#44aa99", marker="d", ms=4.5, label="Debt"),
    }
    lbl_offsets = {
        "congestion": {
            "fifo": (4, -3), "pf": (4, -3), "fud": (5, -3), "aoi_gain": (5, -4),
            "edf": (-16, 6), "fud_ada": (-26, 7), "fud_ada_no_debt": (-28, -9),
            "rr": (5, 2), "wrr": (5, -6), "priority": (-28, 5), "debt": (-18, -9),
        },
        "bursty": {
            "fifo": (-24, -2), "pf": (4, -3), "fud": (-20, 5), "aoi_gain": (5, 2),
            "edf": (-16, 6), "fud_ada": (5, -3), "fud_ada_no_debt": (-30, -8),
            "rr": (4, 3), "wrr": (5, -6), "priority": (-12, 6), "debt": (4, -4),
        },
    }
    for ax, (sc, title) in zip(axes, [("congestion", "(a) Congestion (Held-Out Seeds 300–319)"), ("bursty", "(b) Bursty 4× Arrivals (Seeds 300–319)")]):
        for p in pols_plot:
            r = next(x for x in summary if x["cohort"] == "synthetic_stress" and x["scenario"] == sc and x["policy"] == p)
            x = float(r["mean_aoi_s"])
            y = float(r["event_deadline_miss"]) * 100.0
            if p in STYLES:
                st = STYLES[p]
                ax.scatter(x, y, color=st["color"], marker=st["marker"], s=58 if p == "fud_ada" else 34,
                           edgecolors="#111111" if p == "fud_ada" else "none", linewidths=0.7, zorder=st["zorder"])
            else:
                st = extra_styles[p]
                ax.scatter(x, y, color=st["color"], marker=st["marker"], s=26, zorder=3)
            dx, dy = lbl_offsets[sc].get(p, (4, 2))
            name_disp = {"fud_ada": "FUD-Ada", "fud_ada_no_debt": "NoDebt", "aoi_gain": "AoI-Gain", "fud": "FUD-Quad",
                         "edf": "EDF", "fifo": "FIFO", "pf": "PF", "rr": "RR", "wrr": "WRR", "priority": "Prio", "debt": "Debt"}[p]
            ax.annotate(name_disp, (x, y), xytext=(dx, dy), textcoords="offset points",
                        fontsize=6.3, fontweight="bold" if p == "fud_ada" else "normal",
                        color="#004488" if p == "fud_ada" else "#222222")
        ax.set(title=title, xlabel="State Mean AoI (s) ↓", ylabel="Event Deadline Miss (%) ↓")
        ax.grid(True)
    axes[0].set_xlim(1.5, 13.5); axes[0].set_ylim(24, 103)
    axes[1].set_xlim(5.52, 6.60); axes[1].set_ylim(3, 40)
    axes[0].text(0.97, 0.95, "MaxWeight off-scale:\nAoI=103.2s, Miss=38.0%", transform=axes[0].transAxes,
                 ha="right", va="top", fontsize=6.2, color="#cc4411", bbox=dict(fc="white", ec="#cccccc", pad=2.2))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.88, wspace=0.22)
    _save_both(fig, "fig02_pareto_stress")


def build_fig03_e220(metrics: list[dict]) -> None:
    regimes = ["e220_random_20_congestion", "e220_random_30_congestion", "e220_burst_20_congestion", "e220_burst_30_congestion"]
    reg_lbls = ["Rand 20%", "Rand 30%", "Burst 20%", "Burst 30%"]
    pols = ["fifo", "edf", "pf", "aoi_gain", "fud", "fud_ada_no_debt", "fud_ada"]

    ci_miss = _cluster_ci(metrics, lambda r: r["cohort"] == "e220_hw_trace", lambda r: (r["scenario"], r["policy"]), "event_deadline_miss")
    ci_aoi = _cluster_ci(metrics, lambda r: r["cohort"] == "e220_hw_trace", lambda r: (r["scenario"], r["policy"]), "mean_aoi_s")
    ci_wj = _cluster_ci(metrics, lambda r: r["cohort"] == "e220_hw_trace", lambda r: (r["scenario"], r["policy"]), "jain_weighted_service_share")

    fig, axes = plt.subplots(1, 3, figsize=(IEEE_W, 2.50))
    x = np.arange(len(regimes))
    for p in pols:
        st = STYLES[p]
        for ax, cid, mult in [(axes[0], ci_miss, 100.0), (axes[1], ci_aoi, 1.0), (axes[2], ci_wj, 1.0)]:
            ys = [cid[(reg, p)][0] * mult for reg in regimes]
            los = [cid[(reg, p)][1] * mult for reg in regimes]
            his = [cid[(reg, p)][2] * mult for reg in regimes]
            ax.errorbar(x, ys, yerr=[los, his], capsize=1.8, elinewidth=0.65, **st)

    axes[0].set(title="(a) Event Deadline Miss", ylabel="Event Miss (%) ↓", ylim=(44, 102))
    axes[1].set(title="(b) State Freshness", ylabel="State Mean AoI (s) ↓", ylim=(1.5, 16.5))
    axes[2].set(title="(c) Weighted Fairness", ylabel="Weighted Jain Index ↑", ylim=(0.50, 1.02))
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(reg_lbls, rotation=16, ha="right")
        ax.grid(True)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 1.00), handlelength=1.7, columnspacing=1.0, handletextpad=0.35)
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.19, top=0.77, wspace=0.28)
    _save_both(fig, "fig03_e220_hardware_traces")


def build_fig04_intel_and_h3(summary: list[dict], effects: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(IEEE_W, 2.55), gridspec_kw={"width_ratios": [1.18, 1.0]})

    # Panel (a): Intel Berkeley Real Multi-Flow x E220 (12 held-out dates)
    pols = ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt", "fud_ada"]
    offsets = {
        "fifo": (4, -6), "pf": (4, -3), "fud": (4, -3), "aoi_gain": (-20, -10),
        "fud_ada": (5, -2), "fud_ada_no_debt": (5, -9), "edf": (-14, 5), "maxweight": (-36, -10),
    }
    for p in pols:
        r = next(x for x in summary if x["cohort"] == "intel_real_traffic" and x["scenario"] == "ALL_POOLED" and x["policy"] == p)
        x = float(r["mean_aoi_s"]); y = float(r["event_deadline_miss"]) * 100.0
        st = STYLES[p]
        axes[0].scatter(x, y, color=st["color"], marker=st["marker"], s=58 if p == "fud_ada" else 34,
                        edgecolors="#111111" if p == "fud_ada" else "none", linewidths=0.7, zorder=st["zorder"])
        dx, dy = offsets[p]
        short = {"fud_ada": "FUD-Ada", "fud_ada_no_debt": "NoDebt", "aoi_gain": "AoI-Gain", "fud": "FUD-Quad",
                 "edf": "EDF", "fifo": "FIFO", "pf": "PF", "maxweight": "MaxWeight"}[p]
        axes[0].annotate(short, (x, y), xytext=(dx, dy), textcoords="offset points",
                         fontsize=6.4, fontweight="bold" if p == "fud_ada" else "normal",
                         color="#004488" if p == "fud_ada" else "#222222")
    axes[0].set(title="(a) Real 54-Mote Intel Traffic × E220 (12 Days)", xlabel="State Mean AoI (s) ↓", ylabel="Event Deadline Miss (%) ↓",
                xlim=(14, 88), ylim=(54, 103))
    axes[0].grid(True)

    # Panel (b): Debt-Fairness Ablation (FUD-Ada vs FUD-Ada-NoDebt) across all 3 cohorts vs FUD-Quad
    cats = ["FUD-Quad\n(Cong.)", "FUD-Ada\nSynth Cong.", "FUD-Ada\nE220 Cong.", "FUD-Ada\nIntel Real"]
    # Frozen FUD H3 from REPORT.md: raw +0.00052, weighted +0.00031
    def _get_eff(coh, sub, met):
        r = next(x for x in effects if x["cohort"] == coh and x["subset"] == sub and x["reference"] == "fud_ada_no_debt" and x["metric"] == met)
        return float(r["mean_diff"])
    raw_d = [0.00052, _get_eff("synthetic_stress", "congestion", "jain_service_share"),
             _get_eff("e220_hw_trace", "ALL_CONGESTION", "jain_service_share"),
             _get_eff("intel_real_traffic", "ALL_POOLED", "jain_service_share")]
    w_d = [0.00031, _get_eff("synthetic_stress", "congestion", "jain_weighted_service_share"),
           _get_eff("e220_hw_trace", "ALL_CONGESTION", "jain_weighted_service_share"),
           _get_eff("intel_real_traffic", "ALL_POOLED", "jain_weighted_service_share")]
    xb = np.arange(len(cats))
    b1 = axes[1].bar(xb - 0.175, raw_d, width=0.31, color="#004488", edgecolor="#222222", lw=0.5, label=r"$\Delta$ Raw Jain ↑")
    b2 = axes[1].bar(xb + 0.175, w_d, width=0.31, color="#228833", edgecolor="#222222", lw=0.5, hatch="///", alpha=0.88, label=r"$\Delta$ Weighted Jain ↑")
    for idx_b, bars in enumerate((b1, b2)):
        for i_bar, bar in enumerate(bars):
            h = bar.get_height()
            if i_bar == 0:
                x_off = -0.055 if idx_b == 0 else 0.055
            else:
                x_off = -0.025 if idx_b == 0 else 0.025
            axes[1].text(bar.get_x() + bar.get_width()/2 + x_off, h + 0.0028, f"{h:.3f}", ha="center", va="bottom", fontsize=5.6)
    axes[1].axhline(0.0, color="#222222", lw=0.7)
    axes[1].set(title="(b) Debt Fairness Gain (All $p_{\\mathrm{Holm}}<0.04$)", xticks=xb, xticklabels=cats,
                ylabel="Paired Jain Gain (Full − NoDebt)", ylim=(-0.005, 0.118))
    axes[1].grid(axis="y")
    axes[1].legend(fontsize=6.4, loc="upper center", ncol=2, frameon=True, framealpha=0.94, borderpad=0.25, columnspacing=0.8)

    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.20, top=0.88, wspace=0.26)
    _save_both(fig, "fig04_intel_real_traffic")


def build_fig05_c11() -> None:
    bench = json.loads((OUT_C11 / "benchmark.json").read_text())
    esp_bench = json.loads((OUT_C11 / "esp32s3_onchip_benchmark.json").read_text())
    scales = [8, 24, 48, 96]

    def _esp_ms(pol: str) -> list[float]:
        return [
            next(x["full_us"] for x in esp_bench["benchmarks"] if x["policy"] == pol and x["n_flows"] == n) / 1000.0
            for n in scales
        ]

    fig, axes = plt.subplots(1, 2, figsize=(IEEE_W, 2.32))
    axes[0].plot(scales, _esp_ms("fud_ada"), "o-", color="#004488", lw=1.7, ms=4.8, label="FUD-Ada (ESP32-S3)")
    axes[0].plot(scales, _esp_ms("fud"), "s-", color="#228833", lw=1.35, ms=4.3, label="FUD-Quad")
    axes[0].plot(scales, _esp_ms("edf"), "^--", color="#cc3311", lw=1.15, ms=4.0, label="EDF")
    axes[0].plot(scales, _esp_ms("aoi_gain"), "D-.", color="#aa3377", lw=1.1, ms=3.7, label="AoI-Gain")
    axes[0].plot(scales, _esp_ms("fifo"), "*:", color="#666666", lw=1.1, ms=4.4, label="FIFO")
    ada_ms = _esp_ms("fud_ada")
    for n, va in zip(scales, ada_ms):
        x_txt = n + (1.2 if n == 8 else (-5.0 if n == 96 else 0.0))
        y_off = 0.24 if n == 8 else (0.14 if n != 96 else 0.13)
        axes[0].text(x_txt, va + y_off, f"{va:.2f} ms", ha="center", va="bottom", fontsize=6.4, color="#004488", fontweight="bold",
                     bbox=dict(fc="white", ec="none", alpha=0.78, pad=0.3))
    axes[0].set(title="(a) Real ESP32-S3 (240 MHz) Per-Slot Latency ($O(N)$)", xlabel="Active Concurrent Flows ($N$)",
                ylabel="Measured On-Chip Latency (ms)", xticks=scales, xlim=(1, 105), ylim=(0, 3.45))
    axes[0].text(0.97, 0.54, "<2.91% of 100 ms slot\n(SW FP64, 0 B heap delta)", transform=axes[0].transAxes,
                 ha="right", va="center", fontsize=6.1, color="#004488",
                 bbox=dict(fc="#f4f8fc", ec="#b0c4de", pad=2.0))
    axes[0].grid(True)
    axes[0].legend(fontsize=6.3, loc="upper left", frameon=True, ncol=1, borderpad=0.25)

    # Panel (b): ESP32-S3 static resource footprint bar chart
    items = ["Static RAM\n(96 flows)", "ESP32-S3\nFlash (-Os)", "Runtime Heap\nDelta", "Static .data\n& .bss"]
    kb = [bench["static_ram"]["sizeof_na_sched_t"] / 1024.0,
          bench["esp32s3_cross_compile"]["netadapt_sched_o"]["text_bytes"] / 1024.0,
          float(esp_bench["heap_check"]["delta"]) / 1024.0, 0.0]
    cols = ["#004488", "#228833", "#cccccc", "#cccccc"]
    bars = axes[1].bar(range(len(items)), kb, width=0.52, color=cols, edgecolor="#222222", lw=0.6)
    for b, v in zip(bars, kb):
        lbl = f"{v:.2f} KB" if v > 0 else "0 B"
        axes[1].text(b.get_x() + b.get_width()/2, v + 0.16, lbl, ha="center", va="bottom", fontsize=7.0, fontweight="bold")
    axes[1].set(title="(b) ESP32-S3 Zero-Allocation C11 Footprint", xticks=range(len(items)), xticklabels=items,
                ylabel="Memory Size (KB)", ylim=(0, 5.6))
    axes[1].grid(axis="y")

    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.22, top=0.87, wspace=0.24)
    _save_both(fig, "fig05_c11_scaling")


def build_graphical_abstract(summary: list[dict], effects: list[dict]) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.8})
    fig = plt.figure(figsize=(14.5, 5.4), facecolor="white")
    fig.text(0.5, 0.945, "NetAdapt-IoT (FUD-Ada): Scale-Matched Multi-Flow IoT Gateway Scheduling for AoI, Deadlines & Fairness",
             ha="center", va="center", fontsize=12.0, fontweight="bold", color="#112233")
    fig.text(0.5, 0.892, "Graphical Abstract  |  17,820 Runs (15 Policies)  ·  24 Real E220 Traces  ·  54-Mote Intel Berkeley Traffic  ·  4.52 KB ESP32-S3 C11 Kernel",
             ha="center", va="center", fontsize=8.9, color="#445566")

    # Panel 1: Architecture / Formula Card
    ax1 = fig.add_axes([0.02, 0.11, 0.27, 0.72])
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis("off")
    ax1.add_patch(FancyBboxPatch((0.35, 0.35), 9.3, 9.3, boxstyle="round,pad=0.22", fc="#f4f7fb", ec="#004488", lw=1.4))
    ax1.text(5.0, 9.05, "1. Scale-Matched FUD-Ada (C11)", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#004488")
    cards = [
        (7.35, "#e8eef5", "#335577", "Sub-Quadratic State Freshness\n$F_i = w_i \\sqrt{G_i}$"),
        (5.20, "#dbeafe", "#004488", "Deadline-Feasible Urgency\n$U_i = w_i(1+v_p/\\tau_i)(1+1/(1+\\sigma_p))$"),
        (3.05, "#e6f4ea", "#1b6e35", "Lyapunov-Scaled Service Debt\n$D_i = 2.5\\,w_i\\ln(1 + d_i)$"),
        (1.25, "#fff4e5", "#b25e09", "ESP32-S3 Silicon (240 MHz): 0.20–2.91 ms\n4.52 KB RAM | 2.68 KB Flash | 0 B Heap"),
    ]
    for y, fc, ec, txt in cards:
        ax1.add_patch(FancyBboxPatch((0.85, y - 0.62), 8.3, 1.48, boxstyle="round,pad=0.14", fc=fc, ec=ec, lw=1.0))
        ax1.text(5.0, y + 0.12, txt, ha="center", va="center", fontsize=8.0, color="#111111")

    # Panel 2: Real E220 Congestion Benchmark
    ax2 = fig.add_axes([0.355, 0.17, 0.255, 0.61])
    pols = ["fifo", "fud", "aoi_gain", "edf", "fud_ada"]
    lbls = ["FIFO", "FUD-\nQuad", "AoI-Gain", "EDF", "FUD-Ada\n(Ours)"]
    misses = [next(float(x["event_deadline_miss"]) * 100 for x in summary if x["cohort"] == "e220_hw_trace" and x["scenario"] == "ALL_CONGESTION" and x["policy"] == p) for p in pols]
    aois = [next(float(x["mean_aoi_s"]) for x in summary if x["cohort"] == "e220_hw_trace" and x["scenario"] == "ALL_CONGESTION" and x["policy"] == p) for p in pols]
    cols = ["#777777", "#228833", "#aa3377", "#cc3311", "#004488"]
    x = np.arange(len(pols))
    bars = ax2.bar(x, misses, width=0.52, color=cols, alpha=0.88)
    ax2.set_ylim(35, 108); ax2.set_xticks(x); ax2.set_xticklabels(lbls, fontsize=8.0)
    ax2.set_ylabel("Event Deadline Miss (%) [bars]", color="#004488", fontweight="bold", fontsize=8.4)
    ax2.set_title("2. Real E220 Traces (Congestion)", fontsize=10.0, fontweight="bold", color="#004488", pad=8)
    ax2.spines["top"].set_visible(False); ax2.grid(axis="y", alpha=0.22)
    for idx_m, (b, v) in enumerate(zip(bars, misses)):
        y_pos = v - 5.2 if idx_m == 2 else v + 1.2
        txt_col = "white" if idx_m == 2 else "#111111"
        ax2.text(b.get_x() + b.get_width()/2, y_pos, f"{v:.1f}%", ha="center", va="bottom", fontsize=7.6, fontweight="bold", color=txt_col)
    ax2b = ax2.twinx()
    ax2b.plot(x, aois, "o--", color="#cc3311", lw=2.0, ms=5.5)
    ax2b.set_ylim(0, 17.5); ax2b.set_ylabel("State Mean AoI (s) [line]", color="#cc3311", fontweight="bold", fontsize=8.4)
    ax2b.spines["top"].set_visible(False)
    for xi, av in zip(x, aois):
        ax2b.text(xi, av + 0.85, f"{av:.1f}s", ha="center", va="bottom", fontsize=7.6, color="#cc3311", fontweight="bold",
                  bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.88))
    ax2.text(0.5, -0.23, "Lowest event miss of all 14 comparators (p_Holm=0.0096); -4.2s AoI vs EDF",
             transform=ax2.transAxes, ha="center", fontsize=7.6, color="#333333", style="italic")

    # Panel 3: Real 54-Mote Intel Berkeley + H3
    ax3 = fig.add_axes([0.72, 0.17, 0.26, 0.61])
    pols3 = ["fifo", "fud", "maxweight", "edf", "fud_ada"]
    lbls3 = ["FIFO", "FUD-\nQuad", "MaxWt", "EDF", "FUD-Ada\n(Ours)"]
    m3 = [next(float(x["event_deadline_miss"]) * 100 for x in summary if x["cohort"] == "intel_real_traffic" and x["scenario"] == "ALL_POOLED" and x["policy"] == p) for p in pols3]
    wj3 = [next(float(x["jain_weighted_service_share"]) * 100 for x in summary if x["cohort"] == "intel_real_traffic" and x["scenario"] == "ALL_POOLED" and x["policy"] == p) for p in pols3]
    x3 = np.arange(len(pols3)); w = 0.36
    b3m = ax3.bar(x3 - w/2, m3, width=w, color="#cc3311", alpha=0.82, label="Event Miss (%) ↓")
    b3j = ax3.bar(x3 + w/2, wj3, width=w, color="#004488", alpha=0.90, label="Weighted Jain (%) ↑")
    for b, v in zip(b3m, m3):
        ax3.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=6.9, color="#aa2200", fontweight="bold")
    for b, v in zip(b3j, wj3):
        ax3.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=6.9, color="#003366", fontweight="bold")
    ax3.set_ylim(0, 122); ax3.set_xticks(x3); ax3.set_xticklabels(lbls3, fontsize=8.0)
    ax3.set_ylabel("Rate / Fairness (%)", fontweight="bold", fontsize=8.4)
    ax3.set_title("3. Real 54-Mote Intel Traffic × E220", fontsize=10.0, fontweight="bold", color="#004488", pad=8)
    ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False); ax3.grid(axis="y", alpha=0.22)
    ax3.legend(fontsize=7.3, loc="upper right", frameon=True)
    ax3.text(0.5, -0.23, "Strict 4-metric Pareto win vs EDF & MaxWt; Debt ablation solved (+0.059 Jain)",
             transform=ax3.transAxes, ha="center", fontsize=7.6, color="#333333", style="italic")

    out_p = Path(__file__).resolve().parent
    fig.savefig(out_p / "graphical_abstract.png", dpi=220)
    fig.savefig(out_p / "graphical_abstract.pdf")
    plt.close(fig)


if __name__ == "__main__":
    summary = _load_csv(OUT_P2 / "summary.csv")
    metrics = _load_csv(OUT_P2 / "metrics.csv")
    effects = _load_csv(OUT_P2 / "paired_effects.csv")
    build_fig02_pareto(summary)
    build_fig03_e220(metrics)
    build_fig04_intel_and_h3(summary, effects)
    build_fig05_c11()
    build_graphical_abstract(summary, effects)
    print("Built all 4 IEEE vector figures + PNGs + Graphical Abstract cleanly.")
