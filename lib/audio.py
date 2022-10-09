from typing import BinaryIO, Union

import sounddevice
import soundfile


class AudioFile:
    def __init__(self, file: Union[str, BinaryIO]):
        self.data, self.fs = soundfile.read(file)
        
    def play(self):
        sounddevice.play(self.data, self.fs)
