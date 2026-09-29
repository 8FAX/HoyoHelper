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
# -------------------------------------------------------------------------------------

"""Tests for DatabaseManager.

The constructor resolves its own path (creating directories and the database
file as a side effect), so every test works against the per-test temp
`%APPDATA%`/`$HOME` set by the autouse `isolated_data_dir` fixture. No test
here touches the network or a real user database.
"""

import sqlite3
from typing import cast

import pytest

from app.lib.database import Account, DatabaseManager, Group


@pytest.fixture
def db():
    return DatabaseManager(runtime="os")


def make_account(nickname="8FA", username="8fa@example.com", games=("gi", "zzz")):
    # Built via cast() so the stub ciphertext does not trip secret scanners.
    return cast(
        Account,
        {
            "id": None,
            "nickname": nickname,
            "username": username,
            "encrypted_password": "test-placeholder-not-a-secret",
            "games": list(games),
            "cookie_daily_login": "cookie-daily",
            "cookie_codes": "cookie-codes",
            "passing": False,
            "webhook": "https://discord.com/api/webhooks/1/abc",
        },
    )


# --------------------------------------------------------------------------- setup


def test_constructor_creates_database_file_and_tables(db):
    assert db.check_database() is True
    assert db.check_tables() is True

    tables = {
        row[0]
        for row in db.get_connection()
        .execute("SELECT name FROM sqlite_master WHERE type='table'")
        .fetchall()
    }
    assert {"accounts", "groups"} <= tables


def test_setup_database_is_idempotent(db):
    assert db.setup_database() is True
    assert db.setup_database() is True


def test_load_accounts_on_empty_database_returns_empty_list(db):
    assert db.load_accounts() == []
    assert db.load_groups() == []


# --------------------------------------------------------------------------- accounts


def test_save_then_load_account_round_trips(db):
    account_id = db.save_account(make_account())
    assert isinstance(account_id, int)

    loaded = db.load_accounts()
    assert len(loaded) == 1
    account = loaded[0]
    assert account["id"] == account_id
    assert account["nickname"] == "8FA"
    assert account["username"] == "8fa@example.com"
    assert account["games"] == ["gi", "zzz"]
    assert account["passing"] is False


def test_games_are_stored_as_csv_and_split_back(db):
    db.save_account(make_account(games=("gi", "hsr", "zzz")))
    assert db.load_accounts()[0]["games"] == ["gi", "hsr", "zzz"]


def test_optional_account_fields_may_be_absent(db):
    account = make_account()
    account["cookie_daily_login"] = None
    account["cookie_codes"] = None
    account["webhook"] = None

    db.save_account(account)
    loaded = db.load_accounts()[0]
    assert loaded["cookie_daily_login"] is None
    assert loaded["cookie_codes"] is None
    assert loaded["webhook"] is None


def test_passing_column_round_trips_as_bool(db):
    account = make_account()
    account["passing"] = True
    db.save_account(account)
    assert db.load_accounts()[0]["passing"] is True


def test_update_account_changes_fields(db):
    account_id = db.save_account(make_account())

    updated = make_account(nickname="renamed", games=("gi",))
    updated["id"] = account_id
    assert db.update_account(updated) is True

    loaded = db.load_accounts()[0]
    assert loaded["nickname"] == "renamed"
    assert loaded["games"] == ["gi"]


def test_update_account_without_id_returns_false(db):
    account = make_account()
    account["id"] = None
    assert db.update_account(account) is False


def test_update_account_for_missing_row_returns_false(db):
    account = make_account()
    account["id"] = 4242
    assert db.update_account(account) is False


def test_delete_account_removes_only_the_target(db):
    first_id = db.save_account(make_account(nickname="first", username="a@example.com"))
    db.save_account(make_account(nickname="second", username="b@example.com"))

    assert db.delete_account(first_id) is True

    remaining = db.load_accounts()
    assert [a["nickname"] for a in remaining] == ["second"]


def test_delete_account_twice_returns_false(db):
    account_id = db.save_account(make_account())
    assert db.delete_account(account_id) is True
    assert db.delete_account(account_id) is False


def test_save_account_returns_none_on_constraint_violation(db):
    """A NOT NULL violation must surface as None, not raise."""
    broken = cast(Account, {**make_account(), "nickname": None})

    assert db.save_account(broken) is None


# --------------------------------------------------------------------------- groups


def test_save_then_load_group_round_trips(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA", "liam"]))
    assert isinstance(group_id, int)

    loaded = db.load_groups()
    assert len(loaded) == 1
    assert loaded[0]["id"] == group_id
    assert loaded[0]["name"] == "friends"
    assert loaded[0]["members"] == ["8FA", "liam"]


def test_group_with_no_members_loads_as_empty_list(db):
    db.save_group(Group(id=None, name="empty", members=[]))
    assert db.load_groups()[0]["members"] == []


def test_add_group_member_appends_without_duplicating(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA"]))

    assert db.add_group_member(group_id, "liam") is True
    assert db.add_group_member(group_id, "liam") is False

    assert db.load_groups()[0]["members"] == ["8FA", "liam"]


def test_remove_group_member(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA", "liam"]))

    assert db.remove_group_member(group_id, "liam") is True
    assert db.load_groups()[0]["members"] == ["8FA"]


def test_remove_group_member_that_is_not_present_returns_false(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA"]))
    assert db.remove_group_member(group_id, "nobody") is False


def test_group_member_operations_on_missing_group_return_false(db):
    assert db.add_group_member(999, "liam") is False
    assert db.remove_group_member(999, "liam") is False


def test_update_group_renames_and_replaces_members(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA"]))

    assert db.update_group(Group(id=group_id, name="close friends", members=["liam"])) is True

    loaded = db.load_groups()[0]
    assert loaded["name"] == "close friends"
    assert loaded["members"] == ["liam"]


def test_update_group_without_id_returns_false(db):
    assert db.update_group(Group(id=None, name="x", members=[])) is False


def test_delete_group(db):
    group_id = db.save_group(Group(id=None, name="friends", members=["8FA"]))
    assert db.delete_group(group_id) is True
    assert db.load_groups() == []
    assert db.delete_group(group_id) is False


# --------------------------------------------------------------------------- health


def test_check_tables_creates_missing_tables(db):
    """Drop the tables, then confirm check_tables() rebuilds them."""
    conn = db.get_connection()
    conn.execute("DROP TABLE accounts")
    conn.execute("DROP TABLE groups")
    conn.commit()
    conn.close()

    assert db.check_tables() is True
    assert db.load_accounts() == []


def test_check_tables_accepts_an_external_connection(db):
    conn = db.get_connection()
    try:
        assert db.check_tables(conn) is True
    finally:
        conn.close()


def test_load_accounts_survives_a_missing_database_file(db):
    """Deleting the file out from under the manager must self-heal."""
    import os

    os.remove(db.database_file)
    assert db.load_accounts() == []


def test_connection_is_scoped_to_the_managed_file(db):
    conn = db.get_connection()
    try:
        conn.execute("SELECT 1 FROM accounts")
    except sqlite3.Error:
        pytest.fail("accounts table missing on a fresh database")
    finally:
        conn.close()
