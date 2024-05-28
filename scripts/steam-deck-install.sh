#!/bin/bash
set -e
source ./steam-deck-configure-uinput-access.sh
pipx install ..
mkdir -p ~/.local/share/applications/
cp ../src/LinVAM.desktop ~/.local/share/applications/
