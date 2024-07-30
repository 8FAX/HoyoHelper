import asyncio
import random
from playwright.async_api import async_playwright
import time


async def get_cookie(password: str, username: str) -> list[dict[str, any]]: 
    """
    This Python async function uses Playwright to automate logging into a website and retrieving
    cookies.
    
    Author - Liam Scott
    Last update - 07/19/2024
    @param password (str) - The code you provided is an asynchronous function that uses Playwright to
    automate logging into a website and retrieving cookies. It seems like you were about to provide
    information about the `password` parameter but it got cut off. If you need any assistance with
    completing the code or have any specific questions, feel free
    @param username (str) - The `username` parameter in the `get_cookie` function is used to specify the
    username of the account for which you want to retrieve the authentication cookie. This username will
    be used to log in to the specified website and obtain the necessary cookies for authentication.
    @returns A list of dictionaries containing cookies is being returned if the login is successful. If
    the login fails, it will return False.
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
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
            logged_in = await page.frame_locator("#hyv-account-frame").get_by_role("button", name="Log In").is_visible()
            if not logged_in:
                cookies = await context.cookies()
                await context.close()
                await browser.close()
                return cookies
            else:
                return False

        except Exception as e:
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
    cookies = await get_cookie(input_password, input_username)
    if not cookies:
        print("Failed to get cookies")
    else:
        with open("cookies.txt", "w") as f:
            f.write(format_cookies(cookies))


# The `if __name__ == "__main__":` block in the Python script is a common idiom used to ensure that
# the code inside it is only executed when the script is run directly, and not when it is imported as
# a module in another script.
if __name__ == "__main__":
    asyncio.run(main())
