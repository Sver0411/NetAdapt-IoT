"""Tests for Phase 2 FUD-Ada, real E220 traces, Intel Berkeley multi-flow, and C11 parity."""
import ctypes
import gzip
import heapq
import subprocess
from pathlib import Path

import numpy as np
import pytest

from netadapt.ext import (
    EXTENDED_POLICIES,
    ExtendedScheduler,
    build_e220_trace,
    build_intel_berkeley_multiflow_trace,
    load_e220_regimes,
    simulate_extended,
)
from netadapt.model import Config, flows_for, study_scenarios
from netadapt.queues import Queues
from netadapt.scheduler import pf_update
from netadapt.traffic import generate

ROOT = Path(__file__).resolve().parents[1]
C11_DIR = ROOT / "src/netadapt/c11"


class CFlowCfg(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint16),
        ("kind", ctypes.c_uint8),
        ("weight", ctypes.c_uint8),
        ("tau", ctypes.c_uint16),
        ("deadline", ctypes.c_uint16),
        ("size_bytes", ctypes.c_uint16),
        ("service_slots", ctypes.c_uint16),
    ]


class CHead(ctypes.Structure):
    _fields_ = [
        ("packet_id", ctypes.c_int32),
        ("generated_slot", ctypes.c_int32),
        ("queue_bytes", ctypes.c_uint32),
        ("has_packet", ctypes.c_uint8),
    ]


class CSched(ctypes.Structure):
    _fields_ = [
        ("n_flows", ctypes.c_uint16),
        ("policy", ctypes.c_uint8),
        ("delay_slots", ctypes.c_uint8),
        ("duty", ctypes.c_double),
        ("flows", CFlowCfg * 96),
        ("last_rx_gen", ctypes.c_int32 * 96),
        ("prob", ctypes.c_double * 96),
        ("debt", ctypes.c_double * 96),
        ("throughput", ctypes.c_double * 96),
        ("target_share", ctypes.c_double * 96),
    ]


