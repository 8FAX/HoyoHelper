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
#version 0.5.1
# -------------------------------------------------------------------------------------

import asyncio
import random
from playwright.async_api import Playwright, async_playwright
import time


async def get_token(password: str, username: str, playwright: Playwright = Playwright) -> list[dict[str, any]]: 
    """
    This Python async function uses Playwright to automate logging into a website and retrieving
    cookies.
    
    Author - Liam Scott
    Last update - 07/19/2024
    @param password (str) - The code you provided is an asynchronous function that uses Playwright to
    automate logging into a website and retrieving cookies. It seems like you were about to provide
    information about the `password` parameter but it got cut off. If you need any assistance with
    completing the code or have any specific questions, feel free
    @param username (str) - The `username` parameter in the `get_token` function is used to specify the
    username of the account for which you want to retrieve the authentication token. This username will
    be used to log in to the specified website and obtain the necessary cookies for authentication.
    @param playwright (Playwright) - Playwright is a Python library that provides a high-level API for
    automating browsers. It allows you to control browser instances and interact with web pages
    programmatically. In the provided code snippet, Playwright is used to launch a Chromium browser,
    navigate to a specific webpage, interact with elements on the page
    @returns A list of dictionaries containing cookies is being returned if the login is successful. If
    the login fails, it will return False.
    
    """

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()


    await page.goto("https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481")
    await page.locator(".components-home-assets-__sign-guide_---guide-close---2VvmzE").click()
    time.sleep(random.randint(1, 3))
    await page.locator(".mhy-hoyolab-account-block__avatar-icon").click()
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"text\"]").click()
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"text\"]").fill(username)
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"password\"]").click()
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"password\"]").fill(password)
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").get_by_role("button", name="Log In").click()
    time.sleep(8)

    try:
        await page.locator(".mhy-hoyolab-account-block__avatar-icon").wait_for_element_state("visible")
        print("Logged in")
        print("Waiting for cookies")
        cookies = await context.cookies()
        await context.close()
        await browser.close()
        return cookies

    except AttributeError as e:
        print("Failed to login")
        print(e)
        return False


def format_cookies(cookies: list[dict[str, any]]) -> str:
    """
    The function `format_cookies` takes a list of dictionaries representing cookies and returns a
    formatted string with cookie name-value pairs separated by semicolons.
    
    Author - Liam Scott
    Last update - 07/12/2024
    @param cookies (list[dict[str, any]]) - A list of dictionaries where each dictionary represents a
    cookie with 'name' and 'value' keys.
    @returns The function `format_cookies` takes a list of dictionaries representing cookies, and
    returns a string where each cookie is formatted as "name=value" separated by "; ".
    
    """
    return "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies)

async def main() -> None:
    """
    The function `main` uses Playwright to retrieve cookies and save them to a text file.
    
    Author - Liam Scott
    Last update - 07/12/2024
    
    """

    input_username = input("Enter your username: ")
    input_password = input("Enter your password: ")
    async with async_playwright() as playwright:
        cookies = await get_token(input_password, input_username, playwright)
        with open("cookies.txt", "w") as f:
            f.write(format_cookies(cookies))
    

# The `if __name__ == "__main__":` block in the Python script is a common idiom used to ensure that
# the code inside it is only executed when the script is run directly, and not when it is imported as
# a module in another script.
if __name__ == "__main__":
    asyncio.run(main())
