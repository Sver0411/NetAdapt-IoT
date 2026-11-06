"""Serial transport contract tests with mocked feedback."""
import importlib.util
import io
from pathlib import Path

spec=importlib.util.spec_from_file_location('hardware_runner',Path(__file__).parents[1]/'hardware/run.py')
hw=importlib.util.module_from_spec(spec);spec.loader.exec_module(hw)


class FakeSerial:
    def __init__(self,lines):self.lines=iter(lines);self.written=[]
    def write(self,data):self.written.append(data)
    def readline(self):return next(self.lines,b'')


def test_transport_ignores_unrelated_ack_and_retains_raw_log():
    p=hw.generate(hw.Config(nodes=1,slots=40,warmup=0,rate=0),1)  # no hardware access
    from netadapt.traffic import Packet
    packet=Packet(7,2,3,64)
    device=FakeSerial([b'TX,7,160\n',b'ACK,6,2,300,5\n',b'ACK,7,8,300,6\n',b'ACK,7,2,300,7\n'])
    raw=io.StringIO()
    ok,duration,wire,ack=hw.transaction(device,packet,300,.1,raw)
    assert ok and wire==160 and ack['seq']==7 and ack['flow']==2
    assert device.written[0].startswith(b'SEND,7,2,300,')
    assert len(raw.getvalue().splitlines())==4


def test_transport_error_is_not_success():
    from netadapt.traffic import Packet
    device=FakeSerial([b'ERR,AUX_TIMEOUT\n'])
    ok,duration,wire,error=hw.transaction(device,Packet(1,0,1,64),100,.1,io.StringIO())
    assert not ok and wire is None and error['error']=='ERR,AUX_TIMEOUT'
