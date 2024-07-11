import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
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

        self.settings_button = tk.Button(self.root, text="Settings", command=self.open_settings)
        self.settings_button.pack(pady=5)

        self.add_account_button.config(text="Add Account", relief=tk.RAISED)
        self.add_account_button.bind("<Enter>", lambda event: self.show_tooltip(event, "Add a new account"))
        self.add_account_button.bind("<Leave>", self.hide_tooltip)

        self.settings_button.config(text="Settings", relief=tk.RAISED)
        self.settings_button.bind("<Enter>", lambda event: self.show_tooltip(event, "Open settings menu"))
        self.settings_button.bind("<Leave>", self.hide_tooltip)

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

    def open_settings(self):
        SettingsMenu(self)

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

    def show_tooltip(self, event, text):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

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

class SettingsMenu:
    def __init__(self, app):
        self.app = app
        self.root = tk.Toplevel(app.root)
        self.root.title("Settings")

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.settings_label = tk.Label(self.main_frame, text="Settings")
        self.settings_label.pack()

        self.import_button = tk.Button(self.root, text="Import Accounts", command=self.import_accounts)
        self.import_button.pack(pady=5)

        self.export_button = tk.Button(self.root, text="Export Accounts", command=self.export_accounts)
        self.export_button.pack(pady=5)

        self.database_button = tk.Button(self.root, text="Database Path", command=self.database_path)
        self.database_button.pack(pady=5)

        self.hash_length_button = tk.Button(self.root, text="Hash Length", command=self.hash_length)
        self.hash_length_button.pack(pady=5)

        self.hash_iterations_button = tk.Button(self.root, text="Hash Iterations", command=self.hash_iterations)
        self.hash_iterations_button.pack(pady=5)

        self.rest_button = tk.Button(self.root, text="Rest Time", command=self.rest_time)
        self.rest_button.pack(pady=5)

        self.local_host_button = tk.Button(self.root, text="Local Host", command=self.local_host)
        self.local_host_button.pack(pady=5)

        self.close_button = tk.Button(self.root, text="Close", command=self.close)
        self.close_button.pack(pady=5)

    def import_accounts(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                data = file.read()
                # Import logic here
                messagebox.showinfo("Import Accounts", "Accounts imported successfully.")

    def export_accounts(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, 'w') as file:
                # Export logic here
                file.write("account data")
                messagebox.showinfo("Export Accounts", "Accounts exported successfully.")

    def database_path(self):
        path = filedialog.askdirectory()
        if path:
            messagebox.showinfo("Database Path", f"Database path set to: {path}")

    def hash_length(self):
        length = simpledialog.askinteger("Hash Length", "Enter the hash length:")
        if length:
            messagebox.showinfo("Hash Length", f"Hash length set to: {length}")

    def hash_iterations(self):
        iterations = simpledialog.askinteger("Hash Iterations", "Enter the number of hash iterations:")
        if iterations:
            messagebox.showinfo("Hash Iterations", f"Hash iterations set to: {iterations}")

    def rest_time(self):
        time = simpledialog.askinteger("Rest Time", "Enter the rest time in seconds:")
        if time:
            messagebox.showinfo("Rest Time", f"Rest time set to: {time}")

    def local_host(self):
        host = simpledialog.askstring("Local Host", "Enter the local host:")
        if host:
            messagebox.showinfo("Local Host", f"Local host set to: {host}")

    def close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManagerApp(root)
    root.mainloop()
