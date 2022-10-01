#!/usr/bin/env python3

import sys
import wave
from argparse import ArgumentParser
from io import BytesIO

import pyaudio
from google.cloud import speech
from playsound import playsound

SAMPLE_RATE = 16000

def transcribe_speech(wav_buffer: BytesIO):

    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    # gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
    # audio = speech.RecognitionAudio(uri=gcs_uri)

    print("Uploading audio...", file=sys.stderr)
    audio = speech.RecognitionAudio(content=wav_buffer.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    transcriptions = []
    for result in response.results:
        transcriptions.append(result.alternatives[0].transcript)
        
    return transcriptions


def play_audio_buffer(audio: BytesIO):
    
    with open('myfile.wav', 'wb') as fp:
        fp.write(audio.read())

    playsound('myfile.wav')


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





def main():

    parser = ArgumentParser()
    # parser.add_argument('prompt', help="prompt text")
    parser.add_argument('--secs', required=False, type=int, help="seconds of audio to record", default=7)
    # parser.add_argument('--no-disp', required=False, action="store_true", default=False)

    args = parser.parse_args()

    audio_buffer = record_audio(args.secs)
    audio_buffer.seek(0)

    # play_audio_buffer(audio_buffer)

    transcriptions = transcribe_speech(audio_buffer)

    print(f"Saw {len(transcriptions)} transcriptions returned")
    print(transcriptions[0])


if __name__ == '__main__':
    main()
