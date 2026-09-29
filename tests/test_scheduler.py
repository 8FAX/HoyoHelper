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

"""Tests for the scheduler.

`app/scheduler.py` holds the pure time arithmetic and `app/headless_app.py` holds
the loop, so nothing here opens a browser, sends a webhook, or performs a check-in.
The dry-run tests assert exactly that, by replacing the real managers with
recorders and checking they are never touched.
"""

import math
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.headless_app import WindolessApp
from app.lib.database import Account
from app.scheduler import (
    DEFAULT_REST_HOURS,
    MIN_REST_HOURS,
    format_timestamp,
    next_run_at,
    parse_rest_hours,
    parse_timestamp,
    seconds_until_next_run,
    should_run_now,
)


def make_account(**overrides: Any) -> Account:
    """A complete Account, so a test only names the field it actually cares about."""
    account: dict[str, Any] = {
        "id": 1,
        "nickname": "TestAccount",
        "username": "tester@example.invalid",
        "encrypted_password": "",
        "games": ["gi"],
        "cookie_daily_login": None,
        "cookie_codes": None,
        "passing": True,
        "webhook": None,
    }
    account.update(overrides)
    return cast(Account, account)


# ----------------------------------------------------------------------------------
# parse_rest_hours
# ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (10, 10.0),
        (10.0, 10.0),
        ("10", 10.0),
        ("2.5", 2.5),
        ("  3  ", 3.0),
    ],
)
def test_parse_rest_hours_accepts_numbers_and_numeric_strings(raw, expected):
    assert parse_rest_hours(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [None, "", "garbage", "abc", "10 hours", [], {}, True, False],
)
def test_parse_rest_hours_falls_back_on_unusable_input(raw):
    """Anything unparseable becomes the default rather than a crash or a hot loop."""
    assert parse_rest_hours(raw) == DEFAULT_REST_HOURS


def test_parse_rest_hours_honours_a_custom_default():
    assert parse_rest_hours("nonsense", default=7.5) == 7.5


@pytest.mark.parametrize("raw", [float("nan"), "nan", "NaN", "inf", "-inf"])
def test_parse_rest_hours_rejects_nan_and_infinity(raw):
    """NaN would poison every comparison downstream; inf would mean 'never again'."""
    assert parse_rest_hours(raw) == DEFAULT_REST_HOURS


@pytest.mark.parametrize("raw", [0, 0.0, "0", -1, -0.001, "-5"])
def test_parse_rest_hours_clamps_to_a_floor(raw):
    """A zero or negative rest must not become a tight loop hammering HoYoLAB."""
    assert parse_rest_hours(raw) == MIN_REST_HOURS


def test_min_rest_is_positive():
    assert MIN_REST_HOURS > 0


# ----------------------------------------------------------------------------------
# format_timestamp / parse_timestamp
# ----------------------------------------------------------------------------------


def test_timestamp_round_trip_preserves_the_instant():
    moment = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert parse_timestamp(format_timestamp(moment)) == moment


def test_format_timestamp_is_utc_regardless_of_input_offset():
    """Two instants that are the same moment format to the same string."""
    as_utc = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    offset = as_utc.astimezone(timezone(timedelta(hours=5)))
    assert format_timestamp(offset) == format_timestamp(as_utc)


def test_parse_timestamp_treats_a_naive_value_as_utc():
    """Naive strings must not shift by the machine's local offset."""
    parsed = parse_timestamp("2025-05-26T12:00:00+00:00")
    assert parsed is not None
    assert parsed.tzinfo is not None
    assert parsed == datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)


def test_parse_timestamp_without_offset_is_read_as_utc():
    parsed = parse_timestamp("2025-05-26T12:00:00")
    assert parsed == datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    "raw", [None, "", "   ", "not-a-date", "2025-13-45T99:99:99+00:00", 12345]
)
def test_parse_timestamp_returns_none_for_unusable_input(raw):
    """A corrupt value must mean 'run now', never 'never run'."""
    assert parse_timestamp(raw) is None


# ----------------------------------------------------------------------------------
# next_run_at / seconds_until_next_run / should_run_now
# ----------------------------------------------------------------------------------


def test_next_run_is_last_run_plus_the_rest_interval():
    last = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    result = next_run_at(last, 10, datetime(2025, 5, 26, 14, 0, 0, tzinfo=UTC))
    assert result == last + timedelta(hours=10)


def test_next_run_is_now_when_nothing_has_ever_run():
    """An app that has never checked in should check in now, not in ten hours."""
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert next_run_at(None, 10, now) == now


