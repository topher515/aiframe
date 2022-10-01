#!/usr/bin/env python3

import argparse
import os
import sys
from io import BytesIO
from typing import Tuple

import requests
from dalle2 import Dalle2
from PIL import Image

try:
    from inky.auto import auto
except ImportError:
    auto = None
    print("Could not import inky--assume running on desktop so will just display image", file=sys.stderr)


OPENAPI_BEARER_TOKEN = os.environ.get("OPENAPI_BEARER_TOKEN")


DEF_RES = (600, 448)

def generate_and_open_image(prompt: str) -> Image:


    class DalleSmallBatch(Dalle2):
        def __init__(self, bearer):
            super().__init__(bearer)
            self.batch_size = 1
        
    dalle = DalleSmallBatch(OPENAPI_BEARER_TOKEN)

    generations = dalle.generate(prompt)

    print(f"Generated {len(generations)} images, btw", file=sys.stderr)
    img_url: str = generations[0]["generation"]["image_path"]
    response = requests.get(img_url)
    return Image.open(BytesIO(response.content))


def resize_image(image: Image, resolution: Tuple[int,int]):

    image.thumbnail(resolution)

    canvas = Image.new(mode="RGBA", size=resolution)

    left_offset = int((canvas.width - image.width) / 2)
    canvas.paste(image, (left_offset, 0))
    
    return canvas


def main():

    parser = argparse.ArgumentParser()
    # parser.add_argument('prompt', help="prompt text")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--saturation', required=False, type=float, help="Image file", default=0.5)
    # parser.add_argument('--no-disp', required=False, action="store_true", default=False)

    args = parser.parse_args()

    prompt = args.infile.read()
    print(f"Using prompt '{prompt}'")
    image = generate_and_open_image(prompt)

    if auto:
        inky = auto(ask_user=False, verbose=True)

        new_image = resize_image(image, inky.resolution)
        inky.set_image(new_image, saturation=args.saturation)
        inky.show()
    else:
        new_image = resize_image(image, DEF_RES)
        new_image.show()


if __name__ == '__main__':
    main()
