import sys
from typing import Tuple
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from argparse import ArgumentParser
from pilmoji import Pilmoji

try:
    from inky.auto import auto
except ImportError:
    auto = None
    print("Failed to import inky; cannot render to eink display; probably on desktop", file=sys.stderr)


BTN_SEP_PX = 112


@dataclass
class ViewState:
    a_btn_text: str
    b_btn_text: str
    c_btn_text: str
    d_btn_text: str
    img_path: str


@dataclass
class ImageRenderer:

    resolution: Tuple[int, int]

    def render_image(self, view_state: ViewState) -> Image.Image:

        input_image = Image.open(view_state.img_path)

        input_image.thumbnail(self.resolution)

        canvas = Image.new(mode="RGBA", size=self.resolution)
        font = ImageFont.truetype('assets/arial.ttf', 24)

        left_offset = int((canvas.width - input_image.width) / 2)
        canvas.paste(input_image, (left_offset, 0))
        
        with Pilmoji(canvas) as pilmoji:
            pilmoji.text((2, 16), view_state.a_btn_text, 'white', font)
            pilmoji.text((10, 16+BTN_SEP_PX), view_state.b_btn_text, 'white', font)
            pilmoji.text((10, 16+BTN_SEP_PX*2), view_state.c_btn_text, 'white', font)
            pilmoji.text((10, 16+BTN_SEP_PX*3), view_state.d_btn_text, 'white', font)

        return canvas

    def render(self, view_state: ViewState):
        ...


class DesktopRenderer(ImageRenderer):

    def render(self, view_state: ViewState):
        image = self.render_image(view_state)
        image.show()


class InkyRenderer(ImageRenderer):

    inky: any  # The thing returned by `inky.auto.auto()`
    saturation: float = 0.5

    def __post_init__(self):
        self.resolution = self.inky.resolution

    def render(self, view_state: ViewState):
        image = self.render_image(view_state)
        self.inky.set_image(image, saturation=self.saturation)
        self.inky.show()
        