#!/usr/bin/env python3
"""Phase 2 held-out benchmark for NetAdapt-IoT (zero pandas dependency, stdlib + numpy):
  Cohort 1: Held-out synthetic stress matrix (seeds 300-319, 8 scenarios x 15 policies = 2,400 runs)
  Cohort 2: Real ESP32-S3 + E220 hardware loss traces (seeds 300-319, 8 regimes x 15 policies = 2,400 runs)
  Cohort 3: Real 54-mote MIT Intel Berkeley multi-flow workload x real E220 traces (12 held-out days x 3 links x 15 policies = 540 runs)
"""
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import replace
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netadapt.ext import (
    EXTENDED_POLICIES,
    build_e220_trace,
    build_intel_berkeley_multiflow_trace,
    load_e220_regimes,
    select_intel_berkeley_motes,
    simulate_extended,
)
from netadapt.ext.real_traces import load_intel_berkeley_day_arrivals
from netadapt.model import Config, study_scenarios
from netadapt.traffic import generate

OUT_DIR = ROOT / "output/phase2_validation"
SEEDS = list(range(300, 320))
CALIB_DATES = {"2004-02-28", "2004-02-29", "2004-03-01"}
HELDOUT_DATES = [
    "2004-03-03", "2004-03-04", "2004-03-05", "2004-03-06",
    "2004-03-07", "2004-03-08", "2004-03-09", "2004-03-10",
    "2004-03-11", "2004-03-12", "2004-03-13", "2004-03-14",
]


def _find_intel_berkeley() -> tuple[Path, Path]:
    for base in (ROOT / "data/raw/intel_berkeley", Path("/Users/mac/Documents/TAIS/data/raw/intel_berkeley")):
        gz = base / "data.txt.gz"
        locs = base / "mote_locs.txt"
        if gz.is_file() and locs.is_file():
            return gz, locs
    raise FileNotFoundError("Intel Berkeley data.txt.gz and mote_locs.txt not found.")


def _extract_row(cohort: str, scenario: str, cluster_id: str, policy: str, r: dict) -> dict:
    return dict(
        cohort=cohort,
        scenario=scenario,
        cluster_id=cluster_id,
        policy=policy,
        mean_aoi_s=r["mean_aoi_s"],
        normalized_aoi=r["normalized_aoi"],
        event_deadline_miss=r["event_deadline_miss"],
        event_deadline_success=r["event_deadline_success"],
        event_p95_latency_s=r["event_p95_latency_s"],
        jain_service_share=r["jain_service_share"],
        jain_weighted_service_share=r["jain_weighted_service_share"],
        state_transmission_success=r["state_transmission_success"],
        state_replacement_rate=r["state_replacement_rate"],
        goodput_bps=r["goodput_bps"],
        attempts=r["attempts"],
        e220_airtime_s=r.get("e220_airtime_s", r["attempts"] * 0.0304),
        utilization=r["utilization"],
    )


def _run_seed_worker(seed: int) -> list[dict]:
    rows = []
    sc_map = {s.name: s for s in study_scenarios(Config())}
    synth_names = ["normal", "congestion", "bursty", "nodes_48", "nodes_96", "weak_link", "markov_link", "budget_40"]
    for name in synth_names:
        c = sc_map[name]
        tr = generate(c, seed)
        for pol in EXTENDED_POLICIES:
            r = simulate_extended(c, tr, pol, seed)
            rows.append(_extract_row("synthetic_stress", name, str(seed), pol, r))

    regimes = load_e220_regimes()
    for reg_id in ("e220_random_20", "e220_random_30", "e220_burst_20", "e220_burst_30"):
        hw_runs = regimes[reg_id]
        for load_tag, rate in (("normal", 0.015), ("congestion", 0.10)):
            sc_name = f"{reg_id}_{load_tag}"
            c = Config(name=sc_name, rate=rate)
            tr, airtime = build_e220_trace(c, hw_runs, seed)
            for pol in EXTENDED_POLICIES:
                r = simulate_extended(c, tr, pol, seed, airtime_per_attempt_s=airtime)
                rows.append(_extract_row("e220_hw_trace", sc_name, str(seed), pol, r))
    return rows


