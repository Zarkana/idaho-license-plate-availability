from playwright.sync_api import Playwright, sync_playwright
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto('https://www.accessidaho.org/itd/driver/plates/plate/85')

    plate_input_locator = 'input[type="text"]'
    plate_input = page.locator(plate_input_locator)
    plate_input.fill("WORK")

    page.pause()

    browser.close()