from dataclasses import asdict
import gzip
import json
import pytest
from netadapt.analysis import interval, analyze
from netadapt.model import Config
from netadapt.runner import work


def test_interval_is_deterministic_and_paired():
    assert interval([0,0,0])==(0.,0.,0.)
    assert interval([1,2,3])==interval([1,2,3])
    assert interval([1,2,3])[0]==2


def test_output_roundtrip_and_resume(tmp_path):
    c=Config(slots=100,warmup=10,nodes=3,rate=.05)
    rows,_=work((asdict(c),100,['fifo','fud'],str(tmp_path)))
    again,_=work((asdict(c),100,['fifo','fud'],str(tmp_path)))
    assert rows==again
    p=tmp_path/'runs/normal/100/fud/packets.jsonl.gz'
    with gzip.open(p,'rt') as f:packets=[json.loads(line) for line in f]
    assert len(packets)==sum(rows[1]['status_counts'].values())
    altered=asdict(c);altered['success']=.2
    with pytest.raises(ValueError,match='hash mismatch'):work((altered,100,['fud'],str(tmp_path)))
