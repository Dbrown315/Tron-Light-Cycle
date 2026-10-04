#!/usr/bin/python3
# File: color_test.py
# Group: Group 9
# Purpose: Display a simple pattern on a single matrix panel.
# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Display a simple test pattern of 3 shapes on a single 64x64 matrix panel.

Run using the following command:

$ python3 color_test.py

"""

import numpy as np
from PIL import Image, ImageDraw
import adafruit_blinka_raspberry_pi5_piomatter as piomatter

width = 64
height = 32  # Vary between 32 or 64.

geometry = piomatter.Geometry(
    width=width, height=height, n_addr_lines=4, rotation=piomatter.Orientation.Normal
)

# Image (shapes) should display on the top-left corner
canvas = Image.new("RGB", (width, height), (0, 0, 0))
draw = ImageDraw.draw(canvas)

framebuffer = np.asarray(canvas) + 0  # Mutable copy
matrix = piomatter.Piomatter(
    colorspace=piomatter.Colorspace.RGB888Packed,
    pinout=piomatter.Pinout.AdafruitMatrixBonnet,
    framebuffer=framebuffer,
    geometry=geometry,
)

draw.rectangle((2, 2, 10, 10), fill=0x0088000)
draw.circle((18, 6), 4, fill=0x880000)
draw.polygon([(28, 2), (32, 10), (24, 10)], fill=0x000088)

framebuffer[:] = np.asarray(canvas)
matrix.show()

input("Press `ENTER` to exit:")
