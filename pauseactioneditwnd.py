from PyQt6.QtWidgets import QDialog
from ui_pauseactioneditwnd import Ui_PauseActionEditDialog

class PauseActionEditWnd(QDialog):
    def __init__(self, p_pauseAction, p_parent = None):
        super().__init__(p_parent)
        self.ui = Ui_PauseActionEditDialog()
        self.ui.setupUi(self)

        self.ui.ok.clicked.connect(self.slotOK)
        self.ui.cancel.clicked.connect(super().reject)

        self.m_pauseAction = {}

        if p_pauseAction == None:
            return

        self.ui.secondEdit.setText(str(p_pauseAction['time']))

    def slotOK(self):
        self.m_pauseAction['name'] = 'pause action'
        self.m_pauseAction['time'] = float(self.ui.secondEdit.text())
        super().accept()

