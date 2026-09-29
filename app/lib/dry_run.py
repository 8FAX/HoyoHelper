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

"""A WebhookManager stand-in that logs instead of sending.

Used by `--dry-run` so that a dry run cannot post to Discord even if the caller
misses a guard somewhere. It mirrors the parts of WebhookManager's surface that
the app actually uses: the `send` signature and the `default_url` attribute.
"""

from __future__ import annotations

import logging


class DryRunWebhookManager:
    """Records what would have been sent, without contacting Discord."""

    def __init__(self, default_url: str | None = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.default_url = default_url or "DRY_RUN_NO_WEBHOOK"
        self.messages: list[tuple[str, str | None]] = []

    def send(
        self,
        message: str,
        card: object | None = None,
        url: str | None = None,
    ) -> bool:
        """Record the message. Always reports success so callers proceed normally."""
        self.messages.append((message, url))
        self.logger.info("[DRY RUN] webhook suppressed: %s", message)
        return True
