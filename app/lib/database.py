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
        """
        The function initializes a database file path based on the runtime environment (OS or Docker)
        and creates the necessary directories if they do not exist.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param database_file () Info.db - The `database_file` parameter is a string that specifies the
        name of the database file to be used. By default, it is set to 'Info.db'. This parameter is used
        to determine the path where the database file will be stored based on the runtime environment
        specified.
        
        .-.-.-.
        
        @ param runtime () os - The `runtime` parameter in the `__init__` method is used to specify the
        runtime environment in which the code is running. It can have two possible values:
        
        .-.-.-.
        
        
        """
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
        """
        The function `get_connection` returns a connection to a SQLite database using the specified
        database file.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns An SQLite database connection is being returned.
        
        .-.-.-.
        
        
        """
        return sqlite3.connect(self.database_file)

    def setup_database(self) -> bool:
        """
        The `setup_database` function creates two tables, 'accounts' and 'groups', in a database if they
        do not already exist.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `setup_database` method returns a boolean value `True` indicating that the
        database setup was successful.
        
        .-.-.-.
        
        
        """
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
        """
        This function loads account information from a database and returns a list of Account objects.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns A list of Account objects is being returned. Each Account object contains the
        following attributes: id, nickname, username, encrypted_password, games (a list of strings),
        cookie_daily_login, cookie_codes, passing (a boolean value), and webhook.
        
        .-.-.-.
        
        
        """
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
        """
        This function saves an account's data into a database table and returns the ID of the newly
        inserted row.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param account_data (Account)  - The `account_data` parameter is an instance of the `Account`
        class, which likely contains information about a user account. Based on the usage in the code
        snippet, it seems to have the following attributes:
        
        .-.-.-.
        
        
        
        @ returns The `save_account` method returns an optional integer value, which is the last row id
        of the inserted account data in the database table. If an error occurs during the database
        operation, it returns `None`.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function updates account information in a database table based on the provided
        account data.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param account_data (Account)  - The `update_account` method is used to update an existing
        account in a database. It takes an `account_data` parameter of type `Account`, which presumably
        contains information about the account to be updated.
        
        .-.-.-.
        
        
        
        @ returns The `update_account` method returns a boolean value. It returns `True` if the account
        update was successful (if `cursor.rowcount` is greater than 0), and `False` if there was an
        error during the update process or if the account data does not have an 'id' key.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function deletes an account from a database using the provided account ID.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param account_id (int)  - The `account_id` parameter is an integer that represents the unique
        identifier of the account that needs to be deleted from the database. This identifier is used to
        specify which account record should be removed from the `accounts` table when the
        `delete_account` method is called.
        
        .-.-.-.
        
        
        
        @ returns The `delete_account` method returns a boolean value indicating whether the deletion of
        the account with the specified `account_id` was successful. It returns `True` if at least one
        row was affected by the deletion operation, and `False` otherwise.
        
        .-.-.-.
        
        
        """
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
        """
        The function `load_groups` retrieves group data from a database and returns a list of Group
        objects.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns A list of Group objects is being returned. Each Group object contains an id, name, and
        a list of members.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function saves group data into a database table and returns the ID of the newly
        inserted row, handling potential errors along the way.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param group_data (Group)  - The `group_data` parameter is an instance of the `Group` class,
        which likely contains information about a group such as its name and members. In the provided
        code snippet, it is assumed that `group_data` is a dictionary-like object where `'name'` and
        `'members'` are
        
        .-.-.-.
        
        
        
        @ returns The `save_group` method is returning an optional integer value. This integer value
        represents the last row id of the inserted record in the database table. If the insertion is
        successful, the method will return this last row id. If there is an error during the insertion
        process, it will return `None`.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function updates a group's name and members in a database table based on the
        provided group data.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param group_data (Group)  - The `group_data` parameter is an instance of the `Group` class,
        which likely contains information about a group such as its `id`, `name`, and `members`. In the
        `update_group` method, it is used to update the corresponding group record in the database with
        the new values
        
        .-.-.-.
        
        
        
        @ returns The `update_group` method returns a boolean value. It returns `True` if the update
        operation was successful and at least one row was affected in the database. It returns `False`
        if there was an error during the update operation or if the `id` field in the `group_data`
        parameter is `None`.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function removes a specific member from a group by updating the group's members list
        in a SQLite database.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param group_id (int)  - The `group_id` parameter is an integer that represents the unique
        identifier of the group from which you want to remove a member.
        
        .-.-.-.
        
        @ param member_to_remove (str)  - The `member_to_remove` parameter in the `remove_group_member`
        method is a string that represents the member you want to remove from a specific group. This
        method takes the `group_id` of the group from which you want to remove the member and the
        `member_to_remove` string which is
        
        .-.-.-.
        
        
        
        @ returns The `remove_group_member` method returns a boolean value. It returns `True` if the
        member was successfully removed from the group, and `False` otherwise.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function adds a member to a group in a database and returns a boolean indicating
        success.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param group_id (int)  - The `group_id` parameter is an integer that represents the unique
        identifier of the group to which you want to add a member.
        
        .-.-.-.
        
        @ param member_to_add (str)  - The `member_to_add` parameter in the `add_group_member` method
        represents the name or identifier of the member that you want to add to a specific group
        identified by `group_id`. This method is responsible for adding a new member to the group's list
        of members in the database.
        
        .-.-.-.
        
        
        
        @ returns The `add_group_member` method returns a boolean value. It returns `True` if the member
        was successfully added to the group, and `False` otherwise.
        
        .-.-.-.
        
        
        """
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
        """
        This Python function deletes a group from a database using the provided group ID.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param group_id (int)  - The `group_id` parameter in the `delete_group` method is an integer
        that represents the unique identifier of the group that you want to delete from the database.
        This method takes the `group_id` as input, executes a SQL query to delete the group with that
        specific `group_id` from
        
        .-.-.-.
        
        
        
        @ returns The `delete_group` method returns a boolean value indicating whether the deletion
        operation was successful. It returns `True` if one or more rows were deleted from the "groups"
        table with the specified `group_id`, and `False` if an error occurred during the deletion
        process.
        
        .-.-.-.
        
        
        """
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
        """
        The function `check_database` checks if a database directory and file exist, creates them if
        necessary, and verifies the database tables.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `check_database` method returns a boolean value. It returns `True` if the database
        check is successful, and `False` if there is an error during the process.
        
        .-.-.-.
        
        
        """
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
        """
        The function `check_tables` checks if specific tables exist in a SQLite database and creates
        them if they do not.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param conn (Optional[Connection])  - The `conn` parameter in the `check_tables` method is a
        connection object to a SQLite database. It is an optional parameter, meaning it can be provided
        by the caller, but if not provided, the method will attempt to obtain a connection using the
        `self.get_connection()` method.
        
        .-.-.-.
        
        
        
        @ returns The `check_tables` method returns a boolean value. It returns `True` if the 'accounts'
        and 'groups' tables exist in the database, or if they do not exist but were successfully created
        by calling `self.setup_database()`. It returns `False` if there was an error checking the tables
        or if the tables do not exist and could not be created.
        
        .-.-.-.
        
        
        """
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