#!/usr/bin/python3
# File: label_test.py
# Group: Group 9
# Purpose: Display text characters on the matrix display.

"""
Display textual characters on a single 64x64 matrix panel.

Run using the following command:

$ python3 label_test.py

"""

import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import adafruit_blinka_raspberry_pi5_piomatter as piomatter

# Define matrix dimensions and pinout
width = 64
height = 32  # Vary between 32 or 64

geometry = piomatter.Geometry(width=width, height=height, n_addr_lines=4)
framebuffer = np.zeros((height, width, 3), dtype=np.uint8)

matrix = piomatter.PioMatter(
    colorspace=piomatter.Colorspace.RGB888Packed,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    framebuffer=framebuffer,
    geometry=geometry,
)

# Render text message using the Pillow library.
canvas = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(canvas)
draw.text((2, 4), "Hello Clemson.", fill=(255, 0, 0))

# Push message to matrix framebuffer
framebuffer[:] = np.asarray(canvas)
matrix.show()

# Maintain active display
while True:
    time.sleep(1)

# Press `CTRL+C` to exit.
