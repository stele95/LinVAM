from PyQt6.QtWidgets import QDialog

from ui_mouseactioneditwnd import Ui_MouseActionEditDialog


class MouseActionEditWnd(QDialog):
    def __init__(self, p_mouse_action, p_parent=None):
        super().__init__(p_parent)
        self.ui = Ui_MouseActionEditDialog()
        self.ui.setupUi(self)

        self.ui.ok.clicked.connect(self.slot_ok)
        self.ui.cancel.clicked.connect(super().reject)

        self.m_mouse_action = {}

        if p_mouse_action is None:
            return

        if p_mouse_action['name'] == 'mouse click action':
            self.restore_mouse_click_action(p_mouse_action)
        elif p_mouse_action['name'] == 'mouse move action':
            self.ui.mouseActionTabWidget.setCurrentIndex(1)
            if p_mouse_action['absolute']:
                self.ui.moveTo.setChecked(True)
                self.ui.xEdit.setText(str(p_mouse_action['x']))
                self.ui.yEdit.setText(str(p_mouse_action['y']))
            else:
                self.ui.moveOffset.setChecked(True)
                self.ui.xOffsetEdit.setText(str(p_mouse_action['x']))
                self.ui.yOffsetEdit.setText(str(p_mouse_action['y']))
        elif p_mouse_action['name'] == 'mouse scroll action':
            self.ui.mouseActionTabWidget.setCurrentIndex(1)
            if p_mouse_action['delta'] < 0:
                self.ui.scrollUp.setChecked(True)
                self.ui.scrollUpEdit.setText(str(-p_mouse_action['delta']))
            else:
                self.ui.scrollDown.setChecked(True)
                self.ui.scrollDownEdit.setText(str(p_mouse_action['delta']))

    def restore_mouse_click_action(self, p_mouse_action):
        self.ui.mouseActionTabWidget.setCurrentIndex(0)
        match p_mouse_action['button']:
            case 'left':
                match p_mouse_action['type']:
                    case 10:  # click
                        self.ui.leftClick.setChecked(True)
                    case 1:  # down
                        self.ui.leftDown.setChecked(True)
                    case 0:  # up
                        self.ui.leftUp.setChecked(True)
                    case 11:  # double-click
                        self.ui.leftDclick.setChecked(True)
            case 'right':
                match p_mouse_action['type']:
                    case 10:  # click
                        self.ui.rightClick.setChecked(True)
                    case 1:  # down
                        self.ui.rightDown.setChecked(True)
                    case 0:  # up
                        self.ui.rightUp.setChecked(True)
                    case 11:  # double-click
                        self.ui.rightDclick.setChecked(True)
            case 'middle':
                match p_mouse_action['type']:
                    case 10:  # click
                        self.ui.middleClick.setChecked(True)
                    case 1:  # down
                        self.ui.middleDown.setChecked(True)
                    case 0:  # up
                        self.ui.middleUp.setChecked(True)
                    case 11:  # double-click
                        self.ui.middleDclick.setChecked(True)

    def slot_ok(self):
        if self.ui.mouseActionTabWidget.currentIndex() == 0:
            if self.ui.leftClick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'left', 'type': 10}
            elif self.ui.rightClick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'right', 'type': 10}
            elif self.ui.middleClick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'middle', 'type': 10}

            elif self.ui.leftDclick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'left', 'type': 11}
            elif self.ui.rightDclick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'right', 'type': 11}
            elif self.ui.middleDclick.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'middle', 'type': 11}

            elif self.ui.leftDown.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'left', 'type': 1}
            elif self.ui.rightDown.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'right', 'type': 1}
            elif self.ui.middleDown.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'middle', 'type': 1}

            elif self.ui.leftUp.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'left', 'type': 0}
            elif self.ui.rightUp.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'right', 'type': 0}
            elif self.ui.middleUp.isChecked():
                self.m_mouse_action = {'name': 'mouse click action', 'button': 'middle', 'type': 0}
        else:
            if self.ui.moveTo.isChecked():
                self.m_mouse_action['name'] = 'mouse move action'
                self.m_mouse_action['x'] = int(self.ui.xEdit.text())
                self.m_mouse_action['y'] = int(self.ui.yEdit.text())
                self.m_mouse_action['absolute'] = True
            elif self.ui.moveOffset.isChecked():
                self.m_mouse_action['name'] = 'mouse move action'
                self.m_mouse_action['x'] = int(self.ui.xOffsetEdit.text())
                self.m_mouse_action['y'] = int(self.ui.yOffsetEdit.text())
                self.m_mouse_action['absolute'] = False
            elif self.ui.scrollUp.isChecked():
                self.m_mouse_action['name'] = 'mouse scroll action'
                self.m_mouse_action['delta'] = -(abs(int(self.ui.scrollUpEdit.text())))
            elif self.ui.scrollDown.isChecked():
                self.m_mouse_action['name'] = 'mouse scroll action'
                self.m_mouse_action['delta'] = abs(int(self.ui.scrollDownEdit.text()))

        super().accept()
