import requests
import json
from playwright.sync_api import Playwright, sync_playwright

def fetch_words(num_words):
    """
    Fetches a list of random words using Datamuse API.
    """
    url = f"https://api.datamuse.com/words?sp=*&max=1000"
    response = requests.get(url)
    data = response.json()
    words = [word['word'] for word in data][:num_words]
    return words

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto('https://www.accessidaho.org/itd/driver/plates/plate/85')

    # Load the existing list of words from the JSON file, if it exists
    try:
        with open('random_words.json', 'r') as f:
            words = json.load(f)
    except FileNotFoundError:
        words = []

    # Set the number of words to fetch and insert
    num_words = 5

    # Initialize a variable to store whether the element exists
    plate_not_available = False

    # Fetch the list of words to insert
    new_words = fetch_words(num_words)

    for word in new_words:
        plate_input = page.locator('input[type="text"]')
        plate_input.fill(word)

        page.click("text=Generate Preview")

        page.wait_for_timeout(1000)

        page.click("text=Check Availability")
        
        # Check if the error element exists
        page.wait_for_timeout(1000)
        
        plate_available = page.locator("#available").is_visible()

        if plate_available:
            words.append(word)
            print(f"{word} is available")
            try_a_new_plate_button = page.locator("#available").get_by_text("Try a New Plate Message")
        else:
            print(f"{word} is unavailable")
            try_a_new_plate_button = page.locator("#unavailable").get_by_text("Try a New Plate Message")

        try_a_new_plate_button.click()

    browser.close()

# Append the new list of random words and error status to the existing JSON file.
with open('available_words.json', 'w') as f:
    json.dump(words, f, indent=4)