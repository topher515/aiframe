#!/usr/bin/env python3

import sys
from typing import Tuple

from PIL import Image

from argparse import ArgumentParser

from inky.auto import auto


def resize_image(image: Image, resolution: Tuple[int,int]):

    image.thumbnail(resolution)

    canvas = Image.new(mode="RGBA", size=resolution)

    left_offset = int((canvas.width - image.width) / 2)
    canvas.paste(image, (left_offset, 0))
    
    return canvas


def main():

    parser = ArgumentParser()
    parser.add_argument('img_file', help="Image file")
    parser.add_argument('--saturation', required=False, type=float, help="Image file", default=0.5)

    args = parser.parse_args()

    inky = auto(ask_user=False, verbose=True)

    image = Image.open(args.img_file)
    

    image.thumbnail(inky.resolution, Image.LANCZOS)

    canvas = Image.new(mode="RGB", size=inky.resolution)

    left_offset = int((canvas.width - image.width) / 2)
    canvas.paste(image, (left_offset, 0))
    
    inky.set_image(canvas, saturation=args.saturation)
    inky.show()
    


if __name__ == '__main__':
    main()




# inky = auto(ask_user=True, verbose=True)
# saturation = 0.5

# if len(sys.argv) == 1:
#     print("""
# Usage: {file} image-file
# """.format(file=sys.argv[0]))
#     sys.exit(1)

# image = Image.open(sys.argv[1])
# resizedimage = image.resize(inky.resolution)

# if len(sys.argv) > 2:
#     saturation = float(sys.argv[2])

# inky.set_image(resizedimage, saturation=saturation)
# inky.show()
