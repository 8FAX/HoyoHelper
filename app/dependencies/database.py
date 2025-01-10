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
#version 0.1.1
# -------------------------------------------------------------------------------------

import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Dict, Any
import os

DB_NAME = "Info.db"

def get_connection(file: str = DB_NAME) -> Connection:
    """
    The function `get_connection` returns a connection to a SQLite database using the specified file
    name or a default database name.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @param file (str) - The `file` parameter in the `get_connection` function is a string that
    represents the name of the database file to connect to. If no file name is provided, it will default
    to `DB_NAME`.
    @returns A connection to a SQLite database is being returned.
    
    """
    return sqlite3.connect(file)

def setup_database() -> bool:
    """
    The function `setup_database` creates a table named `accounts` `groups` and `settings` in a database if it does not already
    exist.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @returns The function `setup_database()` is returning a boolean value `True` indicating that the
    database setup was successful.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            games TEXT NOT NULL,
            webhook TEXT,
            cookie TEXT,
            passing TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            members TEXT
        )
    ''')
    conn.commit()
    conn.close()
    return True

def load_accounts() -> List[Dict[str, Any]]:
    """
    This Python function loads account information from a database table into a list of dictionaries.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @returns A list of dictionaries representing accounts is being returned. Each dictionary contains
    the following keys: "id", "nickname", "username", "encrypted_password", "games", "cookie",
    "passing", and "webhook".
    
    """
    if not os.path.exists(DB_NAME):
        print("you ended up calling load_accounts without a database, this should not happen - database.py")
        setup_database()
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    rows = cursor.fetchall()
    conn.close()
    accounts: List[Dict[str, Any]] = []
    for row in rows:
        account = {
            "id": row[0],
            "nickname": row[1],
            "username": row[2],
            "encrypted_password": row[3],
            "games": row[4].split(','),
            "cookie": row[5],
            "passing": row[6],
            "webhook": row[7]
        }
        accounts.append(account)
    return accounts

def save_account(nickname: str, username: str, encrypted_password: str, games: List[str], webhook: str, cookie: str, passing: bool = False) -> bool:
    """
    The function `save_account` saves user account information into a database table.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @param nickname (str) - The `nickname` parameter in the `save_account` function is a string that
    represents the nickname associated with the account being saved.
    @param username (str) - The `username` parameter in the `save_account` function refers to the
    username of the account being saved. It is a string type parameter that should be provided when
    calling the function to specify the username associated with the account being saved.
    @param encrypted_password (str) - The `encrypted_password` parameter in the `save_account` function
    is a string that represents the password of the user's account. It is expected to be encrypted for
    security reasons before being stored in the database.
    @param games (List[str]) - The `games` parameter in the `save_account` function is a list of strings
    representing the games associated with the account being saved.
    @param webhook (str) - A webhook is a way for an application to provide other applications with
    real-time information. It is a URL that serves as a communication endpoint for sending data between
    different applications or services. When an event occurs in one application, it can trigger a
    webhook to send data to another application in real-time.
    @param cookie (str) - The `cookie` parameter in the `save_account` function seems to be a cookie or
    identifier that is being stored in the database along with other account information. It is being
    passed as a string parameter to the function.
    @param passing (bool) - The `passing` parameter in the `save_account` function is a boolean
    parameter with a default value of `False`. This parameter is used to indicate whether the account
    has passed certain criteria or not. If `passing` is set to `True`, it means that the account has
    passed the
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO accounts (nickname, username, encrypted_password, games, cookie, passing, webhook)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nickname, username, encrypted_password, ','.join(games), cookie, passing, webhook))
    conn.commit()
    conn.close()

def update_account(id: int, nickname: str, username: str, encrypted_password: str, games: List[str], webhook: str, cookie: str, passing: bool = False) -> bool: 
    """
    The function `update_account` updates account information in a database table.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @param id (int) - The `id` parameter in the `update_account` function is an integer that represents
    the unique identifier of the account that needs to be updated in the database.
    @param nickname (str) - A nickname is a name that is different from a person's actual name, often
    used informally. It can be a unique identifier or a more casual name that someone goes by.
    @param username (str) - The `update_account` function seems to be updating an account in a database
    table named `accounts`. It takes several parameters including `id`, `nickname`, `username`,
    `encrypted_password`, `games`, `webhook`, `cookie`, and `passing`.
    @param encrypted_password (str) - The `encrypted_password` parameter in the `update_account`
    function is a string that represents the encrypted password of the user account. This parameter is
    used to update the encrypted password of the account in the database when the function is called.
    @param games (List[str]) - The `games` parameter in the `update_account` function is expected to be
    a list of strings representing the games associated with the account. These games will be stored in
    the database as a comma-separated string when updating the account information.
    @param webhook (str) - A webhook is a way for an application to provide other applications with
    real-time information. It is a URL that serves as a communication endpoint for sending data between
    different applications or services. In the context of your `update_account` function, the `webhook`
    parameter likely refers to a URL where notifications
    @param cookie (str) - The `cookie` parameter in the `update_account` function seems to be a string
    parameter. It is used to store the cookie information related to the account being updated.
    @param passing (bool) - The `passing` parameter in the `update_account` function is a boolean
    parameter with a default value of `False`. This parameter allows the caller to specify whether the
    account is passing or not. If `passing` is set to `True`, it indicates that the account is in a
    passing
    
    """

    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute('''
        UPDATE accounts
        SET nickname=?, username=?, encrypted_password=?, games=?, webhook=?, cookie=?, passing=?
        WHERE id=?
    ''', (nickname, username, encrypted_password, ','.join(games), webhook, cookie, passing, id))
    conn.commit()
    conn.close()
    return True

