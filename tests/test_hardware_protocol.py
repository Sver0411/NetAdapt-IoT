import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('radio_protocol',Path(__file__).parents[1]/'hardware/protocol.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def test_crc_vector_and_roundtrip():
    assert p.encode_frame('123456789')==b'123456789,29B1\n'
    assert p.decode_frame(p.encode_frame('NA1,1,2,300,ff'))=='NA1,1,2,300,ff'
    with pytest.raises(ValueError):p.decode_frame(b'NA1,1,2,300,00,0000\n')


def test_frame_limit_and_ack_identity():
    assert p.send_command(1,2,300,b'a'*64).startswith(b'SEND,1,2,300,')
    with pytest.raises(ValueError):p.send_command(1,2,300,b'a'*128)
    assert p.parse_ack('ACK,1,2,300,50')['firmware_rtt_ms']==50
    assert p.parse_ack('ERR,CRC') is None
