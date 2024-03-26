#!/bin/bash
sh ./build.sh
sudo cp ../build/linvam /usr/local/bin/
sudo cp ../build/linvamconsole /usr/local/bin/
sh ./setup.sh
cp ../src/LinVAM.desktop ~/.local/share/applications/
sh ./configure-ydotoold.sh
