from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ui_keyactioneditwnd import Ui_KeyActionEditDialog
import keyboard
import threading

class KeyActionEditWnd(QDialog):
    def __init__(self, p_keyAction, p_parent = None):
        super().__init__(p_parent)
        self.ui = Ui_KeyActionEditDialog()
        self.ui.setupUi(self)

        self.ui.ok.clicked.connect(self.slotOK)
        self.ui.cancel.clicked.connect(self.slotCancel)

        self.m_keyAction = {}

        t = threading.Thread(target=self.keyInput)
        t.daemon = True
        t.start()

        if p_keyAction == None:
            return

        w_hotKey = p_keyAction['key']

        self.ui.keyEdit.setText(w_hotKey)


    def slotOK(self):

        w_hotKey = self.ui.keyEdit.text()

        if w_hotKey == '':
            return

        self.m_keyAction = {}
        self.m_keyAction['name'] = 'key action'
        self.m_keyAction['key'] = w_hotKey

        return super().accept()

    def slotCancel(self):
        return super().reject()

    def keyInput(self):
        try:
            while True:
                self.ui.keyEdit.setText(keyboard.read_hotkey(False))
        except:
            pass

