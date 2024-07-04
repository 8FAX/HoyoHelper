import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import sqlite3
import hashlib
import os

DB_NAME = "accounts.db"
SALT_SIZE = 16
HASH_ITERATIONS = 100000

class AccountManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Manager")

        self.setup_database()
        self.load_accounts()

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.account_listbox = tk.Listbox(self.main_frame, width=50)
        self.account_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.main_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.account_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.account_listbox.yview)

        self.add_account_button = tk.Button(self.root, text="Add Account", command=self.add_account)
        self.add_account_button.pack(pady=5)

        self.update_account_list()

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
                token TEXT
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
                "token": row[6]
            }
            self.accounts.append(account)

    def update_account_list(self):
        self.account_listbox.delete(0, tk.END)
        for account in self.accounts:
            status = "✓" if account["token"] else "✗"
            self.account_listbox.insert(tk.END, f"{account['nickname']} ({status})")

    def add_account(self):
        AddAccountDialog(self)

    def save_account(self, account):
        salt = os.urandom(SALT_SIZE)
        password_hash = hashlib.pbkdf2_hmac('sha256', account['password'].encode(), salt, HASH_ITERATIONS)
        salt_hex = salt.hex()
        password_hash_hex = password_hash.hex()

        self.cursor.execute('''
            INSERT INTO accounts (nickname, username, password_hash, salt, games, token)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (account['nickname'], account['username'], password_hash_hex, salt_hex, ','.join(account['games']), account['token']))
        self.conn.commit()

        account_id = self.cursor.lastrowid
        account["id"] = account_id
        self.accounts.append(account)
        self.update_account_list()

    def get_token(self, account):
        # Replace this with the real token retrieval logic
        return True

class AddAccountDialog(simpledialog.Dialog):
    def __init__(self, app):
        self.app = app
        super().__init__(app.root, "Add Account")

    def body(self, master):
        self.nickname_label = tk.Label(master, text="Nickname:")
        self.nickname_label.grid(row=0, column=0, sticky=tk.W)
        self.nickname_entry = tk.Entry(master)
        self.nickname_entry.grid(row=0, column=1)

        self.username_label = tk.Label(master, text="Username/Email:")
        self.username_label.grid(row=1, column=0, sticky=tk.W)
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=1, column=1)

        self.password_label = tk.Label(master, text="Password:")
        self.password_label.grid(row=2, column=0, sticky=tk.W)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=2, column=1)

        self.games_label = tk.Label(master, text="Games:")
        self.games_label.grid(row=3, column=0, sticky=tk.W)
        self.games_vars = []
        self.games_checkbuttons = []
        games = ["Game 1", "Game 2", "Game 3"]
        for i, game in enumerate(games):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(master, text=game, variable=var)
            chk.grid(row=3 + i, column=1, sticky=tk.W)
            self.games_vars.append(var)
            self.games_checkbuttons.append(chk)

        return self.nickname_entry  # initial focus

    def apply(self):
        nickname = self.nickname_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        games = [game for i, game in enumerate(["Game 1", "Game 2", "Game 3"]) if self.games_vars[i].get()]

        if not nickname or not username or not password or not games:
            messagebox.showwarning("Incomplete Data", "Please fill out all fields and select at least one game.")
            return

        account = {
            "nickname": nickname,
            "username": username,
            "password": password,
            "games": games,
            "token": ""
        }
        self.app.save_account(account)


if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManagerApp(root)
    root.mainloop()
