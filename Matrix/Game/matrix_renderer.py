#
# File: matrix_renderer.py
# Group: Group 9
# Purpose: PioMatter adapter for a 64x64 HUB75 RGB matrix on an Adafruit Bonnet

import numpy as np
import adafruit_blinka_raspberry_pi5_piomatter as piomatter


class MatrixRenderer:
    def __init__(self, width=64, height=64):
        self.width, self.height = width, height
        geometry = piomatter.Geometry(
            width=width,
            height=height,
            n_addr_lines=5,
            rotation=piomatter.Orientation.Normal,
        )
        self.framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.matrix = piomatter.PioMatter(
            colorspace=piomatter.Colorspace.RGB888Packed,
            pinout=piomatter.Pinout.AdafruitMatrixBonnet,
            framebuffer=self.framebuffer,
            geometry=geometry,
        )

    def show_pixels(self, pixels):
        """
        Display a height x width x 3 RGB uint8-compatible array.
        """
        frame = np.asarray(pixels, dtype=np.uint8)
        if frame.shape != self.framebuffer.shape:
            raise ValueError(f"Expected {self.framebuffer.shape}, got {frame.shape}")
        self.framebuffer[:] = frame
        self.matrix.show()

    def clear(self):
        self.framebuffer.fill(0)
        self.matrix.show()
