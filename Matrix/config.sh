#!/bin/bash
# File: config.sh
# Group: Group 9
# Purpose: Boot and update the firmware of the Raspberry PI 5

# Check root privileges, re-execute with sudo (if necessary)
if [[ $EUID -ne 0 ]]; then
    echo "Script requires root privileges. Relaunching with sudo..."
    exec sudo "$0" "$@"
fi

# Boot and Update (requires root privileges)
rpi-update
apt update
apt full-upgrade
apt-get install python3-pip
reboot


