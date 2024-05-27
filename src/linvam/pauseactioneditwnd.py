from PyQt6.QtWidgets import QDialog

from src.linvam.ui_pauseactioneditwnd import Ui_PauseActionEditDialog


class PauseActionEditWnd(QDialog):
    def __init__(self, p_pause_action, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_PauseActionEditDialog()
        self.ui.setupUi(self)

        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(super().reject)

        self.m_pause_action = {}

        if p_pause_action is None:
            return

        self.ui.secondEdit.setText(str(p_pause_action['time']))

    def slot_ok(self):
        self.m_pause_action['name'] = 'pause action'
        self.m_pause_action['time'] = float(self.ui.secondEdit.text())
        super().accept()