@pytest.fixture(scope="module")
def c11_lib(tmp_path_factory):
    out_so = tmp_path_factory.mktemp("c11") / "libnetadapt_sched.so"
    cmd = [
        "cc",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-O2",
        "-shared",
        "-fPIC",
        str(C11_DIR / "netadapt_sched.c"),
        "-lm",
        "-o",
        str(out_so),
    ]
    subprocess.run(cmd, check=True)
    lib = ctypes.CDLL(str(out_so))
    lib.na_sched_init.argtypes = [
        ctypes.POINTER(CSched),
        ctypes.c_int,
        ctypes.POINTER(CFlowCfg),
        ctypes.c_uint16,
        ctypes.c_uint8,
        ctypes.c_double,
    ]
    lib.na_sched_on_ack.argtypes = [
        ctypes.POINTER(CSched),
        ctypes.c_uint16,
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.c_uint16,
        ctypes.c_bool,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.na_sched_step_state.argtypes = [
        ctypes.POINTER(CSched),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.na_sched_choose.argtypes = [
        ctypes.POINTER(CSched),
        ctypes.c_int32,
        ctypes.POINTER(CHead),
        ctypes.c_double,
    ]
    lib.na_sched_choose.restype = ctypes.c_int32
    return lib


POLICY_TO_C = {
    "fifo": 0,
    "edf": 1,
    "maxweight": 2,
    "pf": 3,
    "aoi_gain": 4,
    "fud": 5,
    "fud_ada": 6,
    "fud_ada_no_debt": 7,
}
KIND_TO_C = {"event": 0, "status": 1, "telemetry": 2}


@pytest.mark.parametrize("policy", list(POLICY_TO_C.keys()))
@pytest.mark.parametrize("sc_name", ["normal", "congestion", "bursty"])
def test_python_c11_bit_exact_trajectory_parity(c11_lib, policy, sc_name):
    """Verify 100% step-by-step decision & state parity across 24 full trajectories."""
    base = {s.name: s for s in study_scenarios(Config(slots=800, warmup=100))}[sc_name]
    trace = generate(base, seed=299)
    flows = flows_for(base)
    n = len(flows)

    py_q = Queues(flows, base.event_buffer)
    py_sched = ExtendedScheduler(policy, flows)
    last = np.zeros(n, dtype=int)
    prob = np.full(n, 0.8)
    debt = np.zeros(n)
    thr = np.ones(n)
    targets = np.array([
        0.5 * base.duty * 0.8 * f.weight / (sum(x.weight for x in flows) * f.service)
        for f in flows
    ])

    c_state = CSched()
    c_flows = (CFlowCfg * n)()
    for i, f in enumerate(flows):
        c_flows[i] = CFlowCfg(
            id=f.id,
            kind=KIND_TO_C[f.kind],
            weight=f.weight,
            tau=f.tau,
            deadline=f.deadline or 0,
            size_bytes=f.size,
            service_slots=f.service,
        )
    c11_lib.na_sched_init(ctypes.byref(c_state), POLICY_TO_C[policy], c_flows, n, base.delay, base.duty)

    pending = []
    tokens = 0.0
    busy_until = 0
    for t in range(base.end):
        rec = np.zeros(n)
        ackb = np.zeros(n)
        c_rec = (ctypes.c_double * n)()
        c_ackb = (ctypes.c_double * n)()
        while pending and pending[0][0] <= t:
            at, _, p, ok = heapq.heappop(pending)
            i = p.flow
            f = flows[i]
            prob[i] = 0.9 * prob[i] + 0.1 * int(ok)
            if ok:
                fresh = p.generated > last[i]
                timely = f.deadline is None or at <= p.generated + f.deadline
                last[i] = max(last[i], p.generated)
                if timely and (f.kind == "event" or fresh):
                    rec[i] += 1
                ackb[i] += p.size
            c11_lib.na_sched_on_ack(
                ctypes.byref(c_state), i, p.generated, at, p.size, bool(ok), c_rec, c_ackb
            )

        if t < base.slots:
            for p in trace.arrivals[t]:
                py_q.admit(p)
        py_q.expire(t, base.delay)

        back = np.array([bool(q) for q in py_q.items])
        debt = np.minimum(50.0, np.maximum(0.0, debt + targets * back - rec))
        thr = pf_update(thr, ackb)

        c_back = (ctypes.c_uint8 * n)(*[1 if b else 0 for b in back])
        c11_lib.na_sched_step_state(ctypes.byref(c_state), c_back, c_rec, c_ackb)

        tokens = min(base.bucket_slots, tokens + base.duty)
        if t >= busy_until:
            py_pick = py_sched.choose(t, py_q, last, prob, debt, thr, base.delay, tokens)
            c_heads = (CHead * n)()
            for i in range(n):
                if py_q.items[i]:
                    h = py_q.items[i][0]
                    qbytes = sum(x.size for x in py_q.items[i])
                    c_heads[i] = CHead(h.id, h.generated, qbytes, 1)
                else:
                    c_heads[i] = CHead(0, 0, 0, 0)
            c_pick = c11_lib.na_sched_choose(ctypes.byref(c_state), t, c_heads, tokens)
            assert c_pick == (-1 if py_pick is None else py_pick.flow), f"Mismatch at t={t}, {policy}, {sc_name}"
            if py_pick is not None:
                f = flows[py_pick.flow]
                py_q.items[py_pick.flow].popleft()
                tokens -= f.service
                busy_until = t + f.service
                heapq.heappush(pending, (t + f.service + base.delay, py_pick.id, py_pick, bool(trace.success[t, py_pick.flow])))

    for i in range(n):
        assert abs(c_state.prob[i] - prob[i]) < 1e-12
        assert abs(c_state.debt[i] - debt[i]) < 1e-11
        assert abs(c_state.throughput[i] - thr[i]) < 1e-11
        assert c_state.last_rx_gen[i] == last[i]


def test_e220_hardware_traces_load_and_run():
    regimes = load_e220_regimes()
    assert set(regimes.keys()) == {"e220_random_20", "e220_random_30", "e220_burst_20", "e220_burst_30"}
    assert sum(len(v) for v in regimes.values()) == 24
    c = Config(name="e220_smoke", slots=600, warmup=100)
    tr, airtime = build_e220_trace(c, regimes["e220_burst_30"], seed=301)
    assert 0.02 < airtime < 0.05
    r_fud = simulate_extended(c, tr, "fud", seed=301, airtime_per_attempt_s=airtime)
    r_ada = simulate_extended(c, tr, "fud_ada", seed=301, airtime_per_attempt_s=airtime)
    assert r_fud["e220_airtime_s"] > 0 and r_ada["e220_airtime_s"] > 0
    assert r_ada["metric_version"] == 2


def test_intel_berkeley_multiflow_builder_synthetic_fixture():
    c = Config(name="ib_smoke", nodes=6, slots=400, warmup=50)
    motes = [1, 2, 3, 4, 5, 6]
    # 4 hours = 8:00..12:00
    day_rec = {
        m: [(8 * 3600 + k * 600, 20.0 + (0.5 if k % 3 == 0 else 0.0), 40.0) for k in range(20)]
        for m in motes
    }
    tr, airtime = build_intel_berkeley_multiflow_trace(c, day_rec, motes, hw_runs=None, seed=1)
    assert sum(len(b) for b in tr.arrivals) > 100
    res = simulate_extended(c, tr, "fud_ada", seed=1, airtime_per_attempt_s=airtime)
    assert res["event_resolved"] > 0
    assert 0.0 <= res["jain_service_share"] <= 1.0
