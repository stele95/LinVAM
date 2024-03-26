#!/usr/bin/python3
import json
from profileexecutor import ProfileExecutor
import sys
import signal
import os
import subprocess
import shlex
from soundfiles import SoundFiles


class LinVAMConsole:
    def __init__(self):
        self.m_config = {
            'testEnv': 0,
            'profileName': ''
        }
        self.m_sound = SoundFiles()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def startListening(self, args):
        self.handleArgs(args)
        self.m_profileExecutor = ProfileExecutor(None, self)
        profileName = self.m_config['profileName']
        if len(profileName) == 0:
            print('LinVAM Console: No profile specified, not listening...')
            return
        profile = self.getProfileFromDatabase(profileName)
        if len(profile) > 0:
            print('LinVAM Console: Listening for profile: ' + str(profile['name']))
            self.m_profileExecutor.setProfile(profile)
            self.m_profileExecutor.setEnableListening(True)
        else:
            print('LinVAM Console: Profile not found, not listening...')

    def handleArgs(self, args):
        if len(args) == 0:
            return
        for arg in args:
            try:
                argSplit = arg.split('=')
                if argSplit[0] == '--profile':
                    self.m_config['profileName'] = argSplit[1]
            except:
                if arg == '-testEnv':
                    self.m_config['testEnv'] = 1
                else:
                    print('LinVAM Console: Unknown or unsupported argument')

    def signalHandler(self, signal, frame):
        self.shutDown()

    def shutDown(self):
        self.m_profileExecutor.setEnableListening(False)
        print('LinVAM Console: Shutting down')

    def getProfileFromDatabase(self, profileName):
        with open(self.getSettingsPath("profiles.json"), "r") as f:
            profiles = f.read()
            f.close()
            try:
                w_profiles = json.loads(profiles)
                for position, w_profile in enumerate(w_profiles):
                    name = w_profile['name']
                    if name == profileName:
                        return w_profile
            except:
                print("LinVAM Console: No profiles found in file")
        return ''

    def getSettingsPath(self, setting):
        home = os.path.expanduser("~") + '/.local/share/LinVAM/'
        if not os.path.exists(home):
            os.mkdir(home)
        file = home + setting
        if not os.path.exists(file):
            with(open(file, "w")) as f:
                f.close()
        return file

if __name__ == "__main__":
    linvamConsole = LinVAMConsole()
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
                    runCommands = runCommands + ' '
                runCommands = runCommands + '\'' + arg + '\''
            i += 1
    linvamConsole.startListening(args)
    if len(runCommands) > 0:
        argsForSubprocess = shlex.split(runCommands)
        try:
            result = subprocess.run(argsForSubprocess)
        except subprocess.CalledProcessError as e:
            print('LinVAM Console: Command failed with return code {e.returncode}')
        linvamConsole.shutDown()
        sys.exit()
    else:
        print('LinVAM Console: Close the app with Ctrl + C')
        signal.signal(signal.SIGTERM, linvamConsole.signalHandler)
        signal.signal(signal.SIGHUP, linvamConsole.signalHandler)
        signal.signal(signal.SIGINT, linvamConsole.signalHandler)
        signal.pause()
        sys.exit()
