#!/bin/bash
sudo cp ./linvam /usr/local/bin/
sudo cp ./linvamconsole /usr/local/bin/
sh ./setup.sh
sh ./configure-ydotoold.sh
cp ./LinVAM.desktop ~/.local/share/applications
