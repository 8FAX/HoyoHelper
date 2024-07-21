import sys
import hashlib
import os
import asyncio
from PyQt5 import QtWidgets, QtCore, QtGui
from dependencies.login import run_account
from dependencies.pips import get_token, format_cookies
from dependencies.encrypt import encrypt, decrypt
from database import setup_database, load_accounts, save_account, update_account, delete_account

SALT_SIZE = 16
HASH_ITERATIONS = 100000
NOTIFICATION_DURATION = 3000  # Duration in milliseconds
NOTIFICATION_SPACING = 10     # Spacing between notifications
ENCRIPTION_KEY = "123"

class NotificationWidget(QtWidgets.QWidget):
    def __init__(self, message, parent=None, color="red"):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool | QtCore.Qt.X11BypassWindowManagerHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 60)

        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)

        self.setStyleSheet(f"color: {color}; text-align: center; text-decoration: none; font-weight: bold; font-family: Arial; background-color: #2c2f33;  border: 3px solid {color}; border-radius: 10px;")

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(NOTIFICATION_DURATION)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_notification)

        self.adjust_font_size(message)

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

    def show_notification(self, position):
        self.move(position)
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
        self.anim.finished.connect(lambda: self.parent().remove_notification(self))
        self.anim.start()

class AccountManagerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Account Manager")
        self.resize(800, 600)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        setup_database()
        self.accounts = load_accounts()
        self.setup_ui()
        self.load_css()

        self.notifications = []

        self._start_pos = None
        self._is_resizing = False
        self._resize_direction = None
        self._margin = 10 

    def load_css(self):
        css_file_path = os.path.join(os.path.dirname(__file__), 'styles.css')
        if os.path.exists(css_file_path):
            with open(css_file_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"CSS file not found at {css_file_path}")

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.title_bar = self.create_title_bar()
        main_layout.addWidget(self.title_bar)

        central_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(central_layout)

        self.nav_list = QtWidgets.QListWidget()
        self.nav_list.setFixedWidth(150)
        self.nav_list.addItem("Home")
        self.nav_list.addItem("Add Account")
        self.nav_list.addItem("Settings")
        self.nav_list.currentRowChanged.connect(self.display_page)
        central_layout.addWidget(self.nav_list)

        self.stacked_widget = QtWidgets.QStackedWidget()
        central_layout.addWidget(self.stacked_widget)

        self.home_page = QtWidgets.QWidget()
        self.setup_home_ui()
        self.stacked_widget.addWidget(self.home_page)

        self.add_account_page = QtWidgets.QWidget()
        self.setup_add_account_ui()
        self.stacked_widget.addWidget(self.add_account_page)

        self.settings_page = QtWidgets.QWidget()
        self.setup_settings_ui()
        self.stacked_widget.addWidget(self.settings_page)

        self.edit_account_page = QtWidgets.QWidget()
        self.setup_edit_account_ui()
        self.stacked_widget.addWidget(self.edit_account_page)

        self.nav_list.setCurrentRow(0)  #

    def create_title_bar(self):
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #2c2f33;")

        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QtWidgets.QLabel("Account Manager")
        title_label.setStyleSheet("color: white; font-size: 16px; margin-left: 10px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        minimize_button = self.create_title_button("—")
        minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_button)

        maximize_button = self.create_title_button("⬜")
        maximize_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(maximize_button)

        close_button = self.create_title_button("✖")
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)

        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent

        self.is_maximized = False
        self.start_pos = None

        return title_bar

    def clear_account_inputs(self):
        self.nickname_entry.clear()
        self.username_entry.clear()
        self.password_entry.clear()
        self.webhook_entry.clear()
        for checkbox in self.games_vars:
            checkbox.setChecked(False)

    def setup_home_ui(self):
        layout = QtWidgets.QVBoxLayout(self.home_page)

        self.account_listbox = QtWidgets.QListWidget()
        self.account_listbox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.account_listbox.customContextMenuRequested.connect(self.show_context_menu)
        self.account_listbox.itemClicked.connect(self.show_context_menu)
        layout.addWidget(self.account_listbox)

        self.update_account_list()

    def setup_add_account_ui(self):
        layout = QtWidgets.QFormLayout(self.add_account_page)

        self.nickname_entry = QtWidgets.QLineEdit()
        layout.addRow("Nickname:", self.nickname_entry)

        self.username_entry = QtWidgets.QLineEdit()
        layout.addRow("Username/Email:", self.username_entry)

        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addRow("Password:", self.password_entry)

        self.webhook_entry = QtWidgets.QLineEdit()
        layout.addRow("Webhook:", self.webhook_entry)

        self.toggle_password_visibility_button = QtWidgets.QPushButton("Show/Hide Password")
        self.toggle_password_visibility_button.clicked.connect(self.toggle_password_visibility)
        layout.addRow(self.toggle_password_visibility_button)

        self.games_layout = QtWidgets.QVBoxLayout()
        self.games_vars = []
        games = ["GI", "HRS", "ZZZ"]
        for game in games:
            checkbox = QtWidgets.QCheckBox(game)
            self.games_layout.addWidget(checkbox)
            self.games_vars.append(checkbox)
        layout.addRow("Games:", self.games_layout)

        self.save_account_button = QtWidgets.QPushButton("Save Account")
        self.save_account_button.clicked.connect(self.save_account)
        layout.addWidget(self.save_account_button)

    def setup_settings_ui(self):
        layout = QtWidgets.QVBoxLayout(self.settings_page)

        self.database_button = QtWidgets.QPushButton("Database Path")
        self.database_button.clicked.connect(self.database_path)
        layout.addWidget(self.database_button)

        self.hash_length_button = QtWidgets.QPushButton("Salt Length")
        self.hash_length_button.clicked.connect(self.hash_length)
        layout.addWidget(self.hash_length_button)

        self.hash_iterations_button = QtWidgets.QPushButton("Hash Iterations")
        self.hash_iterations_button.clicked.connect(self.hash_iterations)
        layout.addWidget(self.hash_iterations_button)

        self.rest_button = QtWidgets.QPushButton("Rest Time")
        self.rest_button.clicked.connect(self.rest_time)
        layout.addWidget(self.rest_button)

    def setup_edit_account_ui(self):
        layout = QtWidgets.QFormLayout(self.edit_account_page)

        self.edit_password_verify_entry = QtWidgets.QLineEdit()
        self.edit_password_verify_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addRow("Verify Password:", self.edit_password_verify_entry)

        self.verify_password_button = QtWidgets.QPushButton("Verify")
        self.verify_password_button.clicked.connect(self.verify_password)
        layout.addWidget(self.verify_password_button)

        self.toggle_verify_password_visibility_button = QtWidgets.QPushButton("Show/Hide Password")
        self.toggle_verify_password_visibility_button.clicked.connect(self.toggle_verify_password_visibility)
        layout.addRow(self.toggle_verify_password_visibility_button)

        self.edit_details_widget = QtWidgets.QWidget()
        self.edit_details_layout = QtWidgets.QFormLayout(self.edit_details_widget)

        self.edit_nickname_entry = QtWidgets.QLineEdit()
        self.edit_details_layout.addRow("Nickname:", self.edit_nickname_entry)

        self.edit_username_entry = QtWidgets.QLineEdit()
        self.edit_details_layout.addRow("Username/Email:", self.edit_username_entry)

        self.edit_password_entry = QtWidgets.QLineEdit()
        self.edit_password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edit_details_layout.addRow("Password:", self.edit_password_entry)

        self.edit_webhook_entry = QtWidgets.QLineEdit()
        self.edit_details_layout.addRow("Webhook:", self.edit_webhook_entry)

        self.toggle_edit_password_visibility_button = QtWidgets.QPushButton("Show/Hide Password")
        self.toggle_edit_password_visibility_button.clicked.connect(self.toggle_edit_password_visibility)
        self.edit_details_layout.addRow(self.toggle_edit_password_visibility_button)

        self.edit_games_layout = QtWidgets.QVBoxLayout()
        self.edit_games_vars = []
        games = ["GI", "HRS", "ZZZ"]
        for game in games:
            checkbox = QtWidgets.QCheckBox(game)
            self.edit_games_layout.addWidget(checkbox)
            self.edit_games_vars.append(checkbox)
        self.edit_details_layout.addRow("Games:", self.edit_games_layout)

        self.save_edit_button = QtWidgets.QPushButton("Save")
        self.save_edit_button.clicked.connect(self.save_account_info)
        self.edit_details_layout.addWidget(self.save_edit_button)

        self.delete_account_button = QtWidgets.QPushButton("Delete Account")
        self.delete_account_button.clicked.connect(self.delete_account)
        self.edit_details_layout.addWidget(self.delete_account_button)

        layout.addWidget(self.edit_details_widget)

        self.disable_edit_fields()
        self.edit_details_widget.hide()

    def verify_password(self):
        password = self.edit_password_verify_entry.text()
        if not password:
            self.show_notification("Please enter the password.", "red")
            return

        decrypted_password = decrypt(ENCRIPTION_KEY, self.current_account['encrypted_password'])
        if password == decrypted_password:
            self.enable_edit_fields()
            self.load_edit_account_page(password)
            self.edit_password_verify_entry.hide()
            self.edit_password_verify_entry.clear()
            self.verify_password_button.hide()
            self.toggle_verify_password_visibility_button.hide()
            self.edit_details_widget.show()
        else:
            self.show_notification("Incorrect Password", "red")

    def load_edit_account_page(self, password=""):
        if self.current_account:
            self.edit_nickname_entry.setText(self.current_account['nickname'])
            self.edit_username_entry.setText(self.current_account['username'])
            self.edit_password_entry.setText(password)
            self.edit_webhook_entry.setText(self.current_account['webhook'])
            for checkbox in self.edit_games_vars:
                checkbox.setChecked(checkbox.text() in self.current_account['games'])

    def disable_edit_fields(self):
        self.edit_nickname_entry.setEnabled(False)
        self.edit_username_entry.setEnabled(False)
        self.edit_password_entry.setEnabled(False)
        self.save_edit_button.setEnabled(False)
        self.delete_account_button.setEnabled(False)
        for checkbox in self.edit_games_vars:
            checkbox.setEnabled(False)

    def enable_edit_fields(self):
        self.edit_nickname_entry.setEnabled(True)
        self.edit_username_entry.setEnabled(True)
        self.edit_password_entry.setEnabled(True)
        self.edit_webhook_entry.setEnabled(True)
        self.save_edit_button.setEnabled(True)
        self.delete_account_button.setEnabled(True)
        for checkbox in self.edit_games_vars:
            checkbox.setEnabled(True)

    def display_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def update_account_list(self):
        self.account_listbox.clear()
        for account in self.accounts:
            status = "✓" if account["passing"] else "✗"
            self.account_listbox.addItem(f"{account['nickname']} ({status})")

    def save_account(self):
        nickname = self.nickname_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        webhook = self.webhook_entry.text()
        games = [checkbox.text() for checkbox in self.games_vars if checkbox.isChecked()]

        if not nickname or not username or not password or not games or not webhook:
            print(nickname, username, password, games, webhook)
            self.show_notification("Please fill out all fields and select at least one game.", "red")
            return

        password_ciphertext = encrypt(ENCRIPTION_KEY, password)
        save_account(nickname, username, password_ciphertext, games, webhook)

        self.accounts = load_accounts()
        self.update_account_list()
        self.display_page(0)
        self.clear_account_inputs()
        self.show_notification("Account saved successfully!", "green")
        self.show_notification("Attempting to get the token...", "green")
    
        asyncio.run(get_token(self.accounts[-1], self.conn, self.cursor))
        
    def database_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Database Path")
        if path:
            self.show_notification(f"Database path set to: {path}", "green")

    def hash_length(self):
        length, ok = QtWidgets.QInputDialog.getInt(self, "Hash Length", "Enter the hash length:")
        if ok:
            self.show_notification(f"Hash length set to: {length}", "green")

    def hash_iterations(self):
        iterations, ok = QtWidgets.QInputDialog.getInt(self, "Hash Iterations", "Enter the number of hash iterations:")
        if ok:
            self.show_notification(f"Hash iterations set to: {iterations}", "green")

    def rest_time(self):
        time, ok = QtWidgets.QInputDialog.getInt(self, "Rest Time", "Enter the rest time in seconds:")
        if ok:
            self.show_notification(f"Rest time set to: {time}", "green")

    def show_context_menu(self, item):
        if not item:
            return
        try:
            selected_account = item.text().split(" (")[0]
        except AttributeError:
            return
        
        self.current_account = next((account for account in self.accounts if account['nickname'] == selected_account), None)

        if not self.current_account:
            return

        menu = QtWidgets.QMenu()

        run_action = menu.addAction("Run this account")
        token_action = menu.addAction("Get new token")
        group_action = menu.addAction("Add to group")
        edit_action = menu.addAction("Edit/Remove account")

        run_action.triggered.connect(self.run_account)
        token_action.triggered.connect(self.get_new_token)
        group_action.triggered.connect(self.add_to_group)
        edit_action.triggered.connect(self.navigate_to_edit_account_page)

        menu.exec_(self.account_listbox.viewport().mapToGlobal(self.account_listbox.visualItemRect(item).bottomLeft()))

    def run_account(self):
        pass

    def get_new_token(self):
        pass

    def add_to_group(self):
        pass

    def navigate_to_edit_account_page(self):
        self.stacked_widget.setCurrentIndex(3)  
        self.reset_edit_account_page()

    def save_account_info(self):
        nickname = self.edit_nickname_entry.text()
        username = self.edit_username_entry.text()
        password = self.edit_password_entry.text()
        webhook = self.edit_webhook_entry.text()
        games = [checkbox.text() for checkbox in self.edit_games_vars if checkbox.isChecked()]

        if not nickname or not username or not webhook or (password and not games):
            self.show_notification("Please fill out all fields and select at least one game.", "red")
            return

        if password:
            encrypted_password = encrypt(ENCRIPTION_KEY, password)
        else:
            encrypted_password = self.current_account['encrypted_password']

        update_account(self.current_account['id'], nickname, username, encrypted_password, games, webhook)

        self.accounts = load_accounts()
        self.update_account_list()
        self.show_notification("Account updated successfully!", "green")
        self.show_notification("Attempting to get the token...", "green")
        self.display_page(0)

    def delete_account(self):
        reply = QtWidgets.QMessageBox.question(self, 'Delete Account', "Are you sure you want to delete this account?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            delete_account(self.current_account['id'])
            self.accounts = load_accounts()
            self.update_account_list()
            self.show_notification("Account deleted successfully!", "red")
            self.display_page(0)

    def show_notification(self, message, color):
        notification = NotificationWidget(message, self, color)
        self.notifications.append(notification)
        self.update_notification_positions()
        notification.show_notification(self.notifications[-1].pos())

    def remove_notification(self, notification):
        self.notifications.remove(notification)
        self.update_notification_positions()

    def update_notification_positions(self):
        if self.notifications:
            parent_geometry = self.geometry()
            for i, notification in enumerate(self.notifications):
                x = parent_geometry.x() + parent_geometry.width() - notification.width() - 15
                y = parent_geometry.y() + parent_geometry.height() - (notification.height() + NOTIFICATION_SPACING) * (i + 1) - 40
                notification.move(x, y)

    def toggle_password_visibility(self):
        if self.password_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.password_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)

    def toggle_verify_password_visibility(self):
        if self.edit_password_verify_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.edit_password_verify_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.edit_password_verify_entry.setEchoMode(QtWidgets.QLineEdit.Password)

    def toggle_edit_password_visibility(self):
        if self.edit_password_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.edit_password_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.edit_password_entry.setEchoMode(QtWidgets.QLineEdit.Password)

    def reset_edit_account_page(self):
        self.edit_nickname_entry.clear()
        self.edit_username_entry.clear()
        self.edit_password_entry.clear()
        self.webhook_entry.clear()
        for checkbox in self.edit_games_vars:
            checkbox.setChecked(False)
        self.edit_password_verify_entry.show()
        self.verify_password_button.show()
        self.toggle_verify_password_visibility_button.show()
        self.edit_details_widget.hide()
        self.disable_edit_fields()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AccountManagerApp()
    window.show()
    sys.exit(app.exec_())
