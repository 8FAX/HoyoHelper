import asyncio
import random
from playwright.async_api import Playwright, async_playwright
import time


async def run(playwright: Playwright) -> list[dict[str, any]]:
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
    return "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies)

async def main() -> None:
    async with async_playwright() as playwright:
        cookies = await run(playwright)
        with open("cookies.txt", "w") as f:
            f.write(format_cookies(cookies))
    


asyncio.run(main())
