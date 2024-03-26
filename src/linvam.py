#!/usr/bin/python3
from PyQt6.QtWidgets import QWidget, QApplication, QDialog, QInputDialog, QMessageBox, QLineEdit
from ui_mainwnd import Ui_MainWidget
from profileeditwnd import ProfileEditWnd
import json
from profileexecutor import ProfileExecutor
import sys
import signal
import os
from soundfiles import SoundFiles

class MainWnd(QWidget):
	def __init__(self, p_parent = None):
		super().__init__(p_parent)

		self.ui = Ui_MainWidget()
		self.ui.setupUi(self)
		self.handleArgs()
		self.m_sound = SoundFiles()
		self.m_profileExecutor = ProfileExecutor(None, self)

		self.ui.profileCbx.currentIndexChanged.connect(self.slotProfileChanged)
		self.ui.addBut.clicked.connect(self.slotAddNewProfile)
		self.ui.editBut.clicked.connect(self.slotEditProfile)
		self.ui.copyBut.clicked.connect(self.slotCopyProfile)
		self.ui.removeBut.clicked.connect(self.slotRemoveProfile)
		self.ui.listeningChk.stateChanged.connect(self.slotListeningEnabled)
		self.ui.sliderVolume.valueChanged.connect(lambda: self.m_sound.setVolume(self.ui.sliderVolume.value()))
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		position = self.loadFromDatabase()
		if position >= 0:
			self.ui.profileCbx.setCurrentIndex(position)

		self.checkButtonsStates()

	def checkButtonsStates(self):
		enabled = self.ui.profileCbx.count() > 0
		self.ui.editBut.setEnabled(enabled)
		self.ui.copyBut.setEnabled(enabled)
		self.ui.removeBut.setEnabled(enabled)
		self.ui.listeningChk.setEnabled(enabled)
		if not enabled:
			self.ui.listeningChk.setChecked(False)

	def saveToDatabase(self):
		w_profiles = []
		w_profileCnt = self.ui.profileCbx.count()
		for w_idx in range(w_profileCnt):
			w_jsonProfile = self.ui.profileCbx.itemData(w_idx)
			if w_jsonProfile == None:
				continue

			w_profile = json.loads(w_jsonProfile)
			w_profiles.append(w_profile)

		with open(self.getSettingsPath("profiles.json"), "w") as f:
			json.dump(w_profiles, f, indent=4)
			f.close()

	def loadFromDatabase(self):
		selectedProfileFile = open(self.getSettingsPath('selectedProfile'), "r")
		selectedProfile = selectedProfileFile.read()
		selectedProfileFile.close()
		selectedProfilePosition = 0
		with open(self.getSettingsPath("profiles.json"), "r") as f:
			profiles = f.read()
			f.close()
			noOfProfiles = 0
			try:
				w_profiles = json.loads(profiles)
				noOfProfiles = len(w_profiles)
				print("No of profiles read from file: " + str(noOfProfiles))
				for position, w_profile in enumerate(w_profiles):
					name = w_profile['name']
					self.ui.profileCbx.addItem(name)
					w_jsonProfile = json.dumps(w_profile)
					self.ui.profileCbx.setItemData(self.ui.profileCbx.count() - 1, w_jsonProfile)
					if name == selectedProfile:
						selectedProfilePosition = position
			except:
				print("No profiles found in file")

		if noOfProfiles < 1:
			selectedProfilePosition = -1

		return selectedProfilePosition

	def getSettingsPath(self, setting):
		home = os.path.expanduser("~") + '/.local/share/LinVAM/'
		if not os.path.exists(home):
			os.mkdir(home)
		file = home + setting
		if not os.path.exists(file):
			with (open(file, "w")) as f:
				f.close()
		return file

	def slotProfileChanged(self, p_idx):
		print("position " + str(p_idx))
		w_jsonProfile = self.ui.profileCbx.itemData(p_idx)
		if w_jsonProfile != None:
			self.m_activeProfile = json.loads(w_jsonProfile)
			self.m_profileExecutor.setProfile(self.m_activeProfile)
			selectedProfileFile = open(self.getSettingsPath('selectedProfile'), "w")
			selectedProfileFile.write(self.m_activeProfile['name'])
			selectedProfileFile.close()

	def slotAddNewProfile(self):
		w_profileEditWnd = ProfileEditWnd(None, self)
		if w_profileEditWnd.exec() == QDialog.DialogCode.Accepted:
			w_profile = w_profileEditWnd.m_profile
			self.m_profileExecutor.setProfile(w_profile)
			self.ui.profileCbx.addItem(w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(self.ui.profileCbx.count()-1, w_jsonProfile)
			self.saveToDatabase()
			self.checkButtonsStates()

	def slotEditProfile(self):
		w_idx = self.ui.profileCbx.currentIndex()
		w_jsonProfile = self.ui.profileCbx.itemData(w_idx)
		w_profile = json.loads(w_jsonProfile)
		w_profileEditWnd = ProfileEditWnd(w_profile, self)
		if w_profileEditWnd.exec() == QDialog.DialogCode.Accepted:
			w_profile = w_profileEditWnd.m_profile
			self.m_profileExecutor.setProfile(w_profile)
			self.ui.profileCbx.setItemText(w_idx, w_profile['name'])
			w_jsonProfile = json.dumps(w_profile)
			self.ui.profileCbx.setItemData(w_idx, w_jsonProfile)
			self.saveToDatabase()

	def slotCopyProfile(self):
		text, okPressed = QInputDialog.getText(self, "Copy profile", "Enter new profile name:", QLineEdit.EchoMode.Normal, "")
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
		w_curIdx = self.ui.profileCbx.currentIndex()
		w_jsonProfile = self.ui.profileCbx.itemData(w_curIdx)
		profileName = json.loads(w_jsonProfile)['name']

		buttonReply = QMessageBox.question(self, 'Remove ' + profileName, "Do you really want to delete " + profileName +"?", QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
		if buttonReply == QMessageBox.StandardButton.No:
			return

		self.ui.listeningChk.setChecked(False)

		w_curIdx = self.ui.profileCbx.currentIndex()
		if w_curIdx >= 0:
			self.ui.profileCbx.removeItem(w_curIdx)

		w_curIdx = self.ui.profileCbx.currentIndex()
		if w_curIdx >= 0:
			w_jsonProfile = self.ui.profileCbx.itemData(w_curIdx)
			w_profile = json.loads(w_jsonProfile)
			self.m_profileExecutor.setProfile(w_profile)

		self.saveToDatabase()
		self.checkButtonsStates()

	def slotListeningEnabled(self, p_enabled):
		if p_enabled:
			self.m_profileExecutor.setEnableListening(True)
		else:
			self.m_profileExecutor.setEnableListening(False)

	def closeEvent(self, event):
		self.m_profileExecutor.shutdown()
		event.accept()

	def handleArgs(self):
		self.m_config = {
			'testEnv': 0,
		}

		if len(sys.argv) == 1:
			return

		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-testEnv':
				self.m_config['testEnv'] = 1
			i += 1

if __name__ == "__main__":
	app = QApplication(sys.argv)
	QApplication.setApplicationName('LinVAM')
	mainWnd = MainWnd()
	mainWnd.show()
	sys.exit(app.exec())
