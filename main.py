import random
import requests
import json
from playwright.sync_api import Playwright, sync_playwright
import os

def fetch_words(num_words):
    """
    Fetches a list of words ordered by length using Datamuse API.
    """
    url = f"https://api.datamuse.com/words?sp=*&max=1000&orderby=length"
    response = requests.get(url)
    data = response.json()
    words = [word['word'] for word in data]
    return words[:num_words]

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

    # Set the number of words to fetch and insert
    num_words = 15

    # Initialize a variable to store whether the element exists
    plate_not_available = False

    # Fetch the list of words to insert
    new_words = fetch_words(num_words)

    for word in new_words:
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
            if word not in words["available"]:
                words["available"].append(word)
                print(f"{word} is available")
            else:
                print(f"{word} was already in the list of available words")
            try_a_new_plate_button = page.locator("#available").get_by_text("Try a New Plate Message")
        else:
            if word not in words["unavailable"]:
                words["unavailable"].append(word)
                print(f"{word} is unavailable")
            else:
                print(f"{word} was already in the list of unavailable words")
            try_a_new_plate_button = page.locator("#unavailable").get_by_text("Try a New Plate Message")

        try_a_new_plate_button.click()

    browser.close()

# Append the new list of random words and error status to the existing JSON file.
with open('license_plates.json', 'w') as f:
    json.dump(words, f, indent=4)