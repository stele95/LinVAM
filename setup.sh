#!/bin/bash
echo "Starting LinVAM setup..."
mkdir -p ~/.local/lib/
mkdir -p ~/.local/share/LinVAM
rsync -av ./LinVAM ~/.local/lib/ --exclude .git --exclude data --exclude model
cp ./LinVAM/LinVAM.desktop ~/.local/share/applications/
cp -r ./LinVAM/model ~/.local/share/LinVAM
rm -rf ./LinVAM
echo "LinVAM setup finished. You can now start LinVAM from the apps list."
