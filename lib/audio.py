from typing import BinaryIO, Union

import wave
from contextlib import contextmanager
from ctypes import c_char_p, c_int, CFUNCTYPE, cdll
import pyaudio
import sounddevice
import soundfile

## I could not get pyaudio for playback working on raspberry pi, 
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


class AudioFileOld:
    chunk = 1024

    def __init__(self, file: Union[str, BinaryIO]):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        with noalsaerr():
            self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()


class AudioFile:
    def __init__(self, file: Union[str, BinaryIO]):
        self.data, self.fs = soundfile.read(file) #, dtype='float32')
        
    def play(self):
        sounddevice.play(self.data, self.fs) #  device=args.device)
        # sounddevice.wait()

    def close(self):
        pass
