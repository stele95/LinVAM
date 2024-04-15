import codecs
import json
import os
import re
import subprocess
import sys

CONST_VERSION = '0.6.4-git'
HOME_DIR = os.path.expanduser('~')
LINVAM_SETTINGS_FOLDER = HOME_DIR + '/.local/share/LinVAM/'
COMMANDS_LIST_FILE = 'commands.list'
LINVAM_COMMANDS_FILE_PATH = LINVAM_SETTINGS_FOLDER + COMMANDS_LIST_FILE
YDOTOOLD_SOCKET_PATH = LINVAM_SETTINGS_FOLDER + '.ydotoold_socket'
KEYS_SPLITTER = '->'
OLD_KEYS_SPLITTER = '+'
DEFAULT_KEY_DELAY_IN_MILLISECONDS = 60
PROFILES_FILE_NAME = 'profiles.json'


def handle_args(config):
    if len(sys.argv) == 1:
        return
    for argument in sys.argv:
        # noinspection PyBroadException
        # pylint: disable=bare-except
        try:
            arg_split = argument.split('=')
            match arg_split[0]:
                case '--debug':
                    config['debug'] = 1
                case '--use-keyboard':
                    config['keyboard'] = 1
                case '--use-mouse':
                    config['mouse'] = 1
                case '--profile':
                    config['profileName'] = arg_split[1]
                case '--language':
                    config['language'] = arg_split[1]
                case '--open-commands':
                    config['openCommandsFile'] = 1
        except Exception as ex:
            print('Error parsing argument ' + str(argument) + ": " + str(ex))


def get_supported_languages():
    return [
        'English',
        'Russian',
        'Chinese',
        'French',
        'German'
    ]


# pylint: disable=too-many-nested-blocks
def update_profiles_for_new_version():
    if not get_config('profiles_updated'):
        try:
            profiles = json.loads(read_profiles())
            for profile in profiles:
                for command in profile['commands']:
                    for action in command['actions']:
                        if action['name'] == 'key action':
                            if 'key_events' not in action:
                                commands = create_commands_list(action['key'])
                                action['key_events'] = commands
                            if 'delay' not in action:
                                action['delay'] = DEFAULT_KEY_DELAY_IN_MILLISECONDS
            save_profiles(profiles)
            save_config('profiles_updated', True)
        except Exception as ex:
            print(str(ex))


