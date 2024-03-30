#!/usr/bin/python3
import json
import signal
import sys

from PyQt6.QtWidgets import QWidget, QApplication, QDialog, QInputDialog, QMessageBox, QLineEdit

from profileeditwnd import ProfileEditWnd
from profileexecutor import ProfileExecutor, get_settings_path
from soundfiles import SoundFiles
from ui_mainwnd import Ui_MainWidget


class MainWnd(QWidget):
    def __init__(self, p_parent=None):
        super().__init__(p_parent)

        self.m_config = None
        self.m_active_profile = None
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.handle_args()
        self.m_sound = SoundFiles()
        self.m_profile_executor = ProfileExecutor(None, self)

        self.ui.profileCbx.currentIndexChanged.connect(self.slot_profile_changed)
        self.ui.addBut.clicked.connect(self.slot_add_new_profile)
        self.ui.editBut.clicked.connect(self.slot_edit_profile)
        self.ui.copyBut.clicked.connect(self.slot_copy_profile)
        self.ui.removeBut.clicked.connect(self.slot_remove_profile)
        self.ui.listeningChk.stateChanged.connect(self.slot_listening_enabled)
        self.ui.sliderVolume.valueChanged.connect(lambda: self.m_sound.set_volume(self.ui.sliderVolume.value()))
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        position = self.load_from_database()
        if position >= 0:
            if position == 0:
                self.slot_profile_changed(position)
            else:
                self.ui.profileCbx.setCurrentIndex(position)

        self.check_buttons_states()

    def check_buttons_states(self):
        enabled = self.ui.profileCbx.count() > 0
        self.ui.editBut.setEnabled(enabled)
        self.ui.copyBut.setEnabled(enabled)
        self.ui.removeBut.setEnabled(enabled)
        self.ui.listeningChk.setEnabled(enabled)
        if not enabled:
            self.ui.listeningChk.setChecked(False)

    def save_to_database(self):
        w_profiles = []
        w_profile_cnt = self.ui.profileCbx.count()
        for w_idx in range(w_profile_cnt):
            w_json_profile = self.ui.profileCbx.itemData(w_idx)
            if w_json_profile is None:
                continue

            w_profile = json.loads(w_json_profile)
            w_profiles.append(w_profile)

        with open(get_settings_path("profiles.json"), "w", encoding="utf-8") as f:
            json.dump(w_profiles, f, indent=4)
            f.close()

    def load_from_database(self):
        with open(get_settings_path('selectedProfile'), "r", encoding="utf-8") as selected_profile_file:
            selected_profile = selected_profile_file.read()
            selected_profile_file.close()
        selected_profile_position = 0
        with open(get_settings_path("profiles.json"), "r", encoding="utf-8") as f:
            profiles = f.read()
            f.close()
            no_of_profiles = 0

            # noinspection PyBroadException
            try:
                w_profiles = json.loads(profiles)
                no_of_profiles = len(w_profiles)
                print("No of profiles read from file: " + str(no_of_profiles))
                for position, w_profile in enumerate(w_profiles):
                    name = w_profile['name']
                    self.ui.profileCbx.addItem(name)
                    w_json_profile = json.dumps(w_profile)
                    self.ui.profileCbx.setItemData(self.ui.profileCbx.count() - 1, w_json_profile)
                    if name == selected_profile:
                        selected_profile_position = position
            except Exception as e:
                print("Error loading profiles: " + str(e))

        if no_of_profiles < 1:
            selected_profile_position = -1

        return selected_profile_position

    def slot_profile_changed(self, p_idx):
        print("position " + str(p_idx))
        w_json_profile = self.ui.profileCbx.itemData(p_idx)
        if w_json_profile is not None:
            self.m_active_profile = json.loads(w_json_profile)
            self.m_profile_executor.set_profile(self.m_active_profile)
            with open(get_settings_path('selectedProfile'), "w", encoding="utf-8") as selected_profile_file:
                selected_profile_file.write(self.m_active_profile['name'])
                selected_profile_file.close()

    def slot_add_new_profile(self):
        w_profile_edit_wnd = ProfileEditWnd(None, self)
        if w_profile_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            w_profile = w_profile_edit_wnd.m_profile
            self.m_profile_executor.set_profile(w_profile)
            self.ui.profileCbx.addItem(w_profile['name'])
            w_json_profile = json.dumps(w_profile)
            self.ui.profileCbx.setItemData(self.ui.profileCbx.count() - 1, w_json_profile)
            self.save_to_database()
            self.check_buttons_states()

    def slot_edit_profile(self):
        w_idx = self.ui.profileCbx.currentIndex()
        w_json_profile = self.ui.profileCbx.itemData(w_idx)
        w_profile = json.loads(w_json_profile)
        w_profile_edit_wnd = ProfileEditWnd(w_profile, self)
        if w_profile_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            w_profile = w_profile_edit_wnd.m_profile
            self.m_profile_executor.set_profile(w_profile)
            self.ui.profileCbx.setItemText(w_idx, w_profile['name'])
            w_json_profile = json.dumps(w_profile)
            self.ui.profileCbx.setItemData(w_idx, w_json_profile)
            self.save_to_database()

    def slot_copy_profile(self):
        text, ok_pressed = QInputDialog.getText(self, "Copy profile", "Enter new profile name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            if self.name_exists(text):
                return
            w_idx = self.ui.profileCbx.currentIndex()
            w_json_profile = self.ui.profileCbx.itemData(w_idx)
            w_profile = json.loads(w_json_profile)
            w_profile_copy = w_profile
            w_profile_copy['name'] = text
            self.ui.profileCbx.addItem(w_profile_copy['name'])
            w_json_profile = json.dumps(w_profile_copy)
            self.ui.profileCbx.setItemData(self.ui.profileCbx.count() - 1, w_json_profile)

    def name_exists(self, text):
        all_items = [json.loads(self.ui.profileCbx.itemData(i)) for i in range(self.ui.profileCbx.count())]
        found = False
        i = 0
        while not found and i < len(all_items):
            found = all_items[i]['name'] == text
            i += 1
        return found

    def slot_remove_profile(self):
        w_cur_idx = self.ui.profileCbx.currentIndex()
        w_json_profile = self.ui.profileCbx.itemData(w_cur_idx)
        profile_name = json.loads(w_json_profile)['name']

        button_reply = QMessageBox.question(self, 'Remove ' + profile_name,
                                            "Do you really want to delete " + profile_name + "?",
                                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                            QMessageBox.StandardButton.No)
        if button_reply == QMessageBox.StandardButton.No:
            return

        self.ui.listeningChk.setChecked(False)

        w_cur_idx = self.ui.profileCbx.currentIndex()
        if w_cur_idx >= 0:
            self.ui.profileCbx.removeItem(w_cur_idx)

        w_cur_idx = self.ui.profileCbx.currentIndex()
        if w_cur_idx >= 0:
            w_json_profile = self.ui.profileCbx.itemData(w_cur_idx)
            w_profile = json.loads(w_json_profile)
            self.m_profile_executor.set_profile(w_profile)

        self.save_to_database()
        self.check_buttons_states()

    def slot_listening_enabled(self, p_enabled):
        if p_enabled:
            self.m_profile_executor.set_enable_listening(True)
        else:
            self.m_profile_executor.set_enable_listening(False)

    # disabling pylint invalid-name since this is an override of a method from QWidget
    # pylint: disable=invalid-name
    def closeEvent(self, event):
        self.m_profile_executor.shutdown()
        event.accept()

    def handle_args(self):
        self.m_config = {
            'testEnv': 0,
        }

        if len(sys.argv) == 1:
            return

        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-testEnv':
                self.m_config['testEnv'] = 1
            i += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName('LinVAM')
    mainWnd = MainWnd()
    mainWnd.show()
    sys.exit(app.exec())