"""Host/firmware wire contract, independent of serial transport."""
import binascii


def encode_frame(body):
    data=body.encode('ascii')
    return data+b','+f'{binascii.crc_hqx(data,0xffff):04X}'.encode()+b'\n'


def decode_frame(frame):
    body,checksum=frame.rstrip(b'\r\n').rsplit(b',',1)
    if len(checksum)!=4 or int(checksum,16)!=binascii.crc_hqx(body,0xffff):
        raise ValueError('CRC mismatch')
    return body.decode('ascii')


def send_command(seq,flow,generated_ms,payload):
    if min(seq,flow,generated_ms)<0 or not isinstance(payload,bytes):raise ValueError('invalid packet')
    body=f'NA1,{seq},{flow},{generated_ms},{payload.hex()}'
    if len(encode_frame(body))>200:raise ValueError('encoded radio frame exceeds 200 bytes')
    return f'SEND,{seq},{flow},{generated_ms},{payload.hex()}\n'.encode()


def parse_ack(line):
    fields=line.strip().split(',')
    if len(fields)!=5 or fields[0]!='ACK':return None
    try:return dict(seq=int(fields[1]),flow=int(fields[2]),generated_ms=int(fields[3]),firmware_rtt_ms=int(fields[4]))
    except ValueError:return None