def save_profiles(profiles):
    with codecs.open(get_settings_path(PROFILES_FILE_NAME), "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)
        f.close()


def read_profiles():
    try:
        with codecs.open(get_settings_path(PROFILES_FILE_NAME), "r", encoding="utf-8") as f:
            profiles = f.read()
            f.close()
        return profiles
    except Exception as ex:
        print(str(ex))
        return '[]'


def copy_profiles_to_dir(directory_path):
    os.system('cp ' + get_settings_path(PROFILES_FILE_NAME) + ' ' + directory_path)


def import_profiles_from_file(file_path):
    try:
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            profiles = f.read()
            f.close()
            save_profiles(json.loads(profiles))
    except Exception as ex:
        print(str(ex))


def merge_profiles(file_path):
    try:
        current_profiles = json.loads(read_profiles())
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            new_profiles = f.read()
            f.close()
        for profile in json.loads(new_profiles):
            profile['name'] = get_safe_name(current_profiles, profile['name'])
            current_profiles.append(profile)
        save_profiles(current_profiles)
    except Exception as ex:
        print(str(ex))


def get_safe_name(profiles, text):
    i = 0
    while name_exists(profiles, text):
        number = '(' + str(i) + ')'
        if number in text:
            text = str(text).replace(number, '').strip()
        i += 1
        text = text + ' (' + str(i) + ')'
    return text


def name_exists(profiles, text):
    found = False
    i = 0
    while not found and i < len(profiles):
        found = profiles[i]['name'] == text
        i += 1
    return found


def save_to_commands_file(commands):
    with codecs.open(get_settings_path(COMMANDS_LIST_FILE), 'w', encoding="utf-8") as f:
        json.dump(commands, f, indent=4, ensure_ascii=False)
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
        json.dump(configs, f, indent=4, ensure_ascii=False)
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
        json.dump(configs, f, indent=4, ensure_ascii=False)
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
    # noinspection PyBroadException
    # pylint: disable=bare-except
    try:
        return get_configs()[config_name]
    except:
        return ''


def save_config(config_name, value):
    configs = get_configs()
    configs[config_name] = value
    with codecs.open(get_settings_path('config'), "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)
        f.close()


def get_default_config_values():
    return json.dumps({'profile': '', 'language': 'English'}, indent=4, ensure_ascii=False)


def get_default_run_config_values():
    return json.dumps({'profile': '', 'language': ''}, indent=4, ensure_ascii=False)


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


def create_commands_list(keys):
    if KEYS_SPLITTER in keys:
        keys_list = keys.split(KEYS_SPLITTER)
    else:
        keys_list = keys.split(OLD_KEYS_SPLITTER)
    commands = ""
    for key in keys_list:
        if not commands:
            commands = create_key_event(key)
        else:
            commands += KEYS_SPLITTER + create_key_event(key)
    return commands


def create_key_event(w_key):
    if "hold" in w_key:
        w_key = re.sub('hold', '', w_key, flags=re.IGNORECASE)
        w_key = map_key(w_key.strip())
        if len(w_key) < 1:
            return ''
        return str(w_key) + ":1"

    if "release" in w_key:
        w_key = re.sub('release', '', w_key, flags=re.IGNORECASE)
        w_key = map_key(w_key.strip())
        if len(w_key) < 1:
            return ''
        return str(w_key) + ":0"

    w_key = map_key(w_key.strip())
    if len(w_key) < 1:
        return ''
    return str(w_key) + ":1" + KEYS_SPLITTER + str(w_key) + ":0"


# pylint: disable=too-many-return-statements
def map_key(w_key):
    # ydotool has a different key mapping.
    # check /usr/include/linux/input-event-codes.h for key mappings
    match w_key.casefold():
        case 'ctrl':
            return '29'
        case 'left ctrl':
            return '29'
        case 'right ctrl':
            return '97'
        case 'left shift':
            return '42'
        case 'right shift':
            return '54'
        case 'alt':
            return '56'
        case 'left alt':
            return '56'
        case 'right alt':
            return '100'
        case 'alt gr':
            return '100'
        case 'windows':
            return '125'
        case 'left windows':
            return '125'
        case 'right windows':
            return '126'
        case 'left super':
            return '125'
        case 'right super':
            return '126'
        case 'left meta':
            return '125'
        case 'right meta':
            return '126'
        case 'tab':
            return '15'
        case 'esc':
            return '1'
        case 'left':
            return '105'
        case 'right':
            return '106'
        case 'up':
            return '103'
        case 'down':
            return '108'
        case 'insert':
            return '110'
        case 'delete':
            return '111'
        case 'home':
            return '102'
        case 'end':
            return '107'
        case 'pageup':
            return '104'
        case 'pagedown':
            return '109'
        case 'return':
            return '28'
        case 'enter':
            return '28'
        case 'backspace':
            return '14'
        case '1':
            return '2'
        case '2':
            return '3'
        case '3':
            return '4'
        case '4':
            return '5'
        case '5':
            return '6'
        case '6':
            return '7'
        case '7':
            return '8'
        case '8':
            return '9'
        case '9':
            return '10'
        case '0':
            return '11'
        case '-':
            return '12'
        case '=':
            return '13'
        case 'q':
            return '16'
        case 'w':
            return '17'
        case 'e':
            return '18'
        case 'r':
            return '19'
        case 't':
            return '20'
        case 'y':
            return '21'
        case 'u':
            return '22'
        case 'i':
            return '23'
        case 'o':
            return '24'
        case 'p':
            return '25'
        case 'left bracket':
            return '26'
        case 'right bracket':
            return '27'
        case 'a':
            return '30'
        case 's':
            return '31'
        case 'd':
            return '32'
        case 'f':
            return '33'
        case 'g':
            return '34'
        case 'h':
            return '35'
        case 'j':
            return '36'
        case 'k':
            return '37'
        case 'l':
            return '38'
        case ';':
            return '39'
        case '\'':
            return '40'
        case 'backslash':
            return '43'
        case 'z':
            return '44'
        case 'x':
            return '45'
        case 'c':
            return '46'
        case 'v':
            return '47'
        case 'b':
            return '48'
        case 'n':
            return '49'
        case 'm':
            return '50'
        case ',':
            return '51'
        case '.':
            return '52'
        case 'forwardslash':
            return '53'
        case 'space':
            return '57'
        case 'capslock':
            return '58'
        case 'f1':
            return '59'
        case 'f2':
            return '60'
        case 'f3':
            return '61'
        case 'f4':
            return '62'
        case 'f5':
            return '63'
        case 'f6':
            return '64'
        case 'f7':
            return '65'
        case 'f8':
            return '66'
        case 'f9':
            return '67'
        case 'f10':
            return '68'
        case 'f11':
            return '87'
        case 'f12':
            return '88'
        case 'scrolllock':
            return '70'
        case 'numlock':
            return '69'
        case 'n7':  # Num 7
            return '71'
        case 'n8':  # Num 8
            return '72'
        case 'n9':  # Num 9
            return '73'
        case 'n-':  # Num -
            return '74'
        case 'n4':  # Num 4
            return '75'
        case 'n5':  # Num 5
            return '76'
        case 'n6':  # Num 6
            return '77'
        case 'nplus':  # Num +
            return '78'
        case 'n1':  # Num 1
            return '79'
        case 'n2':  # Num 2
            return '80'
        case 'n3':  # Num 3
            return '81'
        case 'n0':  # Num 0
            return '82'
        case 'ndot':  # Num .
            return '83'
        case _:
            return ''


MANGOHUD_CONF_FILE_APPEND_COMMANDS = [
    'custom_text=LinVAM',
    'exec=sh ~/.local/share/LinVAM/mangohud-profile.sh',
    'exec=sh ~/.local/share/LinVAM/mangohud-language.sh'
]

MANGOHUD_LANGUAGE_SCRIPT = [
    '#!/bin/bash',
    'if [ -f ~/.local/share/LinVAM/.linvamrun ]',
    'then',
    # pylint: disable=line-too-long
    '  language=$(cat ~/.local/share/LinVAM/.linvamrun | grep "language" | sed "s/\\"language\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '  echo "$language"',
    'elif [ -f ~/.local/share/LinVAM/.linvam ]',
    'then',
    # pylint: disable=line-too-long
    '  language=$(cat ~/.local/share/LinVAM/.linvam | grep "language" | sed "s/\\"language\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '  echo "$language"',
    'fi'
]

MANGOHUD_PROFILE_SCRIPT = [
    '#!/bin/bash',
    'if [ -f ~/.local/share/LinVAM/.linvamrun ]',
    'then',
    # pylint: disable=line-too-long
    '  profile=$(cat ~/.local/share/LinVAM/.linvamrun | grep "profile" | sed "s/\\"profile\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '  echo "$profile"',
    'elif [ -f ~/.local/share/LinVAM/.linvam ]',
    'then',
    # pylint: disable=line-too-long
    '  profile=$(cat ~/.local/share/LinVAM/.linvam | grep "profile" | sed "s/\\"profile\\"://g;s/^[ \\t]*//;s/[\\",]//g;s/[ \\t]*$//")',
    '  echo "$profile"',
    'else',
    '  echo "OFF"',
    'fi'
]
