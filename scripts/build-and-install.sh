#!/bin/bash
set -e
echo "Installing python requirements with pip..."
pip install -r requirements.txt
sh ./build.sh
sudo cp linvam /usr/local/bin/
sudo cp linvamrun /usr/local/bin/
sudo cp ../src/LinVAM.desktop /usr/share/applications/
sh ./configure-ydotoold.sh
echo "Set up MangoHud for displaying LinVAM? [y/N]: "
read MANGOHUD
if [ "$MANGOHUD" == "y" ] || [ "$MANGOHUD" == "Y" ]
    then
        echo "Setting up MangoHud"
        linvam --setup-mangohud
fi
