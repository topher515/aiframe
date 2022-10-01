## Setup APIs

## Setup RPI

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

- install pyaudio with:
    - `CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" python3 -m pip install pyaudio`


## Setup RPI

