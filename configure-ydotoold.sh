#!/bin/bash
sudo usermod -aG input $USER
echo '## Give ydotoold access to the uinput device
## Solution by https://github.com/ReimuNotMoe/ydotool/issues/25#issuecomment-535842993
KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"
' | sudo tee /etc/udev/rules.d/80-ydotoold-uinput.rules > /dev/null
systemd=`pacman -Qs systemd`
if [ -n "$systemd" ]
    then
        echo "Systemd installed, setting up service"
        echo 'YDOTOOL_SOCKET=/tmp/.ydotool_socket' | sudo tee -a /etc/environment > /dev/null
        echo '[Unit]
Description=ydotoold service for listening for inputs from ydotool

[Service]
ExecStart=ydotoold -p /tmp/.ydotool_socket -P 0666
RestartSec=5
Restart=on-failure

[Install]
WantedBy=graphical.target
' | sudo tee /etc/systemd/system/ydotoold.service > /dev/null
        sudo systemctl enable ydotoold.service
    else
        echo "Systemd not installed, skipping service setup"
fi
