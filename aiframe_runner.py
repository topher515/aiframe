#!/usr/bin/env python3

import argparse
import os
import re
import signal
import sys
import threading
import traceback
from dataclasses import dataclass
from enum import Enum, auto
from random import choice, randint
from time import sleep, time
from typing import Optional
from uuid import uuid4

from lib.ai_generator import generate_image
from lib.gpio_watcher import watch_gpio_buttons
from lib.io_watcher import ButtonHandler
from lib.keyboard_watcher import watch_keyboard_buttons
from lib.model import ImageDataModel
from lib.recording import record_audio
from lib.transcribe import transcribe_speech
from lib.ux_feedback_audio import (cache_sounds, play_failure, play_interact, play_refusal,
                                   play_success, play_thinking,
                                   play_voicemail_beep)
from lib.view import DesktopRenderer, ImageRenderer, InkyRenderer, ViewState

try:
    from inky.auto import auto as auto_inky_setup
except ImportError:
    auto_inky_setup = None

AUDIO_REC_SECS = 7
MIN_DISPLAY_SECS = 28
MAX_DISPLAY_SECS = 30 * 60 
NO_MIC_FAKE_PROMPT = choice([
    "an extra furry, extra cute pikachu",
    "a long dog made of lasers",
    "a hamster dressed like a medieval priest"
])


def get_env_or_fail(env_var_name: str):
    if val := os.environ.get(env_var_name):
        return val
    raise Exception(f"Configuration error; Can't find credential env var: {env_var_name}")


def watch_fake_random_buttons(button_handler: ButtonHandler):

    def randomly_press():
        while True:
            sleep(randint(0, 15))
            choice([button_handler.press_a, button_handler.press_b, button_handler.press_c, button_handler.press_d])()

    th = threading.Thread(target=randomly_press)
    th.start()


def make_dalle_filename(prompt: str):
    prompt_str = ''.join(x if re.match(r'\w', x) else '_' for x in prompt)
    return f'aiframe_{prompt_str}_{uuid4().hex}.png'


class DisplayState(Enum):
    initializing = auto()
    normal = auto()
    waiting_new_img = auto()
    newly_created_img = auto()


@dataclass
class AIFrameRunner(ButtonHandler):

    open_api_bearer_token: str
    renderer: ImageRenderer
    no_mic: bool = False
    no_audio: bool = False
    displayed_img_path: str = None
    # selected_img_path = None
    displayed_at_time: float = None
    min_display_secs: Optional[int] = MIN_DISPLAY_SECS  # ~30 secs min display time
    max_display_secs = MAX_DISPLAY_SECS  # 30 mins max display time
    display_state: DisplayState = DisplayState.initializing
        
    def __post_init__(self):
        print(f"Starting aiframe runner with no-mic={self.no_mic} no-audio={self.no_audio}", file=sys.stderr)

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
            c_emoji = '🤮' # '👎'

        view_state = ViewState(
            a_btn_text='➡️',
            b_btn_text='❤️' if rating <= 0 else f'❤️ {rating}',
            c_btn_text=c_emoji if rating >= 0 else f'{c_emoji} {abs(rating)}',
            d_btn_text='🎤',
            img_path=self.displayed_img_path
        )

        if self.display_state == DisplayState.newly_created_img:
            self.renderer.render(view_state)
        elif self.display_state == DisplayState.normal:
            self.renderer.render(view_state)

        # FYI: The eink renderer returns before it completes displaying


    def a(self):
        if self.is_before_min_display_time():
            play_refusal(dummy=self.no_audio)
            return

        if not self.is_before_min_display_time():
            self.display_next()
            play_interact(dummy=self.no_audio)


    def b(self):
        # Button behaves like: "like"
        if self.is_before_min_display_time():
            play_refusal(dummy=self.no_audio)
            return

        if self.display_state == DisplayState.newly_created_img:
            ImageDataModel().incr_image_rating(self.displayed_img_path, 1)
            play_interact(dummy=self.no_audio)

        elif self.display_state == DisplayState.normal:
            ImageDataModel().incr_image_rating(self.displayed_img_path, 1)
            play_interact(dummy=self.no_audio)


    def c(self):
        # Button behaves like: "dislike" / delete
        if self.is_before_min_display_time():
            play_refusal(dummy=self.no_audio)
            return

        if self.display_state == DisplayState.newly_created_img:
            print(f"Deleting unliked image {self.displayed_img_path}...", file=sys.stderr)
            ImageDataModel().delete_image(self.displayed_img_path)
            play_interact(dummy=self.no_audio)
            
        elif self.display_state == DisplayState.normal:
            ImageDataModel().incr_image_rating(self.displayed_img_path, -1)
            play_interact(dummy=self.no_audio)
        
        else:
            play_refusal(dummy=self.no_audio)


    def d(self):
        # Start record / transcribe / generate
        if self.is_before_min_display_time():
            play_refusal(dummy=self.no_audio)
            return

        last_display_state = self.display_state
        self.display_state = DisplayState.waiting_new_img
        try:
            play_voicemail_beep(dummy=self.no_audio)
            audio_buffer = record_audio(AUDIO_REC_SECS)
            play_voicemail_beep(dummy=self.no_audio)

            audio_buffer.seek(0)

            threading.Thread(target=play_thinking).start()
            if self.no_mic:
                print("Use fake transcription, because no mic")
                transcription = NO_MIC_FAKE_PROMPT
            else:
                print("Begin transcribing...", file=sys.stderr)
                transcription = transcribe_speech(audio_buffer)

            print(f"Transcription: '{transcription}'", file=sys.stderr)
            img_buffer = generate_image(self.open_api_bearer_token, transcription)
            img_buffer.seek(0)

            filename = make_dalle_filename(transcription)
            filepath = f'imgs/{filename}'

            with open(filepath, 'wb') as fp:
                fp.write(img_buffer.read())

            self.display(filepath, as_new=True)

        except Exception as err:
            print(f"Failed to display image: {err}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            play_failure(dummy=self.no_audio)
            self.display_state = last_display_state
        else:
            play_success(dummy=self.no_audio)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--watch', 
        required=False,
        help="Watch keyboard instead GPIO buttons", 
        choices=["gpio","keyboard","random"], 
        default="gpio"
    )
    parser.add_argument('--no-mic', required=False, action='store_true', default=False)
    parser.add_argument('--no-audio', required=False, action='store_true', default=False)

    OPENAPI_BEARER_TOKEN = get_env_or_fail("OPENAPI_BEARER_TOKEN")
    get_env_or_fail("GOOGLE_APPLICATION_CREDENTIALS")  # Googles APIs will read this later

    args = parser.parse_args()

    aiframerunner_kwargs = dict(
        open_api_bearer_token=OPENAPI_BEARER_TOKEN,
        no_mic=args.no_mic,
        no_audio=args.no_audio
    )

    if not args.no_audio:
        cache_sounds()

    if auto_inky_setup:
        inky = auto_inky_setup()
        renderer = InkyRenderer(inky=inky, resolution=inky.resolution)
    else:
        renderer = DesktopRenderer(resolution=(600, 448))
        aiframerunner_kwargs['min_display_secs'] = 3

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
