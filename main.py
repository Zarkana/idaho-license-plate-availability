import json
from playwright.sync_api import Playwright, sync_playwright
import os

def fetch_words():
    """
    Reads a list of words from a JSON file.
    """
    with open('english_words.json', 'r') as f:
        words = json.load(f)
    return words


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto('https://www.accessidaho.org/itd/driver/plates/plate/85')

    # Load the existing list of words from the JSON file, if it exists
    if os.path.isfile('license_plates.json') and os.path.getsize('license_plates.json') > 0:
        with open('license_plates.json', 'r') as f:
            words = json.load(f)
    else:
        words = {"available": [], "unavailable": []}

    # Fetch the list of words to insert
    words_to_check = fetch_words()

    for word in words_to_check:
        if word not in words["available"] and word not in words["unavailable"]:
            plate_input = page.locator('input[type="text"]')
            plate_input.fill(word)

            page.wait_for_load_state()

            page.click("text=Generate Preview")

            page.wait_for_load_state()
            page.wait_for_timeout(2000)

            page.click("text=Check Availability")
            
            page.wait_for_load_state()
            page.wait_for_timeout(2000)

            plate_available = page.locator("#available").is_visible()

            if plate_available:
                words["available"].append(word)
                print(f"{word} is available")
                try_a_new_plate_button = page.locator("#available").get_by_text("Try a New Plate Message")
            else:
                words["unavailable"].append(word)
                print(f"{word} is unavailable")
                try_a_new_plate_button = page.locator("#unavailable").get_by_text("Try a New Plate Message")

            try_a_new_plate_button.click()
        else:
            print(f"{word} was already in the list of license plates")

        # Write the current list of words and error status to the file after each word check
        with open('license_plates.json', 'w') as f:
            json.dump(words, f, indent=4)

    browser.close()