def test_next_run_is_in_the_past_when_the_interval_has_elapsed():
    last = datetime(2025, 5, 26, 0, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert next_run_at(last, 10, now) < now


def test_seconds_until_next_run_counts_down():
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_next_run(now + timedelta(hours=3), now) == 3 * 3600


def test_seconds_until_next_run_is_never_negative():
    """Past deadlines clamp to zero so a caller cannot sleep for a negative span."""
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_next_run(now - timedelta(hours=3), now) == 0


def test_should_run_now_is_true_when_never_run():
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert should_run_now(None, 10, now) is True


def test_should_run_now_is_false_inside_the_interval():
    last = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 15, 0, 0, tzinfo=UTC)
    assert should_run_now(last, 10, now) is False


def test_should_run_now_is_true_once_the_interval_has_passed():
    last = datetime(2025, 5, 26, 0, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert should_run_now(last, 10, now) is True


def test_rest_interval_is_applied_even_when_it_is_a_float():
    last = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 12, 30, 0, tzinfo=UTC)
    result = next_run_at(last, 0.5, now)
    assert math.isclose((result - last).total_seconds(), 1800)


# ----------------------------------------------------------------------------------
# headless_app scheduling glue
# ----------------------------------------------------------------------------------


def test_startup_wait_is_zero_when_nothing_has_run():
    from app.headless_app import seconds_until_startup_run

    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_startup_run("", 10, now) == 0


def test_startup_wait_is_zero_for_a_corrupt_timestamp():
    """A broken record must not strand the scheduler for a whole interval."""
    from app.headless_app import seconds_until_startup_run

    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_startup_run("garbage", 10, now) == 0


