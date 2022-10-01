#!/usr/bin/env python3

import sys
import wave
from io import BytesIO

import pyaudio

SAMPLE_RATE = 16000


def record_audio(seconds: int) -> BytesIO:

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    # fs = 44100  # Record at 44100 samples per second
    fs = SAMPLE_RATE
    filename = "output.wav"

    bytes_buffer = BytesIO()

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print(f'Recording for {seconds} seconds', file=sys.stderr)


    class dummy:
        recording = True

    def on_press():
        dummy.recording = False

    # listener = keyboard.Listener(on_press=on_press)
    # listener.start() 

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for a few seconds or early escape

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
        if not dummy.recording:
            print("Exit early", file=sys.stderr)
            break

    # listener.stop()

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording', file=sys.stderr)

    # Save the recorded data as a WAV file
    wf = wave.open(bytes_buffer, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # bytes_buffer.seek(0)

    return bytes_buffer