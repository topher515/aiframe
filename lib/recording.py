#!/usr/bin/env python3

import sys
from io import BytesIO
import sounddevice
import soundfile


def iter_input_devices():
    for dev in sounddevice.query_devices():
        if dev.get("max_input_channels") > 0:
            yield dev

def get_input_device_info():
    # Find preferred
    for dev in iter_input_devices():
        if 'USB PnP Sound Device' in dev['name']:
            return dev

    # Use the one called default
    for dev in iter_input_devices():
        if 'default' == dev['name']:
            return dev
    
    # Ok just use the first one we see
    for dev in iter_input_devices():
        return dev

    
def record_audio(seconds: int) -> BytesIO:

    device_info = get_input_device_info()
    channels = 1 
    samplerate = int(device_info["default_samplerate"])

    print(f'Using sound input device name="{device_info["name"]}" samplerate={samplerate}', file=sys.stderr)

    rec = sounddevice.rec(
        int(seconds * samplerate), 
        samplerate=samplerate, 
        channels=channels
    )
    sounddevice.wait()

    bytes_buffer = BytesIO()
    soundfile.write(bytes_buffer, rec, samplerate, format='wav')
    bytes_buffer.seek(0)

    return bytes_buffer
