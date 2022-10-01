import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    print("Failed to import RPi.GPIO; cannot read buttons; probably running on desktop", file=sys.stderr)

from .io_watcher import ButtonHandler


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
