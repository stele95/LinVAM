import codecs
import json
import os
import subprocess

CONST_VERSION = '0.6.1'
HOME_DIR = os.path.expanduser('~')
LINVAM_SETTINGS_FOLDER = HOME_DIR + '/.local/share/LinVAM/'
COMMANDS_LIST_FILE = 'commands.list'
LINVAM_COMMANDS_FILE_PATH = LINVAM_SETTINGS_FOLDER + COMMANDS_LIST_FILE
YDOTOOLD_SOCKET_PATH = LINVAM_SETTINGS_FOLDER + '.ydotoold_socket'
KEYS_SPLITTER = '->'
OLD_KEYS_SPLITTER = '+'
DEFAULT_KEY_DELAY_IN_MILLISECONDS = 60
PROFILES_FILE_NAME = 'profiles.json'


def get_supported_languages():
    return [
        'English',
        'Russian',
        'Chinese',
        'French',
        'German'
    ]


def save_profiles(profiles):
    with codecs.open(get_settings_path(PROFILES_FILE_NAME), "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4)
        f.close()


def read_profiles():
    with codecs.open(get_settings_path(PROFILES_FILE_NAME), "r", encoding="utf-8") as f:
        profiles = f.read()
        f.close()
    return profiles


def save_profiles_to_file(directory_path):
    os.system('cp ' + get_settings_path(PROFILES_FILE_NAME) + ' ' + directory_path)


def save_to_commands_file(commands):
    with codecs.open(get_settings_path(COMMANDS_LIST_FILE), 'w', encoding="utf-8") as f:
        json.dump(commands, f, indent=4)
        f.close()


def get_language_code(language_name):
    if language_name in ['English', 'english', 'en']:
        return 'en-us'
    if language_name in ['Russian', 'russian', 'ru', 'русский']:
        return 'ru'
    if language_name in ['Chinese', 'cn']:
        return 'cn'
    if language_name in ['French', 'fr']:
        return 'fr'
    if language_name in ['German', 'de']:
        return 'de'
    return None


def get_language_name(language_name):
    if language_name in ['English', 'english', 'en']:
        return 'English'
    if language_name in ['Russian', 'russian', 'ru', 'русский']:
        return 'Russian'
    if language_name in ['Chinese', 'cn']:
        return 'Chinese'
    if language_name in ['French', 'fr']:
        return 'French'
    if language_name in ['German', 'de']:
        return 'German'
    return None


def init_config_folder():
    if not os.path.exists(LINVAM_SETTINGS_FOLDER):
        os.mkdir(LINVAM_SETTINGS_FOLDER)


def get_settings_path(setting, default_value=None):
    file = LINVAM_SETTINGS_FOLDER + setting
    if not os.path.exists(file):
        with (codecs.open(file, "w", encoding="utf-8")) as f:
            if default_value is not None:
                f.write(default_value)
            f.close()
    return file


def get_linvam_run_file_path():
    return get_settings_path('.linvam', get_default_run_config_values())


def delete_linvam_run_file():
    file = get_linvam_run_file_path()
    os.remove(file)


def save_linvam_run_config(config_name, value):
    configs = get_linvam_run_configs()
    configs[config_name] = value
    with codecs.open(get_linvam_run_file_path(), "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4)
        f.close()


def get_linvam_run_configs():
    with codecs.open(get_linvam_run_file_path(), "r", encoding="utf-8") as f:
        config_text = f.read()
        f.close()
    return json.loads(config_text)


def delete_linvamrun_run_file():
    file = get_linvamrun_run_file_path()
    os.remove(file)


def get_linvamrun_run_file_path():
    return get_settings_path('.linvamrun', get_default_run_config_values())


def save_linvamrun_run_config(config_name, value):
    configs = get_linvamrun_run_configs()
    configs[config_name] = value
    with codecs.open(get_linvamrun_run_file_path(), "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4)
        f.close()


def get_linvamrun_run_configs():
    with codecs.open(get_linvamrun_run_file_path(), "r", encoding="utf-8") as f:
        config_text = f.read()
        f.close()
    return json.loads(config_text)


def get_configs():
    with codecs.open(get_settings_path('config', get_default_config_values()), "r", encoding="utf-8") as f:
        config_text = f.read()
        f.close()
    return json.loads(config_text)


def get_config(config_name):
    return get_configs()[config_name]


def save_config(config_name, value):
    configs = get_configs()
    configs[config_name] = value
    with codecs.open(get_settings_path('config'), "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4)
        f.close()


def get_default_config_values():
    return json.dumps({'profile': '', 'language': 'English'}, indent=4)


def get_default_run_config_values():
    return json.dumps({'profile': '', 'language': ''}, indent=4)


def get_voice_packs_folder_path():
    return HOME_DIR + '/voicepacks/'


MANGOHUD_CONF_DIR = HOME_DIR + '/.config/MangoHud/'
MANGOHUD_CONF_FILE = 'MangoHud.conf'


def does_mangohud_conf_file_exist(directory):
    return os.path.exists(get_mangohud_file_path(directory))


def is_mangohud_set_up(directory):
    # pylint: disable=consider-using-with
    ps = subprocess.Popen("cat " + get_mangohud_file_path(directory) + " | grep custom_text=LinVAM", shell=True,
                          stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return 'custom_text=LinVAM' in str(output)


def setup_mangohud(directory=MANGOHUD_CONF_DIR):
    if not does_mangohud_conf_file_exist(directory):
        print('MangoHud.conf file not found in ' + directory)
    elif is_mangohud_set_up(directory):
        print('MangoHud already set up')
    else:
        init_config_folder()
        write_to_mangohud_language_script_file()
        write_to_mangohud_profile_script_file()
        with (codecs.open(get_mangohud_file_path(directory), "a", encoding="utf-8")) as f:
            f.writelines(line + '\n' for line in MANGOHUD_CONF_FILE_APPEND_COMMANDS)
            f.close()
        print('Setup finished.')


def get_mangohud_file_path(directory):
    prefix = ''
    if str(directory).startswith('~'):
        prefix = os.path.expanduser('~')
    directory = directory.replace('~', prefix)
    if str(directory).endswith('/'):
        return directory + MANGOHUD_CONF_FILE
    return directory + '/' + MANGOHUD_CONF_FILE


def write_to_mangohud_language_script_file():
    with (codecs.open(LINVAM_SETTINGS_FOLDER + 'mangohud-language.sh', "w", encoding="utf-8")) as f:
        f.writelines(line + '\n' for line in MANGOHUD_LANGUAGE_SCRIPT)
        f.close()


def write_to_mangohud_profile_script_file():
    with (codecs.open(LINVAM_SETTINGS_FOLDER + 'mangohud-profile.sh', "w", encoding="utf-8")) as f:
        f.writelines(line + '\n' for line in MANGOHUD_PROFILE_SCRIPT)
        f.close()


MANGOHUD_CONF_FILE_APPEND_COMMANDS = [
    'custom_text=LinVAM',
    'exec=sh ~/.local/share/LinVAM/mangohud-profile.sh',
    'exec=sh ~/.local/share/LinVAM/mangohud-language.sh'
]

MANGOHUD_LANGUAGE_SCRIPT = [
    '#!/bin/bash',
    'linvam=$(ps --no-headers -C linvam -o args,state)',
    'linvamrun=$(ps --no-headers -C linvamrun -o args,state)',
    'if [ -n "$linvamrun" ] || [ -f ~/.local/share/LinVAM/.linvamrun ]',
    'then',
    '  if [ -f ~/.local/share/LinVAM/.linvamrun ]',
    '  then',
    # pylint: disable=line-too-long
    '    language=$(cat ~/.local/share/LinVAM/.linvamrun | grep "language" | sed "s/\\"language\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '    echo "$language"',
    '  fi',
    'elif [ -n "$linvam" ] || [ -f ~/.local/share/LinVAM/.linvam ]',
    'then',
    '  if [ -f ~/.local/share/LinVAM/.linvam ]',
    '    then',
    # pylint: disable=line-too-long
    '      language=$(cat ~/.local/share/LinVAM/.linvam | grep "language" | sed "s/\\"language\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '      echo "$language"',
    '  fi',
    'fi'
]

MANGOHUD_PROFILE_SCRIPT = [
    '#!/bin/bash',
    'linvam=$(ps --no-headers -C linvam -o args,state)',
    'linvamrun=$(ps --no-headers -C linvamrun -o args,state)',
    'if [ -n "$linvamrun" ] || [ -f ~/.local/share/LinVAM/.linvamrun ]',
    'then',
    '  if [ -f ~/.local/share/LinVAM/.linvamrun ]',
    '  then',
    # pylint: disable=line-too-long
    '    profile=$(cat ~/.local/share/LinVAM/.linvamrun | grep "profile" | sed "s/\\"profile\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '    echo "$profile"',
    '  else',
    '    echo "ON"',
    '  fi',
    'elif [ -n "$linvam" ] || [ -f ~/.local/share/LinVAM/.linvam ]',
    'then',
    '  if [ -f ~/.local/share/LinVAM/.linvam ]',
    '    then',
    # pylint: disable=line-too-long
    '      profile=$(cat ~/.local/share/LinVAM/.linvam | grep "profile" | sed "s/\\"profile\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '      echo "$profile"',
    '  else',
    '    echo "ON"',
    '  fi',
    'else',
    '  echo "OFF"',
    'fi'
]
