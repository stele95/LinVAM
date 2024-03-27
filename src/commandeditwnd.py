import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QMenu, QListWidgetItem, QInputDialog, QLineEdit

from keyactioneditwnd import KeyActionEditWnd
from mouseactioneditwnd import MouseActionEditWnd
from pauseactioneditwnd import PauseActionEditWnd
from soundactioneditwnd import SoundActionEditWnd
from ui_commandeditwnd import Ui_CommandEditDialog


class CommandEditWnd(QDialog):
    def __init__(self, p_command, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_CommandEditDialog()
        self.ui.setupUi(self)
        self.m_parent = p_parent

        self.ui.deleteBut.clicked.connect(self.slot_delete)
        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)
        self.ui.keyBut.clicked.connect(self.slot_new_key_edit)
        self.ui.mouseBut.clicked.connect(self.slot_new_mouse_edit)
        self.ui.pauseBut.clicked.connect(self.slot_new_pause_edit)
        self.ui.upBut.clicked.connect(self.slot_action_up)
        self.ui.downBut.clicked.connect(self.slot_action_down)
        self.ui.editBut.clicked.connect(self.slot_action_edit)
        self.ui.actionsListWidget.doubleClicked.connect(self.slot_action_edit)

        w_other_menu = QMenu()
        w_other_menu.addAction('Stop Another Command', self.slot_stop_another_command)
        w_other_menu.addAction('Execute Another Command', self.slot_do_another_command)
        w_other_menu.addAction('Play Sound', self.slot_new_sound_edit)
        self.ui.otherBut.setMenu(w_other_menu)

        self.m_command = {}
        if p_command is not None:
            self.ui.say.setText(p_command['name'])
            self.ui.thresholdSpin.setValue(p_command['threshold'])
            w_actions = p_command['actions']
            for w_action in w_actions:
                w_json_action = json.dumps(w_action)
                w_item = QListWidgetItem(w_json_action)
                w_item.setData(Qt.ItemDataRole.UserRole, w_json_action)
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

    def add_action(self, p_action):
        w_json_action = json.dumps(p_action)
        w_item = QListWidgetItem(w_json_action)
        w_item.setData(Qt.ItemDataRole.UserRole, w_json_action)
        self.ui.actionsListWidget.addItem(w_item)

    def slot_stop_another_command(self):
        text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another command name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            w_command_stop_action = {'name': 'command stop action', 'command name': text}
            self.add_action(w_command_stop_action)

    def slot_do_another_command(self):
        text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another command name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            w_command_do_action = {'name': 'command execute action', 'command name': text}
            self.add_action(w_command_do_action)

    def slot_do_play_sound(self):
        text, ok_pressed = QInputDialog.getItem(self, "Set sound to play", "Enter sound file:",
                                                list(self.m_parent.m_parent.m_sound.m_sounds), 0, False)
        if ok_pressed and text != '':
            w_command_do_action = {'name': 'command play sound', 'command name': text}
            self.add_action(w_command_do_action)

    def slot_new_key_edit(self):
        w_key_edit_wnd = KeyActionEditWnd(None, self)
        if w_key_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_key_edit_wnd.m_key_action)

    def slot_new_mouse_edit(self):
        w_mouse_edit_wnd = MouseActionEditWnd(None, self)
        if w_mouse_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_mouse_edit_wnd.m_mouseAction)

    def slot_new_pause_edit(self):
        w_pause_edit_wnd = PauseActionEditWnd(None, self)
        if w_pause_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_pause_edit_wnd.m_pauseAction)

    def slot_new_sound_edit(self):
        w_sound_edit_wnd = SoundActionEditWnd(self.m_parent.m_parent.m_sound, None, self)
        if w_sound_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_sound_edit_wnd.m_sound_action)

    def slot_action_up(self):
        current_index = self.ui.actionsListWidget.currentRow()
        current_item = self.ui.actionsListWidget.takeItem(current_index)
        self.ui.actionsListWidget.insertItem(current_index - 1, current_item)
        self.ui.actionsListWidget.setCurrentRow(current_index - 1)

    def slot_action_down(self):
        current_index = self.ui.actionsListWidget.currentRow()
        current_item = self.ui.actionsListWidget.takeItem(current_index)
        self.ui.actionsListWidget.insertItem(current_index + 1, current_item)
        self.ui.actionsListWidget.setCurrentRow(current_index + 1)

    def slot_action_edit(self):
        w_list_items = self.ui.actionsListWidget.selectedItems()
        if len(w_list_items) < 1:
            return

        w_item = w_list_items[0]
        w_json_action = w_item.data(Qt.ItemDataRole.UserRole)
        w_action = json.loads(w_json_action)

        if w_action['name'] == 'key action':
            w_key_edit_wnd = KeyActionEditWnd(w_action, self)
            if w_key_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                w_json_action = json.dumps(w_key_edit_wnd.m_key_action)
        elif (w_action['name'] == 'mouse click action' or w_action['name'] == 'mouse move action' or w_action['name']
              == 'mouse scroll action'):
            w_mouse_edit_wnd = MouseActionEditWnd(w_action, self)
            if w_mouse_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                w_json_action = json.dumps(w_mouse_edit_wnd.m_mouseAction)
        elif w_action['name'] == 'pause action':
            w_pause_edit_wnd = PauseActionEditWnd(w_action, self)
            if w_pause_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                w_json_action = json.dumps(w_pause_edit_wnd.m_pauseAction)
        elif w_action['name'] == 'command stop action' or w_action['name'] == 'command execute action':
            text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another command name:",
                                                    QLineEdit.EchoMode.Normal, w_action['command name'])
            if ok_pressed and text != '':
                w_action['command name'] = text
                w_json_action = json.dumps(w_action)
        elif w_action['name'] == 'play sound':
            w_sound_edit_wnd = SoundActionEditWnd(self.m_parent.m_parent.m_sound, w_action, self)
            if w_sound_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                w_json_action = json.dumps(w_sound_edit_wnd.m_sound_action)

        w_item.setText(w_json_action)
        w_item.setData(Qt.ItemDataRole.UserRole, w_json_action)

    def slot_delete(self):
        w_list_items = self.ui.actionsListWidget.selectedItems()
        if not w_list_items:
            return
        for w_item in w_list_items:
            self.ui.actionsListWidget.takeItem(self.ui.actionsListWidget.row(w_item))

    def save_command(self):
        w_action_cnt = self.ui.actionsListWidget.count()
        self.m_command['name'] = self.ui.say.text()
        w_actions = []
        for w_idx in range(w_action_cnt):
            w_json_action = self.ui.actionsListWidget.item(w_idx).data(Qt.ItemDataRole.UserRole)
            w_action = json.loads(w_json_action)
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

    def slot_ok(self):
        self.save_command()
        super().accept()

    def slot_cancel(self):
        super().reject()
