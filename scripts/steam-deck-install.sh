#!/bin/bash
set -e
pip install --user --break-system-packages pipx
pipx install ..
source ./steam-deck-configure-uinput-access.sh
mkdir -p ~/.local/share/applications/
cp ../LinVAM.desktop ~/.local/share/applications/
mkdir -p ~/.local/share/icons/hicolor/scalable/apps/
cp ../linvam/assets/icons/linvam.svg ~/.local/share/icons/hicolor/scalable/apps/
