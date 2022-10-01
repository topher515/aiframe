## Setup APIs

- Sign up for Dalle

  - Get bearer token, see readme: https://github.com/ezzcodeezzlife/dalle2-in-python
  - export OPENAPI_BEARER_TOKEN='sess-d...FdkA'

- In google cloud console
    - gcloud iam service-accounts create \
        speech-to-text-quickstart \
        --project aiframe-364203

    - gcloud projects \
        add-iam-policy-binding \
        aiframe-364203 --member \
        serviceAccount:speech-to-text-quickstart@aiframe-364203.iam.gserviceaccount.com \
        --role roles/speech.serviceAgent

    - gcloud iam service-accounts keys \
        create speech-to-text-key.json \
        --iam-account \
        speech-to-text-quickstart@aiframe-364203.iam.gserviceaccount.com

    - export \
        GOOGLE_APPLICATION_CREDENTIALS=speech-to-text-key.json


## Dev Setup on Mac

- run `pipenv install`
- install pyaudio with:
    - `CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" python3 -m pip install pyaudio`
    - or, maybe: `CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" pipenv install pyaudio`

- 

## Setup RPI

- curl https://get.pimoroni.com/ink | bash

- Then manually use `pip3` to install all the stuff in `Pipfile` (pipenv isnt working on my rpi as of now)