#!/bin/bash
set -e
source ./configure-uinput-access.sh
pipx install ..
sudo cp ../LinVAM.desktop /usr/share/applications/
sudo cp ../linvam/assets/icons/linvam.svg /usr/share/icons/hicolor/scalable/apps/
