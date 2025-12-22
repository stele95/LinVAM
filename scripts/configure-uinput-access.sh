#!/bin/bash
set -e
sudo usermod -aG tty,input $USER
sudo cp ../rules/12-input-arch.rules /etc/udev/rules.d/12-input.rules
sudo cp ../rules/50-uinput.rules /etc/udev/rules.d/
sudo cp ../rules/80-uinput.rules /etc/udev/rules.d/
sudo udevadm control --reload
sudo udevadm trigger
