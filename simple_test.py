import asyncio
from playwright.async_api import async_playwright
from healer import SelfHealer

URL = "http://localhost:5000"
ORIGINAL_LOCATOR = "button:text-is('Print')"
INTENT = "the main print/publish button"

print("---- STARTING TEST ----", flush=True)

async def run():
    healer = SelfHealer(model="llama3.2")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # headless=False so you SEE the browser
        page = await browser.new_page()

        print(f"Going to {URL} ...", flush=True)
        await page.goto(URL)
        await page.wait_for_load_state("networkidle")

        btn_text = await page.locator("#primary-action").text_content()
        print(f"Current button text on site is: '{btn_text}'", flush=True)

        print(f"Trying to heal locator: {ORIGINAL_LOCATOR}", flush=True)

        try:
            await healer.smart_click(page, ORIGINAL_LOCATOR, INTENT)
            print(" SUCCESS - Healed and clicked!", flush=True)
        except Exception as e:
            print(f"❌ FAILED: {e}", flush=True)

        print(healer.stats(), flush=True)
        print("---- Check your browser, it should show success message ----", flush=True)
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(run())
print("---- TEST FINISHED ----", flush=True)
