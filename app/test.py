import sys
import ctypes
from ctypes import wintypes
import win32con
import win32api
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QIcon

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel("Custom Title Bar")

        btn_size = 35

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(btn_size, btn_size)
        self.btn_close.clicked.connect(self.parent.close)

        self.btn_min = QPushButton("−")
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.clicked.connect(self.parent.showMinimized)

        self.btn_max = QPushButton("□")
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.clicked.connect(self.maximize_restore)

        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)

        self.setLayout(self.layout)

        self.start = QPoint(0, 0)
        self.pressing = False

    def resizeEvent(self, QResizeEvent):
        super(CustomTitleBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.parent.width())

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                    self.mapToGlobal(self.movement).y(),
                                    self.parent.width(),
                                    self.parent.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def maximize_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setText("□")
        else:
            self.parent.showMaximized()
            self.btn_max.setText("❐")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)

        self.content = QWidget()
        self.content.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
        """)
        self.layout.addWidget(self.content)

        self.central_widget.setLayout(self.layout)

        self.start = QPoint(0, 0)
        self.pressing = False

    def resizeEvent(self, QResizeEvent):
        super(MainWindow, self).resizeEvent(QResizeEvent)
        self.title_bar.setFixedWidth(self.width())

    def mousePressEvent(self, event):
        self.start = event.globalPos()
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = event.globalPos()
            self.movement = self.end - self.start
            self.setGeometry(self.pos().x() + self.movement.x(),
                             self.pos().y() + self.movement.y(),
                             self.width(),
                             self.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def nativeEvent(self, eventType, message):
        retval, result = super(MainWindow, self).nativeEvent(eventType, message)
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == win32con.WM_NCHITTEST:
                x = win32api.LOWORD(msg.lParam) - self.frameGeometry().x()
                y = win32api.HIWORD(msg.lParam) - self.frameGeometry().y()
                w = self.width()
                h = self.height()
                lx = x < 8
                rx = x > w - 8
                ty = y < 8
                by = y > h - 8
                if lx and ty:
                    return True, win32con.HTTOPLEFT
                if rx and by:
                    return True, win32con.HTBOTTOMRIGHT
                if rx and ty:
                    return True, win32con.HTTOPRIGHT
                if lx and by:
                    return True, win32con.HTBOTTOMLEFT
                if ty:
                    return True, win32con.HTTOP
                if by:
                    return True, win32con.HTBOTTOM
                if lx:
                    return True, win32con.HTLEFT
                if rx:
                    return True, win32con.HTRIGHT
        return retval, result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.setGeometry(100, 100, 300, 200)
    mw.show()
    sys.exit(app.exec_())