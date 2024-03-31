# LinVAM
Linux Voice Activated Macro

## Status
Currently supported languages (just for voice input, UI is in English):
- English
- Russian
- Chinese
- French
- German

Utilising [VOSK-API](https://github.com/alphacep/vosk-api), a lightweight voice to text engine you can specify voice commands for the tool to recognise and actions to perform.

### Planned additions
- Add location selection for output sounds instead of a hardcoded location
- Support for joysticks and gaming devices

## Install
### Requirements
- PyQt6
- sounddevice
- srt
- vosk
- ffmpeg
- ydotool (https://github.com/ReimuNotMoe/ydotool)

### Optional requirements
- HCS voicepacks

### Install steps
- install python3 and pip
- install python packages: PyQt6, sounddevice, srt and vosk by running the following command

        pip install -r requirements.txt

- After installing ydotool, [configure it to run without sudo](https://github.com/stele95/LinVAM?tab=readme-ov-file#configuring-ydotool)
- Download the latest release from the [Releases page](https://github.com/stele95/LinVAM/releases), extract it and run ``setup-and-install.sh`` from the extracted files

## Build
### Build dependencies
- python3
- Nuitka (https://github.com/Nuitka/Nuitka)

### Steps for building and running successfully
#### Building without installing
- install python3 and pip
- install [Nuitka](https://github.com/Nuitka/Nuitka) by running the following command

        python -m pip install nuitka

- For building without installing, run the ``build.sh`` script

#### Building and installing
- do steps from [Building without installing](https://github.com/stele95/LinVAM?tab=readme-ov-file#building-without-installing)
- install run dependencies

      pip install -r requirements.txt

- install ydotool (https://github.com/ReimuNotMoe/ydotool)
- install ffmpeg for playing audio files
- [Configure ydotool](https://github.com/stele95/LinVAM?tab=readme-ov-file#configuring-ydotool)
- run the ``build-and-install.sh`` script

## Configuring ydotool
### TL/DR
If you have a system that uses systemd, you are good to go and don't need to do anything because a script is executed when running any install script. If not, read [Ydotoold daemon autostart](https://github.com/stele95/LinVAM?tab=readme-ov-file#ydotoold-daemon-autostart)

### Manual configuration
#### Udev rule for input
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

#### Ydotoold daemon autostart
``ydotool`` works with a daemon that you leave running in the background, ``ydotoold``, for performance reasons.
You needs to run ``ydotoold`` before you start using ``LinVAM`` since it relies on ``ydotool`` for executing input commands.

To avoid running it every time you start the computer, you can add it to your startup programs. The steps depend on your distribution.
If the install script detects that the system uses a ``systemd``, it will add a ``systemd`` service for starting ``ydotoold``. The service file ``ydotoold.service`` looks like this:

    [Unit]
    Description=ydotoold service for listening for inputs from ydotool

    [Service]
    ExecStart=ydotoold -p /tmp/.ydotool_socket -P 0666
    RestartSec=5
    Restart=on-failure

    [Install]
    WantedBy=graphical.target

Also, the install script adds ``YDOTOOL_SOCKET=/tmp/.ydotool_socket`` to ``/etc/environment``


## Usage
Start LinVAM from your list of applications or by typing ``linvam`` in the terminal. This works on both X11 and Wayland, but prior ydotool setup is required, read [Configuring ydotool](https://github.com/stele95/LinVAM?tab=readme-ov-file#configuring-ydotool)

### Usage with Steam
After setting up profiles in the GUI app, you can add ``linvamrun --profile='Profile name' -- %command%`` to the game launch options for starting the console app for listening when opening games.

You can also use ``--language='languageName'`` for specifying a language. If ``--language`` argument is not used, app defaults to language selected in the GUI app.

![Steam launch options](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/steam.png)

### Display LinVAM profile and language in MangoHud
If you are using [MangoHud](https://github.com/flightlessmango/MangoHud), you can set it up for displaying selected LinVAM profile and language.

If ``setup-and-install.sh`` has been executed, it will ask for setting up MangoHud. If you are building and installing by yourself, you can run ``setup-mangohud.sh`` script to set it up.

### Profiles
Multiple profiles are supported.  To create a new profile for a specific task/game click new and the main profile editor window will be displayed.
Profiles are saved to and loaded from ``profiles.json`` file located at ``/home/$USER/.local/share/LinVAM/`` and can be backed up from there.

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/main-gui.png)
### Key combinations
To assign key combinations, input the wanted sequence in the input field. Keys are separated by ```+```, use ``hold`` and ``release`` keywords for representing when a specific key should be held or released.

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/combination.png)
### Complex commands
It is possible to add multiple actions to a voice command for complex macros with the ability to add a pause between each action.
You can also assign mouse movements and system commands if you require (eg opening applications such as calculator, browser etc)

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/complex.png)

### Output audio
In the Command Edit Dialog, chose 'Other' and then 'Play sound'. Pick the sound you would like to play.

For this to work you need to create a folder ``voicepacks`` inside your home directory (e.g. by executing ``mkdir ~/voicepacks`` in the terminal) and copy any audio file you would like to use to that folder.
Within ``voicepacks`` folder you can create as many folders as you like to group your audio files (category folders).
Place the audio file into these category folders or in any subfolder within a category folder.
In theory any audio file should work, but tested only with MP3 files.

Example:
~/voicepacks/my voicepack/custom commands/hello.mp3
~/voicepacks/my voicepack/other/thank you.mp3

If you own a HCS voicepack, copy the whole voicepack folder (like 'hcspack', 'hcspack-eden', ...) to the ``voicepacks`` folder, so it reads like this:
``~/voicepacks/hcspack/...``

### Improve voice recognition accuracy
Default recognition accuracy should be good enough for most usages.
If you want to improve voice recognition accuracy, please see this resource on how to train the acoustic model:
https://alphacephei.com/vosk/adaptation
