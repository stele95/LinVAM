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
            # expecting following paths
            # /home/{user}/voicepacks/file.mp3
            # /home/{user}/voicepacks/subfolder/file.mp3
            # /home/{user}/voicepacks/subfolder/subfolder/file.mp3
            for file in files:
                if file.endswith(".mp3"):
                    path_parts = root.split('/')

                    if len(path_parts) < 5 or path_parts[4] == '':
                        continue

                    voicepack = path_parts[4]

                    if not voicepack in self.m_sounds:
                        self.m_sounds[voicepack] = {}

                    if len(path_parts) > 5:
                        category = path_parts[5]
                    else:
                        category = 'default'
                    # there might be subfolders, so we have more than 6 split results...
                    # for the ease of mind, we concat the voicepack subfolders to 1 category name
                    # like voicepacks/hcspack/Characters/Astra/blah.mp3 will become:
                    #
                    # voicepack = hcspack
                    # category  = Characters/Astra
                    # file      = blah.mp4

                    if len(path_parts) > 6:
                        for i in range(6, len(path_parts)):
                            category = category + '/' + path_parts[i]

                    if category not in self.m_sounds[voicepack]:
                        self.m_sounds[voicepack][category] = []

                    self.m_sounds[voicepack][category].append(file)

    def play(self, sound_file):
        # replace /default/ because it's not a subdirectory
        sound_file = str(sound_file).replace("/default/", "/")
        if not os.path.isfile(sound_file):
            print("ERROR - Sound file not found: ", sound_file)
            return
        self.stop()
        cmd = "ffplay -nodisp -autoexit -loglevel quiet -volume " + str(self.volume) + " \"" + sound_file + "\""
        args = shlex.split(cmd)
        # noinspection PyBroadException
        try:
            self.thread_play = subprocess.Popen(args)
        except Exception as e:
            print('Failed to load ffplay: ' + str(e))

    def stop(self):
        if self.thread_play is not None:
            # that aint no nice, but it's the only way i got the subprocess reliably killed.
            # self.thread_play.terminate() or kill() should do the trick, but it won't
            try:
                os.kill(self.thread_play.pid, signal.SIGKILL)
                self.thread_play = None
            except OSError:
                pass

    def set_volume(self, volume):
        self.volume = volume
