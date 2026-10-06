#!/bin/bash
# File: virtual.sh
# Group: Group 9
# Purpose:  Setup required virtual environment for installing and managing
#           Raspberry PI 5 and the PIO Subsystem.

# Create Virtual environment (python3/python)
# python -m venv ~/venvs/tron_venv
python3 -m venv ~/venvs/tron_venv

# PIP Installation Requirements
source ~/venvs/tron_venv/bin/activate
pip install adafruit-blinka
pip install pillow
pip install numpy
pip install click
pip install Adafruit-Blinka-Raspberry-Pi5-Piomatter

# ---------------------------------
# PIO Subsystem Rule Configuration
# ---------------------------------
# - Open a rules file using the nano text editor (from the terminal)
# sudo nano /etc/udev/rules.d/99-com.rules

# - Add an empty line or two to the top of the file. Then add the below statement
#   to one of the empty lines
# SUBSYSTEM=="*-pio", GROUP="gpio", MODE="0660"

# - Save the file: `CTRL+S`. Exit the file: `CTRL+X`. Reboot the PI (below)
# sudo reboot

# Note: Ignore the `#` sign when using commands that start with `sudo` or `SUBSYSTEM`,
#       since those commands are to run in the terminal.


