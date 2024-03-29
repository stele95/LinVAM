#!/bin/bash
sh ./build.sh
sudo cp ../build/linvam /usr/local/bin/
sudo cp ../build/linvamrun /usr/local/bin/
cp ../src/LinVAM.desktop ~/.local/share/applications/
sh ./configure-ydotoold.sh
