#!/bin/bash
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
