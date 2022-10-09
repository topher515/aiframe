import sys
from io import BytesIO

from google.cloud import speech

# from 

# SAMPLE_RATE = 16000  # 44100

def transcribe_speech(wav_buffer: BytesIO):
    # Instantiates a client
    client = speech.SpeechClient()

    print("Uploading audio...", file=sys.stderr)
    audio = speech.RecognitionAudio(content=wav_buffer.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=SAMPLE_RATE,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    transcriptions = []
    for result in response.results:
        transcriptions.append(result.alternatives[0].transcript)
        
    return ' '.join(transcriptions)
