#!/bin/bash
echo "Starting LinVAM setup..."
mkdir -p ~/.local/lib/
mkdir -p ~/.local/share/LinVAM
rsync -av ./LinVAM ~/.local/lib/ --exclude .git
cp ./LinVAM/LinVAM.desktop ~/.local/share/applications/
cp ./LinVAM/command.list ~/.local/share/LinVAM/
cp ./LinVAM/profiles.json ~/.local/share/LinVAM/
rm -rf ~/.local/lib/LinVAM/.git
rm -rf ./LinVAM
echo "LinVAM setup finished. You can now start LinVAM from the apps list."
