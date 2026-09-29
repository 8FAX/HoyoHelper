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

"""Decides *when* HoYo Helper should run its daily check-in cycle.

Everything in this module is pure: it takes an explicit `now` and explicit
inputs, and returns a value. It never reads the clock, never touches the
network, and never performs a check-in. That is deliberate -- the decisions
that decide whether a real sign-in fires deserve to be testable without
touching anyone's account, and the caller owns all the I/O.

The rest interval comes from the `App.rest` setting in settings.json, which
has existed in the config since the beginning but was never actually read by
the app. It is stored as a string, so it is parsed leniently here.
"""

import math
from datetime import UTC, datetime, timedelta

# Used when the setting is missing, empty, or unparseable. Matches the
# historical default written by ConfigManager.load_defaults().
DEFAULT_REST_HOURS = 10.0

# Guard against a config value like "0" turning into a hot loop that hammers
# the HoYoLAB API every few seconds.
MIN_REST_HOURS = 0.05  # ~3 minutes

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"


def parse_rest_hours(raw, default: float = DEFAULT_REST_HOURS) -> float:
    """Coerce the `App.rest` setting into a usable number of hours.

    Accepts numbers and strings because the setting is persisted as JSON that
    may hold either. Anything unparseable -- a blank string, a corrupted
    config, someone typing "ten" -- falls back to `default` rather than
    raising, because a bad interval should never stop the app from starting.
    """
    if raw is None or isinstance(raw, bool):
        return default

    try:
        hours = float(raw)
    except (TypeError, ValueError):
        return default

    # NaN fails every comparison downstream, and an infinite interval would
    # silently mean "never check in again". Both fall back to the default.
    if not math.isfinite(hours):
        return default

    return max(MIN_REST_HOURS, hours)


def format_timestamp(moment: datetime) -> str:
    """Render a datetime as the UTC string stored in settings.json."""
    return moment.astimezone(UTC).strftime(TIMESTAMP_FORMAT)


def parse_timestamp(raw: str | None) -> datetime | None:
    """Read a stored timestamp back, returning None if it is absent or invalid.

    A corrupt or legacy value must not be fatal: returning None tells the
    caller "we have no idea when this last ran", which makes the next run
    happen immediately rather than never.
    """
    if not raw or not isinstance(raw, str):
        return None

    try:
        parsed = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None

    # Settings written before the timestamps were made timezone-aware would
    # parse as naive. Treat those as UTC rather than as local time, so the
    # schedule does not silently shift by the machine's offset.
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def next_run_at(
    last_run: datetime | None,
    rest_hours: float,
    now: datetime,
) -> datetime:
    """Return when the next cycle is due.

    With no previous run recorded, the answer is `now`: an app that has never
    checked in should check in now, not sit idle for a full interval.
    """
    if last_run is None:
        return now

    return last_run + timedelta(hours=rest_hours)


def seconds_until_next_run(next_run: datetime, now: datetime) -> float:
    """Seconds to wait before `next_run`, clamped at zero so a due cycle runs now."""
    return max(0.0, (next_run - now).total_seconds())


def should_run_now(
    last_run: datetime | None,
    rest_hours: float,
    now: datetime,
) -> bool:
    """Whether a cycle is due at `now`."""
    return seconds_until_next_run(next_run_at(last_run, rest_hours, now), now) == 0.0
