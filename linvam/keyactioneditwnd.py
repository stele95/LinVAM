import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog

from linvam import keyboard
from linvam.ui_keyactioneditwnd import Ui_KeyActionEditDialog
from linvam.util import KEYS_SPLITTER, DEFAULT_KEY_DELAY_IN_MILLISECONDS, Command


class KeyActionEditWnd(QDialog):
    def __init__(self, action, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_KeyActionEditDialog()
        self.ui.setupUi(self)
        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)
        self.ui.recordingButton.clicked.connect(self.recording_click)
        self.ui.recordingButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.resetDelay.clicked.connect(self.reset_delay)
        self.m_key_action = {}
        self.key_events = []
        self.keyboard_listener = None
        self.rejectAllowed = True
        if action is not None:
            self.ui.keyEdit.setText(action['key'])
            if 'delay' in action:
                self.ui.sbDelay.setValue(action['delay'])
            else:
                self.ui.sbDelay.setValue(DEFAULT_KEY_DELAY_IN_MILLISECONDS)
            if 'key_events' in action:
                self.key_events = str(action['key_events']).split(KEYS_SPLITTER)
        else:
            self.ui.sbDelay.setValue(DEFAULT_KEY_DELAY_IN_MILLISECONDS)

    def reject(self):
        if self.rejectAllowed:
            super().reject()
        else:
            print("Reject not allowed, skipping reject")

    def reset_delay(self):
        self.ui.sbDelay.setValue(DEFAULT_KEY_DELAY_IN_MILLISECONDS)

    def recording_click(self):
        if self.keyboard_listener is None:
            self.keyboard_listener = keyboard.hook(callback=self.on_key_event)
            self.ui.keyEdit.setText('')
            self.key_events = []
            self.ui.recordingButton.setText('Stop recording')
            self.set_buttons_enabled(False)
        else:
            self._stop_keyboard_listener()
            self.ui.recordingButton.setText('Start recording')
            self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled):
        self.ui.sbDelay.setEnabled(enabled)
        self.ui.resetDelay.setEnabled(enabled)
        self.ui.ok.setEnabled(enabled)
        self.ui.cancel.setEnabled(enabled)
        self.rejectAllowed = enabled

    def slot_ok(self):
        w_hot_key = self.ui.keyEdit.text()
        if w_hot_key == '':
            return
        events = ''
        for event in self.key_events:
            if not events:
                events = event
            else:
                events += KEYS_SPLITTER + event

        self.m_key_action = {'name': Command.KEY_ACTION, 'key': w_hot_key, 'delay': self.ui.sbDelay.value(),
                             'key_events': events}
        self._stop_keyboard_listener()
        super().accept()

    def slot_cancel(self):
        self._stop_keyboard_listener()
        super().reject()

    # disabling pylint invalid-name since this is an override of a method from QWidget
    # pylint: disable=invalid-name
    def closeEvent(self, event):
        self._stop_keyboard_listener()
        event.accept()

    def _stop_keyboard_listener(self):
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
            self.append_key_event(event)
            return
        keys = current_text.split(KEYS_SPLITTER)
        previous_key = keys[len(keys) - 1]
        if previous_key != key:
            if 'release' in key and 'hold' in previous_key:
                keys[len(keys) - 1] = event.name
            else:
                keys.append(key)
            self.append_key_event(event)
            command = ''
            for single_key in keys:
                if not command:
                    command = single_key
                else:
                    command += KEYS_SPLITTER + single_key
            self.ui.keyEdit.setText(command)

    def append_key_event(self, event):
        if 'down' in event.event_type:
            event_type_int = 1
        elif 'up' in event.event_type:
            event_type_int = 0
        else:
            return
        self.key_events.append(str(event.scan_code) + ':' + str(event_type_int))
