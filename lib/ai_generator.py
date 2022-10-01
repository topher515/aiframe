#!/usr/bin/env python3

import argparse
import os
import sys
from io import BytesIO
from typing import Tuple

import requests
from dalle2 import Dalle2


def generate_image(auth_token: str, prompt: str) -> BytesIO:

    class DalleSmallBatch(Dalle2):
        def __init__(self, bearer):
            super().__init__(bearer)
            self.batch_size = 1
        
    dalle = DalleSmallBatch(auth_token)

    generations = dalle.generate(prompt)

    if not generations:
        raise Exception("Failed to generate AI image")

    print(f"Generated {len(generations)} images", file=sys.stderr)
    img_url: str = generations[0]["generation"]["image_path"]
    response = requests.get(img_url)
    return BytesIO(response.content)