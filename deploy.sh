#/bin/bash

IMGS_TOO="$1"

scp -r \
    Pipfile \
    aiframe.service \
    aiframe_runner.py \
    disp_image.py \
    generate_and_display.py \
    record_and_transcribe.py \
    speech-to-text-key.json \
    pi@$RPI_IP:/home/pi/app


if [[ $IMGS_TOO == "--imgs" ]]; then
  scp -r imgs pi@$RPI_IP:/home/pi/app
fi
