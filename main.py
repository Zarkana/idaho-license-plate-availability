import json
import os
from playwright.sync_api import Playwright, sync_playwright

def wait_for_one_to_be_visible(selector):
    # Wait for one or more and then find the one that is visible
    elements = page.locator(selector).all()
    visible_element_count = len([element for element in elements if element.is_visible()])
    while visible_element_count == 0:
        elements = page.locator(selector).all()
        visible_element_count = len([element for element in elements if element.is_visible()])

def fetch_words():
    """Reads a list of words from a JSON file."""
    with open('english_words.json', 'r') as f:
        words = json.load(f)
    return words

def enter_word(word):
    global current_word
    if word not in words["available"] and word not in words["unavailable"]:
        current_word = word
        plate_input = page.locator('input[type="text"]')
        plate_input.fill(word)

        page.click("text=Generate Preview")
    else:
        print(f"{word} was already in the list of license plates")
        current_word = enter_word(words_to_check.pop())

    # Write the current list of words and error status to the file after each word check
    with open('license_plates.json', 'w') as f:
        json.dump(words, f, indent=4)

def handle_request(route, request):
    if 'https://www.accessidaho.org/itd/driver/plates/checkAvailability' in request.url:
        route.continue_()
        global current_word
        word = current_word
        
        wait_for_one_to_be_visible('.modal-dialog')

        plate_available = page.locator("#available .modal-dialog").is_visible()
        if plate_available:
            words["available"].append(word)
            print(f"{word} is available")
            # try_a_new_plate_button = page.locator("#available").get_by_text("Try a New Plate Message")
            try_a_new_plate_button = page.locator('//*[@id="available"]/div/div/div[3]/button')
        else:
            words["unavailable"].append(word)
            print(f"{word} is unavailable")
            # try_a_new_plate_button = page.locator("#unavailable").get_by_text("Try a New Plate Message")
            try_a_new_plate_button = page.locator('//*[@id="unavailable"]/div/div/div[3]/button')

        try_a_new_plate_button.click()
        enter_word(words_to_check.pop())
    elif 'https://www.accessidaho.org/itd/driver/plates/check' in request.url:
        route.continue_()
        page.click("text=Check Availability")

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

    page.route('**/*', lambda route, request: handle_request(route, request))

    current_word = ""
    enter_word(words_to_check.pop())


    page.wait_for_timeout(200000)

    browser.close()