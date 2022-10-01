#!/usr/bin/env python3

import glob
import os
import signal
import sys
import threading
from random import choice, randint, random
from time import sleep, time
import subprocess

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    print("Failed to import RPi.GPIO. Probably running on desktop")
import subprocess


class ButtonHandler:
    def press_a(self):
        print("Pressed A", file=sys.stderr)
        self.a()

    def press_b(self):
        print("Pressed B", file=sys.stderr)
        self.b()
        
    def press_c(self):
        print("Pressed C", file=sys.stderr)
        self.c()
        
    def press_d(self):
        print("Pressed D", file=sys.stderr)
        self.d()

    def a(self):
        ...
    def b(self):
        ...
    def c(self):
        ...
    def d(self):
        ...  

def watch_gpio_buttons(button_handler: ButtonHandler):
    # Gpio pins for each button (from top to bottom)
    BUTTONS = [5, 6, 16, 24]

    # These correspond to buttons A, B, C and D respectively
    LABELS = ['A', 'B', 'C', 'D']

    # Set up RPi.GPIO with the "BCM" numbering scheme
    GPIO.setmode(GPIO.BCM)

    # Buttons connect to ground when pressed, so we should set them up
    # with a "PULL UP", which weakly pulls the input signal to 3.3V.
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # "handle_button" will be called every time a button is pressed
    # It receives one argument: the associated input pin.
    def handle_button(pin):
        label = LABELS[BUTTONS.index(pin)]
        if str(label) == 'A':
            button_handler.press_a()
        elif str(label) == 'B':
            button_handler.press_b()
        elif str(label) == 'C':
            button_handler.press_c()
        elif str(label) == 'D':
            button_handler.press_d()

    # Loop through out buttons and attach the "handle_button" function to each
    # We're watching the "FALLING" edge (transition from 3.3V to Ground) and
    # picking a generous bouncetime of 250ms to smooth out button presses.
    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

    # Finally, since button handlers don't require a "while True" loop,
    # we pause the script to prevent it exiting immediately.
    # signal.pause()


def watch_fake_random_buttons(button_handler: ButtonHandler):

    def randomly_press():
        while True:
            sleep(randint(0, 15))
            choice([button_handler.press_a, button_handler.press_b, button_handler.press_c, button_handler.press_d])()

    th = threading.Thread(target=randomly_press)
    th.start()


class ImageDisplayer(ButtonHandler):

    def __init__(self):
        self.displayed_img_path = None
        self.selected_img_path = None
        self.displayed_at_time = None
        self.min_display_secs = 28  # ~30 secs min display time
        self.max_display_secs = 30 * 60  # 30 mins max display time

    def get_avail_img_paths(self):   
        return glob.glob(os.path.join(os.getcwd(), "imgs", "*"))

    def get_next_img_path(self):
        img_paths = self.get_avail_img_paths()
        try:
            index = img_paths.index(self.selected_img_path)
        except ValueError:
            index = 0
        else:
            if index >= len(img_paths):
                index = 0
            else:
                index = index + 1

        return img_paths[index]


    def select_random(self):
        self.selected_img_path = choice(self.get_avail_img_paths())


    def select_next(self):
        self.selected_img_path = self.get_next_img_path()
        print(f"Selecting img '{self.selected_img_path}'", file=sys.stderr)


    def poke(self):

        if not self.selected_img_path:
            self.select_next()

        if self.selected_img_path != self.displayed_img_path:
            self.display_selected()

        if self.is_after_max_display_time():
            self.select_next()
            self.display_selected()

    def is_after_max_display_time(self):
        return self.displayed_at_time and self.displayed_at_time + self.max_display_secs < time()

    def is_before_min_display_time(self):
        return self.displayed_at_time and self.displayed_at_time + self.min_display_secs > time()

    def display_selected(self):
        if self.is_before_min_display_time():
            print(f"Refusing to display image because one was displayed {self.displayed_at_time - time()} seconds ago", file=sys.stderr)
            return

        self.displayed_img_path = self.selected_img_path
        self.displayed_at_time = time()
        print(f"Displaying img '{self.displayed_img_path}'", file=sys.stderr)
        subprocess.run(["pipenv", "run", "./disp_image.py", self.displayed_img_path])

    def a(self):
        if not self.is_before_min_display_time():
            self.select_next()
            self.display_selected()

    def b(self):
        # if not self.is_before_min_display_time():
        #     self.select_next()
        #     self.display_selected()
        pass

    def c(self):
        # if not self.is_before_min_display_time():
        #     self.select_next()
        #     self.display_selected()
        pass

    def d(self):
        if not self.is_before_min_display_time():
            self.select_next()
            self.display_selected()


def main():
    displayer = ImageDisplayer()
    displayer.select_random()

    watch_gpio_buttons(displayer)
    # watch_fake_random_buttons(displayer)  # For debugging

    while True:
        displayer.poke()
        sleep(0.5)


if __name__ == '__main__':
    main()
