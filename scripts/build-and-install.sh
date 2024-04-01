#!/bin/bash
set -e
echo "Installing python requirements with pip..."
pip install -r requirements.txt
sh ./build.sh
sudo cp linvam /usr/local/bin/
sudo cp linvamrun /usr/local/bin/
cp ../src/LinVAM.desktop ~/.local/share/applications/
echo "Set up MangoHud for displaying LinVAM? [y/N]: "
read MANGOHUD
if [ "$MANGOHUD" == "y" ] || [ "$MANGOHUD" == "Y" ]
    then
        echo "Setting up MangoHud"
        sh setup-mangohud.sh
fi
