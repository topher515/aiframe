## Dev Setup on Mac

- install brew install portaudio   # needed to support pyaudio


## Setup

- curl https://get.pimoroni.com/ink | bash



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
