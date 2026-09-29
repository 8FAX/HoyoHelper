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

"""Shared pytest fixtures.

Every test runs against a throwaway data directory. `DatabaseManager` and
`ConfigManager` both resolve their paths from `%APPDATA%` (Windows) or `$HOME`
(other platforms) at construction time, so redirecting those environment
variables is what keeps the suite from touching a real user install.
"""

import itertools
import os
import sys
from pathlib import Path

import pytest

# Make the project root importable so tests can use `app.lib.*` package imports.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point %APPDATA% and $HOME at a per-test temp dir.

    Autouse so no test can accidentally read or write the developer's real
    HoyoHelper data directory, and so the suite is safe to run in CI.
    """
    data_dir = tmp_path / "userdata"
    data_dir.mkdir()
    redirect_data_dir(monkeypatch, data_dir)

    return data_dir


@pytest.fixture
def isolate_data_dir(tmp_path, monkeypatch):
    """Return a callable that repoints the data directory at a new path.

    `ConfigManager` and `DatabaseManager` resolve their paths from the ambient
    environment at construction time, so a test that needs a *second* install
    has to build it against a different directory. This exists so that the
    platform branch lives in exactly one place: a test that set only
    `APPDATA` would silently keep using `$HOME` when run on Linux, and the two
    "installs" would resolve to the same file.

    Directories are created under `tmp_path` so a test can never leave stray
    install directories behind in the working tree.
    """
    counter = itertools.count()

    def _isolate(name=None):
        target = tmp_path / (name or f"install{next(counter)}")
        target.mkdir(parents=True, exist_ok=True)
        redirect_data_dir(monkeypatch, target)
        return target

    return _isolate


def redirect_data_dir(monkeypatch, data_dir):
    """Point the env vars `ConfigManager`/`DatabaseManager` actually read at `data_dir`.

    Mirrors the `os.name == "nt"` branch in `app/lib/settings.py` and
    `app/lib/database.py`: `%APPDATA%` on Windows, `$HOME` and
    `$XDG_CONFIG_HOME` elsewhere.
    """
    if os.name == "nt":
        monkeypatch.setenv("APPDATA", str(data_dir))
    else:
        monkeypatch.setenv("HOME", str(data_dir))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(data_dir / ".config"))

    return data_dir
