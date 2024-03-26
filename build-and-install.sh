#!/bin/bash
echo "Starting LinVAM setup..."
cd ./LinVAM
sh ./build.sh
sudo cp ./build/linvam /usr/local/bin/
sudo cp ./build/linvamconsole /usr/local/bin/
mkdir -p ~/.local/share/LinVAM
cp -r ./model ~/.local/share/LinVAM
cp ./LinVAM.desktop ~/.local/share/applications/
cd ..
rm -rf ./LinVAM
echo "LinVAM setup finished. You can now start LinVAM from the apps list."
