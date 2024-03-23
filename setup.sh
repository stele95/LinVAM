#!/bin/bash
echo "Starting LinVAM setup..."
mkdir -p ~/.local/lib/
mkdir -p ~/.local/share/LinVAM
cp -r ./LinVAM ~/.local/lib/
cp ./LinVAM/LinVAM.desktop ~/.local/share/applications/
cp ./LinVAM/command.list ~/.local/share/LinVAM/
cp ./LinVAM/profiles.json ~/.local/share/LinVAM/
rm -rf ./LinVAM
echo "LinVAM setup finished. You can now start LinVAM from the apps list."
