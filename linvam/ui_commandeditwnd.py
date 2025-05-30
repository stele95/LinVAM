# Form implementation generated from reading ui file 'commandeditwnd.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CommandEditDialog(object):
    def setupUi(self, CommandEditDialog):
        CommandEditDialog.setObjectName("CommandEditDialog")
        CommandEditDialog.resize(900, 607)
        font = QtGui.QFont()
        font.setPointSize(10)
        CommandEditDialog.setFont(font)
        CommandEditDialog.setSizeGripEnabled(False)
        self.gridLayout = QtWidgets.QGridLayout(CommandEditDialog)
        self.gridLayout.setContentsMargins(25, 25, 25, 25)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.oneExe = QtWidgets.QRadioButton(parent=CommandEditDialog)
        self.oneExe.setAutoExclusive(True)
        self.oneExe.setObjectName("oneExe")
        self.horizontalLayout_9.addWidget(self.oneExe)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_9, 9, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.actionsListWidget = QtWidgets.QListWidget(parent=CommandEditDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.actionsListWidget.setFont(font)
        self.actionsListWidget.setObjectName("actionsListWidget")
        self.horizontalLayout_7.addWidget(self.actionsListWidget)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.upBut = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.upBut.setMinimumSize(QtCore.QSize(0, 0))
        self.upBut.setAutoDefault(False)
        self.upBut.setObjectName("upBut")
        self.verticalLayout_6.addWidget(self.upBut)
        self.downBut = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.downBut.setMinimumSize(QtCore.QSize(0, 0))
        self.downBut.setAutoDefault(False)
        self.downBut.setObjectName("downBut")
        self.verticalLayout_6.addWidget(self.downBut)
        self.editBut = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.editBut.setMinimumSize(QtCore.QSize(0, 0))
        self.editBut.setAutoDefault(False)
        self.editBut.setObjectName("editBut")
        self.verticalLayout_6.addWidget(self.editBut)
        self.deleteBut = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.deleteBut.setMinimumSize(QtCore.QSize(0, 0))
        self.deleteBut.setAutoDefault(False)
        self.deleteBut.setObjectName("deleteBut")
        self.verticalLayout_6.addWidget(self.deleteBut)
        self.duplicateBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.duplicateBtn.setMinimumSize(QtCore.QSize(0, 0))
        self.duplicateBtn.setObjectName("duplicateBtn")
        self.verticalLayout_6.addWidget(self.duplicateBtn)
        self.horizontalLayout_7.addLayout(self.verticalLayout_6)
        self.gridLayout.addLayout(self.horizontalLayout_7, 3, 0, 1, 7)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtWidgets.QLabel(parent=CommandEditDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_6, 2, 0, 1, 2)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.repeatExe = QtWidgets.QRadioButton(parent=CommandEditDialog)
        self.repeatExe.setAutoExclusive(True)
        self.repeatExe.setObjectName("repeatExe")
        self.horizontalLayout_11.addWidget(self.repeatExe)
        self.repeatCnt = QtWidgets.QSpinBox(parent=CommandEditDialog)
        self.repeatCnt.setMinimum(2)
        self.repeatCnt.setObjectName("repeatCnt")
        self.horizontalLayout_11.addWidget(self.repeatCnt)
        self.label_3 = QtWidgets.QLabel(parent=CommandEditDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_11.addWidget(self.label_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_11, 11, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.asyncChk = QtWidgets.QCheckBox(parent=CommandEditDialog)
        self.asyncChk.setChecked(True)
        self.asyncChk.setObjectName("asyncChk")
        self.horizontalLayout_8.addWidget(self.asyncChk)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem4)
        self.gridLayout.addLayout(self.horizontalLayout_8, 8, 0, 1, 3)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem5, 7, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(parent=CommandEditDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.keyBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.keyBtn.setAutoDefault(False)
        self.keyBtn.setObjectName("keyBtn")
        self.horizontalLayout_2.addWidget(self.keyBtn)
        self.mouseBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.mouseBtn.setAutoDefault(False)
        self.mouseBtn.setObjectName("mouseBtn")
        self.horizontalLayout_2.addWidget(self.mouseBtn)
        self.pauseBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.pauseBtn.setAutoDefault(False)
        self.pauseBtn.setObjectName("pauseBtn")
        self.horizontalLayout_2.addWidget(self.pauseBtn)
        self.playSoundBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.playSoundBtn.setAutoDefault(False)
        self.playSoundBtn.setObjectName("playSoundBtn")
        self.horizontalLayout_2.addWidget(self.playSoundBtn)
        self.stopSoundBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.stopSoundBtn.setAutoDefault(False)
        self.stopSoundBtn.setObjectName("stopSoundBtn")
        self.horizontalLayout_2.addWidget(self.stopSoundBtn)
        self.otherBtn = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.otherBtn.setAutoDefault(False)
        self.otherBtn.setObjectName("otherBtn")
        self.horizontalLayout_2.addWidget(self.otherBtn)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(parent=CommandEditDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.say = QtWidgets.QLineEdit(parent=CommandEditDialog)
        self.say.setObjectName("say")
        self.horizontalLayout.addWidget(self.say)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 8)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.continueExe = QtWidgets.QRadioButton(parent=CommandEditDialog)
        self.continueExe.setAutoExclusive(True)
        self.continueExe.setObjectName("continueExe")
        self.horizontalLayout_10.addWidget(self.continueExe)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem7)
        self.gridLayout.addLayout(self.horizontalLayout_10, 10, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem8)
        self.ok = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.ok.setMinimumSize(QtCore.QSize(130, 0))
        self.ok.setAutoDefault(False)
        self.ok.setObjectName("ok")
        self.horizontalLayout_12.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(parent=CommandEditDialog)
        self.cancel.setMinimumSize(QtCore.QSize(130, 0))
        self.cancel.setAutoDefault(False)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_12.addWidget(self.cancel)
        self.gridLayout.addLayout(self.horizontalLayout_12, 15, 0, 1, 4)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem9, 4, 0, 1, 2)

        self.retranslateUi(CommandEditDialog)
        QtCore.QMetaObject.connectSlotsByName(CommandEditDialog)

    def retranslateUi(self, CommandEditDialog):
        _translate = QtCore.QCoreApplication.translate
        CommandEditDialog.setWindowTitle(_translate("CommandEditDialog", "Command Edit Dialog"))
        self.oneExe.setText(_translate("CommandEditDialog", "This command executes once"))
        self.upBut.setText(_translate("CommandEditDialog", "Up"))
        self.downBut.setText(_translate("CommandEditDialog", "Down"))
        self.editBut.setText(_translate("CommandEditDialog", "Edit"))
        self.deleteBut.setText(_translate("CommandEditDialog", "Delete"))
        self.duplicateBtn.setText(_translate("CommandEditDialog", "Duplicate"))
        self.label_2.setText(_translate("CommandEditDialog", "When this command excutes, do the following:"))
        self.repeatExe.setText(_translate("CommandEditDialog", "This command repeats"))
        self.label_3.setText(_translate("CommandEditDialog", "times"))
        self.asyncChk.setText(_translate("CommandEditDialog", "Allow other commands to execute while this one is running"))
        self.label_4.setText(_translate("CommandEditDialog", "Add new:"))
        self.keyBtn.setText(_translate("CommandEditDialog", "Key press/combination"))
        self.mouseBtn.setText(_translate("CommandEditDialog", "Mouse related event"))
        self.pauseBtn.setText(_translate("CommandEditDialog", "Pause"))
        self.playSoundBtn.setText(_translate("CommandEditDialog", "Play sound"))
        self.stopSoundBtn.setText(_translate("CommandEditDialog", "Stop sound"))
        self.otherBtn.setText(_translate("CommandEditDialog", "Other"))
        self.label.setText(_translate("CommandEditDialog", "When I say :"))
        self.continueExe.setText(_translate("CommandEditDialog", "This command repeats continuously"))
        self.ok.setText(_translate("CommandEditDialog", "Save"))
        self.cancel.setText(_translate("CommandEditDialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CommandEditDialog = QtWidgets.QDialog()
    ui = Ui_CommandEditDialog()
    ui.setupUi(CommandEditDialog)
    CommandEditDialog.show()
    sys.exit(app.exec())
