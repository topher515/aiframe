import sys
from typing import Any, Optional, Tuple
from dataclasses import MISSING, dataclass, field

from PIL import Image, ImageDraw, ImageFont

from argparse import ArgumentParser
from pilmoji import Pilmoji

from lib.img_utils import average_image_color, is_closer_to_black_than_white

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

        # avg_color = average_image_color(input_image)
        if is_closer_to_black_than_white(input_image):
            bg_color = 'black'
        else:
            bg_color = 'white'

        canvas = Image.new(mode="RGB", size=self.resolution, color=bg_color)
        font = ImageFont.truetype('assets/arial.ttf', 17)

        left_offset = int((canvas.width - input_image.width) / 2)
        top_offset = int((canvas.height - input_image.height) / 2)
        canvas.paste(input_image, (left_offset, top_offset))

        with Pilmoji(canvas) as pilmoji:
            pilmoji.text((4, 44), view_state.a_btn_text, fill='black', font=font, stroke_fill='white')
            pilmoji.text((4, 44 + BTN_SEP_PX), view_state.b_btn_text, fill='black', font=font, stroke_fill='white')
            pilmoji.text((4, 44 + BTN_SEP_PX*2), view_state.c_btn_text, fill='black', font=font, stroke_fill='white')
            pilmoji.text((4, 44 + BTN_SEP_PX*3), view_state.d_btn_text, fill='black', font=font, stroke_fill='white')

        return canvas

    def render(self, view_state: ViewState):
        ...


class DesktopRenderer(ImageRenderer):

    def render(self, view_state: ViewState):
        image = self.render_image(view_state)
        image.show()

@dataclass
class InkyRenderer(ImageRenderer):

    inky: Any = None
    saturation: float = 0.5

    def __post_init__(self):
        self.resolution = self.inky.resolution

    def render(self, view_state: ViewState):
        image = self.render_image(view_state)
        self.inky.set_image(image, saturation=self.saturation)
        self.inky.show()
        