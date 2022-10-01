#!/usr/bin/env python3

import os
from pprint import pprint

from dalle2 import Dalle2
import requests
from io import BytesIO

OPENAPI_BEARER_TOKEN = os.environ.get("OPENAPI_BEARER_TOKEN")


class DalleSmallBatch(Dalle2):
    def __init__(self, bearer):
        super().__init__(bearer)
        self.batch_size = 1


def main():
    dalle = DalleSmallBatch(OPENAPI_BEARER_TOKEN)
    generations = dalle.generate_and_download("tiny magic samurai")


if __name__ == '__main__':
    main()