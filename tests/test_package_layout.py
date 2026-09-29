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

"""Packaging invariants.

These are regression guards for the import-layout fix: the project used to mix
`from lib.x import y` (needs `app/` on sys.path) with `from app.lib.x import y`
(needs the project root on sys.path), which only worked because
`temp_database_loader.py` was mutating `sys.path` at import time.
"""

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"

# `from lib.foo import bar` / `import lib.foo` — the broken bare form.
BARE_LIB_IMPORT = re.compile(r"^\s*(?:from\s+lib(?:\.\w+)*\s+import\b|import\s+lib(?:\.\w+)*\b)")

# `sys.path.insert(...)` outside the one file that legitimately needs a shim.
SYS_PATH_MUTATION = re.compile(r"sys\.path\.(?:insert|append)\b")

# `temp_database_loader.py` is invoked as a script, so it may add the project root.
FILES_ALLOWED_SYS_PATH = {"temp_database_loader.py"}


def _python_sources():
    return sorted(p for p in APP_DIR.rglob("*.py") if "__pycache__" not in p.parts)


def _all_sources():
    return sorted(
        p
        for p in PROJECT_ROOT.rglob("*.py")
        if not any(
            part in {".venv", "__pycache__", ".git", "tests", "client scrips"}
            for part in p.parts
        )
    )


def test_app_is_a_package():
    assert (APP_DIR / "__init__.py").is_file(), "app/__init__.py missing"
    assert (APP_DIR / "lib" / "__init__.py").is_file(), "app/lib/__init__.py missing"


def test_lib_imports_resolve():
    """Every lib submodule must be importable through the package path."""
    import importlib

    for name in ("database", "settings", "exceptions", "encrypt", "webhook_manager"):
        assert importlib.import_module(f"app.lib.{name}") is not None


def test_bare_lib_imports_are_gone():
    """No source file may use the `lib.*` form that requires app/ on sys.path."""
    offenders = []
    for path in _all_sources():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if BARE_LIB_IMPORT.match(line):
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{lineno}: {line.strip()}")

    assert not offenders, "bare 'lib.' imports reintroduced:\n" + "\n".join(offenders)


def test_sys_path_hacks_are_confined():
    """Only temp_database_loader.py may touch sys.path."""
    offenders = []
    for path in _python_sources():
        if path.name in FILES_ALLOWED_SYS_PATH:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if SYS_PATH_MUTATION.search(line):
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}:{lineno}: {line.strip()}")

    assert not offenders, "sys.path mutated outside the entry script:\n" + "\n".join(offenders)


@pytest.mark.parametrize("entry", ["headless_app.py", "main_app.py", "temp_database_loader.py"])
def test_entry_points_use_package_imports(entry):
    """Each entry point must parse and use absolute app.lib.* imports."""
    tree = ast.parse((APP_DIR / entry).read_text(encoding="utf-8"))

    package_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.lib")
    ]
    assert package_imports, f"{entry} has no 'from app.lib... import' statements"
