from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QAbstractItemView, QHeaderView
from ui_profileeditwnd import Ui_ProfileEditDialog
from commandeditwnd import CommandEditWnd
import json
from profileexecutor import *

class ProfileEditWnd(QDialog):
    def __init__(self, p_profile, p_parent = None):
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
        self.ui.newCmd.clicked.connect(self.slotNewCmd)
        self.ui.editCmd.clicked.connect(self.slotEditCmd)
        self.ui.cmdTable.doubleClicked.connect(self.slotEditCmd)
        self.ui.deleteCmd.clicked.connect(self.slotDeleteCmd)
        self.ui.ok.clicked.connect(self.slotOK)
        self.ui.cancel.clicked.connect(self.slotCancel)

        if p_profile == None or p_profile == {}:
            self.ui.cmdTable.setRowCount(0)
            return

        self.ui.profileNameEdit.setText(p_profile['name'])
        w_commands = p_profile['commands']
        self.ui.cmdTable.setRowCount(len(w_commands))
        i = 0
        for w_command in w_commands:
            self.ui.cmdTable.setItem(i, 0, QTableWidgetItem(w_command['name']))
            w_text = json.dumps(w_command)
            w_item = QTableWidgetItem(w_text)
            w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(w_command))
            self.ui.cmdTable.setItem(i, 1, w_item)
            i = i + 1

        QTimer.singleShot(100, self.ui.cmdTable.resizeRowsToContents)

    def importCommand(self, p_command, p_update):
        w_commandCnt = self.ui.cmdTable.rowCount()
        for w_i in range(w_commandCnt):
            w_jsonCommand = self.ui.cmdTable.item(w_i, 1).data(Qt.ItemDataRole.UserRole)
            w_command = json.loads(w_jsonCommand)
            if w_command['name'] == p_command['name']:
                if p_update:
                    w_text = json.dumps(p_command)
                    w_item = QTableWidgetItem(w_text)
                    w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(p_command))
                    self.ui.cmdTable.setItem(w_i, 1, w_item)
                    self.ui.cmdTable.resizeRowsToContents()
                    return True
                return False

        w_rowCnt = self.ui.cmdTable.rowCount()
        self.ui.cmdTable.setRowCount(w_rowCnt + 1)
        self.ui.cmdTable.setItem(w_rowCnt, 0, QTableWidgetItem(p_command['name']))
        w_text = json.dumps(p_command)
        w_item = QTableWidgetItem(w_text)
        w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(p_command))
        self.ui.cmdTable.setItem(w_rowCnt, 1, w_item)
        self.ui.cmdTable.resizeRowsToContents()

    def slotNewCmd(self):
        w_cmdEditWnd = CommandEditWnd(None, self)
        if w_cmdEditWnd.exec() == QDialog.DialogCode.Accepted:
            if self.importCommand(w_cmdEditWnd.m_command, False) == False:
                QMessageBox.critical(None, 'Error', 'Adding a new command was failed')
                return
            self.ui.cmdTable.selectRow(self.ui.cmdTable.rowCount() - 1)
            self.ui.cmdTable.setFocus()

    def slotEditCmd(self):
        w_modelIdxs = self.ui.cmdTable.selectionModel().selectedRows()
        if len(w_modelIdxs) == 0:
            return
        w_modelIdx = w_modelIdxs[0]
        w_jsonCommand = self.ui.cmdTable.item(w_modelIdx.row(), 1).data(Qt.ItemDataRole.UserRole)
        w_command = json.loads(w_jsonCommand)

        w_cmdEditWnd = CommandEditWnd(w_command, self)
        if w_cmdEditWnd.exec() == QDialog.DialogCode.Accepted:
            self.ui.cmdTable.setItem(w_modelIdx.row(), 0, QTableWidgetItem(w_cmdEditWnd.m_command['name']))
            w_text = json.dumps(w_cmdEditWnd.m_command)
            w_item = QTableWidgetItem(w_text)
            w_item.setData(Qt.ItemDataRole.UserRole, json.dumps(w_cmdEditWnd.m_command))
            self.ui.cmdTable.setItem(w_modelIdx.row(), 1, w_item)
            self.ui.cmdTable.resizeRowsToContents()

    def slotDeleteCmd(self):
        w_modelIdxs = self.ui.cmdTable.selectionModel().selectedRows()
        i = 0
        for w_modelIdx in sorted(w_modelIdxs):
            self.ui.cmdTable.removeRow(w_modelIdx.row() - i)
            i = i + 1
        self.ui.cmdTable.setFocus()

    def slotOK(self):
        self.m_profile = {}
        self.m_profile['name'] = self.ui.profileNameEdit.text()
        w_commands = []

        w_commandCnt = self.ui.cmdTable.rowCount()
        for w_i in range(w_commandCnt):
            w_jsonCommand = self.ui.cmdTable.item(w_i, 1).data(Qt.ItemDataRole.UserRole)
            w_command = json.loads(w_jsonCommand)
            w_commands.append(w_command)
        self.m_profile['commands'] = w_commands

        super().accept()

    def slotCancel(self):
        super().reject()
