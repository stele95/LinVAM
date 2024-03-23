from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ui_commandeditwnd import Ui_CommandEditDialog
from keyactioneditwnd import KeyActionEditWnd
from mouseactioneditwnd import MouseActionEditWnd
from pauseactioneditwnd import PauseActionEditWnd
from soundactioneditwnd import SoundActionEditWnd
import json

class CommandEditWnd(QDialog):
    def __init__(self, p_command, p_parent = None):
        super().__init__(p_parent)
        self.ui = Ui_CommandEditDialog()
        self.ui.setupUi(self)
        self.m_parent = p_parent

        self.ui.deleteBut.clicked.connect(self.slotDelete)
        self.ui.ok.clicked.connect(self.slotOK)
        self.ui.cancel.clicked.connect(self.slotCancel)
        self.ui.keyBut.clicked.connect(self.slotNewKeyEdit)
        self.ui.mouseBut.clicked.connect(self.slotNewMouseEdit)
        self.ui.pauseBut.clicked.connect(self.slotNewPauseEdit)
        self.ui.upBut.clicked.connect(self.slotActionUp)
        self.ui.downBut.clicked.connect(self.slotActionDown)
        self.ui.editBut.clicked.connect(self.slotActionEdit)
        self.ui.actionsListWidget.doubleClicked.connect(self.slotActionEdit)

        w_otherMenu = QMenu()
        w_otherMenu.addAction('Stop Another Command', self.slotStopAnotherCommand)
        w_otherMenu.addAction('Execute Another Command', self.slotDoAnotherCommand)
        w_otherMenu.addAction('Play Sound', self.slotNewSoundEdit)
        self.ui.otherBut.setMenu(w_otherMenu)

        self.m_command = {}
        if p_command != None:
            self.ui.say.setText(p_command['name'])
            self.ui.thresholdSpin.setValue(p_command['threshold'])
            w_actions = p_command['actions']
            for w_action in w_actions:
                w_jsonAction = json.dumps(w_action)
                w_item = QListWidgetItem(w_jsonAction)
                w_item.setData(Qt.ItemDataRole.UserRole, w_jsonAction)
                self.ui.actionsListWidget.addItem(w_item)
            self.ui.asyncChk.setChecked(p_command['async'])
            if p_command['repeat'] == -1:
                self.ui.continueExe.setChecked(True)
            elif p_command['repeat'] == 1:
                self.ui.oneExe.setChecked(True)
            else:
                self.ui.repeatExe.setChecked(True)
                self.ui.repeatCnt.setValue(p_command['repeat'])
        else:
            self.ui.asyncChk.setChecked(False)
            self.ui.oneExe.setChecked(True)

    def addAction(self, p_action):
        w_jsonAction = json.dumps(p_action)
        w_item = QListWidgetItem(w_jsonAction)
        w_item.setData(Qt.ItemDataRole.UserRole, w_jsonAction)
        self.ui.actionsListWidget.addItem(w_item)

    def slotStopAnotherCommand(self):
        text, okPressed = QInputDialog.getText(self, "Get Command Name", "Another command name:", QLineEdit.EchoMode.Normal, "")
        if okPressed and text != '':
            w_commandStopAction = {}
            w_commandStopAction['name'] = 'command stop action'
            w_commandStopAction['command name'] = text
            self.addAction(w_commandStopAction)

    def slotDoAnotherCommand(self):
        text, okPressed = QInputDialog.getText(self, "Get Command Name", "Another command name:", QLineEdit.EchoMode.Normal, "")
        if okPressed and text != '':
            w_commandDoAction = {}
            w_commandDoAction['name'] = 'command execute action'
            w_commandDoAction['command name'] = text
            self.addAction(w_commandDoAction)

    def slotDoPlaySound(self):
        text, okPressed = QInputDialog.getItem(self, "Set sound to play", "Enter sound file:", list(self.m_parent.m_parent.m_sound.m_sounds), 0, False)
        if okPressed and text != '':
            w_commandDoAction = {}
            w_commandDoAction['name'] = 'command play sound'
            w_commandDoAction['command name'] = text
            self.addAction(w_commandDoAction)

    def slotNewKeyEdit(self):
        w_keyEditWnd = KeyActionEditWnd(None, self)
        if w_keyEditWnd.exec() == QDialog.DialogCode.Accepted:
            self.addAction(w_keyEditWnd.m_keyAction)

    def slotNewMouseEdit(self):
        w_mouseEditWnd = MouseActionEditWnd(None, self)
        if w_mouseEditWnd.exec() == QDialog.DialogCode.Accepted:
            self.addAction(w_mouseEditWnd.m_mouseAction)

    def slotNewPauseEdit(self):
        w_pauseEditWnd = PauseActionEditWnd(None, self)
        if w_pauseEditWnd.exec() == QDialog.DialogCode.Accepted:
            self.addAction(w_pauseEditWnd.m_pauseAction)

    def slotNewSoundEdit(self):
        w_soundEditWnd = SoundActionEditWnd(self.m_parent.m_parent.m_sound, None, self)
        if w_soundEditWnd.exec() == QDialog.DialogCode.Accepted:
            self.addAction(w_soundEditWnd.m_soundAction)

    def slotActionUp(self):
        currentIndex = self.ui.actionsListWidget.currentRow()
        currentItem = self.ui.actionsListWidget.takeItem(currentIndex);
        self.ui.actionsListWidget.insertItem(currentIndex - 1, currentItem);
        self.ui.actionsListWidget.setCurrentRow(currentIndex - 1);

    def slotActionDown(self):
        currentIndex = self.ui.actionsListWidget.currentRow();
        currentItem = self.ui.actionsListWidget.takeItem(currentIndex);
        self.ui.actionsListWidget.insertItem(currentIndex + 1, currentItem);
        self.ui.actionsListWidget.setCurrentRow(currentIndex + 1);

    def slotActionEdit(self):
        w_listItems = self.ui.actionsListWidget.selectedItems()
        if not w_listItems: return

        w_action = {}

        for w_item in w_listItems:
            w_jsonAction = w_item.data(Qt.ItemDataRole.UserRole)
            w_action = json.loads(w_jsonAction)
            break

        if w_action['name'] == 'key action':
            w_keyEditWnd = KeyActionEditWnd(w_action, self)
            if w_keyEditWnd.exec() == QDialog.DialogCode.Accepted:
                w_jsonAction = json.dumps(w_keyEditWnd.m_keyAction)
        elif w_action['name'] == 'mouse click action' \
                or w_action['name'] == 'mouse move action'\
                or w_action['name'] == 'mouse scroll action':
            w_mouseEditWnd = MouseActionEditWnd(w_action, self)
            if w_mouseEditWnd.exec() == QDialog.DialogCode.Accepted:
                w_jsonAction = json.dumps(w_mouseEditWnd.m_mouseAction)
        elif w_action['name'] == 'pause action':
            w_pauseEditWnd = PauseActionEditWnd(w_action, self)
            if w_pauseEditWnd.exec() == QDialog.DialogCode.Accepted:
                w_jsonAction = json.dumps(w_pauseEditWnd.m_pauseAction)
        elif w_action['name'] == 'command stop action' \
            or w_action['name'] == 'command execute action':
            text, okPressed = QInputDialog.getText(self, "Get Command Name", "Another command name:", QLineEdit.EchoMode.Normal,
                                                   w_action['command name'])
            if okPressed and text != '':
                w_action['command name'] = text
                w_jsonAction = json.dumps(w_action)
        elif w_action['name'] == 'play sound':
            w_soundEditWnd = SoundActionEditWnd(self.m_parent.m_parent.m_sound, w_action, self)
            if w_soundEditWnd.exec() == QDialog.DialogCode.Accepted:
                w_jsonAction = json.dumps(w_soundEditWnd.m_soundAction)

        w_item.setText(w_jsonAction)
        w_item.setData(Qt.ItemDataRole.UserRole, w_jsonAction)

    def slotDelete(self):
        w_listItems = self.ui.actionsListWidget.selectedItems()
        if not w_listItems: return
        for w_item in w_listItems:
            self.ui.actionsListWidget.takeItem(self.ui.actionsListWidget.row(w_item))

    def saveCommand(self):
        w_actionCnt = self.ui.actionsListWidget.count()
        self.m_command['name'] = self.ui.say.text()
        w_actions = []
        for w_idx in range(w_actionCnt):
            w_jsonAction = self.ui.actionsListWidget.item(w_idx).data(Qt.ItemDataRole.UserRole)
            w_action = json.loads(w_jsonAction)
            w_actions.append(w_action)
        self.m_command['actions'] = w_actions
        self.m_command['async'] = self.ui.asyncChk.isChecked()
        self.m_command['threshold'] = self.ui.thresholdSpin.value()
        if self.ui.oneExe.isChecked():
            self.m_command['repeat'] = 1
        elif self.ui.continueExe.isChecked():
            self.m_command['repeat'] = -1
        elif self.ui.repeatExe.isChecked():
            self.m_command['repeat'] = self.ui.repeatCnt.value()

    def slotOK(self):
        self.saveCommand()
        super().accept()

    def slotCancel(self):
        super().reject()

