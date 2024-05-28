# LinVAM
Linux Voice Activated Macro

### Table of contents
* [Status](#status)
  * [Planned additions](#planned-additions-)
* [Install](#install)
  * [Available packages](#available-packages)
    * [AUR](#aur)
  * [Install manually](#install-manually)
    * [Requirements](#requirements)
    * [Installation steps](#installation-steps)

* [Configuring uinput access](#configuring-uinput-access)
  * [TL/DR](#tldr)
  * [Manual configuration](#manual-configuration)
    * [Udev rule for input](#udev-rule-for-input)
* [Usage](#usage)
  * [Usage with Steam](#usage-with-steam)

  * [Display LinVAM profile and language in MangoHud](#display-linvam-profile-and-language-in-mangohud)
  * [Profiles](#profiles)
  * [Input mode](#input-mode)
  * [Key combinations](#key-combinations)
  * [Complex commands](#complex-commands)
  * [Output audio](#output-audio)
  * [Improve voice recognition accuracy](#improve-voice-recognition-accuracy)
* [Debugging if something isn't working](#debugging-if-something-isnt-working)

## Status
This project is in a work in progress state, meaning both UI and functionality will be improved in the future.

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
If a package is available for your distribution, that's the recommended way for installing. If not, install by following the [manual installation steps](#install-manually)
#### AUR
[![AUR](https://img.shields.io/aur/version/linvam)](https://aur.archlinux.org/packages/linvam)

After installing from AUR, run ``sudo usermod -aG tty,input $USER`` to allow [uinput access without sudo](#udev-rule-for-input)

### Install manually

#### Requirements
- python packages:
  - PyQt6
  - sounddevice
  - srt
  - requests
  - tqdm
  - vosk
- ffmpeg
- [ydotool](https://github.com/ReimuNotMoe/ydotool)

#### Installation steps
<details>
<summary>PC</summary>

The recommended way for the manual installation is by using [`pipx`](https://pypa.github.io/pipx/) to benefit from isolated environments
- Download the latest release source code from the [Releases page](https://github.com/stele95/LinVAM/releases), extract it, enter scripts folder, open terminal in that folder and execute the following command:

      sh install.sh

- Restart your device when finished

</details>

####

<details>
<summary>Steam Deck</summary>

You will have to use the desktop mode on the Steam Deck for installing and setting up ``LinVAM``

- Install [`pipx`](https://pypa.github.io/pipx/) to benefit from isolated environments by running in the terminal:

      python3 -m pip install --user pipx && python3 -m pipx ensurepath

- Download the latest release source code from the [Releases page](https://github.com/stele95/LinVAM/releases), extract it, enter scripts folder, open terminal in that folder and execute the following command:

      sh steam-deck-install.sh

- Restart your device when finished

Since SteamOS is built around the read-only root partition, you will have to do the following steps after every SteamOS update:
- Update SteamOS and restart your Steam Deck
- Run the following command from the scripts folder

      sh steam-deck-configure-uinput-access.sh

- Restart your Steam Deck

</details>

## Configuring uinput access
### TL/DR
- Run ``configure-uinput-access.sh`` if you didn't install by running ``build-and-install.sh``, this will set up [Udev rule for input](#udev-rule-for-input)

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
Start LinVAM from your list of applications or by typing ``linvam`` in the terminal. This works on both X11 and Wayland, but prior uinput access setup is required, read [Configuring uinput access](#configuring-uinput-access)

### Usage with Steam

<details>
<summary>PC</summary>

After setting up profiles in the GUI app, you can add ``linvamrun --profile='Profile name' -- %command%`` to the game launch options for starting the console app for listening when opening games.

You can also use ``--language='languageName'`` for specifying a language. If ``--language`` argument is not used, app defaults to language selected in the GUI app.

![Steam launch options](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/steam.png)
</details>

####

<details>
<summary>Steam Deck</summary>

After setting up profiles in the GUI app, you can add ``linvamrun --use-keyboard --use-mouse --profile='Profile name' -- %command%`` to the game launch options for starting the console app for listening when opening games.

You can also use ``--language='languageName'`` for specifying a language. If ``--language`` argument is not used, app defaults to language selected in the GUI app.

![Steam launch options](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/steam.png)
</details>

### Display LinVAM profile and language in MangoHud
If you are using [MangoHud](https://github.com/flightlessmango/MangoHud), you can set it up for displaying selected LinVAM profile and language.

Run the following command in the terminal after installing ``LinVAM``:

    linvam --setup-mangohud

This expects a ``MangoHud.conf`` file located at ``~/.config/MangoHud/``. If your config file is located in some other place, execute the previous command like this where ``/path/to/dir/`` is a path to a dir containing ``MangoHud.conf`` file:

    linvam --setup-mangohud --path='/path/to/dir/'

For this to work, you will need ``sed`` and ``grep`` which are probably already installed, if not install them with your package managers.

### Profiles
Multiple profiles are supported. To create a new profile for a specific task/game click ``Add`` and the main profile editor window will be displayed.
Profiles are saved to and loaded from ``profiles.json`` file located at ``/home/$USER/.local/share/LinVAM/``.

Backup options:
- Use ``Export`` to export ``profiles.json`` file to selected location for backing up.
- Use ``Import`` to import profiles from ``profiles.json`` file when restoring backup. CAUTION! This overrides any existing profiles.
- Use ``Merge`` to add profiles from ``profiles.json`` file you selected. This doesn't delete existing profiles, it adds new ones alongside existing ones.

![Main GUI Profiles](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/main-gui-profiles.png)
### Input mode
You can choose between two input modes for LinVAM to listen to your commands (``linvamrun`` will use the option selected in the GUI before starting ``linvamrun``):
- ``Always on`` - LinVAM is always listening to what you are saying
- ``Push to listen`` - LinVAM is only listening when you hold the set keybind. If this mode is selected and no keybind is set, listening will be always active as if ``Always on`` was selected

![Main GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/main-gui.png)
### Key combinations
For inputting combinations, press the ``Start recording`` button and then enter the desired combination by pressing keys on the keyboard in the desired order. Once finished, press ``Stop recording``.

![Combinations](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/combination.png)
### Complex commands
It is possible to add multiple actions to a voice command for complex macros with the ability to add a pause between each action.
You can also assign mouse movements and system commands if you require (e.g. opening applications such as calculator, browser etc.)

![Commands GUI](https://raw.githubusercontent.com/stele95/LinVAM/master/.img/complex.png)

### Output audio
In the Command Edit Dialog, choose 'Play sound'. Pick the sound you would like to play.

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

## Debugging if something isn't working
You can use the following arguments with ``linvam`` or ``linvamrun`` for debugging when something isn't working:
- ``--debug`` - prints additional info while running
- ``--use-keyboard`` - LinVAM will try and input keyboard events directly to ``input`` instead of through ``ydotool``
- ``--use-mouse`` - LinVAM will try and input mouse events directly to ``input`` instead of through ``ydotool``
