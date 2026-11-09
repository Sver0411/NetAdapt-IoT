"""Verify selected SDK, memory/USB macros, GPIO source, and binary flash header."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root=Path(__file__).resolve().parents[1];firmware=root/'hardware/firmware';out=root/'docs/validation/refined_v1'
with (out/'compiledb.log').open('w') as log:
    subprocess.run([sys.executable,'-m','platformio','run','-d',str(firmware),'-e','sender','-t','compiledb'],stdout=log,stderr=subprocess.STDOUT,check=True)
compdb=firmware/'compile_commands.json'
row=next(r for r in json.loads(compdb.read_text()) if r['file']=='src/main.cpp')
cmd=row['command']
sdk=Path.home()/'.platformio/packages/framework-arduinoespressif32/tools/sdk/esp32s3/qio_opi/include/sdkconfig.h'
source=(firmware/'src/main.cpp').read_text()
report={'board':'esp32-s3-n16r8','expected_module':'N16R8','flash_mb':16,'flash_mode':'qio',
 'psram_interface':'opi','psram_expected_mb':8,'psram_size_configuration':'runtime detection (CONFIG_SPIRAM_SIZE=-1)',
 'sdk_qio_opi_used':'/qio_opi/' in cmd,
 'sdk_oct_psram':bool(re.search(r'^#define CONFIG_SPIRAM_MODE_OCT 1$',sdk.read_text(),re.M)),
 'usb_cdc':'-DARDUINO_USB_CDC_ON_BOOT=1' in cmd,'usb_mode':'-DARDUINO_USB_MODE=1' in cmd,
 'board_has_psram':'-DBOARD_HAS_PSRAM' in cmd,
 'pins':{key:int(re.search(r'\b'+key+r'=(\d+)',source)[1]) for key in ['RADIO_RX','RADIO_TX','M0','M1','AUX']},
 'uart':'UART1 9600 8N1','usb_serial':115200,'binaries':{},'physical_memory_readout_performed':False}
assert all(report[k] for k in ['sdk_qio_opi_used','sdk_oct_psram','usb_cdc','usb_mode','board_has_psram'])
for role in ['sender','receiver']:
    binary=(firmware/f'.pio/build/{role}/firmware.bin').read_bytes()
    assert binary[0]==0xe9 and binary[3]>>4==4 # Espressif image flash-size code 4 = 16 MB.
    report['binaries'][role]={'sha256':hashlib.sha256(binary).hexdigest(),'size_bytes':len(binary),'flash_header_size_code':binary[3]>>4}
(out/'firmware-config.json').write_text(json.dumps(report,indent=2)+'\n')
compdb.unlink();print('PASS: sender/receiver images, SDK, PSRAM mode, USB, and pins')
