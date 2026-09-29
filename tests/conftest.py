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

    if os.name == "nt":
        monkeypatch.setenv("APPDATA", str(data_dir))
    else:
        monkeypatch.setenv("HOME", str(data_dir))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(data_dir / ".config"))

    return data_dir
