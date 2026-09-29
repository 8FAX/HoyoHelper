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

"""Tests for the exception hierarchy in app/lib/exceptions.py.

The hierarchy is the backbone of the app's error handling:
``HoyoHelperError`` -> ``LoginManagerError`` -> the five specific API errors,
plus a sibling ``WebhookError``. These tests pin the tree shape and the
context-carrying attributes, because callers catch these by type and read
those attributes for log/webhook messages.
"""

import pytest

from app.lib.exceptions import (
    APIDataError,
    APIRequestError,
    AssetFetchError,
    CardGenerationError,
    HoyoHelperError,
    LoginManagerError,
    SigninError,
    WebhookError,
)

# Every concrete error must be catchable as HoyoHelperError.
ALL_ERRORS = [
    WebhookError,
    LoginManagerError,
    APIRequestError,
    APIDataError,
    AssetFetchError,
    CardGenerationError,
    SigninError,
]


@pytest.mark.parametrize("error_cls", ALL_ERRORS)
def test_every_error_derives_from_base(error_cls):
    assert issubclass(error_cls, HoyoHelperError)


@pytest.mark.parametrize(
    "error_cls", [APIRequestError, APIDataError, AssetFetchError, CardGenerationError, SigninError]
)
def test_login_manager_errors_share_a_parent(error_cls):
    assert issubclass(error_cls, LoginManagerError)


def test_webhook_error_is_not_a_login_manager_error():
    """WebhookError is a sibling branch; login handlers must not swallow it."""
    assert not issubclass(WebhookError, LoginManagerError)


def test_base_error_keeps_message_and_str():
    err = HoyoHelperError("something broke")
    assert err.message == "something broke"
    assert str(err) == "something broke"


def test_base_error_is_a_real_exception():
    with pytest.raises(HoyoHelperError, match="boom"):
        raise HoyoHelperError("boom")


def test_webhook_error_carries_url_and_original_exception():
    cause = TimeoutError("timed out")
    err = WebhookError("send failed", url="https://discord.com/api/webhooks/1/abc", original_exception=cause)

    assert err.url == "https://discord.com/api/webhooks/1/abc"
    assert err.original_exception is cause
    assert "WebhookError: send failed" in str(err)
    # The URL is deliberately truncated in __str__ so webhook secrets are not
    # splashed into logs at full length.
    assert "https://discord.com/api/webhooks/1/abc" not in str(err)


def test_api_request_error_carries_full_context():
    err = APIRequestError(
        "request failed",
        url="https://sg-hk4e-api.hoyolab.com/event/sol/sign",
        status_code=503,
        response_text="upstream unavailable",
        original_exception=ConnectionError("reset"),
    )

    rendered = str(err)
    assert "APIRequestError: request failed" in rendered
    assert "Status: 503" in rendered
    assert "https://sg-hk4e-api.hoyolab.com/event/sol/sign" in rendered
    assert "ConnectionError" in rendered
    # APIRequestError renders the URL in full (unlike WebhookError).
    assert "upstream unavailable" in rendered


def test_api_request_error_response_preview_is_truncated():
    err = APIRequestError("bad", response_text="x" * 500)
    assert "x" * 100 in str(err)
    assert "x" * 101 not in str(err)


def test_api_data_error_carries_api_context():
    err = APIDataError(
        "missing key",
        key_missing="retcode",
        retcode=-1,
        api_message="game not logged in",
        api_response_preview='{"retcode":-1}',
    )

    assert err.key_missing == "retcode"
    assert err.retcode == -1
    assert err.api_message == "game not logged in"
    assert err.api_response_preview == '{"retcode":-1}'
    assert "APIDataError: missing key" in str(err)


def test_asset_fetch_error_carries_url():
    err = AssetFetchError("download failed", url="https://cdn.hoyohelper.com/gi/cards/gi_cards_6.png")
    assert err.url == "https://cdn.hoyohelper.com/gi/cards/gi_cards_6.png"
    assert "AssetFetchError: download failed" in str(err)


def test_signin_error_carries_risk_code():
    err = SigninError("signin rejected", retcode=-101, api_message="Captcha required", gt_risk_code=200)
    assert err.retcode == -101
    assert err.api_message == "Captcha required"
    assert err.gt_risk_code == 200
    assert "Captcha required" in str(err)


def test_errors_constructed_with_message_only_do_not_raise():
    """Every error must be constructible with just a message.

    Login_manager raises these from many places, often without URL/context
    available, so optional arguments have to genuinely be optional.
    """
    for error_cls in ALL_ERRORS:
        err = error_cls("bare message")
        assert err.message == "bare message"
        assert error_cls.__name__ in str(err) or str(err) == "bare message"
