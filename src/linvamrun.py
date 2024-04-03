#!/usr/bin/python3
import json
import signal
import subprocess
import sys

from profileexecutor import ProfileExecutor, get_settings_path
from soundfiles import SoundFiles
from util import (get_config, get_language_name, save_linvamrun_run_config, delete_linvamrun_run_file, CONST_VERSION,
                  init_config_folder, LINVAM_COMMANDS_FILE_PATH)


class LinVAMRun:
    def __init__(self):
        self.m_profile_executor = None
        self.m_config = {
            'profileName': '',
            'language': self.get_language_from_database(),
            'openCommandsFile': 0
        }
        init_config_folder()
        self.m_sound = SoundFiles()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def start_listening(self, run_args):
        self.handle_args(run_args)
        self.m_profile_executor = ProfileExecutor(self)
        language = self.m_config['language']
        self.m_profile_executor.set_language(language)
        language_name = get_language_name(language)
        save_linvamrun_run_config('language', language_name)
        profile_name = self.m_config['profileName']
        if len(profile_name) == 0:
            print('linvamrun: No profile specified, not listening...')
            return
        profile = self._get_profile_from_database(profile_name)
        if len(profile) > 0:
            self.m_profile_executor.set_profile(profile)
            save_linvamrun_run_config('profile', profile['name'])
            self.m_profile_executor.set_enable_listening(True)
            if self.m_config['openCommandsFile']:
                # pylint: disable=consider-using-with
                subprocess.Popen(['xdg-open', LINVAM_COMMANDS_FILE_PATH])
        else:
            print('linvamrun: Profile not found, not listening...')

    def handle_args(self, run_args):
        if len(run_args) == 0:
            return
        for argument in run_args:
            # noinspection PyBroadException
            # pylint: disable=bare-except
            try:
                arg_split = argument.split('=')
                match arg_split[0]:
                    case '--profile':
                        self.m_config['profileName'] = arg_split[1]
                    case '--language':
                        self.m_config['language'] = arg_split[1]
                    case '--open-commands':
                        self.m_config['openCommandsFile'] = 1
            except Exception as ex:
                print('Error parsing argument ' + str(argument) + ": " + str(ex))

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    def signal_handler(self, s, f):
        self.shut_down()

    def shut_down(self):
        self.m_profile_executor.shutdown()
        delete_linvamrun_run_file()
        print('linvamrun: Shutting down')

    @staticmethod
    def _get_profile_from_database(profile_name):
        with open(get_settings_path("profiles.json"), "r", encoding="utf-8") as f:
            profiles = f.read()
            f.close()
            # noinspection PyBroadException
            try:
                w_profiles = json.loads(profiles)
                for w_profile in w_profiles:
                    name = w_profile['name']
                    if name == profile_name:
                        return w_profile
            except Exception as ex:
                print("linvamrun: failed loading profiles from file: " + str(ex))
        return {}

    @staticmethod
    def get_language_from_database():
        try:
            return get_config('language')
        except Exception as ex:
            print("linvamrun: failed to load selected language file: " + str(ex))
            return 'en'


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print("Version: " + str(CONST_VERSION))
        sys.exit()
    linvamrun = LinVAMRun()
    args = []
    RUN_COMMANDS = []
    IS_ARGS = True
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            arg = sys.argv[i]
            if IS_ARGS:
                if arg == '--':
                    IS_ARGS = False
                else:
                    args.append(arg)
            else:
                RUN_COMMANDS.append(arg)
            i += 1
    linvamrun.start_listening(args)
    if len(RUN_COMMANDS) > 0:
        try:
            result = subprocess.run(RUN_COMMANDS, check=False)
        except subprocess.CalledProcessError as e:
            print('linvamrun: Command failed with return code ' + str(e.returncode))
        linvamrun.shut_down()
        sys.exit()
    else:
        print('linvamrun: Close the app with Ctrl + C')
        signal.signal(signal.SIGTERM, linvamrun.signal_handler)
        signal.signal(signal.SIGHUP, linvamrun.signal_handler)
        signal.signal(signal.SIGINT, linvamrun.signal_handler)
        signal.pause()
        sys.exit()
