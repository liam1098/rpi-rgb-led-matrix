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
    "w" : "record.jpg",
    "s" : "2SAUCEmushroom.jpg",
    "r" : "records.gif",
    "t" : "records-fade.gif",
    "y" : "records-fade-more.gif",
    "f" : "fat-man.gif",
    "l" : "loading.gif"
}

##################################################################
# Strobe key mapping
strobe_dict = {
    "1" : [1],
    "2" : [1, 0.5, 0.5],
    "3" : [1, 1, 1, 1, 1, 1, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25],
    "6" : [0.25],
    "0" : [0.01]
}

##################################################################
# Command mapping for help dict
help_dict = {
    "H" : "Display all commands",
    "." : "Show all current GIF/image key mappings",
    "," : "Show all current strobe settings",
    "B" : "Manual BPM change",
    "F" : "Manual GIF framerate change",
    "G" : "Toggle GIF select/image select",
    "*" : "Double BPM",
    "/" : "Half BPM",
    "+" : "Double GIF framerate",
    "-" : "Half GIF framerate"
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

gif_mode = False
strobe_mode = False

controller = Controller(matrix, strobe_dict)
controller.SetBpm(130)
image_factory = ImageFactory(matrix, controller, image_dict)
image_factory.SetGifFrameRate(130)

controller.StartStrobeWorker()
image_factory.StartImageWorker()

##################################################################

# ascii_image = image_to_ascii_art(image)
# print(ascii_image)

##################################################################

def CheckInt(input):
    try:
        input = int(input)
        return input
    except:
        print("Invalid Input.")
        return False

# Continuous loop that handles keystrokes
try:
    while True:
        user_input = getch()

        match user_input:
            case "B":
                bpm = input("Enter BPM and press enter: ")
                if CheckInt(bpm):
                    controller.SetBpm(bpm)

            case "F":
                gif_fr = input("Enter GIF framerate and press enter: ")
                if CheckInt(gif_fr):
                    image_factory.SetGifFrameRate(gif_fr)

            case "G":  # Toggle GIF mode
                gif_mode = not gif_mode
                if gif_mode:
                    print("GIF select.")
                else:
                    print("Image select.")

            case "H":
                print("\nInstructions:\n")
                for key, value in help_dict.items():
                    print(f"\t{key}: {value}")
                print()

            case ".":
                print("\nList of images:\n")
                for key, value in image_dict.items():
                    print(f"\t{key}: {value}")
                print()

            case ",":
                print("\nList of strobe patterns:\n")
                for key, value in strobe_dict.items():
                    print(f"\t{key}: {value}")
                print()

            case "*":
                controller.DoubleBpmMultiplier()
            case "/":
                controller.HalfBpmMultiplier()
            case "+":
                image_factory.DoubleFRMultiplier()
            case "-":
                image_factory.HalfFRMultiplier()

            case _:
                # Send the input to both strobe and Image Workers
                controller.SetStrobeMode(user_input)
                if gif_mode:
                    user_input = user_input + " (gif)"
                image_factory.SetImage(user_input)
                output = "Setting var: " + user_input
                print(output)

except KeyboardInterrupt:
    sys.exit(0)
