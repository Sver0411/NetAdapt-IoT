"""Identical admission and expiration semantics for every policy."""
from collections import deque


class Queues:
    def __init__(self, flows, capacity):
        self.flows=flows;self.capacity=capacity
        self.items=[deque() for _ in flows]
    def admit(self, packet):
        q=self.items[packet.flow];f=self.flows[packet.flow]
        removed=[]
        if f.kind!='event':
            if q:removed.append((q.popleft(),'replaced'))
            q.append(packet)
        elif len(q)>=self.capacity:removed.append((packet,'overflow'))
        else:q.append(packet)
        return removed
    def expire(self,t,delay):
        removed=[]
        for f,q in zip(self.flows,self.items):
            if f.deadline is not None:
                while q and t+f.service+delay>q[0].generated+f.deadline:
                    removed.append((q.popleft(),'expired'))
        return removed
    def heads(self):
        return [q[0] for q in self.items if q]
