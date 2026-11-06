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
    counts=rng.poisson(np.broadcast_to(rates*mult,(c.slots,c.nodes)))
    loss=np.random.default_rng(b).random((c.slots,c.nodes))
    probabilities=np.full((c.slots,c.nodes),c.success)
    if c.link=="markov":
        switches=np.random.default_rng(d).random((c.slots,c.nodes))
        bad=np.zeros(c.nodes,dtype=bool)
        for t in range(c.slots):
            bad=np.where(bad,switches[t]>=0.1,switches[t]<0.025)
            probabilities[t]=np.where(bad,0.20,c.success)
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
