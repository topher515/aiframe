#!/usr/bin/env python3

# import pyaudio

# p = pyaudio.PyAudio()
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')

# for i in range(0, numdevices):
#     print(p.get_device_info_by_host_api_device_index(0, 1))
#     # if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#     #     print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
from pprint import pprint
import sounddevice
import soundfile
'DEvices'
print(sounddevice.query_devices())

for dev in sounddevice.query_devices():
    pprint(dev)
    # print('def samp rate', dev.get('default_samplerate'))