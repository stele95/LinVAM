import re

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog

from linvam.ui_soundactioneditwnd import Ui_SoundSelect

from linvam.util import get_voice_packs_folder_path


class SoundActionEditWnd(QDialog):
    def __init__(self, p_sounds, p_sound_action=None, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_SoundSelect()
        self.ui.setupUi(self)

        if p_sounds is None:
            return

        self.p_sounds = p_sounds
        self.selected_voice_pack = None
        self.selected_category = None
        self.selected_file = None
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
            self.selected_category = p_sound_action['cat']
            self.selected_file = p_sound_action['file']
            self.ui.buttonOkay.setEnabled(True)

        self.list_voice_packs_model = QStandardItemModel()
        self.ui.listVoicepacks.setModel(self.list_voice_packs_model)
        self.ui.listVoicepacks.clicked.connect(self.on_voice_pack_select)

        self.list_categories_model = QStandardItemModel()
        self.ui.listCategories.setModel(self.list_categories_model)
        self.ui.listCategories.clicked.connect(self.on_category_select)

        self.list_files_model = QStandardItemModel()
        self.ui.listFiles.setModel(self.list_files_model)
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
        self.select_old_entries()

    def slot_ok(self):
        self.m_sound_action = {'name': 'play sound', 'pack': self.selected_voice_pack, 'cat': self.selected_category,
                               'file': self.selected_file}
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
        self.selected_category = item_text
        self.populate_files()
        self.ui.buttonOkay.setEnabled(False)
        self.ui.buttonPlaySound.setEnabled(False)

    def on_file_select(self):
        index = self.ui.listFiles.currentIndex()
        item_text = index.data()
        self.selected_file = item_text
        self.ui.buttonOkay.setEnabled(True)
        self.ui.buttonPlaySound.setEnabled(True)

    def select_and_play(self):
        self.on_file_select()
        self.play_sound()

    def populate_categories(self, reset=True):
        if self.selected_voice_pack is None:
            return

        if reset:
            self.list_categories_model.removeRows(0, self.list_categories_model.rowCount())
            self.list_files_model.removeRows(0, self.list_files_model.rowCount())
            self.selected_category = None
            self.selected_file = None

        filter_categories = self.ui.filterCategories.toPlainText()
        if len(filter_categories) == 0:
            filter_categories = None

        s = sorted(self.p_sounds.m_sounds[self.selected_voice_pack])
        for v in s:
            if filter_categories is not None:
                if not re.search(filter_categories, v, re.IGNORECASE):
                    continue
            item = QStandardItem(v)
            self.list_categories_model.appendRow(item)

    def populate_files(self, reset=True):
        if self.selected_voice_pack is None or self.selected_category is None:
            return

        if reset:
            self.list_files_model.removeRows(0, self.list_files_model.rowCount())
            self.selected_file = None

        filter_files = self.ui.filterFiles.toPlainText()
        if len(filter_files) == 0:
            filter_files = None

        s = sorted(self.p_sounds.m_sounds[self.selected_voice_pack][self.selected_category])
        for v in s:
            if filter_files is not None:
                if not re.search(filter_files, v, re.IGNORECASE):
                    continue
            item = QStandardItem(v)
            self.list_files_model.appendRow(item)

    def play_sound(self):
        sound_file = (get_voice_packs_folder_path() + self.selected_voice_pack + '/' + self.selected_category + '/'
                      + self.selected_file)
        self.p_sounds.play(sound_file)
        self.ui.buttonStopSound.setEnabled(True)

    def stop_sound(self):
        self.p_sounds.stop()

    def select_old_entries(self):
        # when editing, select old entries
        if self.selected_voice_pack is not None:
            item = self.list_voice_packs_model.findItems(self.selected_voice_pack)
            if len(item) > 0:
                index = self.list_voice_packs_model.indexFromItem(item[0])
                self.ui.listVoicepacks.setCurrentIndex(index)

        if self.selected_category is not None:
            item = self.list_categories_model.findItems(self.selected_category)
            if len(item) > 0:
                index = self.list_categories_model.indexFromItem(item[0])
                self.ui.listCategories.setCurrentIndex(index)

        if self.selected_file is not None:
            item = self.list_files_model.findItems(self.selected_file)
            if len(item) > 0:
                index = self.list_files_model.indexFromItem(item[0])
                self.ui.listFiles.setCurrentIndex(index)
                self.ui.buttonPlaySound.setEnabled(True)
