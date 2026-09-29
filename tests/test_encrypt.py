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

"""Tests for the crypto helpers in app/lib/encrypt.py.

`encrypt` returns a single blob of `salt(16) || iv(16) || ciphertext`, which is
what gets persisted in the `accounts.encrypted_password` column. `decrypt`
reverses it. These tests are pure and local — no network, no database.
"""

import pytest

from app.lib.encrypt import decrypt, derive_key, encrypt

SALT_LEN = 16
IV_LEN = 16


def test_encrypt_returns_a_single_bytes_blob():
    blob = encrypt("correct horse battery staple", "hello world")

    assert isinstance(blob, bytes)
    # AES-CBC with PKCS7 always pads to a 16-byte multiple, so the ciphertext
    # portion is at least one full block.
    assert len(blob) > SALT_LEN + IV_LEN
    assert (len(blob) - SALT_LEN - IV_LEN) % 16 == 0


def test_encrypt_decrypt_round_trip():
    plaintext = "hunter2"
    assert decrypt("correct horse battery staple", encrypt("correct horse battery staple", plaintext)) == plaintext


@pytest.mark.parametrize(
    "plaintext",
    [
        "",
        "a",
        "exactly sixteen!!",
        "unicode: é你好🔒",
        "a" * 500,
    ],
)
def test_round_trip_preserves_various_payloads(plaintext):
    key = "test-key"
    assert decrypt(key, encrypt(key, plaintext)) == plaintext


def test_encrypt_is_non_deterministic():
    """A random salt and IV per call means identical input yields different blobs."""
    key = "test-key"
    first = encrypt(key, "same plaintext")
    second = encrypt(key, "same plaintext")

    assert first != second
    assert decrypt(key, first) == decrypt(key, second) == "same plaintext"


def test_salt_and_iv_are_fresh_per_call():
    blob_a = encrypt("test-key", "x")
    blob_b = encrypt("test-key", "x")

    assert blob_a[:SALT_LEN] != blob_b[:SALT_LEN]
    assert blob_a[SALT_LEN : SALT_LEN + IV_LEN] != blob_b[SALT_LEN : SALT_LEN + IV_LEN]


def test_decrypt_with_wrong_key_returns_empty_string():
    blob = encrypt("correct key", "secret")
    assert decrypt("wrong key", blob) == ""


def test_decrypt_rejects_truncated_input():
    # Too short to contain salt(16) + iv(16), so slicing/parsing fails outright.
    blob = encrypt("test-key", "secret")
    with pytest.raises((IndexError, ValueError, TypeError)):
        decrypt("test-key", blob[:10])


def test_derive_key_is_deterministic_for_the_same_salt():
    salt = b"\x01" * 16
    assert derive_key("password", salt) == derive_key("password", salt)


def test_derive_key_depends_on_salt_and_password():
    salt_a = b"\x01" * 16
    salt_b = b"\x02" * 16

    base = derive_key("password", salt_a)
    assert len(base) == 32
    assert base != derive_key("password", salt_b)
    assert base != derive_key("different password", salt_a)


def test_derive_key_does_not_leak(capsys):
    """The derived key is the account encryption key and must never be logged."""
    key = derive_key("password", b"\x01" * 16)
    assert key.hex() not in capsys.readouterr().out
