"""Validated experiment schema and non-preemptive shared-link service model."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math


@dataclass(frozen=True)
class Config:
    name: str = "normal"
    nodes: int = 24
    slots: int = 4000
    warmup: int = 500
    dt: float = 0.1
    rate: float = 0.015
    duty: float = 0.8
    success: float = 0.95
    delay: int = 1
    link: str = "iid"
    burst: bool = False
    unequal_rates: bool = False
    equal_weights: bool = False
    mixed_sizes: bool = False
    bitrate: int = 6400
    header: int = 16
    event_buffer: int = 32
    bucket_slots: int = 4
    def __post_init__(self):
        if self.nodes < 1 or self.slots < 1 or self.warmup < 0:
            raise ValueError("positive nodes/slots and nonnegative warmup required")
        if not 0 < self.duty <= 1 or not 0 <= self.success <= 1:
            raise ValueError("duty in (0,1], success in [0,1]")
        if self.rate < 0 or self.dt <= 0 or self.delay < 0 or self.bitrate < 1 or self.header < 0 or self.event_buffer < 1:
            raise ValueError("invalid traffic/service configuration")
        if self.link not in {"iid", "markov"}:
            raise ValueError("link must be iid or markov")
        if self.slots - self.warmup <= self.guard:
            raise ValueError("evaluation cohort must have a positive duration")
        if self.bucket_slots < self.service(128 if self.mixed_sizes else 64):
            raise ValueError("bucket must hold the largest packet service cost")
    @property
    def guard(self):
        return 6 + self.service(128 if self.mixed_sizes else 64) + self.delay
    @property
    def cohort_end(self):
        return self.slots - self.guard
    def service(self, payload):
        return max(1, math.ceil((payload+self.header)*8/(self.bitrate*self.dt)))
    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Flow:
    id: int
    kind: str
    weight: int
    tau: int
    deadline: int | None
    size: int
    service: int
    rate: float


def flows_for(c):
    result=[]
    for i in range(c.nodes):
        kind,weight,tau,deadline = [("event",4,6,6),("status",3,12,None),("telemetry",1,30,None)][i%3]
        size=128 if c.mixed_sizes and i%2 else 64
        rate=c.rate*([0.25,1,2][i%3] if c.unequal_rates else 1)
        result.append(Flow(i,kind,1 if c.equal_weights else weight,tau,deadline,size,c.service(size),rate))
    return result


def study_scenarios(base):
    changes=[("normal",{}),("congestion",{"rate":0.10}),("nodes_8",{"nodes":8}),
             ("nodes_48",{"nodes":48}),("nodes_96",{"nodes":96}),
             ("unequal_rates",{"unequal_rates":True}),("equal_weights",{"equal_weights":True}),
             ("weak_link",{"success":0.55}),("markov_link",{"link":"markov"}),
             ("bursty",{"burst":True}),("budget_40",{"duty":0.4}),
             ("budget_100",{"duty":1.0}),("long_delay",{"delay":5}),
             ("mixed_sizes",{"mixed_sizes":True}),("lossless",{"success":1.0})]
    return [replace(base,name=n,**kw) for n,kw in changes]
