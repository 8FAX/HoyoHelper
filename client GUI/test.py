# -------------------------------------------------------------------------------------
# HoYo Helper - a hoyolab helper tool
# Made with ♥ by 8FA (Uilliam.com)

# Copyright (C) 2024 copyright.Uilliam.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see https://github.com/8FAX/HoyoHelper/blob/main/LICENSE.md.
# SPDX-License-Identifier: AGPL-3.0-or-later
# do not remove this notice

# This file is part of [HoYo Helper].
#version 0.5.0
# -------------------------------------------------------------------------------------



from PyQt5 import QtWidgets, QtCore, QtGui

NOTIFICATION_DURATION = 3000  # Duration in milliseconds

class NotificationWidget(QtWidgets.QWidget):
    def __init__(self, message, parent=None, color="red"):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)

        self.setStyleSheet(f"color: {color}; text-align: center; text-decoration: none; font-weight: bold; font-family: Arial;")

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(NOTIFICATION_DURATION)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_notification)

        self.adjust_font_size(message)
        self.adjustSize()

    def adjust_font_size(self, message):
        font_size = 14
        self.label.setText(message)
        self.label.setStyleSheet(f"font-size: {font_size}px;")
        fm = QtGui.QFontMetrics(self.label.font())
        text_rect = fm.boundingRect(self.label.text())

        while (text_rect.width() > self.width() - 20 or text_rect.height() > self.height() - 20) and font_size > 14:
            font_size -= 1
            self.label.setStyleSheet(f"font-size: {font_size}px;")
            fm = QtGui.QFontMetrics(self.label.font())
            text_rect = fm.boundingRect(self.label.text())

        self.label.setText(message)

    def show_notification(self):
        if self.parent():
            parent_geometry = self.parent().geometry()
            widget_geometry = self.geometry()
            x = max(0, parent_geometry.x() + parent_geometry.width() - widget_geometry.width() - 15)
            y = max(0, parent_geometry.y() + parent_geometry.height() - widget_geometry.height() - 40)
            self.move(x, y)
        self.show()
        self.timer.start()
        self.animate_popup()

    def hide_notification(self):
        self.animate_disappearance()

    def animate_popup(self):
        self.anim = QtCore.QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setStartValue(QtCore.QPoint(self.x(), self.y() + self.height()))
        self.anim.setEndValue(QtCore.QPoint(self.x(), self.y()))
        self.anim.start()

    def animate_disappearance(self):
        self.anim = QtCore.QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setStartValue(QtCore.QPoint(self.x(), self.y()))
        self.anim.setEndValue(QtCore.QPoint(self.x(), self.y() + self.height()))
        self.anim.finished.connect(self.close)
        self.anim.start()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)
        self.notifications = []

        # Main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Button to trigger notifications
        self.notify_button = QtWidgets.QPushButton("Show Notification long")
        self.notify_button.clicked.connect(lambda: self.show_notification("This is a test notification. It may be long, so it needs to fit within the box. and thats super super cool!"))

        self.notify_button2 = QtWidgets.QPushButton("Show Notification short")
        self.notify_button2.clicked.connect(lambda: self.show_notification("This is a test notification."))
        main_layout.addWidget(self.notify_button)
        main_layout.addWidget(self.notify_button2)

    def show_notification(self, message, color="red"):
        notification = NotificationWidget(message, self, color)
        notification.show_notification()
        self.notifications.append(notification)
        notification.timer.timeout.connect(lambda: self.remove_notification(notification))

    def remove_notification(self, notification):
        self.notifications.remove(notification)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
