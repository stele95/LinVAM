#!/bin/bash
set -e
source ./steam-deck-configure-uinput-access.sh
mkdir -p ~/.local/bin
source ./setup-python-virtual-environment.sh
source ./build.sh
sudo cp linvam ~/.local/bin/
sudo cp linvamrun ~/.local/bin/
sudo cp ../src/LinVAM-SD.desktop ~/.local/share/applications/
