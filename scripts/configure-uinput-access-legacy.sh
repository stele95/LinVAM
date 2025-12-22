#!/bin/bash
set -e
sudo usermod -aG tty,input,plugdev $USER
sudo cp ../rules/12-input-legacy.rules /etc/udev/rules.d/
sudo cp ../rules/50-uinput.rules /etc/udev/rules.d/
sudo cp ../rules/80-uinput.rules /etc/udev/rules.d/
sudo udevadm control --reload
sudo udevadm trigger
