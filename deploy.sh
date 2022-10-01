#/bin/bash

scp -r \
    Pipfile \
    aiframe_runner.py \
    disp_image.py \
    generate_and_display.py \
    record_and_transcribe.py \
    speech-to-text-key.json \
    imgs \
    pi@$RPI_IP:/home/pi/app