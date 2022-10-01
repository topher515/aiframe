#!/usr/bin/env python3

import argparse
import os
import signal
import sys
import threading
import traceback
from dataclasses import dataclass
from enum import Enum, auto
from random import choice, randint
from time import sleep, time
from typing import Optional

from lib.ai_generator import generate_image
from lib.gpio_watcher import watch_gpio_buttons
from lib.io_watcher import ButtonHandler
from lib.keyboard_watcher import watch_keyboard_buttons
from lib.model import ImageDataModel
from lib.recording import record_audio
from lib.transcribe import transcribe_speech
from lib.ux_feedback_audio import (play_failure, play_interact, play_refusal,
                                   play_success, play_thinking, play_voicemail_beep)
from lib.view import DesktopRenderer, ImageRenderer, InkyRenderer, ViewState

try:
    from inky.auto import auto as auto_inky_setup
except ImportError:
    auto_inky_setup = None

AUDIO_REC_SECS = 7
MIN_DISPLAY_SECS = 28
MAX_DISPLAY_SECS = 30 * 60 

OPENAPI_BEARER_TOKEN = os.environ.get("OPENAPI_BEARER_TOKEN")


def watch_fake_random_buttons(button_handler: ButtonHandler):

    def randomly_press():
        while True:
            sleep(randint(0, 15))
            choice([button_handler.press_a, button_handler.press_b, button_handler.press_c, button_handler.press_d])()

    th = threading.Thread(target=randomly_press)
    th.start()


class DisplayState(Enum):
    initializing = auto()
    normal = auto()
    waiting_new_img = auto()
    newly_created_img = auto()


@dataclass
class AIFrameRunner(ButtonHandler):

    renderer: ImageRenderer
    displayed_img_path: str = None
    # selected_img_path = None
    displayed_at_time: float = None
    min_display_secs: Optional[int] = MIN_DISPLAY_SECS  # ~30 secs min display time
    max_display_secs = MAX_DISPLAY_SECS  # 30 mins max display time
    display_state: DisplayState = DisplayState.initializing
        
    def get_avail_img_paths(self):   
        return ImageDataModel().get_avail_images()

    def get_next_img_path(self):
        img_paths = self.get_avail_img_paths()
        try:
            index = img_paths.index(self.displayed_img_path)
        except ValueError:
            index = 0
        else:
            if index >= len(img_paths):
                index = 0
            else:
                index = index + 1

        return img_paths[index]

    def display_random(self):
        self.display(choice(self.get_avail_img_paths()))

    def display_next(self):
        self.display(self.get_next_img_path())

    # def display_normal()

    def poke(self):
        if self.is_after_max_display_time():
            self.display_next()

    def is_after_max_display_time(self):
        return self.displayed_at_time and self.displayed_at_time + self.max_display_secs < time()

    def is_before_min_display_time(self):
        return self.displayed_at_time and self.displayed_at_time + self.min_display_secs > time()

    def display(self, img_path: str, as_new=False):
        if self.is_before_min_display_time():
            print(f"Refusing to display image because one was displayed {self.displayed_at_time - time()} seconds ago", file=sys.stderr)
            return

        print(f"Displaying img '{img_path}'", file=sys.stderr)
        self.displayed_img_path = img_path
        self.displayed_at_time = time()
        self.display_state = DisplayState.newly_created_img if as_new else DisplayState.normal 
        self.render()

    def render(self):

        rating = ImageDataModel().get_image_rating(self.displayed_img_path)

        c_emoji = '?'
        if self.display_state == DisplayState.newly_created_img:
            c_emoji = '❌'
        elif self.display_state == DisplayState.normal:
            c_emoji = '👎'

        view_state = ViewState(
            a_btn_text='➡️',
            b_btn_text='❤️' if rating < 0 else f'❤️ {rating}',
            c_btn_text=c_emoji if rating > 0 else f'{c_emoji} {rating}',
            d_btn_text='🎤',
            img_path=self.displayed_img_path
        )

        if self.display_state == DisplayState.newly_created_img:
            self.renderer.render(view_state)
        elif self.display_state == DisplayState.normal:
            self.renderer.render(view_state)

        print(f"At after renderer btw", file=sys.stderr)


    def a(self):
        if self.is_before_min_display_time():
            play_refusal()
            return

        if not self.is_before_min_display_time():
            self.display_next()
            play_interact()


    def b(self):
        # Button behaves like: "like"
        if self.is_before_min_display_time():
            play_refusal()
            return

        if self.display_state == DisplayState.newly_created_img:
            ImageDataModel().incr_image_rating(self.displayed_img_path, 1)
            play_interact()

        elif self.display_state == DisplayState.normal:
            ImageDataModel().incr_image_rating(self.displayed_img_path, 1)
            play_interact()


    def c(self):
        # Button behaves like: "dislike" / delete
        if self.is_before_min_display_time():
            play_refusal()
            return

        if self.display_state == DisplayState.newly_created_img:
            ImageDataModel().delete_image(self.displayed_img_path)
            play_interact()
            
        elif self.display_state == DisplayState.normal:
            ImageDataModel().incr_image_rating(self.displayed_img_path, -1)
            play_interact()
        
        else:
            play_refusal()


    def d(self):
        # Start record / transcribe / generate
        if self.is_before_min_display_time():
            play_refusal()
            return

        last_display_state = self.display_state
        self.display_state = DisplayState.waiting_new_img
        try:
            play_voicemail_beep()
            audio_buffer = record_audio(AUDIO_REC_SECS)
            play_voicemail_beep()

            audio_buffer.seek(0)

            threading.Thread(target=play_thinking).start()
            print("Begin transcribing...", file=sys.stderr)
            transcription = transcribe_speech(audio_buffer)
            img_buffer = generate_image(OPENAPI_BEARER_TOKEN, transcription)
            img_buffer.seek(0)

            with open('imgs/tmp-name.png', 'wb') as fp:
                fp.write(img_buffer.read())

            self.display('imgs/tmp-name.png', as_new=True)

        except Exception as err:
            print(f"Failed to display image: {err}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            play_failure()
            self.display_state = last_display_state
        else:
            play_success()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--watch', 
        required=False,
        help="Watch keyboard instead GPIO buttons", 
        choices=["gpio","keyboard","random"], 
        default="gpio"
    )

    args = parser.parse_args()

    aiframerunner_kwargs = {}
    if auto_inky_setup:
        inky = auto_inky_setup()
        renderer = InkyRenderer(inky=inky, resolution=inky.resolution)
    else:
        renderer = DesktopRenderer(resolution=(600, 448))
        aiframerunner_kwargs = dict(min_display_secs=3)

    runner = AIFrameRunner(renderer=renderer, **aiframerunner_kwargs)
    runner.display_random()

    if args.watch == 'keyboard':
        watch_keyboard_buttons(runner)

    elif args.watch == 'random':
        watch_fake_random_buttons(runner)  # For debugging

    else:
        watch_gpio_buttons(runner)

    while True:
        runner.poke()
        sleep(1)


if __name__ == '__main__':
    main()
