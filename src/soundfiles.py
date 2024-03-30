import os
import shlex
import signal
import subprocess
from os import path

from util import get_voice_packs_folder_path


# I've tried a couple of libs that are capable of playing mp3:
# pysound - offers no way to stop sounds. can't play files with whitespace in path
# pygame  - has problems with certain mp3 files from voice packs
# mpg123 - does not offer volume control. need to be threaded as it's a system binary
#
# ffplay - need to be threaded as it's a system binary. i picked this one as it uses ffmpeg which
#          is an excellent tool and should be installed on any system already
#          I needed some process stuff to be able to stop an already playing sound (kill ffplay subprocess)


class SoundFiles:
    def __init__(self):
        print("SoundFiles: init")
        self.m_sounds = {}
        self.scan_sound_files()
        self.thread_play = None
        self.volume = 100

    def scan_sound_files(self):
        print("SoundFiles: scanning")
        voicepacks = get_voice_packs_folder_path()
        if not path.exists(voicepacks):
            print("No folder 'voicepacks' found. Please create one and copy all your voicepacks in there.")
            return

        for root, _, files in os.walk(voicepacks):
            for file in files:
                if file.endswith(".mp3"):
                    # we expect a path like this:
                    # voicepacks/VOICEPACKNAME/COMMANDGROUP/(FURTHER_OPTIONAL_FOLDERS/)FILE
                    path_parts = root.split('/')

                    if len(path_parts) < 4:
                        continue

                    if not path_parts[2] in self.m_sounds:
                        self.m_sounds[path_parts[2]] = {}

                    category = path_parts[3]
                    # there might be subfolders, so we have more than just 4 split results...
                    # for the ease of my mind, we concat the voicepack subfolders to 1 category name
                    # like voicepacks/hcspack/Characters/Astra/blah.mp3 will become:
                    #
                    # voicepack = hcspack
                    # category  = Characters/Astra
                    # file      = blah.mp4

                    if len(path_parts) > 4:
                        for i in range(4, len(path_parts)):
                            category = category + '/' + path_parts[i]

                    if category not in self.m_sounds[path_parts[2]]:
                        self.m_sounds[path_parts[2]][category] = []

                    self.m_sounds[path_parts[2]][category].append(file)

    def play(self, sound_file):
        if not os.path.isfile(sound_file):
            print("ERROR - Sound file not found: ", sound_file)
            return
        self.stop()
        # construct shell command. use shlex to split it up into valid args for Popen.
        cmd = "ffplay -nodisp -autoexit -loglevel quiet -volume " + str(self.volume) + " \"" + sound_file + "\""
        args = shlex.split(cmd)
        # noinspection PyBroadException
        try:
            with subprocess.Popen(args) as process:
                self.thread_play = process
        except Exception as e:
            print('Failed to load ffplay: ' + str(e))

    def stop(self):
        if self.thread_play is not None:
            # that aint no nice, but it's the only way i got the subprocess reliably killed.
            # self.thread_play.terminate() or kill() should do the trick, but it won't
            try:
                os.kill(self.thread_play.pid, signal.SIGKILL)
            except OSError:
                pass

    def set_volume(self, volume):
        self.volume = volume
