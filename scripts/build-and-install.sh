#!/bin/bash
sh ./build.sh
sudo cp linvam /usr/local/bin/
sudo cp linvamrun /usr/local/bin/
cp ../src/LinVAM.desktop ~/.local/share/applications/
sh ./configure-ydotoold.sh
