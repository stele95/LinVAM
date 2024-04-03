import re

from PyQt6.QtWidgets import QDialog

import keyboard
from ui_keyactioneditwnd import Ui_KeyActionEditDialog
from util import KEYS_SPLITTER


class KeyActionEditWnd(QDialog):
    def __init__(self, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_KeyActionEditDialog()
        self.ui.setupUi(self)
        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)
        self.m_key_action = {}
        self.keyboard_listener = keyboard.hook(callback=self.on_key_event)

    def slot_ok(self):
        w_hot_key = self.ui.keyEdit.text()
        if w_hot_key == '':
            return
        self.m_key_action = {'name': 'key action', 'key': w_hot_key}
        self.stop_keyboard_listener()
        super().accept()

    def slot_cancel(self):
        self.stop_keyboard_listener()
        super().reject()

    # disabling pylint invalid-name since this is an override of a method from QWidget
    # pylint: disable=invalid-name
    def closeEvent(self, event):
        self.stop_keyboard_listener()
        event.accept()

    def stop_keyboard_listener(self):
        # noinspection PyBroadException
        # pylint: disable=bare-except
        try:
            if self.keyboard_listener is not None:
                self.keyboard_listener()
                self.keyboard_listener = None
        except Exception as ex:
            print(str(ex))

    def on_key_event(self, event):
        current_text = self.ui.keyEdit.text()

        if event.name == 'unknown':
            return
        event_type = event.event_type
        event_type = re.sub('down', 'hold', event_type, flags=re.IGNORECASE)
        event_type = re.sub('up', 'release', event_type, flags=re.IGNORECASE)
        key = event_type + " " + event.name

        if not current_text:
            self.ui.keyEdit.setText(key)
            return
        keys = current_text.split(KEYS_SPLITTER)
        previous_key = keys[len(keys) - 1]
        if previous_key != key:
            if 'release' in key and 'hold' in previous_key:
                keys[len(keys) - 1] = event.name
            else:
                keys.append(key)
            command = ''
            for single_key in keys:
                if not command:
                    command = single_key
                else:
                    command += KEYS_SPLITTER + single_key
            self.ui.keyEdit.setText(command)
