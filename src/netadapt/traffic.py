"""Policy-independent, indexed exogenous traffic and channel potential outcomes."""
from dataclasses import dataclass
import hashlib
import numpy as np
from .model import Config, flows_for


@dataclass(frozen=True)
class Packet:
    id: int
    flow: int
    generated: int
    size: int


@dataclass
class Trace:
    arrivals: list[list[Packet]]
    success: np.ndarray
    digest: str


def generate(c: Config, seed: int):
    # Independent random streams for arrivals and channel outcomes.
    a,b,d=np.random.SeedSequence(seed).spawn(3)
    rng=np.random.default_rng(a)
    flows=flows_for(c)
    rates=np.array([f.rate for f in flows])[None,:]
    mult=np.ones((c.slots,1))
    if c.burst:mult[(np.arange(c.slots)%400)<80]=4
    if c.total_rate is None:
        counts=rng.poisson(np.broadcast_to(rates*mult,(c.slots,c.nodes)))
    else:
        # Poisson thinning preserves each flow's rate and gives scale B the
        # same class arrivals for a seed, independently of the flow count.
        class_counts=rng.poisson(np.broadcast_to(c.total_rate/3*mult,(c.slots,3)))
        counts=np.zeros((c.slots,c.nodes),dtype=int)
        for t,kind in zip(*np.nonzero(class_counts)):
            ids=np.arange(kind,c.nodes,3)
            chosen=ids[(rng.random(int(class_counts[t,kind]))*len(ids)).astype(int)]
            np.add.at(counts[t],chosen,1)
    loss=np.random.default_rng(b).random((c.end,c.nodes))
    probabilities=np.full((c.end,c.nodes),c.success)
    if c.link=="markov":
        switches=np.random.default_rng(d).random((c.end,c.nodes))
        bad=np.zeros(c.nodes,dtype=bool)
        for t in range(c.end):
            bad=np.where(bad,switches[t]>=c.bad_to_good,switches[t]<c.good_to_bad)
            probabilities[t]=np.where(bad,c.bad_success,c.success)
    successes=loss<probabilities
    arrivals=[];pid=0
    for t in range(c.slots):
        batch=[]
        for i,n in enumerate(counts[t]):
            for _ in range(int(n)):
                batch.append(Packet(pid,i,t,flows[i].size));pid+=1
        arrivals.append(batch)
    h=hashlib.sha256()
    for array in (counts.astype('<i8'),successes):h.update(array.tobytes())
    h.update(c.digest().encode());h.update(str(seed).encode())
    return Trace(arrivals,successes,h.hexdigest())
