"""Serial sender control and logical-flow replay."""
import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import serial
from serial.tools import list_ports
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from protocol import send_command,parse_ack
from netadapt.model import Config,flows_for
from netadapt.traffic import generate
from netadapt.queues import Queues
from netadapt.scheduler import Scheduler,POLICIES,pf_update


def pf_slot(throughput,t,feedback):
    """Quantize host ACK completion to the next logical slot boundary."""
    ack_bytes=np.zeros(len(throughput))
    for at,flow,size in feedback:
        if at==t:ack_bytes[flow]+=size
    return pf_update(throughput,ack_bytes)


def connect(port):
    device=serial.Serial(port,115200,timeout=.1)
    time.sleep(1);device.reset_input_buffer();device.write(b'PING\n')
    until=time.monotonic()+3
    while time.monotonic()<until:
        line=device.readline().decode(errors='replace').strip()
        if line=='READY,SENDER':return device
    device.close();raise RuntimeError('selected device did not identify as READY,SENDER')


def transaction(device,p,generated_ms,timeout,raw):
    command=send_command(p.id,p.flow,generated_ms,bytes([p.flow%256])*p.size)
    start=time.monotonic();device.write(command);wire=None
    while time.monotonic()-start<timeout:
        line=device.readline().decode(errors='replace').strip()
        if not line:continue
        raw.write(json.dumps({'host_monotonic':time.monotonic(),'line':line})+'\n');raw.flush()
        if line.startswith(f'TX,{p.id},'):wire=int(line.split(',')[2])
        ack=parse_ack(line)
        if ack and (ack['seq'],ack['flow'],ack['generated_ms'])==(p.id,p.flow,generated_ms):
            return True,time.monotonic()-start,wire,ack
        if line.startswith('ERR,'):return False,time.monotonic()-start,wire,{'error':line}
    return False,time.monotonic()-start,wire,{'error':'ACK_TIMEOUT'}


def run(args):
    c=Config(**json.loads(Path(args.config).read_text()))
    if c.mixed_sizes:raise ValueError('ASCII radio payload size: use 64 bytes')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    # Host timeout sets the wall-clock transaction pacing cost.
    if args.timeout<=0:raise ValueError('timeout must be positive')
    with connect(args.port) as device:
        device.write(b'PARAMS\n');time.sleep(1)
        parameters=[]
        while device.in_waiting:parameters.append(device.readline().decode(errors='replace').strip())
        (out/'manifest.json').write_text(json.dumps({'measurement_type':'physical_single_link_logical_flow_replay',
            'config':asdict(c),'seed':args.seed,'policy':args.policy,'port':args.port,'radio_register_response':parameters,
            'one_way_latency_measured':False,'timeout_s':args.timeout},indent=2))
        fs=flows_for(c);q=Queues(fs,c.event_buffer);sched=Scheduler(args.policy,fs);trace=generate(c,args.seed)
        last=np.zeros(c.nodes);prob=np.full(c.nodes,.8);debt=np.zeros(c.nodes);tp=np.ones(c.nodes)
        targets=np.array([.5*c.duty*.8*f.weight/(sum(x.weight for x in fs)*f.service) for f in fs])
        next_slot=0;prev_t=0.;tokens=0.;cap=c.bucket_slots;pf_feedback=[]
        start=time.monotonic();ledger={}
        with (out/'raw_serial.jsonl').open('w') as raw:
            while True:
                now=(time.monotonic()-start)/c.dt;t=int(now)
                tokens=min(cap,tokens+(now-prev_t)*c.duty);prev_t=now
                if t>=c.slots:break
                while next_slot<=t:
                    tp=pf_slot(tp,next_slot,pf_feedback)
                    pf_feedback=[ack for ack in pf_feedback if ack[0]>next_slot]
                    for p in trace.arrivals[next_slot]:
                        ledger[p.id]={**asdict(p),'status':'queued'}
                        for old,status in q.admit(p):ledger[old.id]['status']=status
                    debt=np.minimum(50,debt+targets*np.array([bool(x) for x in q.items]))
                    next_slot+=1
                for p,status in q.expire(t,c.delay):ledger[p.id]['status']=status
                p=sched.choose(t,q,last,prob,debt,tp,c.delay,tokens)
                if p is None:time.sleep(min(.02,c.dt/10));continue
                q.items[p.flow].popleft();f=fs[p.flow]
                ok,duration,wire,ack=transaction(device,p,int(p.generated*c.dt*1000),args.timeout,raw)
                # Charge conservative wall-clock transaction duration incl ACK/timeout.
                tokens-=max(f.service,duration/c.dt)
                arrival=(time.monotonic()-start)/c.dt
                timely=f.deadline is None or arrival<=p.generated+f.deadline
                ledger[p.id].update(status=('delivered' if timely else 'late') if ok else 'unconfirmed',
                    sent_slot=t,ack_slot=arrival,host_rtt_s=duration,wire_bytes=wire,feedback=ack)
                prob[p.flow]=.9*prob[p.flow]+.1*int(ok)
                if ok:
                    last[p.flow]=max(last[p.flow],p.generated)
                    if timely:debt[p.flow]=max(0,debt[p.flow]-1)
                if ok:pf_feedback.append((math.ceil(arrival),p.flow,p.size))
        (out/'packets.json').write_text(json.dumps(list(ledger.values()),indent=2))
        sent=[r for r in ledger.values() if 'sent_slot' in r]
        # ACK timeout is recorded as an unconfirmed transaction.
        summary={'measurement_type':'physical_single_link_logical_flow_replay','offered_released':len(ledger),
            'attempted':len(sent),'confirmed':sum(r['status'] in ('delivered','late') for r in sent),
            'unconfirmed':sum(r['status']=='unconfirmed' for r in sent),
            'note':'ACK timeout is unconfirmed, not proof of receiver loss; no one-way latency/AoI measurement'}
        (out/'summary.json').write_text(json.dumps(summary,indent=2));print(summary)


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('ports')
    p=sub.add_parser('probe');p.add_argument('--port',required=True)
    p=sub.add_parser('run');p.add_argument('--port',required=True);p.add_argument('--config',default='configs/hardware.json')
    p.add_argument('--policy',choices=POLICIES,default='fud');p.add_argument('--seed',type=int,default=100)
    p.add_argument('--timeout',type=float,default=3);p.add_argument('--out',default='output/hardware/session')
    args=parser.parse_args()
    if args.command=='ports':print(json.dumps([{'device':p.device,'description':p.description} for p in list_ports.comports()],indent=2))
    elif args.command=='probe':
        with connect(args.port) as device:print('READY,SENDER verified')
    else:run(args)


if __name__=='__main__':main()
