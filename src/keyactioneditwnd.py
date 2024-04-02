import threading

from PyQt6.QtWidgets import QDialog

import keyboard

from ui_keyactioneditwnd import Ui_KeyActionEditDialog


class KeyActionEditWnd(QDialog):
    def __init__(self, p_key_action, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_KeyActionEditDialog()
        self.ui.setupUi(self)

        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)

        self.m_key_action = {}

        t = threading.Thread(target=self.key_input())
        t.daemon = True
        t.start()

        if p_key_action is None:
            return

        w_hot_key = p_key_action['key']

        self.ui.keyEdit.setText(w_hot_key)

    def slot_ok(self):
        w_hot_key = self.ui.keyEdit.text()
        if w_hot_key == '':
            return
        self.m_key_action = {'name': 'key action', 'key': w_hot_key}
        super().accept()

    def slot_cancel(self):
        super().reject()

    def key_input(self):
        print('Starting listening for keys')
        try:
            while True:
                event = keyboard.read_event()
                print('Event: ' + str(event))
                text = self.ui.keyEdit.text()
                if len(text) > 0:
                    text += "+"
                #self.ui.keyEdit.setText(text+event)
        except Exception as ex:
            print(str(ex))
            pass
