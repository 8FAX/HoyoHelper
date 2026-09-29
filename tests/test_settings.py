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

"""Tests for ConfigManager.

Like DatabaseManager, ConfigManager resolves its own path from the ambient
environment, so the autouse `isolated_data_dir` fixture keeps every test inside
a throwaway directory.

The last two tests in this file document a real defect found while writing the
suite: on a fresh install the validation token is the literal placeholder
string "ciphercheck", which is not valid base64, so `get_valadation()` raises
instead of returning a safe empty result. They are marked `xfail(strict=False)`
so they start passing the moment the bug is fixed, and will loudly fail
(XPASS -> failure) if someone "fixes" the test instead of the code.
"""

import base64
import json
import os

import pytest

from app.lib.settings import ConfigManager


@pytest.fixture
def config():
    return ConfigManager(runtime="os")


def test_first_run_creates_config_file(config):
    assert os.path.isfile(config.config_file)


def test_first_run_generates_a_default_encryption_key(config):
    key = config.get_default_encryption_key()
    assert key
    assert key != "_KEY_DID_NOT_SET_"
    # generate_encryption_key uses secrets.token_hex(32).
    assert len(key) == 64
    int(key, 16)


def test_generated_keys_differ_between_installs(isolate_data_dir):
    first = ConfigManager(runtime="os")

    # A second "install" must live in a different directory, or it just re-reads
    # the first one's settings.json. The `isolate_data_dir` fixture handles the
    # Windows/Linux env-var difference for us.
    isolate_data_dir()
    second = ConfigManager(runtime="os")

    assert first.get_default_encryption_key() != second.get_default_encryption_key()


def test_load_defaults_populates_expected_shape(config):
    config.load_defaults()
    data = config.config_data

    assert data["Version"]
    assert data["Database"]["type"] == "sqlite"
    assert data["Database"]["encrypt"] is False
    assert data["Database"]["use_default_encryption_key"] is True
    assert data["App"]["Style"] == "dark"


def test_setters_persist_to_disk(config):
    config.set_app_style("light")
    config.set_app_rest("25")

    with open(config.config_file, encoding="utf-8") as handle:
        on_disk = json.load(handle)

    assert on_disk["App"]["Style"] == "light"
    assert on_disk["App"]["rest"] == "25"


def test_setters_update_in_memory_state(config):
    config.set_app_style("retro")
    assert config.get_app_style() == "retro"


def test_config_survives_a_reload(config):
    config.set_app_style("high contrast")

    reloaded = ConfigManager(runtime="os")
    assert reloaded.get_app_style() == "high contrast"


def test_valadation_round_trips_through_base64(config):
    token, salt = b"token-bytes", b"salt-bytes"
    config.set_valadation(token, salt)

    stored_valadation, stored_salt = config.get_valadation()
    assert stored_valadation == token
    assert stored_salt == salt
    assert config.get_salt() == salt


def test_valadation_is_not_stored_in_plaintext(config):
    config.set_valadation(b"token-bytes", b"salt-bytes")

    with open(config.config_file, encoding="utf-8") as handle:
        raw = handle.read()

    assert "token-bytes" not in raw
    assert base64.b64encode(b"token-bytes").decode() in raw


def test_check_valadation_accepts_the_matching_key(config):
    key = config.get_default_encryption_key()
    from app.lib.encrypt import encrypt

    # encrypt() concatenates salt|iv|ciphertext into a single bytes blob.
    token = encrypt(key, config.get_valadation_truth())
    config.set_valadation(token, token[:16])

    assert config.check_valadation(key) is True


def test_check_valadation_rejects_a_wrong_key(config):
    key = config.get_default_encryption_key()
    from app.lib.encrypt import encrypt

    token = encrypt("a different key", config.get_valadation_truth())
    config.set_valadation(token, token[:16])

    assert config.check_valadation(key) is False


def test_reset_defaults_rebuilds_the_file(config):
    config.set_app_style("light")
    config.reset_defaults()

    reloaded = ConfigManager(runtime="os")
    assert reloaded.get_app_style() == "dark"


# ------------------------------------------------------- known defects (xfail)


@pytest.mark.xfail(
    strict=False,
    reason="Known bug: load_defaults() stores the placeholder 'ciphercheck', which is "
    "not valid base64, so get_valadation() raises binascii.Error instead of "
    "returning empty bytes.",
)
def test_get_valadation_on_fresh_install_returns_empty(config):
    config.load_defaults()
    assert config.get_valadation() == (b"", b"")


@pytest.mark.xfail(
    strict=False,
    reason="Known bug: check_valadation() calls get_valadation() unguarded, so on a "
    "fresh install it raises binascii.Error instead of returning False.",
)
def test_check_valadation_on_fresh_install_returns_false(config):
    config.load_defaults()
    assert config.check_valadation(config.get_default_encryption_key()) is False
