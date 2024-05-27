#!/bin/bash
set -e
source ./steam-deck-configure-uinput-access.sh
mkdir -p ~/.local/bin
source ./setup-python-virtual-environment.sh
source ./build.sh
cp linvam ~/.local/bin/
cp linvamrun ~/.local/bin/
cp ../src/LinVAM-SD.desktop ~/.local/share/applications/
