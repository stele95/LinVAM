import re

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog

from ui_soundactioneditwnd import Ui_SoundSelect


class SoundActionEditWnd(QDialog):
    def __init__(self, p_sounds, p_sound_action=None, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_SoundSelect()
        self.ui.setupUi(self)

        if p_sounds is None:
            return

        self.p_sounds = p_sounds
        self.selected_voice_pack = False
        self.selectedCategory = False
        self.selectedFile = False
        self.m_sound_action = {}

        self.ui.buttonOkay.clicked.connect(self.slot_ok)
        self.ui.buttonCancel.clicked.connect(super().reject)
        self.ui.buttonPlaySound.clicked.connect(self.play_sound)
        self.ui.buttonStopSound.clicked.connect(self.stop_sound)
        self.ui.buttonPlaySound.setEnabled(False)
        self.ui.buttonStopSound.setEnabled(False)
        self.ui.buttonOkay.setEnabled(False)

        # restore stuff when editing
        if p_sound_action is not None:
            self.selected_voice_pack = p_sound_action['pack']
            self.selectedCategory = p_sound_action['cat']
            self.selectedFile = p_sound_action['file']
            self.ui.buttonOkay.setEnabled(True)

        self.list_voice_packs_model = QStandardItemModel()
        self.ui.listVoicepacks.setModel(self.list_voice_packs_model)
        self.ui.listVoicepacks.clicked.connect(self.on_voice_pack_select)

        self.listCategories_model = QStandardItemModel()
        self.ui.listCategories.setModel(self.listCategories_model)
        self.ui.listCategories.clicked.connect(self.on_category_select)

        self.listFiles_model = QStandardItemModel()
        self.ui.listFiles.setModel(self.listFiles_model)
        self.ui.listFiles.clicked.connect(self.on_file_select)
        self.ui.listFiles.doubleClicked.connect(self.select_and_play)

        s = sorted(p_sounds.m_sounds)
        for v in s:
            item = QStandardItem(v)
            self.list_voice_packs_model.appendRow(item)

        self.ui.filterCategories.textChanged.connect(self.populate_categories)
        self.ui.filterFiles.textChanged.connect(self.populate_files)

        self.populate_categories(False)
        self.populate_files(False)

        # when editing, select old entries
        if self.selected_voice_pack:
            item = self.list_voice_packs_model.findItems(self.selected_voice_pack)
            if len(item) > 0:
                index = self.list_voice_packs_model.indexFromItem(item[0])
                self.ui.listVoicepacks.setCurrentIndex(index)

        if self.selectedCategory:
            item = self.listCategories_model.findItems(self.selectedCategory)
            if len(item) > 0:
                index = self.listCategories_model.indexFromItem(item[0])
                self.ui.listCategories.setCurrentIndex(index)

        if self.selectedFile:
            item = self.listFiles_model.findItems(self.selectedFile)
            if len(item) > 0:
                index = self.listFiles_model.indexFromItem(item[0])
                self.ui.listFiles.setCurrentIndex(index)

    def slot_ok(self):
        self.m_sound_action = {'name': 'play sound', 'pack': self.selected_voice_pack, 'cat': self.selectedCategory,
                               'file': self.selectedFile}
        super().accept()

    def slot_cancel(self):
        super().reject()

    def on_voice_pack_select(self):
        index = self.ui.listVoicepacks.currentIndex()
        item_text = index.data()
        self.selected_voice_pack = item_text
        self.populate_categories()
        self.ui.buttonOkay.setEnabled(False)
        self.ui.buttonPlaySound.setEnabled(False)

    def on_category_select(self):
        index = self.ui.listCategories.currentIndex()
        item_text = index.data()
        self.selectedCategory = item_text
        self.populate_files()
        self.ui.buttonOkay.setEnabled(False)
        self.ui.buttonPlaySound.setEnabled(False)

    def on_file_select(self):
        index = self.ui.listFiles.currentIndex()
        item_text = index.data()
        self.selectedFile = item_text
        self.ui.buttonOkay.setEnabled(True)
        self.ui.buttonPlaySound.setEnabled(True)

    def select_and_play(self):
        self.on_file_select()
        self.play_sound()

    def populate_categories(self, reset=True):
        if not self.selected_voice_pack:
            return

        if reset:
            self.listCategories_model.removeRows(0, self.listCategories_model.rowCount())
            self.listFiles_model.removeRows(0, self.listFiles_model.rowCount())
            self.selectedCategory = False
            self.selectedFile = False

        filter_categories = self.ui.filterCategories.toPlainText()
        if len(filter_categories) == 0:
            filter_categories = None

        s = sorted(self.p_sounds.m_sounds[self.selected_voice_pack])
        for v in s:
            if filter_categories is not None:
                if not re.search(filter_categories, v, re.IGNORECASE):
                    continue
            item = QStandardItem(v)
            self.listCategories_model.appendRow(item)

    def populate_files(self, reset=True):
        if not self.selected_voice_pack or not self.selectedCategory:
            return

        if reset:
            self.listFiles_model.removeRows(0, self.listFiles_model.rowCount())
            self.selectedFile = False

        filter_files = self.ui.filterFiles.toPlainText()
        if len(filter_files) == 0:
            filter_files = None

        s = sorted(self.p_sounds.m_sounds[self.selected_voice_pack][self.selectedCategory])
        for v in s:
            if filter_files is not None:
                if not re.search(filter_files, v, re.IGNORECASE):
                    continue
            item = QStandardItem(v)
            self.listFiles_model.appendRow(item)

    def play_sound(self):
        sound_file = './voicepacks/' + self.selected_voice_pack + '/' + self.selectedCategory + '/' + self.selectedFile
        self.p_sounds.play(sound_file)

    def stop_sound(self):
        self.p_sounds.stop()
