# Form implementation generated from reading ui file 'soundactioneditwnd.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SoundSelect(object):
    def setupUi(self, SoundSelect):
        SoundSelect.setObjectName("SoundSelect")
        SoundSelect.resize(1119, 362)
        SoundSelect.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.labelVoicepacks = QtWidgets.QLabel(parent=SoundSelect)
        self.labelVoicepacks.setGeometry(QtCore.QRect(10, 30, 111, 17))
        self.labelVoicepacks.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.labelVoicepacks.setObjectName("labelVoicepacks")
        self.labelCategories = QtWidgets.QLabel(parent=SoundSelect)
        self.labelCategories.setGeometry(QtCore.QRect(160, 30, 111, 17))
        self.labelCategories.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.labelCategories.setObjectName("labelCategories")
        self.listFiles = QtWidgets.QListView(parent=SoundSelect)
        self.listFiles.setGeometry(QtCore.QRect(660, 90, 451, 231))
        self.listFiles.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.listFiles.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listFiles.setProperty("showDropIndicator", False)
        self.listFiles.setAlternatingRowColors(True)
        self.listFiles.setObjectName("listFiles")
        self.listCategories = QtWidgets.QListView(parent=SoundSelect)
        self.listCategories.setEnabled(True)
        self.listCategories.setGeometry(QtCore.QRect(160, 90, 491, 231))
        self.listCategories.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.listCategories.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listCategories.setProperty("showDropIndicator", False)
        self.listCategories.setAlternatingRowColors(True)
        self.listCategories.setObjectName("listCategories")
        self.listVoicepacks = QtWidgets.QListView(parent=SoundSelect)
        self.listVoicepacks.setGeometry(QtCore.QRect(10, 50, 141, 271))
        self.listVoicepacks.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.listVoicepacks.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listVoicepacks.setProperty("showDropIndicator", False)
        self.listVoicepacks.setAlternatingRowColors(True)
        self.listVoicepacks.setObjectName("listVoicepacks")
        self.labelFiles = QtWidgets.QLabel(parent=SoundSelect)
        self.labelFiles.setGeometry(QtCore.QRect(660, 30, 111, 17))
        self.labelFiles.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.labelFiles.setObjectName("labelFiles")
        self.buttonOkay = QtWidgets.QPushButton(parent=SoundSelect)
        self.buttonOkay.setEnabled(True)
        self.buttonOkay.setGeometry(QtCore.QRect(940, 330, 80, 25))
        self.buttonOkay.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.buttonOkay.setObjectName("buttonOkay")
        self.buttonCancel = QtWidgets.QPushButton(parent=SoundSelect)
        self.buttonCancel.setGeometry(QtCore.QRect(1030, 330, 80, 25))
        self.buttonCancel.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.buttonCancel.setObjectName("buttonCancel")
        self.filterCategories = QtWidgets.QPlainTextEdit(parent=SoundSelect)
        self.filterCategories.setGeometry(QtCore.QRect(160, 50, 491, 31))
        self.filterCategories.setObjectName("filterCategories")
        self.filterFiles = QtWidgets.QPlainTextEdit(parent=SoundSelect)
        self.filterFiles.setGeometry(QtCore.QRect(660, 50, 451, 31))
        self.filterFiles.setPlainText("")
        self.filterFiles.setObjectName("filterFiles")
        self.buttonPlaySound = QtWidgets.QPushButton(parent=SoundSelect)
        self.buttonPlaySound.setGeometry(QtCore.QRect(410, 330, 80, 25))
        self.buttonPlaySound.setToolTip("")
        self.buttonPlaySound.setObjectName("buttonPlaySound")
        self.buttonStopSound = QtWidgets.QPushButton(parent=SoundSelect)
        self.buttonStopSound.setGeometry(QtCore.QRect(500, 330, 80, 25))
        self.buttonStopSound.setToolTip("")
        self.buttonStopSound.setObjectName("buttonStopSound")

        self.retranslateUi(SoundSelect)
        QtCore.QMetaObject.connectSlotsByName(SoundSelect)

    def retranslateUi(self, SoundSelect):
        _translate = QtCore.QCoreApplication.translate
        SoundSelect.setWindowTitle(_translate("SoundSelect", "Sound selection"))
        self.labelVoicepacks.setText(_translate("SoundSelect", "VoicePacks:"))
        self.labelCategories.setText(_translate("SoundSelect", "Categories:"))
        self.labelFiles.setText(_translate("SoundSelect", "Voice files:"))
        self.buttonOkay.setText(_translate("SoundSelect", "Save"))
        self.buttonCancel.setText(_translate("SoundSelect", "Cancel"))
        self.filterCategories.setToolTip(_translate("SoundSelect", "Filter categories"))
        self.filterCategories.setStatusTip(_translate("SoundSelect", "Filter"))
        self.filterFiles.setToolTip(_translate("SoundSelect", "Filter voice files"))
        self.filterFiles.setStatusTip(_translate("SoundSelect", "Filter"))
        self.buttonPlaySound.setText(_translate("SoundSelect", "Play Sound"))
        self.buttonStopSound.setText(_translate("SoundSelect", "Stop Sound"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SoundSelect = QtWidgets.QGroupBox()
    ui = Ui_SoundSelect()
    ui.setupUi(SoundSelect)
    SoundSelect.show()
    sys.exit(app.exec())
