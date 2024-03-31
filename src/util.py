import json
import os


def get_supported_languages():
    return [
        'English',
        'Russian',
        'Chinese',
        'French',
        'German'
    ]


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


def get_settings_path(setting, default_value=None):
    home = os.path.expanduser("~") + '/.local/share/LinVAM/'
    if not os.path.exists(home):
        os.mkdir(home)
    file = home + setting
    if not os.path.exists(file):
        with (open(file, "w", encoding="utf-8")) as f:
            if default_value is not None:
                f.write(default_value)
            f.close()
    return file


def get_configs():
    with open(get_settings_path('config', get_default_config_values()), "r", encoding="utf-8") as f:
        config_text = f.read()
        f.close()
    return json.loads(config_text)


def get_config(config_name):
    return get_configs()[config_name]


def save_config(config_name, value):
    configs = get_configs()
    configs[config_name] = value
    with open(get_settings_path('config'), "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4)
        f.close()


def get_default_config_values():
    return json.dumps({'profile': '', 'language': 'English'}, indent=4)


def get_voice_packs_folder_path():
    return os.path.expanduser("~") + '/voicepacks/'
