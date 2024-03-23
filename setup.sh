#!/bin/bash
mkdir -p ~/.local/lib/LinVAM
mkdir -p ~/.local/share/LinVAM
cp -r ./LinVAM ~/.local/lib/LinVAM
cp ./LinVAM/LinVAM.desktop ~/.local/share/applications/
cp ./LinVAM/command.list ~/.local/share/LinVAM/
cp ./LinVAM/profiles.json ~/.local/share/LinVAM/
rm -rf ./LinVAM