def delete_account(id: int) -> bool: 
    """
    The `delete_account` function deletes an account from a database based on the provided ID.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @param id (int) - The `id` parameter in the `delete_account` function is an integer that represents
    the unique identifier of the account that needs to be deleted from the database.
    @returns The function `delete_account` is returning a boolean value `True`.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True

def load_groups() -> List[Dict[str, Any]]:
    """
    The `load_groups` function loads group information from a database table into a list of dictionaries.
    
    Author - Liam Scott
    Last update - 07/20/2024
    @returns The `load_groups` function returns a list of dictionaries representing groups. Each dictionary
    contains the following keys: "id", "name", and "members".
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups")
    rows = cursor.fetchall()
    conn.close()
    groups: List[Dict[str, Any]] = []
    for row in rows:
        group = {
            "id": row[0],
            "name": row[1],
            "members": row[2].split(',')
        }
        groups.append(group)
    return groups

def save_group(name: str, members: List[str]) -> bool:
    """
    The `save_group` function saves group information into a database table.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param name (str) - The `name` parameter in the `save_group` function is a string that represents the
    name of the group being saved.
    @param members (List[str]) - The `members` parameter in the `save_group` function is a list of strings
    representing the members of the group being saved. These members will be stored in the database as a
    comma-separated string when saving the group information.
    @returns The function `save_group` is returning a boolean value `True`.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO groups (name, members)
        VALUES (?, ?)
    ''', (name, ','.join(members)))
    conn.commit()
    conn.close()
    return True

def remove_group_member(group_id: int, member: str) -> bool:
    """
    The `remove_group_member` function removes a member from a group in a database table.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param group_id (int) - The `group_id` parameter in the `remove_group_member` function is an integer
    that represents the unique identifier of the group from which the member needs to be removed.
    @param member (str) - The `member` parameter in the `remove_group_member` function is a string that
    represents the member to be removed from the group.
    @returns The function `remove_group_member` is returning a boolean value `True`.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT members FROM groups WHERE id=?", (group_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False
    members = row[0].split(',')
    if member in members:
        members.remove(member)
        cursor.execute("UPDATE groups SET members=? WHERE id=?", (','.join(members), group_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def add_group_member(group_id: int, member: str) -> bool:
    """
    The `add_group_member` function adds a member to a group in a database table.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param group_id (int) - The `group_id` parameter in the `add_group_member` function is an integer that
    represents the unique identifier of the group to which the member needs to be added.
    @param member (str) - The `member` parameter in the `add_group_member` function is a string that
    represents the member to be added to the group.
    @returns The function `add_group_member` is returning a boolean value `True`.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT members FROM groups WHERE id=?", (group_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False
    members = row[0].split(',')
    if member not in members:
        members.append(member)
        cursor.execute("UPDATE groups SET members=? WHERE id=?", (','.join(members), group_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def delete_group(id: int) -> bool:
    """
    The `delete_group` function deletes a group from a database based on the provided ID.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param id (int) - The `id` parameter in the `delete_group` function is an integer that represents the
    unique identifier of the group that needs to be deleted from the database.
    @returns The function `delete_group` is returning a boolean value `True`.
    
    """
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("DELETE FROM groups WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True
    
def check_database():
    """
    The `check_database` function checks if the database exists and sets it up if it does not.
    
    Author - Liam Scott
    Last update - 09/5/2024
    
    """
    if not os.path.exists(DB_NAME):
        setup_database()
    try:
        conn: Connection = get_connection()
        conn.close()
        return True
    except sqlite3.OperationalError:
        return False
    

def check_tables() -> bool:
    conn: Connection = get_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
    if cursor.fetchone() is None:
        return False
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
    if cursor.fetchone() is None:
        return False
    conn.close()
    return True 