#!/usr/bin/env python3

import sys
import wave
from argparse import ArgumentParser
from io import BytesIO

from lib.transcribe import transcribe_speech
from lib.recording import record_audio




# def play_audio_buffer(audio: BytesIO):
    
#     with open('myfile.wav', 'wb') as fp:
#         fp.write(audio.read())

#     playsound('myfile.wav')




def main():

    parser = ArgumentParser()
    # parser.add_argument('prompt', help="prompt text")
    parser.add_argument('--secs', required=False, type=int, help="seconds of audio to record", default=7)
    # parser.add_argument('--no-disp', required=False, action="store_true", default=False)

    args = parser.parse_args()

    audio_buffer = record_audio(args.secs)
    audio_buffer.seek(0)

    # play_audio_buffer(audio_buffer)

    transcription = transcribe_speech(audio_buffer)

    # print(f"Saw {len(transcriptions)} transcriptions returned")
    print(transcription)


if __name__ == '__main__':
    main()
