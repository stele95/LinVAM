import time
import threading
import os
from os import path
import subprocess
import shlex
import signal

# I've tried a couple of libs that are capable of playing mp3:
# pysound - offers no way to stop sounds. can't play files with whitespace in path
# pygame  - has problems with certain mp3 files from voice packs
# mpg123 - does not offer volume control. need to be threaded as it's a system binary
#
# ffplay - need to be threaded as it's a system binary. i picked this one as it uses ffmpeg which
#          is an excellent tool and should be installed on any system already
#          I needed some process stuff to be able to stop an already playing sound (kill ffplay subprocess)


class SoundFiles():
	def __init__(self):
		print("SoundFiles: init")
		self.m_sounds = {}
		self.scanSoundFiles()
		self.thread_play = False
		self.volume = 100

	def scanSoundFiles(self):
		print("SoundFiles: scanning")
		if not path.exists('./voicepacks'):
			print("No folder 'voicepacks' found. Please create one and copy all your voicepacks in there.")
			return

		for root, dirs, files in os.walk("./voicepacks"):
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

					if not category in self.m_sounds[path_parts[2]]:
						self.m_sounds[path_parts[2]][category] = []

					self.m_sounds[path_parts[2]][category].append(file)

	def play(self, sound_file):
		if not os.path.isfile(sound_file):
			print("ERROR - Sound file not found: ", sound_file)
			return

		self.stop()

		# construct shell command. use shlex to split it up into valid args for Popen.
		cmd = "ffplay -nodisp -autoexit -loglevel quiet -volume " + str(self.volume) + " \"" + sound_file + "\"";
		args = shlex.split(cmd)
		self.thread_play = subprocess.Popen(args)

	def stop(self):
		if not self.thread_play == False:
			# that aint no nice, but it's the only way i got the subprocess reliably killed.
			# self.thread_play.terminate() or kill() should do the trick, but it won't
			try:
				os.kill(self.thread_play.pid, signal.SIGKILL)
			except OSError:
				pass

	def setVolume(self, volume):
		self.volume = volume;