def _run_intel_date_worker(date: str, day_records: dict, motes: list[int]) -> list[dict]:
    rows = []
    regimes = load_e220_regimes()
    date_seed = int(hashlib.sha256(date.encode()).hexdigest()[:8], 16) % 100000
    c = Config(name=f"intel_{date}", nodes=len(motes), slots=4000, warmup=500, duty=0.55)
    link_specs = [
        ("intel_lossless", None),
        ("intel_e220_burst_20", regimes["e220_burst_20"]),
        ("intel_e220_random_30", regimes["e220_random_30"]),
    ]
    for lname, hw_runs in link_specs:
        tr, airtime = build_intel_berkeley_multiflow_trace(
            replace(c, name=lname), day_records, motes, hw_runs, seed=date_seed
        )
        for pol in EXTENDED_POLICIES:
            r = simulate_extended(replace(c, name=lname), tr, pol, date_seed, airtime_per_attempt_s=airtime)
            rows.append(_extract_row("intel_real_traffic", lname, date, pol, r))
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def _mean_finite(vals) -> float | None:
    arr = [float(v) for v in vals if v is not None]
    return float(np.mean(arr)) if arr else None


def holm(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, p[idx] * (m - rank))
        running = max(running, val)
        adj[idx] = running
    return [float(x) for x in adj]


