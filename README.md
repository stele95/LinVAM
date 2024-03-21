# LinVAM
Linux Voice Activated Macro

## Status
This project is currently a work-in-progress and is minimally functional only for English.

Utilising Pocketsphinx, a lightweight voice to text engine you can specify voice commands for the tool to recognise and actions to perform.

Known bugs and planned additions
- To save and use changes click Ok on the main GUI then reload.
- Remember last loaded profile and load on start
- Log window showing spoken words the V2T recognises with ability to right click and assign voice command and actions to current profile
- Support for joysticks and gaming devices

## Requirements
- python3
- PyQt5
- python3-xlib
- pyaudio
- pocketsphinx
- swig3.0
- ydotool (https://github.com/ReimuNotMoe/ydotool)

## Optional requirements
- ffplay (part of ffmpeg, usually already installed)
- HCS voicepacks

## Install
- install python packages: PyQt5, python3-xlib, pyaudio, pocketsphinx
- install swig3.0
- install ydotool (https://github.com/ReimuNotMoe/ydotool)
- (optional) sudo apt install ffmpeg
- sudo ln -s /usr/bin/swig3.0 /usr/bin/swig
- git clone https://github.com/stele95/LinVAM.git

## Configuring ydotool
To simulate typing, the program needs access to your ``/dev/uinput`` device.
By default, this requires root privileges every time you run ``ydotool``.

To avoid that, you can give the program permanent access to the input device by adding your username to the ``input``
user group on your system and giving the group write access to the ``uinput`` device.

To do that, we use a udev rule.
Udev is the Linux system that detects and reacts to devices getting plugged or unplugged on your computer.
It also works with virtual devices like ``ydotool``.

To add the current ``$USER`` to a group, you can use the ``usermod`` command:

    sudo usermod -aG input $USER


You then need to define a new udev rule that will give the ``input`` group permanent write access to the uinput device
(this will give ``ydotool`` write access too).

    echo '## Give ydotoold access to the uinput device
    ## Solution by https://github.com/ReimuNotMoe/ydotool/issues/25#issuecomment-535842993
    KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"
    ' | sudo tee /etc/udev/rules.d/80-uinput.rules > /dev/null


You will need to restart your computer for the change to take effect.

Finally, ``ydotool`` works with a daemon that you leave running in the background, ``ydotoold``,
for performance reasons. You needs to run ``ydotoold`` before you start using ``ydotool``.

To avoid running it every time you start the computer, you can add it to your startup programs.
The steps depend on your distribution. I am running it as a ``systemd`` service. My service file ``ydotoold.service`` looks like this:

    [Unit]
    Description=ydotoold service for listening for inputs from ydotool

    [Service]
    ExecStart=ydotoold -p /tmp/.ydotool_socket -P 0666
    RestartSec=5
    Restart=on-failure

    [Install]
    WantedBy=graphical.target

Also, I've added ``YDOTOOL_SOCKET=/tmp/.ydotool_socket`` to ``/etc/environment``


## Usage
If using X11, this script must be run with root privilege because it must hook and simulate input devices such as keyboard, mouse etc.
- $ cd LinVAM
- $ xhost +
- $ sudo ./main.py

As an alternative (works both on X11 and Wayland, but prior ydotool setup is required, read [Configuring ydotool](https://github.com/stele95/LinVAM?tab=readme-ov-file#configuring-ydotool)), you can run the script like this and it will use ydotool:
- $ cd LinVAM
- $ ./main.py -noroot

### Profiles
Multiple profiles are supported.  To create a new profile for a specific task/game click new and the main profile editor window will be displayed

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/gui.png)
### Key combinations
To assign key combinations first decide which functional key to press by clicking on Ctrl, Alt, Shift or Win to denote left or right key then press the actual command key

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/combination.png)
### Complex commands
It is possible to add multiple actions to a voice command for complex macros with the ability to add a pause between each action.
You can also assign mouse movements and system commands if you require (eg opening applications such as calculator, browser etc)

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/complex.png)
### Threshold
As a rough guide use a value of 10 for each syllable of a word then tweak it down for better accuracy.

### Output audio
In the Command Edit Dialog, chose 'Other' and then 'Play sound'. Pick the sound you would like to play.
For this to work you need to copy any audio file you would like to use to the folder 'voicepacks'.
You are required to create a subfolder to hold all your audio files (voicepack folder), then within that subfolder, create as many folders as you like to group your audio files (category folders).
Place the audio file into these category folders or in any subfolder within a category folder.
In theory any audio file should work, but tested only with MP3 files.

Example:
/voicepacks/my voicepack/custom commands/hello.mp3
/voicepacks/my voicepack/other/thank you.mp3

If you own a HCS voicepack, copy the whole voicepack folder (like 'hcspack', 'hcspack-eden', ...) to the 'voicepacks' folder, so it reads like this:
/voicepacks/hcspack/...

### Improve voice recognition accuracy
Please see this resource on how to train the acoustic model of pocketsphinx to match your voice:
https://cmusphinx.github.io/wiki/tutorialadapt/
