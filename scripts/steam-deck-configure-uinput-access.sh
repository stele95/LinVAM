#!/bin/bash
set -e
STEAMOS=0
STEAMOS_READONLY=0

# Test for SteamOS and disable readonly mode if we're running on it
if command -v steamos-readonly >& /dev/null
then
	# Test if SteamOS readonly mode is enabled
	if sudo steamos-readonly status | grep 'enabled'
	then
		echo "steamos readonly mode is true"
		STEAMOS_READONLY=1
	fi

	STEAMOS=1
	sudo steamos-readonly disable
fi
sudo usermod -aG tty,input $USER
sudo cp ../rules/12-input-arch.rules /etc/udev/rules.d/12-input.rules
sudo cp ../rules/50-uinput.rules /etc/udev/rules.d/
sudo cp ../rules/80-uinput.rules /etc/udev/rules.d/
sudo udevadm control --reload
sudo udevadm trigger
if [ "$STEAMOS" = 1 ] ; then
	if [ "$STEAMOS_READONLY" = 1 ] ; then
		sudo steamos-readonly enable
	fi
fi
