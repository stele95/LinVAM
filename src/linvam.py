#!/usr/bin/python3
import json
import signal
import sys

from PyQt6.QtWidgets import QWidget, QApplication, QDialog, QInputDialog, QMessageBox, QLineEdit, QFileDialog

from profileeditwnd import ProfileEditWnd
from profileexecutor import ProfileExecutor
from soundfiles import SoundFiles
from ui_mainwnd import Ui_MainWidget
from util import (get_supported_languages, get_config, save_config, save_linvam_run_config, delete_linvam_run_file,
                  CONST_VERSION, init_config_folder, setup_mangohud, read_profiles, save_profiles,
                  copy_profiles_to_dir, HOME_DIR, import_profiles_from_file, merge_profiles, get_safe_name,
                  update_profiles_for_new_version, handle_args, PUSH_TO_LISTEN_ENABLED_CONFIG,
                  PUSH_TO_LISTEN_HOTKEY_CONFIG)


class MainWnd(QWidget):
    def __init__(self, p_parent=None):
        super().__init__(p_parent)
        update_profiles_for_new_version()

        self.m_config = {
            'debug': 0,
            'keyboard': 0,
            'mouse': 0
        }
        self.m_active_profile = None
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self._setup_input_mode()
        handle_args(self.m_config)
        init_config_folder()
        self.m_sound = SoundFiles()
        self.m_profile_executor = ProfileExecutor(self)

        self.ui.addBut.clicked.connect(self.slot_add_new_profile)
        self.ui.editBut.clicked.connect(self.slot_edit_profile)
        self.ui.copyBut.clicked.connect(self.slot_copy_profile)
        self.ui.removeBut.clicked.connect(self.slot_remove_profile)
        self.ui.exportBtn.clicked.connect(self._export_profile)
        self.ui.importBtn.clicked.connect(self._import_profile)
        self.ui.mergeBtn.clicked.connect(self._merge_profiles)
        self.ui.listeningChk.stateChanged.connect(self.slot_listening_enabled)
        self.ui.sliderVolume.valueChanged.connect(lambda: self.m_sound.set_volume(self.ui.sliderVolume.value()))
        self.ui.rbAlways.clicked.connect(lambda: self._on_input_mode_changed(ptl_enabled=False))
        self.ui.rbPushToListen.clicked.connect(lambda: self._on_input_mode_changed(ptl_enabled=True))
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self._init_profiles()

        language_position = self.load_languages()
        self.ui.languageCbx.currentIndexChanged.connect(self.language_changed)
        if language_position > 0:
            self.ui.languageCbx.setCurrentIndex(language_position)
        elif language_position == 0:
            self.language_changed(language_position)

        self._check_buttons_states()

    def _setup_input_mode(self):
        ptl_enabled = get_config(PUSH_TO_LISTEN_ENABLED_CONFIG)
        self.ui.rbAlways.setChecked(not ptl_enabled)
        self.ui.rbPushToListen.setChecked(ptl_enabled)
        self._on_input_mode_changed(ptl_enabled, save_to_config=False)

    def _on_input_mode_changed(self, ptl_enabled, save_to_config=True):
        ptl_hotkey = get_config(PUSH_TO_LISTEN_HOTKEY_CONFIG)
        self.ui.pushToListenHotkey.setText(ptl_hotkey)
        self.ui.pushToListenHotkey.setVisible(ptl_enabled)
        self.ui.btnEditKeybind.setVisible(ptl_enabled)
        if save_to_config:
            save_config(PUSH_TO_LISTEN_ENABLED_CONFIG, ptl_enabled)

    def _init_profiles(self):
        self.ui.profileCbx.clear()
        position = self.load_from_database()
        self.ui.profileCbx.currentIndexChanged.connect(self.slot_profile_changed)
        if position > 0:
            self.ui.profileCbx.setCurrentIndex(position)
        elif position == 0:
            self.slot_profile_changed(position)

    def _export_profile(self):
        path = QFileDialog.getExistingDirectory(self, 'Select a location for extracting profiles', HOME_DIR)
        if not path:
            return
        copy_profiles_to_dir(path)

    def _import_profile(self):
        (path, _) = QFileDialog.getOpenFileName(self, 'Select a file for importing profiles from', HOME_DIR,
                                                "Profiles json file (*.json)")
        if not path:
            return
        import_profiles_from_file(path)
        self._init_profiles()

    def _merge_profiles(self):
        (path, _) = QFileDialog.getOpenFileName(self, 'Select a file for merging profiles with', HOME_DIR,
                                                "Profiles json file (*.json)")
        if not path:
            return
        merge_profiles(path)
        self._init_profiles()

    def _check_buttons_states(self):
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
        save_profiles(w_profiles)

    def load_from_database(self):
        selected_profile = get_config('profile')
        selected_profile_position = 0
        profiles = read_profiles()
        no_of_profiles = 0

        # noinspection PyBroadException
        try:
            w_profiles = json.loads(profiles)
            no_of_profiles = len(w_profiles)
            print("No of profiles read from file: " + str(no_of_profiles))
            for position, w_profile in enumerate(w_profiles):
                name = w_profile['name']
                w_json_profile = json.dumps(w_profile, ensure_ascii=False)
                self.ui.profileCbx.addItem(name, w_json_profile)
                if name == selected_profile:
                    selected_profile_position = position
        except Exception as e:
            print("Error loading profiles: " + str(e))

        if no_of_profiles < 1:
            selected_profile_position = -1

        return selected_profile_position

    def load_languages(self):
        selected_language = get_config('language')
        selected_language_position = 0
        languages = get_supported_languages()
        for position, language in enumerate(languages):
            self.ui.languageCbx.addItem(language)
            if language == selected_language:
                selected_language_position = position
        return selected_language_position

    def slot_profile_changed(self, p_idx):
        if p_idx < 0:
            self.m_profile_executor.set_profile(None)
            return
        w_json_profile = self.ui.profileCbx.itemData(p_idx)
        if w_json_profile is not None:
            self.m_active_profile = json.loads(w_json_profile)
            self.m_profile_executor.set_profile(self.m_active_profile)
            profile_name = self.m_active_profile['name']
            save_config('profile', profile_name)
            save_linvam_run_config('profile', profile_name)

    def language_changed(self, index):
        if index < 0:
            return
        language = self.ui.languageCbx.itemText(index)
        self.m_profile_executor.set_language(language)
        save_config('language', language)
        save_linvam_run_config('language', language)

    def slot_add_new_profile(self):
        w_profile_edit_wnd = ProfileEditWnd(None, self)
        if w_profile_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            w_profile = w_profile_edit_wnd.m_profile
            w_profile['name'] = self.get_safe_name(w_profile['name'])
            w_json_profile = json.dumps(w_profile, ensure_ascii=False)
            self.ui.profileCbx.addItem(w_profile['name'], w_json_profile)
            self.ui.profileCbx.setCurrentIndex(self.ui.profileCbx.count() - 1)
            self.save_to_database()
            self._check_buttons_states()

    def slot_edit_profile(self):
        w_idx = self.ui.profileCbx.currentIndex()
        w_json_profile = self.ui.profileCbx.itemData(w_idx)
        w_profile = json.loads(w_json_profile)
        w_profile_edit_wnd = ProfileEditWnd(w_profile, self)
        if w_profile_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            w_profile = w_profile_edit_wnd.m_profile
            self.m_profile_executor.set_profile(w_profile)
            self.ui.profileCbx.setItemText(w_idx, w_profile['name'])
            w_json_profile = json.dumps(w_profile, ensure_ascii=False)
            self.ui.profileCbx.setItemData(w_idx, w_json_profile)
            self.save_to_database()

    def slot_copy_profile(self):
        text, ok_pressed = QInputDialog.getText(self, "Copy profile", "Enter new profile name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            text = self.get_safe_name(text)
            w_idx = self.ui.profileCbx.currentIndex()
            w_json_profile = self.ui.profileCbx.itemData(w_idx)
            w_profile = json.loads(w_json_profile)
            w_profile_copy = w_profile
            w_profile_copy['name'] = text
            w_json_profile = json.dumps(w_profile_copy, ensure_ascii=False)
            self.ui.profileCbx.addItem(w_profile_copy['name'], w_json_profile)
            self.ui.profileCbx.setCurrentIndex(self.ui.profileCbx.currentIndex() + 1)
            self.save_to_database()

    def get_safe_name(self, text):
        return get_safe_name(
            [json.loads(self.ui.profileCbx.itemData(i)) for i in range(self.ui.profileCbx.count())],
            text
        )

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

        self.save_to_database()
        self._check_buttons_states()

    def slot_listening_enabled(self, p_enabled):
        if p_enabled:
            self.m_profile_executor.set_enable_listening(True)
        else:
            self.m_profile_executor.set_enable_listening(False)

    # disabling pylint invalid-name since this is an override of a method from QWidget
    # pylint: disable=invalid-name
    def closeEvent(self, event):
        self.m_profile_executor.shutdown()
        delete_linvam_run_file()
        event.accept()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        match sys.argv[1]:
            case '--version':
                print("Version: " + str(CONST_VERSION))
                sys.exit()
            case '--setup-mangohud':
                setup_mangohud()
                sys.exit()
    elif len(sys.argv) == 3 and sys.argv[1] == '--setup-mangohud':
        # noinspection PyBroadException
        # pylint: disable=bare-except
        try:
            arg_split = sys.argv[2].split('=')
            if arg_split[0] == '--path':
                setup_mangohud(arg_split[1])
            else:
                print("Unexpected second argument, expecting --path='path/to/file'," +
                      " e.g. --path='/home/user/.config/MangoHud/")
        except:
            print("Unexpected second argument, expecting --path='path/to/file'," +
                  " e.g. --path='/home/user/.config/MangoHud/")
        sys.exit()
    app = QApplication(sys.argv)
    mainWnd = MainWnd()
    mainWnd.setWindowTitle("LinVAM v" + CONST_VERSION)
    mainWnd.show()
    sys.exit(app.exec())
