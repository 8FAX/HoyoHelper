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

# This file is part of HoYo Helper.
#version 0.3.0
# -------------------------------------------------------------------------------------

import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Dict, Any, TypedDict, Optional
import os

class Account(TypedDict):
    id: Optional[int]
    nickname: str
    username: str
    encrypted_password: str
    games: List[str]
    cookie_daily_login: Optional[str]
    cookie_codes: Optional[str]
    passing: bool
    webhook: Optional[str]

class Group(TypedDict):
    id: Optional[int]
    name: str
    members: List[str]

class DatabaseManager:
    def __init__(self, database_file='Info.db', runtime='os'):
        self.runtime = runtime
        self.database_file = database_file

        if self.runtime == 'os':
            if os.name == 'nt':
                app_data_path = os.getenv('APPDATA')
                if app_data_path:
                    self.database_file = os.path.join(app_data_path, 'HoyoHelper', 'data', 'database', database_file)
                else: # Fallback if APPDATA is not set
                    self.database_file = os.path.join(os.path.expanduser("~"), '.HoyoHelper', 'data', 'database', database_file)
            else:
                home_path = os.getenv('HOME')
                if home_path:
                    self.database_file = os.path.join(home_path, '.config', 'HoyoHelper', 'data', 'database', database_file)
                else: # Fallback if HOME is not set
                     self.database_file = os.path.join(os.path.expanduser("~"), '.HoyoHelper', 'data', 'database', database_file)
            
            db_dir = os.path.dirname(self.database_file)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # print(f"Database path set to: {self.database_file}") # Optional: for debugging

        elif runtime == 'docker':
            self.database_file = os.path.join('/app', 'data', 'database', database_file)
            db_dir = os.path.dirname(self.database_file)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # print(f"Database path set to: {self.database_file}") # Optional: for debugging
        
        self.check_database()


    def get_connection(self) -> Connection:
        return sqlite3.connect(self.database_file)

    def setup_database(self) -> bool:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                games TEXT NOT NULL,
                cookie_daily_login TEXT,
                cookie_codes TEXT,
                passing INTEGER NOT NULL DEFAULT 0,
                webhook TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                members TEXT
            )
        ''')
        conn.commit()
        conn.close()
        return True

    def load_accounts(self) -> List[Account]:
        if not os.path.exists(self.database_file):
            self.setup_database()
        
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT id, nickname, username, encrypted_password, games, cookie_daily_login, cookie_codes, passing, webhook FROM accounts")
        rows = cursor.fetchall()
        conn.close()
        
        accounts: List[Account] = []
        for row in rows:
            account: Account = {
                "id": row[0],
                "nickname": row[1],
                "username": row[2],
                "encrypted_password": row[3],
                "games": row[4].split(',') if row[4] else [],
                "cookie_daily_login": row[5],
                "cookie_codes": row[6],
                "passing": bool(row[7]),
                "webhook": row[8]
            }
            accounts.append(account)
        return accounts

    def save_account(self, account_data: Account) -> Optional[int]:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO accounts (nickname, username, encrypted_password, games, cookie_daily_login, cookie_codes, passing, webhook)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_data['nickname'], 
                account_data['username'], 
                account_data['encrypted_password'], 
                ','.join(account_data['games']), 
                account_data.get('cookie_daily_login'), 
                account_data.get('cookie_codes'), 
                int(account_data['passing']), 
                account_data.get('webhook')
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error in save_account: {e}")
            return None
        finally:
            conn.close()


    def update_account(self, account_data: Account) -> bool:
        if account_data.get('id') is None:
            return False 
            
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE accounts
                SET nickname=?, username=?, encrypted_password=?, games=?, 
                    cookie_daily_login=?, cookie_codes=?, passing=?, webhook=?
                WHERE id=?
            ''', (
                account_data['nickname'], 
                account_data['username'], 
                account_data['encrypted_password'], 
                ','.join(account_data['games']), 
                account_data.get('cookie_daily_login'), 
                account_data.get('cookie_codes'), 
                int(account_data['passing']), 
                account_data.get('webhook'), 
                account_data['id']
            ))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error in update_account: {e}")
            return False
        finally:
            conn.close()


    def delete_account(self, account_id: int) -> bool:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM accounts WHERE id=?", (account_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error in delete_account: {e}")
            return False
        finally:
            conn.close()

    def load_groups(self) -> List[Group]:
        if not os.path.exists(self.database_file):
            self.setup_database()

        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT id, name, members FROM groups")
        rows = cursor.fetchall()
        conn.close()
        
        groups: List[Group] = []
        for row in rows:
            group: Group = {
                "id": row[0],
                "name": row[1],
                "members": row[2].split(',') if row[2] else []
            }
            groups.append(group)
        return groups

    def save_group(self, group_data: Group) -> Optional[int]:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO groups (name, members)
                VALUES (?, ?)
            ''', (
                group_data['name'], 
                ','.join(group_data['members'])
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error in save_group: {e}")
            return None
        finally:
            conn.close()

    def update_group(self, group_data: Group) -> bool:
        if group_data.get('id') is None:
            return False

        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE groups
                SET name=?, members=?
                WHERE id=?
            ''', (
                group_data['name'],
                ','.join(group_data['members']),
                group_data['id']
            ))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error in update_group: {e}")
            return False
        finally:
            conn.close()


    def remove_group_member(self, group_id: int, member_to_remove: str) -> bool:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute("SELECT members FROM groups WHERE id=?", (group_id,))
            row = cursor.fetchone()
            if row is None:
                return False
            
            members = row[0].split(',') if row[0] else []
            if member_to_remove in members:
                members.remove(member_to_remove)
                cursor.execute("UPDATE groups SET members=? WHERE id=?", (','.join(members), group_id))
                conn.commit()
                return cursor.rowcount > 0
            return False
        except sqlite3.Error as e:
            print(f"Database error in remove_group_member: {e}")
            return False
        finally:
            conn.close()

    def add_group_member(self, group_id: int, member_to_add: str) -> bool:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute("SELECT members FROM groups WHERE id=?", (group_id,))
            row = cursor.fetchone()
            if row is None:
                return False
            
            members = row[0].split(',') if row[0] else []
            if member_to_add not in members:
                members.append(member_to_add)
                # Filter out empty strings if members list was empty initially and resulted in ['']
                members = [m for m in members if m] 
                cursor.execute("UPDATE groups SET members=? WHERE id=?", (','.join(members), group_id))
                conn.commit()
                return cursor.rowcount > 0
            return False
        except sqlite3.Error as e:
            print(f"Database error in add_group_member: {e}")
            return False
        finally:
            conn.close()

    def delete_group(self, group_id: int) -> bool:
        conn: Connection = self.get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM groups WHERE id=?", (group_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error in delete_group: {e}")
            return False
        finally:
            conn.close()
        
    def check_database(self) -> bool:
        db_dir = os.path.dirname(self.database_file)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError as e:
                print(f"Error creating database directory {db_dir}: {e}")
                return False

        if not os.path.exists(self.database_file):
            self.setup_database()
        
        try:
            conn: Connection = self.get_connection()
            self.check_tables(conn)
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database check failed for {self.database_file}: {e}")
            return False

    def check_tables(self, conn: Optional[Connection] = None) -> bool:
        close_conn_here = False
        if conn is None:
            conn = self.get_connection()
            close_conn_here = True
        
        try:
            cursor: Cursor = conn.cursor()
            
            table_exists = True
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
            if cursor.fetchone() is None:
                table_exists = False
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
            if cursor.fetchone() is None:
                table_exists = False

            if not table_exists:
                if close_conn_here:
                    conn.close()
                    close_conn_here = False 
                self.setup_database() 
                return True

            return True
        except sqlite3.Error as e:
            print(f"Error checking tables: {e}")
            return False
        finally:
            if close_conn_here and conn:
                conn.close()