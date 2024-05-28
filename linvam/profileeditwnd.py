import json

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QAbstractItemView, QHeaderView

from linvam.commandeditwnd import CommandEditWnd
from linvam.ui_profileeditwnd import Ui_ProfileEditDialog


class ProfileEditWnd(QDialog):
    def __init__(self, p_profile, p_parent=None):
        super().__init__(p_parent)
        self.m_profiles = []
        self.ui = Ui_ProfileEditDialog()
        self.ui.setupUi(self)
        self.m_profile = {}
        self.m_parent = p_parent

        self.ui.cmdTable.setHorizontalHeaderLabels(('Spoken command', 'Actions'))
        self.ui.cmdTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.cmdTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.ui.cmdTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.ui.cmdTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # define actions here
        self.ui.newCmd.clicked.connect(self.slot_new_cmd)
        self.ui.editCmd.clicked.connect(self.slot_edit_cmd)
        self.ui.cmdTable.doubleClicked.connect(self.slot_edit_cmd)
        self.ui.deleteCmd.clicked.connect(self.slot_delete_cmd)
        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(self.slot_cancel)

        if p_profile is None or p_profile == {}:
            self.ui.cmdTable.setRowCount(0)
            return

        self.ui.profileNameEdit.setText(p_profile['name'])
        w_commands = p_profile['commands']
        self.ui.cmdTable.setRowCount(len(w_commands))
        i = 0
        for w_command in w_commands:
            self.ui.cmdTable.setItem(i, 0, QTableWidgetItem(w_command['name']))
            w_text = json.dumps(w_command, ensure_ascii=False)
            w_item = QTableWidgetItem(w_text)
            w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(w_command, ensure_ascii=False))
            self.ui.cmdTable.setItem(i, 1, w_item)
            i += 1

        QTimer.singleShot(100, self.ui.cmdTable.resizeRowsToContents)

    def import_command(self, p_command, p_update):
        w_command_cnt = self.ui.cmdTable.rowCount()
        for w_i in range(w_command_cnt):
            w_json_command = self.ui.cmdTable.item(w_i, 1).data(Qt.ItemDataRole.UserRole)
            w_command = json.loads(w_json_command)
            if w_command['name'] == p_command['name']:
                if p_update:
                    w_text = json.dumps(p_command, ensure_ascii=False)
                    w_item = QTableWidgetItem(w_text)
                    w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(p_command, ensure_ascii=False))
                    self.ui.cmdTable.setItem(w_i, 1, w_item)
                    self.ui.cmdTable.resizeRowsToContents()
                    return True
                return False

        w_row_cnt = self.ui.cmdTable.rowCount()
        self.ui.cmdTable.setRowCount(w_row_cnt + 1)
        self.ui.cmdTable.setItem(w_row_cnt, 0, QTableWidgetItem(p_command['name']))
        w_text = json.dumps(p_command, ensure_ascii=False)
        w_item = QTableWidgetItem(w_text)
        w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(p_command, ensure_ascii=False))
        self.ui.cmdTable.setItem(w_row_cnt, 1, w_item)
        self.ui.cmdTable.resizeRowsToContents()
        return True

    def slot_new_cmd(self):
        w_cmd_edit_wnd = CommandEditWnd(None, self)
        if w_cmd_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            if not self.import_command(w_cmd_edit_wnd.m_command, False):
                QMessageBox.critical(None, 'Error', 'Adding a new command failed')
                return
            self.ui.cmdTable.selectRow(self.ui.cmdTable.rowCount() - 1)
            self.ui.cmdTable.setFocus()

    def slot_edit_cmd(self):
        w_model_indexes = self.ui.cmdTable.selectionModel().selectedRows()
        if len(w_model_indexes) == 0:
            return
        w_model_idx = w_model_indexes[0]
        w_json_command = self.ui.cmdTable.item(w_model_idx.row(), 1).data(Qt.ItemDataRole.UserRole)
        w_command = json.loads(w_json_command)

        w_cmd_edit_wnd = CommandEditWnd(w_command, self)
        if w_cmd_edit_wnd.exec() == QDialog.DialogCode.Accepted:
            self.ui.cmdTable.setItem(w_model_idx.row(), 0, QTableWidgetItem(w_cmd_edit_wnd.m_command['name']))
            w_text = json.dumps(w_cmd_edit_wnd.m_command, ensure_ascii=False)
            w_item = QTableWidgetItem(w_text)
            w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(w_cmd_edit_wnd.m_command, ensure_ascii=False))
            self.ui.cmdTable.setItem(w_model_idx.row(), 1, w_item)
            self.ui.cmdTable.resizeRowsToContents()

    def slot_delete_cmd(self):
        w_model_indexes = self.ui.cmdTable.selectionModel().selectedRows()
        i = 0
        for w_model_idx in sorted(w_model_indexes):
            self.ui.cmdTable.removeRow(w_model_idx.row() - i)
            i += 1
        self.ui.cmdTable.setFocus()

    def slot_ok(self):
        self.m_profile = {'name': self.ui.profileNameEdit.text()}
        w_commands = []

        w_command_cnt = self.ui.cmdTable.rowCount()
        for w_i in range(w_command_cnt):
            w_json_command = self.ui.cmdTable.item(w_i, 1).data(Qt.ItemDataRole.UserRole)
            w_command = json.loads(w_json_command)
            w_commands.append(w_command)
        self.m_profile['commands'] = w_commands

        super().accept()

    def slot_cancel(self):
        super().reject()
