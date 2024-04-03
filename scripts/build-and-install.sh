#!/bin/bash
set -e
source ./build.sh
sudo cp linvam /usr/local/bin/
sudo cp linvamrun /usr/local/bin/
sudo cp ../src/LinVAM.desktop /usr/share/applications/
source ./configure-uinput-access.sh
echo "Set up MangoHud for displaying LinVAM? [y/N]: "
read MANGOHUD
if [ "$MANGOHUD" == "y" ] || [ "$MANGOHUD" == "Y" ]
    then
        echo "Setting up MangoHud"
        linvam --setup-mangohud
fi
