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
### Available packages
#### AUR
[![AUR](https://img.shields.io/aur/version/linvam)](https://aur.archlinux.org/packages/linvam)

After installing from AUR, run ``sudo usermod -aG tty,input $USER`` to allow [uinput access without sudo](https://github.com/stele95/LinVAM?tab=readme-ov-file#udev-rule-for-input)

### Requirements
- python packages:
  - PyQt6
  - sounddevice
  - srt
  - requests
  - tqdm
  - vosk
- ffmpeg
- [ydotool](https://github.com/ReimuNotMoe/ydotool)

### Optional requirements
- HCS voicepacks

### Install
Since ``LinVAM`` relies on ``python`` to run, there are two ways of installing it. Both way require that ``python3`` is installed.

#### 1. Installing by using system python packages (``LinVAM`` should use system theme if installed this way)
- install pip and all [required packages](https://github.com/stele95/LinVAM?tab=readme-ov-file#requirements) using your system package manager
- Download the source code zip file from the latest release from the [Releases page](https://github.com/stele95/LinVAM/releases), extract it and run ``build-and-install.sh`` from the ``scripts`` folder in the extracted files
- Don't forget to restart your device after finishing installation steps

#### 2. Installing by creating a virtual environment for ``LinVAM`` python packages (``LinVAM`` will have a default theme that doesn't use system theme settings)
- install [ydotool](https://github.com/ReimuNotMoe/ydotool) and ffmpeg
- Download the source code zip file from the latest release from the [Releases page](https://github.com/stele95/LinVAM/releases), extract it, enter scripts folder, open terminal in that folder and execute the following command:


    source setup-python-virtual-environment.sh && source build-and-install.sh


- Don't forget to restart your device after finishing installation steps

## Build
- install python3 and pip
- install [Nuitka](https://github.com/Nuitka/Nuitka) by running the following command

        pip install nuitka

- Run the ``build.sh`` script

## Configuring uinput access
### TL/DR
- Run ``configure-uinput-access.sh`` if you didn't install by running ``build-and-install.sh``, this will set up [Udev rule for input](https://github.com/stele95/LinVAM?tab=readme-ov-file#udev-rule-for-input)

### Manual configuration
#### Udev rule for input
To simulate typing and recording key events, the program needs access to your ``/dev/uinput`` device. By default, this requires root privileges.

To avoid that, you can give the program permanent access to the input device by adding your username to ``input`` and ``tty``
user groups on your system and giving the group write access to the ``uinput`` device.

To do that, we use an udev rule.
Udev is the Linux system that detects and reacts to devices getting plugged or unplugged on your computer.
It also works with virtual devices like ``ydotool``.

You also need to define new udev rules that will give needed groups permanent write access to the uinput device
(this will give ``ydotoold`` write access and ``LinVAM`` read access).

For easy setup, execute the ``configure-uinput-access.sh`` script from the ``scripts`` folder.

You will need to restart your computer for the change to take effect.

## Usage
Start LinVAM from your list of applications or by typing ``linvam`` in the terminal. This works on both X11 and Wayland, but prior uinput access setup is required, read [Configuring uinput access](https://github.com/stele95/LinVAM?tab=readme-ov-file#configuring-uinput-access)

### Usage with Steam
After setting up profiles in the GUI app, you can add ``linvamrun --profile='Profile name' -- %command%`` to the game launch options for starting the console app for listening when opening games.

You can also use ``--language='languageName'`` for specifying a language. If ``--language`` argument is not used, app defaults to language selected in the GUI app.

![Steam launch options](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/steam.png)

### Display LinVAM profile and language in MangoHud
If you are using [MangoHud](https://github.com/flightlessmango/MangoHud), you can set it up for displaying selected LinVAM profile and language.

If you are installing using the ``build-and-install.sh`` script, it will ask for setting up MangoHud. If installing by another way, run the following command in the terminal after installing ``LinVAM``:

    linvam --setup-mangohud

This expects a ``MangoHud.conf`` file located at ``~/.config/MangoHud/``. If your config file is located in some other place, execute the previous command like this where ``/path/to/dir/`` is a path to a dir containing ``MangoHud.conf`` file:

    linvam --setup-mangohud --path='/path/to/dir/'

For this to work, you will need ``sed`` and ``grep`` which are probably already installed, if not install them with your package managers.

### Profiles
Multiple profiles are supported.  To create a new profile for a specific task/game click new and the main profile editor window will be displayed.
Profiles are saved to and loaded from ``profiles.json`` file located at ``/home/$USER/.local/share/LinVAM/`` and can be backed up from there.

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/main-gui.png)
### Key combinations
For inputting combinations, press keys in the order you want them to be executed (holding keys is also supported).

![Comnbinations](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/combination.png)
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
- ~/voicepacks/my voicepack/custom commands/hello.mp3
- ~/voicepacks/my voicepack/other/thank you.mp3

### Improve voice recognition accuracy
Default recognition accuracy should be good enough for most usages.
If you want to improve voice recognition accuracy, please see this resource on how to train the acoustic model:
https://alphacephei.com/vosk/adaptation
