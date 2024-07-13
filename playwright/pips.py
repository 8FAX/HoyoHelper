import asyncio
import random
from playwright.async_api import Playwright, async_playwright
import time


async def run(playwright: Playwright) -> list[dict[str, any]]:
    """
    This Python async function uses Playwright to automate logging into a website, collecting cookies
    upon successful login.
    
    Author - Liam Scott
    Last update - 07/12/2024
    @param playwright (Playwright) - The `playwright` parameter in the `run` function is an instance of
    the Playwright library. It is used to interact with browsers and automate web actions such as
    launching a browser, creating a new context, navigating to a webpage, interacting with elements on
    the page, and handling cookies. In
    @returns A list of cookies is being returned if the login is successful. If there is an
    AttributeError during the login process, then False is being returned.
    
    """
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()


    await page.goto("https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481")
    await page.locator(".components-home-assets-__sign-guide_---guide-close---2VvmzE").click()
    time.sleep(random.randint(1, 3))
    await page.locator(".mhy-hoyolab-account-block__avatar-icon").click()
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"text\"]").click()
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"text\"]").fill("Najisagamer")
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"password\"]").click()
    time.sleep(random.randint(1, 3))
    await page.frame_locator("#hyv-account-frame").locator("input[type=\"password\"]").fill("Najah11!")
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
    async with async_playwright() as playwright:
        cookies = await run(playwright)
        with open("cookies.txt", "w") as f:
            f.write(format_cookies(cookies))
    

# The `if __name__ == "__main__":` block in the Python script is a common idiom used to ensure that
# the code inside it is only executed when the script is run directly, and not when it is imported as
# a module in another script.
if __name__ == "__main__":
    asyncio.run(main())