def test_startup_wait_uses_the_remaining_interval_on_restart():
    """Restarting one hour into a ten hour window waits the remaining nine."""
    from app.headless_app import seconds_until_startup_run

    last = datetime(2025, 5, 26, 11, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_startup_run(format_timestamp(last), 10, now) == 9 * 3600


def test_startup_wait_is_zero_once_the_window_has_passed():
    from app.headless_app import seconds_until_startup_run

    last = datetime(2025, 5, 20, 12, 0, 0, tzinfo=UTC)
    now = datetime(2025, 5, 26, 12, 0, 0, tzinfo=UTC)
    assert seconds_until_startup_run(format_timestamp(last), 10, now) == 0


# ----------------------------------------------------------------------------------
# Argument parsing
# ----------------------------------------------------------------------------------


def test_parser_defaults_to_a_single_cycle():
    from app.headless_app import build_parser

    args = build_parser().parse_args([])
    assert args.schedule is False
    assert args.dry_run is False
    assert args.rest_hours is None


def test_parser_reads_the_schedule_flags():
    from app.headless_app import build_parser

    args = build_parser().parse_args(["--schedule", "--rest-hours", "4", "--dry-run"])
    assert args.schedule is True
    assert args.rest_hours == 4
    assert args.dry_run is True


def test_resolve_rest_hours_prefers_the_override():
    app = _FakeApp(config_manager=_StubConfig(rest="10"))
    assert app.resolve_rest_hours(4) == 4


def test_resolve_rest_hours_falls_back_to_the_setting():
    app = _FakeApp(config_manager=_StubConfig(rest="2.5"))
    assert app.resolve_rest_hours() == 2.5


def test_resolve_rest_hours_survives_a_nonsense_setting():
    app = _FakeApp(config_manager=_StubConfig(rest="not-a-number"))
    assert app.resolve_rest_hours() == DEFAULT_REST_HOURS


def test_resolve_rest_hours_clamps_a_zero_setting():
    app = _FakeApp(config_manager=_StubConfig(rest="0"))
    assert app.resolve_rest_hours() == MIN_REST_HOURS


# ----------------------------------------------------------------------------------
# Dry run must not touch the network
# ----------------------------------------------------------------------------------


def test_dry_run_webhook_manager_records_instead_of_sending():
    from app.lib.dry_run import DryRunWebhookManager

    manager = DryRunWebhookManager()
    assert manager.send("hello") is True
    assert manager.messages == [("hello", None)]


def test_dry_run_webhook_manager_always_reports_success():
    """Callers branch on the return value, so a dry run must not look like a failure."""
    from app.lib.dry_run import DryRunWebhookManager

    assert DryRunWebhookManager().send("anything", card=object()) is True


def test_dry_run_webhook_manager_mirrors_the_real_send_signature():
    """A signature drift here would break the app the moment a guard is missed."""
    import inspect

    from app.lib.dry_run import DryRunWebhookManager
    from app.lib.webhook_manager import WebhookManager

    real = list(inspect.signature(WebhookManager.send).parameters)
    dry = list(inspect.signature(DryRunWebhookManager.send).parameters)
    assert real == dry


def test_dry_run_app_never_calls_the_login_manager():
    """The check-in itself is the side effect that matters most."""
    import asyncio

    app = _FakeApp(
        dry_run=True,
        webhook_mgr=_RecordingWebhook(),
        login_mgr=_ExplodingLoginManager(),
    )
    account = make_account(cookie_daily_login="cookie-already-present")
    asyncio.run(app.run_account_async(account))
    assert app.login_mgr.calls == []


def test_dry_run_app_never_persists_a_new_cookie():
    """A dry run must not write to the database either."""
    import asyncio

    app = _FakeApp(
        dry_run=True,
        webhook_mgr=_RecordingWebhook(),
        database_manager=_ExplodingDatabase(),
    )
    # Returning None from the guard means no cookie is available downstream.
    result = asyncio.run(
        app._get_and_update_cookie_if_needed_async(make_account(), None)
    )
    assert result is None
    assert app.database_manager.writes == []


def test_dry_run_app_suppresses_the_completion_webhook():
    """Even the 'all done' message must be suppressed in a dry run."""
    from app.lib.dry_run import DryRunWebhookManager

    manager = DryRunWebhookManager()
    manager.send("INFO: HoYo Helper has completed its daily processing cycle for all accounts.")
    # Recorded, not sent: the stand-in has no Discord client at all.
    assert len(manager.messages) == 1


def test_startup_failure_alert_is_suppressed_in_a_dry_run(monkeypatch):
    """The error path must not become a hole in the dry-run guarantee."""
    from app import headless_app

    sent = []
    monkeypatch.setattr(
        headless_app, "WebhookManager", lambda *a, **k: _StubManager(sent)
    )
    headless_app._report_startup_failure(RuntimeError("boom"), dry_run=True)
    assert sent == []


def test_startup_failure_alert_is_sent_when_not_a_dry_run(monkeypatch):
    from app import headless_app

    sent = []
    monkeypatch.setattr(
        headless_app, "WebhookManager", lambda *a, **k: _StubManager(sent)
    )
    headless_app._report_startup_failure(RuntimeError("boom"), dry_run=False)
    assert sent and "RuntimeError" in sent[0]


# ----------------------------------------------------------------------------------
# Loop behaviour
# ----------------------------------------------------------------------------------


def _stop_after(cycles: int, slept: list[float]) -> Any:
    """A run_once stand-in that ends the scheduler loop after `cycles` passes.

    The loop is infinite by design, so something has to stop it. Interrupting
    via run_once rather than via time.sleep keeps the test independent of
    whether a given pass reaches the sleep at all.
    """
    state = {"cycles": 0}

    def run_once(app: Any) -> None:
        state["cycles"] += 1
        if state["cycles"] > cycles:
            raise KeyboardInterrupt

    return run_once


def test_run_forever_records_a_timestamp_then_sleeps(monkeypatch):
    """One cycle, one persisted timestamp, then it waits for the next window."""
    from app import headless_app

    slept: list[float] = []
    monkeypatch.setattr(headless_app, "run_once", _stop_after(1, slept))
    # A no-op so the wait is recorded without actually pausing the test.
    monkeypatch.setattr(headless_app, "_sleep_until", slept.append)

    app = _StubApp()
    with pytest.raises(KeyboardInterrupt):
        headless_app.run_forever(app, 10)

    assert len(app.config_manager.recorded) == 1
    assert parse_timestamp(app.config_manager.recorded[0]) is not None
    assert len(slept) == 1
    # The post-cycle wait is a full rest interval.
    assert slept[0] == pytest.approx(10 * 3600, rel=0.01)


def test_run_forever_does_not_record_a_cycle_that_crashed(monkeypatch):
    """A failed cycle must not mark the day done, or a crash silently skips a day."""
    from app import headless_app

    def boom(app):
        raise RuntimeError("cycle failed")

    monkeypatch.setattr(headless_app, "run_once", boom)
    app = _StubApp()
    with pytest.raises(RuntimeError):
        headless_app.run_forever(app, 10)
    assert app.config_manager.recorded == []


def test_run_forever_waits_before_the_first_cycle_on_restart(monkeypatch):
    """A restart inside the window must not check in again immediately."""
    from app import headless_app

    slept: list[float] = []
    monkeypatch.setattr(headless_app, "run_once", _stop_after(1, slept))
    monkeypatch.setattr(headless_app, "_sleep_until", slept.append)

    recent = datetime.now(UTC) - timedelta(minutes=5)
    app = _StubApp(last_run=format_timestamp(recent))
    with pytest.raises(KeyboardInterrupt):
        headless_app.run_forever(app, 10)

    # The startup wait comes first, then the post-cycle wait.
    assert len(slept) == 2
    assert slept[0] > 9 * 3600


def test_run_forever_runs_immediately_when_nothing_has_run(monkeypatch):
    from app import headless_app

    slept: list[float] = []
    monkeypatch.setattr(headless_app, "run_once", _stop_after(1, slept))
    monkeypatch.setattr(headless_app, "_sleep_until", slept.append)

    app = _StubApp(last_run="")
    with pytest.raises(KeyboardInterrupt):
        headless_app.run_forever(app, 10)
    # No startup wait, only the post-cycle wait.
    assert len(slept) == 1
    assert slept[0] == pytest.approx(10 * 3600, rel=0.01)


def test_run_forever_keeps_checking_in_on_repeat_cycles(monkeypatch):
    """The whole point of the scheduler: more than one cycle per process."""
    from app import headless_app

    slept: list[float] = []
    monkeypatch.setattr(headless_app, "run_once", _stop_after(3, slept))
    monkeypatch.setattr(headless_app, "_sleep_until", slept.append)

    app = _StubApp()
    with pytest.raises(KeyboardInterrupt):
        headless_app.run_forever(app, 10)

    assert len(app.config_manager.recorded) == 3
    assert len(slept) == 3


def test_main_returns_zero_on_a_clean_single_run(monkeypatch):
    from app import headless_app

    monkeypatch.setattr(headless_app, "run_once", lambda app: None)
    monkeypatch.setattr(headless_app.WindolessApp, "__init__", lambda self, dry_run=False: None)
    monkeypatch.setattr(
        headless_app.WindolessApp, "resolve_rest_hours", lambda self, override=None: 10.0
    )
    assert headless_app.main([]) == 0


def test_main_reports_a_startup_failure_as_exit_code_one(monkeypatch):
    from app import headless_app

    def boom(self, dry_run=False):
        raise RuntimeError("no database")

    monkeypatch.setattr(headless_app.WindolessApp, "__init__", boom)
    monkeypatch.setattr(
        headless_app, "_report_startup_failure", lambda *a, **k: None
    )
    assert headless_app.main([]) == 1


def test_main_treats_an_interrupt_as_a_clean_exit(monkeypatch):
    """Ctrl+C is a normal way to stop the scheduler, not a failure."""
    from app import headless_app

    def interrupt(app):
        raise KeyboardInterrupt

    monkeypatch.setattr(headless_app, "run_once", interrupt)
    monkeypatch.setattr(headless_app.WindolessApp, "__init__", lambda self, dry_run=False: None)
    monkeypatch.setattr(
        headless_app.WindolessApp, "resolve_rest_hours", lambda self, override=None: 10.0
    )
    assert headless_app.main([]) == 0


# ----------------------------------------------------------------------------------
# Test doubles
# ----------------------------------------------------------------------------------


class _StubConfig:
    """Stands in for ConfigManager, recording timestamps written to it."""

    def __init__(self, rest="10", last_run=""):
        self.rest = rest
        self.last_run = last_run
        self.recorded = []

    def get_app_rest(self):
        return self.rest

    def get_app_last_run(self):
        return self.last_run

    def set_app_last_run(self, timestamp):
        self.last_run = timestamp
        self.recorded.append(timestamp)


class _StubApp:
    def __init__(self, last_run=""):
        self.config_manager = _StubConfig(last_run=last_run)


class _FakeApp:
    """A real WindolessApp with its collaborators swapped for recorders.

    Built with __new__ so the methods under test are the genuine ones from
    headless_app rather than reimplementations; only the managers that would
    reach the network or disk are replaced.
    """

    def __init__(self, **overrides: Any) -> None:
        app = WindolessApp.__new__(WindolessApp)
        # The doubles deliberately implement a slice of each manager's surface,
        # not all of it, so they are installed dynamically rather than assigned.
        defaults: dict[str, Any] = {
            "dry_run": True,
            "game_links_map": {"gi": {"name": "Genshin Impact", "short_name": "gi"}},
            "config_manager": _StubConfig(),
            "webhook_mgr": _RecordingWebhook(),
            "login_mgr": _ExplodingLoginManager(),
            "database_manager": _ExplodingDatabase(),
        }
        defaults.update(overrides)
        for name, value in defaults.items():
            setattr(app, name, value)
        self._app = app

    def __getattr__(self, name: str) -> Any:
        return getattr(self._app, name)


class _RecordingWebhook:
    def __init__(self):
        self.messages = []
        self.default_url = None

    def send(self, message, card=None, url=None):
        self.messages.append((message, url))
        return True


class _ExplodingLoginManager:
    """Any call to this is a dry-run failure."""

    def __init__(self):
        self.calls = []

    def process_account(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        raise AssertionError("dry run attempted a real check-in")


class _ExplodingDatabase:
    def __init__(self):
        self.writes = []

    def update_account(self, account):
        self.writes.append(account)
        raise AssertionError("dry run wrote to the database")


class _StubManager:
    def __init__(self, sink, default_url="https://example.invalid/hook"):
        self.sink = sink
        self.default_url = default_url

    def send(self, message, card=None, url=None):
        self.sink.append(message)
        return True
