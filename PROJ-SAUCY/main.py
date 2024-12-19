#!/usr/bin/env python
import sys
import os

from Controller import Controller
from ImageFactory import ImageFactory

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../bindings/python'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions

##################################################################

def image_to_ascii_art(image, output_width=64):
    w, h = image.size
    ascii_chars = "*"

    ascii_image = ""
    for y in range(h):
        for x in range(w):
            r, g, b = image.getpixel((x, y))

            intensity = (r+g+b)/3  # number between 0 and 255

            ascii_char = ascii_chars[int(
                intensity/255 * (len(ascii_chars) - 1))]

            ascii_image += f"\033[;38;2;{r};{g};{b}m {ascii_char} \033[0m"
        ascii_image += "\n"

    return ascii_image

##################################################################

def getch():
    import sys
    import termios
    import tty

    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    try:
        # or tty.setraw(fd) if you prefer raw mode's behavior.
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, orig)
##################################################################
# Image key mapping
image_dict = {
    "q" : "record_rgb.jpg",
    "w" : "cowboy_frog.png"
}

##################################################################
# Startup Initialisation
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 2
options.hardware_mapping = 'regular'
options.gpio_slowdown = 3
options.pixel_mapper_config = 'Rotate:180'
matrix = RGBMatrix(options=options)
matrix.Clear()

controller = Controller(matrix)
controller.SetBpm(130)
image_factory = ImageFactory(matrix, controller, image_dict)

controller.StartStrobeWorker()
image_factory.StartImageWorker()

##################################################################

# ascii_image = image_to_ascii_art(image)
# print(ascii_image)

##################################################################

# Continuous loop that handles keystrokes
try:
    while True:
        user_input = getch()
        if user_input == "b":
            bpm = input("Enter BPM and press enter: ")
            controller.SetBpm(bpm)
        else:
            # Send the input to both strobe and Image Workers
            print("Setting var: " + user_input)
            image_factory.SetImage(user_input)
            controller.SetStrobeMode(user_input)

except KeyboardInterrupt:
    sys.exit(0)
