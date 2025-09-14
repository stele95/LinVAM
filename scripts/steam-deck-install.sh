#!/bin/bash
set -e
source ./steam-deck-configure-uinput-access.sh
pipx install ..
mkdir -p ~/.local/share/applications/
cp ../LinVAM.desktop ~/.local/share/applications/
cp ../linvam/assets/icons/linvam.svg ~/.local/share/icons/hicolor/scalable/apps/
