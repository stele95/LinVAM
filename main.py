#!/usr/bin/python3
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ui_mainwnd import Ui_MainWidget
from profileeditwnd import ProfileEditWnd
import json
from profileexecutor import ProfileExecutor
import sys
import pickle
import signal
import os
import shutil
import subprocess
import shlex
from soundfiles import SoundFiles

class MainWnd(QWidget):
	def __init__(self, p_parent = None):
		super().__init__(p_parent)

		self.ui = Ui_MainWidget()
		self.ui.setupUi(self)
		self.handleArgs()
		self.m_sound = SoundFiles()
		self.m_profileExecutor = ProfileExecutor(None, self)

		if not os.geteuid() == 0 and not self.m_config['noroot'] == 1:
			print("\033[93m\nWARNING: no root privileges, unable to send key strokes to the system.\nConsider running this as root.\nFor that you might need to install some python modules for the root user. \n\033[0m")

		self.ui.profileCbx.currentIndexChanged.connect(self.slotProfileChanged)
		self.ui.addBut.clicked.connect(self.slotAddNewProfile)
		self.ui.editBut.clicked.connect(self.slotEditProfile)
		self.ui.copyBut.clicked.connect(self.slotCopyProfile)
		self.ui.removeBut.clicked.connect(self.slotRemoveProfile)
		self.ui.listeningChk.stateChanged.connect(self.slotListeningEnabled)
		self.ui.ok.clicked.connect(self.slotOK)
		self.ui.cancel.clicked.connect(self.slotCancel)
		self.ui.sliderVolume.valueChanged.connect(lambda: self.m_sound.setVolume(self.ui.sliderVolume.value()))
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		if self.loadFromDatabase() > 0 :
		# if self.loadTestProfiles() > 0:
			w_jsonProfile = self.ui.profileCbx.itemData(0)
			if w_jsonProfile != None:
				self.m_activeProfile = json.loads(w_jsonProfile)
				self.m_profileExecutor.setProfile(self.m_activeProfile)
				#self.m_profileExecutor.start()


	def saveToDatabase(self):
		w_profiles = []
		w_profileCnt = self.ui.profileCbx.count()
		for w_idx in range(w_profileCnt):
			w_jsonProfile = self.ui.profileCbx.itemData(w_idx)
			if w_jsonProfile == None:
				continue

			w_profile = json.loads(w_jsonProfile)
			w_profiles.append(w_profile)

		with open(self.getSettingsPath("profiles.dat"), "wb") as f:
			pickle.dump(w_profiles, f, pickle.HIGHEST_PROTOCOL)

	def loadFromDatabase(self):
		w_profiles = []
		with open(self.getSettingsPath("profiles.dat"), "rb") as f:
			w_profiles = pickle.load(f)

		for w_profile in w_profiles:
			self.ui.profileCbx.addItem(w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(self.ui.profileCbx.count() - 1, w_jsonProfile)

		return len(w_profiles)

	def getSettingsPath(self, setting):
		home = os.path.expanduser("~") + '/.linvam/'
		if not os.path.exists(home):
			os.mkdir(home)
		if not os.path.exists(home + setting):
			shutil.copyfile(setting, home + setting)

		return home + setting

	def loadTestProfiles(self):

		w_carProfileDict = {
			"name": "car game",
			"commands": [
				{'name': 'forward',
				 'actions': [
					 {'name': 'key action', 'key': 'up', 'type': 1}
				 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 12
				 },
				{'name': 'back',
				 'actions': [
					 {'name': 'key action', 'key': 'down', 'type': 1}
				 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 3
				 },
				{'name': 'left',
				 'actions': [{'name': 'key action', 'key': 'right', 'type': 0},
							 {'name': 'key action', 'key': 'left', 'type': 1},
							 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 10
				 },
				{'name': 'right',
				 'actions': [{'name': 'key action', 'key': 'left', 'type': 0},
							 {'name': 'key action', 'key': 'right', 'type': 1},
							 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 3
				 },
				{'name': 'stop',
				 'actions': [
					 {'name': 'key action', 'key': 'left', 'type': 0},
					 {'name': 'key action', 'key': 'right', 'type': 0},
					 {'name': 'key action', 'key': 'up', 'type': 0},
					 {'name': 'key action', 'key': 'down', 'type': 0}
				 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 8
				 }
			]
		}

		w_airplaneProfileDict = {
			"name": "airplane game",
			"commands": [
				{'name': 'up',
				 'actions': [
					 {'name': 'command stop action', 'command name': 'down'},
					 {'name': 'mouse move action', 'x': 0, 'y': -5, 'absolute': False},
					 {'name': 'pause action', 'time': 0.01}
				 ],
				 'repeat': -1,
				 'async': True,
				 'threshold': 3
				 },
				{'name': 'left',
				 'actions': [
					 {'name': 'command stop action', 'command name': 'right'},
					 {'name': 'mouse move action', 'x': -5, 'y': 0, 'absolute': False},
					 {'name': 'pause action', 'time': 0.005}
				 ],
				 'repeat': -1,
				 'async': True,
				 'threshold': 3
				 },
				{'name': 'right',
				 'actions': [
					 {'name': 'command stop action', 'command name': 'left'},
					 {'name': 'mouse move action', 'x': 5, 'y': 0, 'absolute': False},
					 {'name': 'pause action', 'time': 0.005}
				 ],
				 'repeat': -1,
				 'async': True,
				 'threshold': 3
				 },
				{'name': 'down',
				 'actions': [
					 {'name': 'command stop action', 'command name': 'up'},
					 {'name': 'mouse move action', 'x': 0, 'y': 5, 'absolute': False},
					 {'name': 'pause action', 'time': 0.005}
				 ],
				 'repeat': -1,
				 'async': True,
				 'threshold': 3
				 },
				{'name': 'shoot',
				 'actions': [
					 {'name': 'mouse click action', 'button': 'left', 'type': 1},
					 {'name': 'pause action', 'time': 0.03}
				 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 3
				 },
				{'name': 'stop',
				 'actions': [
					 {'name': 'command stop action', 'command name': 'up'},
					 {'name': 'command stop action', 'command name': 'left'},
					 {'name': 'command stop action', 'command name': 'right'},
					 {'name': 'command stop action', 'command name': 'down'},
					 {'name': 'mouse click action', 'button': 'left', 'type': 0}
				 ],
				 'repeat': 1,
				 'async': False,
				 'threshold': 3
				 }
			]
		}
		w_profiles = []
		w_profiles.append(w_carProfileDict)
		w_profiles.append(w_airplaneProfileDict)

		i = 0
		for w_profile in w_profiles:
			self.ui.profileCbx.addItem(w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(i, w_jsonProfile)
			i = i + 1

		return i

	def slotProfileChanged(self, p_idx):
		w_jsonProfile = self.ui.profileCbx.itemData(p_idx)
		if w_jsonProfile != None:
			self.m_activeProfile = json.loads(w_jsonProfile)
			self.m_profileExecutor.setProfile(self.m_activeProfile)

	def slotAddNewProfile(self):
		w_profileEditWnd = ProfileEditWnd(None, self)
		if w_profileEditWnd.exec() == QDialog.Accepted:
			w_profile = w_profileEditWnd.m_profile
			self.m_profileExecutor.setProfile(w_profile)
			self.ui.profileCbx.addItem(w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(self.ui.profileCbx.count()-1, w_jsonProfile)

	def slotEditProfile(self):
		w_idx = self.ui.profileCbx.currentIndex()
		w_jsonProfile = self.ui.profileCbx.itemData(w_idx)
		w_profile = json.loads(w_jsonProfile)
		w_profileEditWnd = ProfileEditWnd(w_profile, self)
		if w_profileEditWnd.exec() == QDialog.Accepted:
			w_profile = w_profileEditWnd.m_profile
			self.m_profileExecutor.setProfile(w_profile)
			self.ui.profileCbx.setItemText(w_idx, w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(w_idx, w_jsonProfile)

	def slotCopyProfile(self):
		text, okPressed = QInputDialog.getText(self, "Copy profile", "Enter new profile name:", QLineEdit.Normal, "")
		if okPressed and text != '':
			# todo: check if name not already in use
			w_idx = self.ui.profileCbx.currentIndex()
			w_jsonProfile = self.ui.profileCbx.itemData(w_idx)
			w_profile = json.loads(w_jsonProfile)
			w_profile_copy = w_profile
			w_profile_copy['name'] = text
			self.ui.profileCbx.addItem(w_profile_copy['name'])
			w_jsonProfile = json.dumps(w_profile_copy)
			self.ui.profileCbx.setItemData(self.ui.profileCbx.count()-1, w_jsonProfile)

	def slotRemoveProfile(self):

		buttonReply = QMessageBox.question(self, 'Remove Profile', "Do you really want to delete this profile?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
		if buttonReply == QMessageBox.No:
			return

		w_curIdx = self.ui.profileCbx.currentIndex()
		if w_curIdx >= 0:
			self.ui.profileCbx.removeItem(w_curIdx)

		w_curIdx = self.ui.profileCbx.currentIndex()
		if w_curIdx >= 0:
			w_jsonProfile = self.ui.profileCbx.itemData(w_curIdx)
			w_profile = json.loads(w_jsonProfile)
			self.m_profileExecutor.setProfile(w_profile)

	def slotListeningEnabled(self, p_enabled):
		if p_enabled:
			self.m_profileExecutor.setEnableListening(True)
		else:
			self.m_profileExecutor.setEnableListening(False)

	def slotOK(self):
		self.saveToDatabase()
		self.m_profileExecutor.shutdown()
		self.close()

	def slotCancel(self):
		self.m_profileExecutor.shutdown()
		self.close()
		exit()

	def handleArgs(self):
		self.m_config = {
			'noroot' : 0,
			'xdowindowid' : None
		}

		if len(sys.argv) == 1:
			return

		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-noroot':
				self.m_config['noroot'] = 1
			elif sys.argv[i] == '-xdowindowid' and (i+1 < len(sys.argv)):
				self.m_config['xdowindowid'] = sys.argv[i+1]
				i = i+1

		# try to help: if -noroot is supplied, but no xdowindowid, try to determine the id
		# Elite Dangerous only
		# try:
		# 	args = shlex.split('xdotool search --name "\(CLIENT\)"')
		# 	window_id = str(subprocess.check_output(args))
		# 	window_id = window_id.replace('b\'', '')
		# 	window_id = window_id.replace('\\n\'','')
		# except subprocess.CalledProcessError:
		# 	window_id = None
		# 	pass
  #
		# if not window_id == None:
		# 	# check if it's really the Client we want
		# 	try:
		# 		window_name = subprocess.check_output(['xdotool', 'getwindowname', str(window_id)])
		# 	except subprocess.CalledProcessError:
		# 		window_name = None
		# 		pass
		# 	if not window_name == None:
		# 		if not str(window_name).find('Elite - Dangerous') == -1:
		# 			print("Window ID: ", str(window_id), ", window name: ", window_name)
		# 			print("Auto-detected window id of ED Client: ", window_id)
		# 			self.m_config['xdowindowid'] = window_id



if __name__ == "__main__":
	app = QApplication(sys.argv)
	mainWnd = MainWnd()
	mainWnd.show()
	sys.exit(app.exec_())
