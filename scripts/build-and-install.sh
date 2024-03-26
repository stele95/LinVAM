#!/bin/bash
echo "Starting LinVAM setup..."
cd ./LinVAM/scripts
sh ./build.sh
sudo cp ../build/linvam /usr/local/bin/
sudo cp ../build/linvamconsole /usr/local/bin/
sh ./setup.sh
cp ../src/LinVAM.desktop ~/.local/share/applications/
sh ./configure-ydotoold.sh
cd ../..
rm -rf ./LinVAM
echo "LinVAM setup finished. You can now start LinVAM from the apps list."
