from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog
import re
import os
from ui_soundactioneditwnd import Ui_SoundSelect

class SoundActionEditWnd(QDialog):
	def __init__(self, p_sounds, p_soundAction = None, p_parent = None):
		super().__init__(p_parent)
		self.ui = Ui_SoundSelect()
		self.ui.setupUi(self)

		if p_sounds == None:
			return

		self.p_sounds = p_sounds
		self.selectedVoicepack = False
		self.selectedCategory  = False
		self.selectedFile      = False

		self.ui.buttonOkay.clicked.connect(self.slotOK)
		self.ui.buttonCancel.clicked.connect(super().reject)
		self.ui.buttonPlaySound.clicked.connect(self.playSound)
		self.ui.buttonStopSound.clicked.connect(self.stopSound)
		self.ui.buttonPlaySound.setEnabled(False)
		self.ui.buttonStopSound.setEnabled(False)
		self.ui.buttonOkay.setEnabled(False)

		# restore stuff when editing
		if not p_soundAction == None:
			self.selectedVoicepack = p_soundAction['pack']
			self.selectedCategory = p_soundAction['cat']
			self.selectedFile = p_soundAction['file']
			self.ui.buttonOkay.setEnabled(True)

		self.listVoicepacks_model = QStandardItemModel()
		self.ui.listVoicepacks.setModel(self.listVoicepacks_model)
		self.ui.listVoicepacks.clicked.connect(self.onVoicepackSelect)

		self.listCategories_model = QStandardItemModel()
		self.ui.listCategories.setModel(self.listCategories_model)
		self.ui.listCategories.clicked.connect(self.onCategorySelect)

		self.listFiles_model = QStandardItemModel()
		self.ui.listFiles.setModel(self.listFiles_model)
		self.ui.listFiles.clicked.connect(self.onFileSelect)
		self.ui.listFiles.doubleClicked.connect(self.selectAndPlay)

		s = sorted(p_sounds.m_sounds)
		for v in s:
			item = QStandardItem(v)
			self.listVoicepacks_model.appendRow(item)

		self.ui.filterCategories.textChanged.connect(self.populateCategories)
		self.ui.filterFiles.textChanged.connect(self.populateFiles)


		self.populateCategories(False)
		self.populateFiles(False)

		# when editing, select old entries
		if not self.selectedVoicepack == False:
			item = self.listVoicepacks_model.findItems(self.selectedVoicepack)
			if len(item) > 0:
				index = self.listVoicepacks_model.indexFromItem(item[0])
				self.ui.listVoicepacks.setCurrentIndex(index)

		if not self.selectedCategory == False:
			item = self.listCategories_model.findItems(self.selectedCategory)
			if len(item) > 0:
				index = self.listCategories_model.indexFromItem(item[0])
				self.ui.listCategories.setCurrentIndex(index)

		if not self.selectedFile == False:
			item = self.listFiles_model.findItems(self.selectedFile)
			if len(item) > 0:
				index = self.listFiles_model.indexFromItem(item[0])
				self.ui.listFiles.setCurrentIndex(index)




	def slotOK(self):
		self.m_soundAction = {'name': 'play sound', 'pack': self.selectedVoicepack, 'cat' : self.selectedCategory, 'file' : self.selectedFile}
		super().accept()

	def slotCancel(self):
		super().reject()

	def onVoicepackSelect(self):
		index = self.ui.listVoicepacks.currentIndex()
		itemText = index.data()
		self.selectedVoicepack = itemText
		self.populateCategories()
		self.ui.buttonOkay.setEnabled(False)
		self.ui.buttonPlaySound.setEnabled(False)

	def onCategorySelect(self):
		index = self.ui.listCategories.currentIndex()
		itemText = index.data()
		self.selectedCategory = itemText
		self.populateFiles()
		self.ui.buttonOkay.setEnabled(False)
		self.ui.buttonPlaySound.setEnabled(False)


	def onFileSelect(self):
		index = self.ui.listFiles.currentIndex()
		itemText = index.data()
		self.selectedFile = itemText
		self.ui.buttonOkay.setEnabled(True)
		self.ui.buttonPlaySound.setEnabled(True)

	def selectAndPlay(self):
		self.onFileSelect()
		self.playSound()

	def populateCategories(self, reset = True):
		if self.selectedVoicepack == False:
			return

		if reset == True:
			self.listCategories_model.removeRows( 0, self.listCategories_model.rowCount() )
			self.listFiles_model.removeRows( 0, self.listFiles_model.rowCount() )
			self.selectedCategory  = False
			self.selectedFile      = False

		filter_categories = self.ui.filterCategories.toPlainText()
		if len(filter_categories) == 0:
			filter_categories = None

		s = sorted(self.p_sounds.m_sounds[self.selectedVoicepack])
		for v in s:
			if not filter_categories == None:
				if not re.search(filter_categories, v, re.IGNORECASE):
					continue
			item = QStandardItem(v)
			self.listCategories_model.appendRow(item)

	def populateFiles(self, reset = True):
		if self.selectedVoicepack == False or self.selectedCategory == False:
			return

		if reset == True:
			self.listFiles_model.removeRows( 0, self.listFiles_model.rowCount() )
			self.selectedFile = False

		filter_files = self.ui.filterFiles.toPlainText()
		if len(filter_files) == 0:
			filter_files = None

		s = sorted(self.p_sounds.m_sounds[self.selectedVoicepack][self.selectedCategory])
		for v in s:
			if not filter_files == None:
				if not re.search(filter_files, v, re.IGNORECASE):
					continue
			item = QStandardItem(v)
			self.listFiles_model.appendRow(item)

	def playSound(self):
		sound_file = './voicepacks/' + self.selectedVoicepack + '/' + self.selectedCategory + '/' + self.selectedFile
		self.p_sounds.play(sound_file)

	def stopSound(self):
		self.p_sounds.stop()
