#!/bin/bash
set -e
source ./configure-uinput-access.sh
pipx install ..
sudo cp ../LinVAM.desktop /usr/share/applications/
