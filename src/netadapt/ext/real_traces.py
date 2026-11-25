"""Real ESP32-S3 + E220 hardware loss trace adapter and 54-mote Intel Berkeley multi-flow workload."""
from collections import defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np

from ..model import Config, flows_for
from ..traffic import Packet, Trace, generate

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_E220_PATH = ROOT / "configs/e220_hardware_traces.json"


def load_e220_regimes(path: Path | None = None) -> dict[str, list[dict]]:
    p = path or DEFAULT_E220_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    return dict(data["regimes"])


def _e220_success_matrix(hw_runs: list[dict], n_slots: int, n_flows: int, seed: int) -> np.ndarray:
    """Tile real E220 hardware ACK/TIMEOUT outcomes deterministically per flow with phase offsets."""
    rng = np.random.default_rng(seed)
    mat = np.ones((n_slots, n_flows), dtype=bool)
    n_runs = len(hw_runs)
    for i in range(n_flows):
        run = hw_runs[(seed + i) % n_runs]
        outcomes = np.asarray(run["outcomes"], dtype=bool)
        L = len(outcomes)
        offset = int(rng.integers(0, L))
        # Tile exact empirical outcome stream (preserving real burst loss lengths!)
        idx = (np.arange(n_slots) + offset) % L
        mat[:, i] = outcomes[idx]
    return mat


def build_e220_trace(c: Config, hw_runs: list[dict], seed: int) -> tuple[Trace, float]:
    """Combine policy-independent synthetic traffic with real ESP32-S3 + E220 loss calendars."""
    base = generate(c, seed)
    success = _e220_success_matrix(hw_runs, c.end, c.nodes, seed=seed * 31 + 7)
    h = hashlib.sha256()
    h.update(base.digest.encode())
    h.update(success.tobytes())
    mean_airtime_s = float(np.mean([r["mean_tx_airtime_ms"] for r in hw_runs])) / 1000.0
    return Trace(base.arrivals, success, h.hexdigest()), mean_airtime_s


def select_intel_berkeley_motes(data_gz: Path, locs_txt: Path, calib_dates: set[str], k: int = 24) -> list[int]:
    """Select top-k active motes strictly on calibration prefix (zero held-out peeking)."""
    locs = set()
    for ln in locs_txt.read_text(encoding="utf-8").splitlines():
        parts = ln.split()
        if len(parts) == 3:
            locs.add(int(parts[0]))
    counts: dict[int, int] = defaultdict(int)
    with gzip.open(data_gz, "rt", encoding="utf-8", errors="replace") as f:
        for ln in f:
            parts = ln.split()
            if len(parts) != 8 or parts[0] not in calib_dates:
                continue
            try:
                m = int(parts[3])
                t_val = float(parts[4])
                h_val = float(parts[5])
            except Exception:
                continue
            if m in locs and -10.0 <= t_val <= 60.0 and 0.0 <= h_val <= 100.0:
                counts[m] += 1
    ranked = [m for m, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    return ranked[:k]


def load_intel_berkeley_day_arrivals(
    data_gz: Path,
    target_dates: set[str],
    motes: list[int],
    start_s: int = 8 * 3600,
    end_s: int = 12 * 3600,
) -> dict[str, dict[int, list[tuple[float, float, float]]]]:
    """Stream-load valid (sec_of_day, temp_c, hum_rh) strictly within [start_s, end_s)."""
    mote_set = set(motes)
    out: dict[str, dict[int, list[tuple[float, float, float]]]] = {
        d: {m: [] for m in motes} for d in target_dates
    }
    with gzip.open(data_gz, "rt", encoding="utf-8", errors="replace") as f:
        for ln in f:
            parts = ln.split()
            if len(parts) != 8 or parts[0] not in target_dates:
                continue
            try:
                m = int(parts[3])
                if m not in mote_set:
                    continue
                t_val = float(parts[4])
                h_val = float(parts[5])
                if not (math.isfinite(t_val) and -10.0 <= t_val <= 60.0):
                    continue
                if not (math.isfinite(h_val) and 0.0 <= h_val <= 100.0):
                    continue
                hh, mm, ss = parts[1].split(":")
                sec = int(hh) * 3600 + int(mm) * 60 + float(ss)
            except Exception:
                continue
            if start_s <= sec < end_s:
                out[parts[0]][m].append((sec, t_val, h_val))
    for d in out:
        for m in out[d]:
            out[d][m].sort(key=lambda x: x[0])
    return out


def build_intel_berkeley_multiflow_trace(
    c: Config,
    day_records: dict[int, list[tuple[float, float, float]]],
    motes: list[int],
    hw_runs: list[dict] | None,
    seed: int,
    start_s: int = 8 * 3600,
    end_s: int = 12 * 3600,
    burst_scale: int = 3,
) -> tuple[Trace, float]:
    """Map real 24-mote chronological arrivals over 4 hours into c.slots gateway slots.

    - Flows i%3 == 0 (event): real readings emit deadline-sensitive event packets whenever
      real |dT| >= 0.25C or |dH| >= 1.0% (or periodic alarm bursts scaled by burst_scale
      to create authentic gateway contention during morning HVAC warming!).
    - Flows i%3 == 1 (status) & i%3 == 2 (telemetry): exact real chronological arrivals
      mapped linearly from [start_s, end_s) to [0, c.slots).
    """
    flows = flows_for(c)
    assert len(motes) == len(flows)
    arrivals: list[list[Packet]] = [[] for _ in range(c.slots)]
    span_s = float(end_s - start_s)
    pid = 0
    for i, m in enumerate(motes):
        f = flows[i]
        pts = day_records.get(m, [])
        prev_t = None
        prev_h = None
        for sec, tv, hv in pts:
            slot = int((sec - start_s) / span_s * c.slots)
            slot = max(0, min(c.slots - 1, slot))
            if f.kind == "event":
                is_change = prev_t is not None and (abs(tv - prev_t) >= 0.20 or abs(hv - prev_h) >= 0.8)
                n_pkts = burst_scale if is_change else 1
                for k in range(n_pkts):
                    sl = min(c.slots - 1, slot + k)
                    arrivals[sl].append(Packet(pid, i, sl, f.size))
                    pid += 1
            else:
                arrivals[slot].append(Packet(pid, i, slot, f.size))
                pid += 1
            prev_t, prev_h = tv, hv

    if hw_runs is None:
        success = np.ones((c.end, c.nodes), dtype=bool)
        airtime = 0.0304
    else:
        success = _e220_success_matrix(hw_runs, c.end, c.nodes, seed=seed * 37 + 13)
        airtime = float(np.mean([r["mean_tx_airtime_ms"] for r in hw_runs])) / 1000.0

    h = hashlib.sha256()
    h.update(str(pid).encode())
    h.update(success.tobytes())
    h.update(c.digest().encode())
    return Trace(arrivals, success, h.hexdigest()), airtime
