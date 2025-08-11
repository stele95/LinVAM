import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QMenu, QListWidgetItem, QInputDialog, QLineEdit

from linvam.keyactioneditwnd import KeyActionEditWnd
from linvam.mouseactioneditwnd import MouseActionEditWnd
from linvam.pauseactioneditwnd import PauseActionEditWnd
from linvam.soundactioneditwnd import SoundActionEditWnd
from linvam.ui_commandeditwnd import Ui_CommandEditDialog
from linvam.util import Command


class CommandEditWnd(QDialog):
    def __init__(self, p_command, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_CommandEditDialog()
        self.ui.setupUi(self)
        self.m_parent = p_parent

        self.ui.deleteBut.clicked.connect(self.slot_delete)
        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)
        self.ui.keyBtn.clicked.connect(self.slot_new_key_edit)
        self.ui.mouseBtn.clicked.connect(self.slot_new_mouse_edit)
        self.ui.pauseBtn.clicked.connect(self.slot_new_pause_edit)
        self.ui.playSoundBtn.clicked.connect(self.slot_new_sound_edit)
        self.ui.stopSoundBtn.clicked.connect(self.slot_stop_sound)
        self.ui.upBut.clicked.connect(self.slot_action_up)
        self.ui.downBut.clicked.connect(self.slot_action_down)
        self.ui.editBut.clicked.connect(self.slot_action_edit)
        self.ui.duplicateBtn.clicked.connect(self.slot_action_duplicate)
        self.ui.actionsListWidget.doubleClicked.connect(self.slot_action_edit)

        w_other_menu = QMenu()
        w_other_menu.addAction('Execute another voice command', self.slot_do_another_voice_command)
        w_other_menu.addAction('Stop another command', self.slot_stop_another_command)
        w_other_menu.addAction('Execute external script or command', self.slot_do_external_command)
        self.ui.otherBtn.setMenu(w_other_menu)

        self.m_command = {}
        if p_command is not None:
            self.ui.say.setText(p_command['name'])
            w_actions = p_command['actions']
            for w_action in w_actions:
                w_json_action = json.dumps(w_action, ensure_ascii=False)
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
        self.check_save_button_enabled_state()

    def check_save_button_enabled_state(self):
        self.ui.ok.setEnabled(self.ui.actionsListWidget.count() > 0)

    def add_action(self, p_action):
        w_json_action = json.dumps(p_action, ensure_ascii=False)
        w_item = QListWidgetItem(w_json_action)
        w_item.setData(Qt.ItemDataRole.UserRole, w_json_action)
        self.ui.actionsListWidget.addItem(w_item)
        self.check_save_button_enabled_state()

    def slot_stop_another_command(self):
        text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another command name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            w_command_stop_action = {'name': Command.COMMAND_STOP_ACTION, 'command name': text}
            self.add_action(w_command_stop_action)

    def slot_do_another_voice_command(self):
        text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another voice command name:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            w_command_do_action = {'name': Command.EXECUTE_VOICE_COMMAND_ACTION, 'command name': text}
            self.add_action(w_command_do_action)

    def slot_do_external_command(self):
        text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Enter external command or script path:",
                                                QLineEdit.EchoMode.Normal, "")
        if ok_pressed and text != '':
            w_command_do_action = {'name': Command.EXECUTE_EXTERNAL_COMMAND_ACTION, 'command': text}
            self.add_action(w_command_do_action)

    def slot_do_play_sound(self):
        text, ok_pressed = QInputDialog.getItem(
            self,
            "Set sound to play", "Enter sound file:",
            list(self.m_parent.m_parent.m_profile_executor.m_sound.m_sounds),
            0,
            False
        )
        if ok_pressed and text != '':
            w_command_do_action = {'name': Command.COMMAND_PLAY_SOUND, 'command name': text}
            self.add_action(w_command_do_action)

    def slot_new_key_edit(self):
        w_key_edit_wnd = KeyActionEditWnd(None, self)
        if w_key_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_key_edit_wnd.m_key_action)

    def slot_new_mouse_edit(self):
        w_mouse_edit_wnd = MouseActionEditWnd(None, self)
        if w_mouse_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_mouse_edit_wnd.m_mouse_action)

    def slot_new_pause_edit(self):
        w_pause_edit_wnd = PauseActionEditWnd(None, self)
        if w_pause_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_pause_edit_wnd.m_pause_action)

    def slot_new_sound_edit(self):
        w_sound_edit_wnd = SoundActionEditWnd(self.m_parent.m_parent.m_profile_executor.m_sound, None, self)
        if w_sound_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.add_action(w_sound_edit_wnd.m_sound_action)

    def slot_stop_sound(self):
        self.add_action({'name': Command.STOP_SOUND})

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

    def slot_action_duplicate(self):
        current_index = self.ui.actionsListWidget.currentRow()
        if current_index < 0:
            return
        current_item = self.ui.actionsListWidget.item(current_index)
        self.ui.actionsListWidget.insertItem(current_index + 1, current_item.clone())

    def slot_action_edit(self):
        w_list_items = self.ui.actionsListWidget.selectedItems()
        if len(w_list_items) < 1:
            return

        w_item = w_list_items[0]
        w_json_action = w_item.data(Qt.ItemDataRole.UserRole)
        w_action = json.loads(w_json_action)

        match w_action['name']:
            case Command.KEY_ACTION:
                w_key_edit_wnd = KeyActionEditWnd(w_action, self)
                if w_key_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                    w_json_action = json.dumps(w_key_edit_wnd.m_key_action, ensure_ascii=False)
            case Command.MOUSE_CLICK_ACTION | Command.MOUSE_MOVE_ACTION | Command.MOUSE_SCROLL_ACTION:
                w_mouse_edit_wnd = MouseActionEditWnd(w_action, self)
                if w_mouse_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                    w_json_action = json.dumps(w_mouse_edit_wnd.m_mouse_action, ensure_ascii=False)
            case Command.PAUSE_ACTION:
                w_pause_edit_wnd = PauseActionEditWnd(w_action, self)
                if w_pause_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                    w_json_action = json.dumps(w_pause_edit_wnd.m_pause_action, ensure_ascii=False)
            case Command.COMMAND_STOP_ACTION | Command.EXECUTE_VOICE_COMMAND_ACTION:
                text, ok_pressed = QInputDialog.getText(self, "Get Command Name", "Another command name:",
                                                        QLineEdit.EchoMode.Normal, w_action['command name'])
                if ok_pressed and text != '':
                    w_action['command name'] = text
                    w_json_action = json.dumps(w_action, ensure_ascii=False)
            case Command.EXECUTE_EXTERNAL_COMMAND_ACTION:
                text, ok_pressed = QInputDialog.getText(
                    self,
                    "Get Command Name",
                    "Enter external command or script path:",
                    QLineEdit.EchoMode.Normal,
                    w_action['command']
                )
                if ok_pressed and text != '':
                    w_action['command'] = text
                    w_json_action = json.dumps(w_action, ensure_ascii=False)
            case Command.PLAY_SOUND:
                w_sound_edit_wnd = SoundActionEditWnd(self.m_parent.m_parent.m_profile_executor.m_sound, w_action, self)
                if w_sound_edit_wnd.exec() == QDialog.DialogCode.Accepted:
                    w_json_action = json.dumps(w_sound_edit_wnd.m_sound_action, ensure_ascii=False)

        w_item.setText(w_json_action)
        w_item.setData(Qt.ItemDataRole.UserRole, w_json_action)

    def slot_delete(self):
        w_list_items = self.ui.actionsListWidget.selectedItems()
        if not w_list_items:
            return
        for w_item in w_list_items:
            self.ui.actionsListWidget.takeItem(self.ui.actionsListWidget.row(w_item))
        self.check_save_button_enabled_state()

    def save_command(self):
        w_action_cnt = self.ui.actionsListWidget.count()
        self.m_command['name'] = self.ui.say.text().lower()
        w_actions = []
        for w_idx in range(w_action_cnt):
            w_json_action = self.ui.actionsListWidget.item(w_idx).data(Qt.ItemDataRole.UserRole)
            w_action = json.loads(w_json_action)
            w_actions.append(w_action)
        self.m_command['actions'] = w_actions
        self.m_command['async'] = self.ui.asyncChk.isChecked()
        if self.ui.oneExe.isChecked():
            self.m_command['repeat'] = 1
        elif self.ui.continueExe.isChecked():
            self.m_command['repeat'] = -1
        elif self.ui.repeatExe.isChecked():
            self.m_command['repeat'] = self.ui.repeatCnt.value()

    def slot_ok(self):
        if not len(self.ui.say.text()) > 0:
            return
        self.save_command()
        super().accept()

    def slot_cancel(self):
        super().reject()
