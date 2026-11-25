"""Strictly additive FUD-Ada scheduler preserving all 13 frozen baseline policies untouched."""
from dataclasses import asdict
import heapq
import math
import numpy as np

from ..metrics import FINAL_STATES, classified, summarize
from ..model import Config, flows_for
from ..queues import Queues
from ..scheduler import POLICIES, Scheduler, pf_update
from ..simulation import simulate as simulate_frozen

ADDITIVE_POLICIES = ("fud_ada", "fud_ada_no_debt")
EXTENDED_POLICIES = POLICIES + ADDITIVE_POLICIES

# Frozen on calibration seeds 200-204 (strictly disjoint from 100-119 and held-out 300-319)
FUD_ADA_ALPHA_U = 1.0
FUD_ADA_BETA_D = 2.5


class ExtendedScheduler:
    """Delegates all 13 frozen policies to netadapt.scheduler.Scheduler; adds FUD-Ada."""

    def __init__(self, name: str, flows):
        if name not in EXTENDED_POLICIES:
            raise ValueError(f"unknown scheduler: {name}")
        self.name = name
        self.flows = flows
        self._base = Scheduler(name, flows) if name in POLICIES else None

    def choose(self, t, queues, last, prob, debt, throughput, delay, tokens):
        if self._base is not None:
            return self._base.choose(t, queues, last, prob, debt, throughput, delay, tokens)
        eligible = [p for p in queues.heads() if self.flows[p.flow].service <= tokens + 1e-9]
        if not eligible:
            return None
        use_debt = self.name == "fud_ada"

        def score(p):
            i = p.flow
            f = self.flows[i]
            s = f.service
            age = t - last[i]
            wait = t - p.generated
            lag = s + delay
            if f.kind == "event":
                slack = p.generated + (f.deadline or f.tau) - (t + lag)
                fresh_term = 0.0
                urg_term = f.weight * (1.0 + wait / f.tau) * (
                    1.0 + FUD_ADA_ALPHA_U / (1.0 + max(0, slack))
                )
            else:
                raw_gain = max(0.0, (age + lag) ** 2 - (wait + lag) ** 2) / (2.0 * f.tau ** 2)
                fresh_term = f.weight * math.sqrt(raw_gain)
                urg_term = 0.0
            debt_term = (FUD_ADA_BETA_D * f.weight * math.log1p(debt[i])) if use_debt else 0.0
            return prob[i] * (fresh_term + urg_term + debt_term) / s

        return max(eligible, key=lambda p: (score(p), -p.generated, -p.flow))


