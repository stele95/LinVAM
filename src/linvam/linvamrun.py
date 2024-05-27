#!/usr/bin/python3
import json
import signal
import subprocess
import sys

from profileexecutor import ProfileExecutor
from util import (get_config, get_language_name, save_linvamrun_run_config, delete_linvamrun_run_file, CONST_VERSION,
                  init_config_folder, LINVAM_COMMANDS_FILE_PATH, read_profiles, update_profiles_for_new_version,
                  handle_args)


class LinVAMRun:
    def __init__(self):
        update_profiles_for_new_version()
        self.m_profile_executor = None
        self.m_config = {
            'profileName': '',
            'language': self.get_language_from_database(),
            'openCommandsFile': 0,
            'debug': 0,
            'keyboard': 0,
            'mouse': 0
        }
        init_config_folder()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def start_listening(self):
        handle_args(self.m_config)
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
        profiles = read_profiles()
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


def linvamrun():
    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print("Version: " + str(CONST_VERSION))
        sys.exit()
    run = LinVAMRun()
    RUN_COMMANDS = []
    IS_ARGS = True
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            arg = sys.argv[i]
            if IS_ARGS:
                if arg == '--':
                    IS_ARGS = False
            else:
                RUN_COMMANDS.append(arg)
            i += 1
    run.start_listening()
    if len(RUN_COMMANDS) > 0:
        try:
            result = subprocess.run(RUN_COMMANDS, check=False)
        except subprocess.CalledProcessError as e:
            print('linvamrun: Command failed with return code ' + str(e.returncode))
        run.shut_down()
        sys.exit()
    else:
        print('linvamrun: Close the app with Ctrl + C')
        signal.signal(signal.SIGTERM, run.signal_handler)
        signal.signal(signal.SIGHUP, run.signal_handler)
        signal.signal(signal.SIGINT, run.signal_handler)
        signal.pause()
        sys.exit()


if __name__ == "__main__":
    linvamrun()
