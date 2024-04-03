# Form implementation generated from reading ui file 'keyactioneditwnd.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_KeyActionEditDialog(object):
    def setupUi(self, KeyActionEditDialog):
        KeyActionEditDialog.setObjectName("KeyActionEditDialog")
        KeyActionEditDialog.resize(710, 280)
        KeyActionEditDialog.setMinimumSize(QtCore.QSize(710, 280))
        self.gridLayout = QtWidgets.QGridLayout(KeyActionEditDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.ok = QtWidgets.QPushButton(parent=KeyActionEditDialog)
        self.ok.setAutoDefault(False)
        self.ok.setObjectName("ok")
        self.horizontalLayout_3.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(parent=KeyActionEditDialog)
        self.cancel.setAutoDefault(False)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_3.addWidget(self.cancel)
        self.gridLayout.addLayout(self.horizontalLayout_3, 7, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.recordingButton = QtWidgets.QPushButton(parent=KeyActionEditDialog)
        self.recordingButton.setMinimumSize(QtCore.QSize(150, 0))
        self.recordingButton.setObjectName("recordingButton")
        self.horizontalLayout_4.addWidget(self.recordingButton)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(parent=KeyActionEditDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(parent=KeyActionEditDialog)
        font = QtGui.QFont()
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.sbDelay = QtWidgets.QSpinBox(parent=KeyActionEditDialog)
        self.sbDelay.setMinimumSize(QtCore.QSize(0, 0))
        self.sbDelay.setMaximum(9999)
        self.sbDelay.setObjectName("sbDelay")
        self.horizontalLayout_2.addWidget(self.sbDelay)
        self.resetDelay = QtWidgets.QToolButton(parent=KeyActionEditDialog)
        self.resetDelay.setToolTipDuration(5000)
        icon = QtGui.QIcon.fromTheme("edit-reset")
        self.resetDelay.setIcon(icon)
        self.resetDelay.setObjectName("resetDelay")
        self.horizontalLayout_2.addWidget(self.resetDelay)
        self.label_3 = QtWidgets.QLabel(parent=KeyActionEditDialog)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        self.label_3.setFont(font)
        self.label_3.setToolTipDuration(30000)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.keyEdit = QtWidgets.QLineEdit(parent=KeyActionEditDialog)
        self.keyEdit.setEnabled(True)
        self.keyEdit.setReadOnly(True)
        self.keyEdit.setObjectName("keyEdit")
        self.horizontalLayout.addWidget(self.keyEdit)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem4, 6, 0, 1, 1)

        self.retranslateUi(KeyActionEditDialog)
        QtCore.QMetaObject.connectSlotsByName(KeyActionEditDialog)

    def retranslateUi(self, KeyActionEditDialog):
        _translate = QtCore.QCoreApplication.translate
        KeyActionEditDialog.setWindowTitle(_translate("KeyActionEditDialog", "Key Action Dialog"))
        self.ok.setText(_translate("KeyActionEditDialog", "Save"))
        self.cancel.setText(_translate("KeyActionEditDialog", "Cancel"))
        self.recordingButton.setText(_translate("KeyActionEditDialog", "Start recording"))
        self.label.setText(_translate("KeyActionEditDialog", "Key combinations (input by pressing start recording and the pressing keys on the keyboard):"))
        self.label_2.setText(_translate("KeyActionEditDialog", "Delay between key events when executing commands (in milliseconds):"))
        self.resetDelay.setToolTip(_translate("KeyActionEditDialog", "Reset to default value"))
        self.resetDelay.setText(_translate("KeyActionEditDialog", "..."))
        self.label_3.setToolTip(_translate("KeyActionEditDialog", "Pressing a key and then releasing a key counts as two events.\n"
"Holding a key is a single event.\n"
"If the game is registering key events too fast, increase this value by a little (e.g. increments of 5).\n"
"Leave at the default value if not sure what to use initially."))
        self.label_3.setText(_translate("KeyActionEditDialog", "Hover here for more info"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    KeyActionEditDialog = QtWidgets.QDialog()
    ui = Ui_KeyActionEditDialog()
    ui.setupUi(KeyActionEditDialog)
    KeyActionEditDialog.show()
    sys.exit(app.exec())
