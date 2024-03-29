#!/usr/bin/python3
import json
import shlex
import signal
import subprocess
import sys

from profileexecutor import ProfileExecutor, get_settings_path
from soundfiles import SoundFiles


class LinVAMRun:
    def __init__(self):
        self.m_profile_executor = None
        self.m_config = {
            'testEnv': 0,
            'profileName': ''
        }
        self.m_sound = SoundFiles()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def start_listening(self, run_args):
        self.handle_args(run_args)
        self.m_profile_executor = ProfileExecutor(None, self)
        profile_name = self.m_config['profileName']
        if len(profile_name) == 0:
            print('linvamrun: No profile specified, not listening...')
            return
        profile = self._get_profile_from_database(profile_name)
        if len(profile) > 0:
            print('linvamrun: Listening for profile: ' + str(profile['name']))
            self.m_profile_executor.set_profile(profile)
            self.m_profile_executor.set_enable_listening(True)
        else:
            print('linvamrun: Profile not found, not listening...')

    def handle_args(self, run_args):
        if len(run_args) == 0:
            return
        for argument in run_args:
            # noinspection PyBroadException
            try:
                arg_split = argument.split('=')
                if arg_split[0] == '--profile':
                    self.m_config['profileName'] = arg_split[1]
            except:
                if argument == '-testEnv':
                    self.m_config['testEnv'] = 1
                else:
                    print('linvamrun: Unknown or unsupported argument')

    # noinspection PyUnusedLocal
    def signal_handler(self, s, f):
        self.shut_down()

    def shut_down(self):
        self.m_profile_executor.set_enable_listening(False)
        print('linvamrun: Shutting down')

    @staticmethod
    def _get_profile_from_database(profile_name):
        with open(get_settings_path("profiles.json"), "r", encoding="utf-8") as f:
            profiles = f.read()
            f.close()
            # noinspection PyBroadException
            try:
                w_profiles = json.loads(profiles)
                for position, w_profile in enumerate(w_profiles):
                    name = w_profile['name']
                    if name == profile_name:
                        return w_profile
            except:
                print("linvamrun: No profiles found in file")
        return {}


if __name__ == "__main__":
    linvamrun = LinVAMRun()
    args = []
    runCommands = ''
    isArgs = True
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            arg = sys.argv[i]
            if isArgs:
                if arg == '--':
                    isArgs = False
                else:
                    args.append(arg)
            else:
                if len(runCommands) != 0:
                    runCommands += ' '
                runCommands = runCommands + '\'' + arg + '\''
            i += 1
    linvamrun.start_listening(args)
    if len(runCommands) > 0:
        argsForSubprocess = shlex.split(runCommands)
        try:
            result = subprocess.run(argsForSubprocess)
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