def simulate_extended(c: Config, trace, policy: str, seed: int, airtime_per_attempt_s: float | None = None):
    """Run any frozen or additive policy under identical queue/tail/metric semantics."""
    if policy in POLICIES:
        res = simulate_frozen(c, trace, policy, seed)
        if airtime_per_attempt_s is not None:
            res["e220_airtime_s"] = res["attempts"] * airtime_per_attempt_s
        return res

    flows = flows_for(c)
    n = len(flows)
    queues = Queues(flows, c.event_buffer)
    scheduler = ExtendedScheduler(policy, flows)
    last = np.zeros(n, dtype=int)
    prob = np.full(n, 0.8)
    debt = np.zeros(n)
    throughput = np.ones(n)
    targets = np.array([
        0.5 * c.duty * 0.8 * f.weight / (sum(x.weight for x in flows) * f.service)
        for f in flows
    ])
    pending = []
    records = {}
    decisions = []
    tokens = 0.0
    cap = c.bucket_slots
    busy_until = 0
    aoi_sum = np.zeros(n)
    qos_slots = np.zeros(n, dtype=int)
    queue_sum = 0.0
    observed_bytes = 0
    occupied = 0
    service_slots = np.zeros(n, dtype=int)
    tail_service = np.zeros(n, dtype=int)
    observation_slots = c.slots - c.warmup
    attempts = 0
    wire_bytes = 0
    total_reserved = 0
    main_reserved = 0
    tail_attempts = 0
    max_budget_excess = 0.0

    def finish(p, status, tt):
        rec = records[p.id]
        assert rec["status"] in ("queued", "inflight"), (p.id, rec["status"], status)
        rec["status"] = status
        rec["finished"] = tt

    for t in range(c.end + 1):
        if t == c.slots:
            for r in records.values():
                r["status_at_main_cutoff"] = r["status"]
        received = np.zeros(n)
        ack_bytes = np.zeros(n)
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
                    received[i] += 1
                ack_bytes[i] += p.size
                finish(p, "delivered" if timely else "late", at)
                records[p.id]["received"] = at
                if c.warmup <= at < c.slots:
                    observed_bytes += p.size
            else:
                finish(p, "link_loss", at)
        if t == c.slots:
            legacy = summarize(c, flows, records, aoi_sum / observation_slots * c.dt)
        if t == c.end:
            break
        if t < c.slots:
            for p in trace.arrivals[t]:
                records[p.id] = {
                    **asdict(p),
                    "status": "queued",
                    "started": None,
                    "received": None,
                    "finished": None,
                }
                for old, status in queues.admit(p):
                    finish(old, status, t)
        for p, status in queues.expire(t, c.delay):
            finish(p, status, t)
        backlogged = np.array([bool(q) for q in queues.items])
        debt = np.minimum(50, np.maximum(0, debt + targets * backlogged - received))
        throughput = pf_update(throughput, ack_bytes)
        tokens = min(cap, tokens + c.duty)
        if t >= busy_until:
            p = scheduler.choose(t, queues, last, prob, debt, throughput, c.delay, tokens)
            if p is not None:
                f = flows[p.flow]
                s = f.service
                assert queues.items[p.flow].popleft() == p
                tokens -= s
                attempts += 1
                wire_bytes += p.size + c.header
                total_reserved += s
                if t < c.slots:
                    main_reserved += s
                else:
                    tail_attempts += 1
                assert tokens >= -1e-8
                max_budget_excess = max(max_budget_excess, total_reserved - (t + 1) * c.duty)
                assert max_budget_excess < 1e-6
                busy_until = t + s
                records[p.id].update(status="inflight", started=t)
                heapq.heappush(pending, (t + s + c.delay, p.id, p, bool(trace.success[t, p.flow])))
                decisions.append({"t": t, "flow": p.flow, "packet": p.id, "service": s})
                service_slots[p.flow] += max(0, min(t + s, c.slots) - max(t, c.warmup))
                tail_service[p.flow] += max(0, min(t + s, c.end) - max(t, c.slots))
        if c.warmup <= t < c.slots:
            age = t - last
            aoi_sum += age
            qos_slots += age <= np.array([f.tau for f in flows])
            queue_sum += sum(len(q) for q in queues.items)
            occupied += int(t < busy_until)

    for r in records.values():
        if r["status"] in ("queued", "inflight"):
            r["pending_kind"] = r["status"]
            r["status"] = "pending_at_cutoff"
        assert r["status"] in FINAL_STATES

    result = {**legacy, **classified(c, flows, records, legacy, service_slots, tail_service, qos_slots)}
    result.update(
        scenario=c.name,
        policy=policy,
        seed=seed,
        config_hash=c.digest(),
        trace_hash=trace.digest,
        main_window=[c.warmup, c.slots],
        tail_window=[c.slots, c.end],
        mean_queue=queue_sum / observation_slots,
        utilization=occupied / observation_slots,
        observation_goodput_bps=8 * observed_bytes / (observation_slots * c.dt),
        attempts=attempts,
        tail_attempts=tail_attempts,
        wire_bytes=wire_bytes,
        payload_attempt_bytes=wire_bytes - attempts * c.header,
        reserved_slots=main_reserved,
        tail_reserved_slots=total_reserved - main_reserved,
        max_budget_excess=max_budget_excess,
    )
    if airtime_per_attempt_s is not None:
        result["e220_airtime_s"] = attempts * airtime_per_attempt_s
    assert sum(result["status_counts"].values()) == len(records)
    assert sum(service_slots) == occupied
    assert all(b["t"] >= a["t"] + a["service"] for a, b in zip(decisions, decisions[1:]))
    return result
