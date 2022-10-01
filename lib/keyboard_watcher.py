from typing import Union
import sys

# import keyboard
# from keyboard import on_press, on_press_key

try:
    # import keyboard
    from pynput import keyboard
except ImportError:
    print("Failed to import keyboard; probably running on RPi", file=sys.stderr)

from .io_watcher import ButtonHandler


def watch_keyboard_buttons(button_handler: ButtonHandler):

    def on_press(key):
        try:
            char = key.char
        except AttributeError:
            print(f'special key {key} pressed', file=sys.stderr)
            char = None

        if char == 'a':
            button_handler.press_a()
        elif char == 'b':
            button_handler.press_b()
        elif char == 'c':
            button_handler.press_c()
        elif char == 'd':
            button_handler.press_d()
            
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # keyboard.on_press_key('a', button_handler.press_a) # , suppress=False)
    # keyboard.on_press_key('b', button_handler.press_b) # , suppress=False)
    # keyboard.on_press_key('c', button_handler.press_c) # , suppress=False)
    # keyboard.on_press_key('d', button_handler.press_d) # , suppress=False)