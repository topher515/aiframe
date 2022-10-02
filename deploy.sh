#/bin/bash

IMGS_TOO="$1"

# rm -r lib/__pycache__
scp -r \
    aiframe_runner.py \
    lib \
    Pipfile \
    aiframe.service \
    speech-to-text-key.json \
    assets \
    pi@$RPI_IP:/home/pi/app

if [[ $IMGS_TOO == "--imgs" ]]; then
  scp -r imgs pi@$RPI_IP:/home/pi/app
fi
