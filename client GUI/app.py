import sys
import sqlite3
import hashlib
import os
from PyQt5 import QtWidgets, QtCore, QtGui

DB_NAME = "accounts.db"
SALT_SIZE = 16
HASH_ITERATIONS = 100000
NOTIFICATION_DURATION = 3000  # Duration in milliseconds
NOTIFICATION_SPACING = 10     # Spacing between notifications

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

        self.setStyleSheet(f"color: {color}; text-align: center; text-decoration: none; font-weight: bold; font-family: Arial; background-color: rgba(204, 153, 255, 200); border-radius: 10px;")

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

        self.setup_database()
        self.load_accounts()
        self.setup_ui()

        self.notifications = []

    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        self.nav_list = QtWidgets.QListWidget()
        self.nav_list.setFixedWidth(150)
        self.nav_list.addItem("Home")
        self.nav_list.addItem("Add Account")
        self.nav_list.addItem("Settings")
        self.nav_list.currentRowChanged.connect(self.display_page)
        layout.addWidget(self.nav_list)

        self.stacked_widget = QtWidgets.QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.home_page = QtWidgets.QWidget()
        self.setup_home_ui()
        self.stacked_widget.addWidget(self.home_page)

        self.add_account_page = QtWidgets.QWidget()
        self.setup_add_account_ui()
        self.stacked_widget.addWidget(self.add_account_page)

        self.settings_page = QtWidgets.QWidget()
        self.setup_settings_ui()
        self.stacked_widget.addWidget(self.settings_page)

    def clear_account_inputs(self):
        self.nickname_entry.clear()
        self.username_entry.clear()
        self.password_entry.clear()
        for checkbox in self.games_vars:
            checkbox.setChecked(False)

    def setup_home_ui(self):
        layout = QtWidgets.QVBoxLayout(self.home_page)

        self.account_listbox = QtWidgets.QListWidget()
        self.account_listbox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.account_listbox.customContextMenuRequested.connect(self.show_context_menu)
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

        self.import_button = QtWidgets.QPushButton("Import Accounts")
        self.import_button.clicked.connect(self.import_accounts)
        layout.addWidget(self.import_button)

        self.export_button = QtWidgets.QPushButton("Export Accounts")
        self.export_button.clicked.connect(self.export_accounts)
        layout.addWidget(self.export_button)

        self.database_button = QtWidgets.QPushButton("Database Path")
        self.database_button.clicked.connect(self.database_path)
        layout.addWidget(self.database_button)

        self.hash_length_button = QtWidgets.QPushButton("Hash Length")
        self.hash_length_button.clicked.connect(self.hash_length)
        layout.addWidget(self.hash_length_button)

        self.hash_iterations_button = QtWidgets.QPushButton("Hash Iterations")
        self.hash_iterations_button.clicked.connect(self.hash_iterations)
        layout.addWidget(self.hash_iterations_button)

        self.rest_button = QtWidgets.QPushButton("Rest Time")
        self.rest_button.clicked.connect(self.rest_time)
        layout.addWidget(self.rest_button)

        self.local_host_button = QtWidgets.QPushButton("Local Host")
        self.local_host_button.clicked.connect(self.local_host)
        layout.addWidget(self.local_host_button)

    def display_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def setup_database(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                nickname TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                games TEXT NOT NULL,
                token TEXT,
                passing TEXT
            )
        ''')
        self.conn.commit()

    def load_accounts(self):
        self.accounts = []
        self.cursor.execute("SELECT * FROM accounts")
        rows = self.cursor.fetchall()
        for row in rows:
            account = {
                "id": row[0],
                "nickname": row[1],
                "username": row[2],
                "password_hash": row[3],
                "salt": row[4],
                "games": row[5].split(','),
                "token": row[6],
                "passing": row[7]
            }
            self.accounts.append(account)

    def update_account_list(self):
        self.account_listbox.clear()
        for account in self.accounts:
            status = "✓" if account["passing"] else "✗"
            self.account_listbox.addItem(f"{account['nickname']} ({status})")

    def save_account(self):
        nickname = self.nickname_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        games = [checkbox.text() for checkbox in self.games_vars if checkbox.isChecked()]

        if not nickname or not username or not password or not games:
            QtWidgets.QMessageBox.warning(self, "Incomplete Data", "Please fill out all fields and select at least one game.")
            return

        salt = os.urandom(SALT_SIZE)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, HASH_ITERATIONS).hex()

        self.cursor.execute('''
            INSERT INTO accounts (nickname, username, password_hash, salt, games, token, passing)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nickname, username, password_hash, salt.hex(), ','.join(games), "", ""))
        self.conn.commit()

        self.load_accounts()
        self.update_account_list()
        self.display_page(0)
        self.clear_account_inputs()
        self.show_notification("Account saved successfully!", "green")

    def import_accounts(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Accounts", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, 'r') as file:
                data = file.read()
                # Import logic here
                self.show_notification("Accounts imported successfully!", "green")

    def export_accounts(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Accounts", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, 'w') as file:
                # Export logic here
                file.write("account data")
                self.show_notification("Accounts exported successfully!", "green")

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

    def local_host(self):
        host, ok = QtWidgets.QInputDialog.getText(self, "Local Host", "Enter the local host:")
        if ok:
            self.show_notification(f"Local host set to: {host}", "green")

    def show_context_menu(self, position):
        selected_items = self.account_listbox.selectedItems()
        if not selected_items:
            return

        selected_account = selected_items[0]
        self.current_account = next((account for account in self.accounts if account['nickname'] in selected_account.text()), None)

        if not self.current_account:
            return

        menu = QtWidgets.QMenu()

        run_action = menu.addAction("Run this account")
        token_action = menu.addAction("Get new token")
        group_action = menu.addAction("Add to group")
        edit_action = menu.addAction("Edit info")
        delete_action = menu.addAction("Delete")

        run_action.triggered.connect(self.run_account)
        token_action.triggered.connect(self.get_new_token)
        group_action.triggered.connect(self.add_to_group)
        edit_action.triggered.connect(self.edit_account_info)
        delete_action.triggered.connect(self.delete_account)

        menu.exec_(self.account_listbox.viewport().mapToGlobal(position))

    def run_account(self):
        pass

    def get_new_token(self):
        pass

    def add_to_group(self):
        pass

    def edit_account_info(self):
        password, ok = QtWidgets.QInputDialog.getText(self, "Password Required", "Enter the account password:", QtWidgets.QLineEdit.Password)
        if ok and self.verify_password(password, self.current_account['password_hash'], self.current_account['salt']):
            dialog = EditAccountDialog(self.current_account, self)
            if dialog.exec_():
                self.load_accounts()
                self.update_account_list()

    def delete_account(self):
        password, ok = QtWidgets.QInputDialog.getText(self, "Password Required", "Enter the account password:", QtWidgets.QLineEdit.Password)
        if ok and self.verify_password(password, self.current_account['password_hash'], self.current_account['salt']):
            reply = QtWidgets.QMessageBox.question(self, 'Delete Account', "Are you sure you want to delete this account?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.cursor.execute("DELETE FROM accounts WHERE id=?", (self.current_account['id'],))
                self.conn.commit()
                self.load_accounts()
                self.update_account_list()
                self.show_notification("Account deleted successfully!", "red")

    def verify_password(self, password, password_hash, salt):
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), HASH_ITERATIONS).hex()
        return hashed_password == password_hash

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

class EditAccountDialog(QtWidgets.QDialog):
    def __init__(self, account, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("Edit Account Info")
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)

        self.nickname_entry = QtWidgets.QLineEdit(self.account['nickname'])
        layout.addRow("Nickname:", self.nickname_entry)

        self.username_entry = QtWidgets.QLineEdit(self.account['username'])
        layout.addRow("Username/Email:", self.username_entry)

        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addRow("Password:", self.password_entry)

        self.games_layout = QtWidgets.QVBoxLayout()
        self.games_vars = []
        games = ["GI", "HRS", "ZZZ"]
        for game in games:
            checkbox = QtWidgets.QCheckBox(game)
            checkbox.setChecked(game in self.account['games'])
            self.games_layout.addWidget(checkbox)
            self.games_vars.append(checkbox)
        layout.addRow("Games:", self.games_layout)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.save_account_info)
        layout.addWidget(self.save_button)

    def save_account_info(self):
        nickname = self.nickname_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        games = [checkbox.text() for checkbox in self.games_vars if checkbox.isChecked()]

        if not nickname or not username or (password and not games):
            QtWidgets.QMessageBox.warning(self, "Incomplete Data", "Please fill out all fields and select at least one game.")
            return

        if password:
            salt = os.urandom(SALT_SIZE)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, HASH_ITERATIONS).hex()
        else:
            password_hash = self.account['password_hash']
            salt = bytes.fromhex(self.account['salt'])

        parent = self.parentWidget()
        parent.cursor.execute('''
            UPDATE accounts
            SET nickname=?, username=?, password_hash=?, salt=?, games=?
            WHERE id=?
        ''', (nickname, username, password_hash, salt.hex(), ','.join(games), self.account['id']))
        parent.conn.commit()

        self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AccountManagerApp()
    window.show()
    sys.exit(app.exec_())
