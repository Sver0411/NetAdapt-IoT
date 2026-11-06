"""Classic scheduling families and FUD component policies."""
import math

POLICIES=('fifo','rr','wrr','edf','priority','maxweight','pf','aoi_gain','debt',
          'fud','fud_no_age','fud_no_urgency','fud_no_debt')


class Scheduler:
    def __init__(self,name,flows):
        if name not in POLICIES:raise ValueError(f'unknown scheduler: {name}')
        self.name=name;self.flows=flows
        self.cursor=-1
        self.wheel=[f.id for f in flows for _ in range(f.weight)]
    def choose(self,t,queues,last,prob,debt,throughput,delay,tokens):
        eligible=[p for p in queues.heads() if self.flows[p.flow].service<=tokens+1e-9]
        if not eligible:return None
        n=self.name
        if n=='fifo':return min(eligible,key=lambda p:(p.generated,p.id))
        if n in ('rr','wrr'):
            wheel=list(range(len(self.flows))) if n=='rr' else self.wheel
            ids={p.flow:p for p in eligible}
            for step in range(1,len(wheel)+1):
                j=(self.cursor+step)%len(wheel)
                if wheel[j] in ids:
                    self.cursor=j;return ids[wheel[j]]
            return None
        def score(p):
            i=p.flow;f=self.flows[i];s=f.service
            age=t-last[i];wait=t-p.generated;lag=s+delay
            gain=f.weight*max(0,(age+lag)**2-(wait+lag)**2)/(2*f.tau**2)
            slack=p.generated+(f.deadline or f.tau)-(t+lag)
            urgency=f.weight*(1+wait/f.tau)/(1+max(0,slack)) if f.kind=='event' else 0
            if n=='edf':return -(p.generated+(f.deadline or f.tau))
            if n=='priority':return f.weight
            if n=='maxweight':return prob[i]*sum(x.size for x in queues.items[i])/s
            if n=='pf':return prob[i]*f.size/(s*max(throughput[i],1e-6))
            if n=='aoi_gain':return prob[i]*gain/s
            if n=='debt':return prob[i]*debt[i]/s
            if f.kind=='event':gain=0
            return prob[i]*((0 if n=='fud_no_age' else gain)
                +(0 if n=='fud_no_urgency' else urgency)
                +(0 if n=='fud_no_debt' else 0.25*debt[i]))/s
        return max(eligible,key=lambda p:(score(p),-p.generated,-p.flow))