def _paired_cluster_test(sub_rows: list[dict], pol_a: str, pol_b: str, metric: str, seed: int = 2026112601):
    by_cl_pol: dict[tuple[str, str], list[float]] = defaultdict(list)
    clusters = set()
    for r in sub_rows:
        if r["policy"] in (pol_a, pol_b) and r[metric] is not None:
            by_cl_pol[(r["cluster_id"], r["policy"])].append(float(r[metric]))
            clusters.add(r["cluster_id"])
    deltas = []
    for cl in sorted(clusters):
        va = by_cl_pol.get((cl, pol_a), [])
        vb = by_cl_pol.get((cl, pol_b), [])
        if va and vb:
            deltas.append(float(np.mean(va)) - float(np.mean(vb)))
    delta = np.asarray(deltas, dtype=float)
    n = len(delta)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, n, size=(5000, n))
    signs = rng.choice([-1, 1], size=(20000, n))
    point = float(delta.mean())
    lo, hi = np.percentile(delta[draw].mean(axis=1), [2.5, 97.5])
    p = (1 + np.count_nonzero(np.abs(signs @ delta / n) >= abs(point) - 1e-12)) / (len(signs) + 1)
    return point, float(lo), float(hi), float(p), n


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data_gz, locs_txt = _find_intel_berkeley()
    motes = select_intel_berkeley_motes(data_gz, locs_txt, CALIB_DATES, k=24)
    print("Calibration-selected top-24 Intel Berkeley motes:", motes, flush=True)
    ib_days = load_intel_berkeley_day_arrivals(data_gz, set(HELDOUT_DATES), motes)

    all_rows = []
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context("spawn")) as pool:
        futs = [pool.submit(_run_seed_worker, s) for s in SEEDS]
        futs += [pool.submit(_run_intel_date_worker, d, ib_days[d], motes) for d in HELDOUT_DATES]
        for fut in as_completed(futs):
            all_rows.extend(fut.result())

    all_rows.sort(key=lambda r: (r["cohort"], r["scenario"], r["cluster_id"], r["policy"]))
    _write_csv(OUT_DIR / "metrics.csv", all_rows)

    agg_cols = [
        "mean_aoi_s", "normalized_aoi", "event_deadline_miss", "event_deadline_success",
        "event_p95_latency_s", "jain_service_share", "jain_weighted_service_share",
        "state_transmission_success", "goodput_bps", "attempts", "e220_airtime_s",
    ]
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    pooled: dict[tuple[str, str], list[dict]] = defaultdict(list)
    e220_cong: dict[str, list[dict]] = defaultdict(list)
    for r in all_rows:
        groups[(r["cohort"], r["scenario"], r["policy"])].append(r)
        pooled[(r["cohort"], r["policy"])].append(r)
        if r["cohort"] == "e220_hw_trace" and r["scenario"].endswith("_congestion"):
            e220_cong[r["policy"]].append(r)

    summary_rows = []
    for (coh, sc, pol), g in sorted(groups.items()):
        row = dict(cohort=coh, scenario=sc, policy=pol, runs=len(g))
        for col in agg_cols:
            row[col] = _mean_finite([x[col] for x in g])
        summary_rows.append(row)
    for (coh, pol), g in sorted(pooled.items()):
        row = dict(cohort=coh, scenario="ALL_POOLED", policy=pol, runs=len(g))
        for col in agg_cols:
            row[col] = _mean_finite([x[col] for x in g])
        summary_rows.append(row)
    for pol, g in sorted(e220_cong.items()):
        row = dict(cohort="e220_hw_trace", scenario="ALL_CONGESTION", policy=pol, runs=len(g))
        for col in agg_cols:
            row[col] = _mean_finite([x[col] for x in g])
        summary_rows.append(row)
    _write_csv(OUT_DIR / "summary.csv", summary_rows)

    effects = []
    test_specs = [
        ("synthetic_stress", "congestion", ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("synthetic_stress", "bursty", ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("synthetic_stress", "budget_40", ["fifo", "edf", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("synthetic_stress", "nodes_96", ["fifo", "edf", "maxweight", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("e220_hw_trace", "ALL_CONGESTION", ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("e220_hw_trace", "ALL_NORMAL", ["fifo", "edf", "aoi_gain", "fud"]),
        ("intel_real_traffic", "ALL_POOLED", ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt"]),
        ("intel_real_traffic", "intel_e220_random_30", ["fifo", "edf", "aoi_gain", "fud", "fud_ada_no_debt"]),
    ]
    for cohort, sc_sel, refs in test_specs:
        if sc_sel == "ALL_POOLED":
            sub = [r for r in all_rows if r["cohort"] == cohort]
        elif sc_sel == "ALL_CONGESTION":
            sub = [r for r in all_rows if r["cohort"] == cohort and r["scenario"].endswith("_congestion")]
        elif sc_sel == "ALL_NORMAL":
            sub = [r for r in all_rows if r["cohort"] == cohort and r["scenario"].endswith("_normal")]
        else:
            sub = [r for r in all_rows if r["cohort"] == cohort and r["scenario"] == sc_sel]
        for ref in refs:
            for met in ("event_deadline_miss", "mean_aoi_s", "jain_service_share", "jain_weighted_service_share"):
                pt, lo, hi, p, n_cl = _paired_cluster_test(sub, "fud_ada", ref, met)
                effects.append(
                    dict(
                        cohort=cohort, subset=sc_sel, policy="fud_ada", reference=ref,
                        metric=met, n_clusters=n_cl, mean_diff=pt, ci95_low=lo, ci95_high=hi,
                        p_signflip=p,
                    )
                )
    padj = holm([e["p_signflip"] for e in effects])
    for e, ph in zip(effects, padj):
        e["p_holm"] = ph
        e["holm_sig_005"] = ph < 0.05
    _write_csv(OUT_DIR / "paired_effects.csv", effects)

    manifest = dict(
        status="COMPLETE",
        total_runs=len(all_rows),
        policies=list(EXTENDED_POLICIES),
        heldout_seeds=SEEDS,
        intel_calib_dates=sorted(CALIB_DATES),
        intel_heldout_dates=HELDOUT_DATES,
        intel_motes_24=motes,
        fud_ada_params=dict(alpha_u=1.0, beta_d=2.5),
    )
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"\nCOMPLETED {len(all_rows)} PHASE 2 HELD-OUT RUNS.")
    show_pols = ["fifo", "edf", "maxweight", "pf", "aoi_gain", "fud", "fud_ada_no_debt", "fud_ada"]
    for label, coh, sc in [
        ("SYNTH CONGESTION", "synthetic_stress", "congestion"),
        ("SYNTH BURSTY", "synthetic_stress", "bursty"),
        ("E220 ALL CONGESTION", "e220_hw_trace", "ALL_CONGESTION"),
        ("INTEL REAL ALL POOLED", "intel_real_traffic", "ALL_POOLED"),
    ]:
        print(f"\n=== {label} ===")
        print(f"{'policy':16s} | {'AoI(s)':>7s} | {'EvMiss%':>7s} | {'Jain':>6s} | {'WJain':>6s} | {'Airtime':>7s}")
        for pol in show_pols:
            r = next(x for x in summary_rows if x["cohort"] == coh and x["scenario"] == sc and x["policy"] == pol)
            print(f"{pol:16s} | {r['mean_aoi_s']:7.2f} | {r['event_deadline_miss']*100:7.2f} | {r['jain_service_share']:6.4f} | {r['jain_weighted_service_share']:6.4f} | {r['e220_airtime_s']:7.2f}")

    print("\n=== KEY HOLM EFFECTS (FUD-Ada vs Refs) ===")
    for e in effects:
        if e["subset"] in ("congestion", "bursty", "ALL_CONGESTION", "ALL_POOLED") and e["reference"] in ("fifo", "edf", "aoi_gain", "fud", "fud_ada_no_debt"):
            print(f"{e['cohort']:18s} {e['subset']:14s} vs {e['reference']:15s} {e['metric']:26s} diff={e['mean_diff']:+8.4f} p_holm={e['p_holm']:.4f} sig={e['holm_sig_005']}")


if __name__ == "__main__":
    main()
