import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("https://doggy.market/dpay")
    return driver

def navigate_to_holders_tab(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Holders')]"))
    ).click()

def scrape_addresses(driver):
    addresses = []
    while True:  # Use a loop to navigate through pagination
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.address a"))
        )
        addresses.extend([elem.get_attribute('href').split('/')[-1] for elem in driver.find_elements(By.CSS_SELECTOR, "td.address a")])

        next_button = driver.find_elements(By.CSS_SELECTOR, ".pagination-item.next:not([aria-disabled='true']) button")
        if next_button:
            next_button[0].click()
        else:
            break  # Exit loop if no next button is active

    return addresses

def save_addresses_to_json(addresses):
    data = {"airDropList": [{"dogecoin_address": addr} for addr in addresses]}
    with open('addresses.json', 'w') as file:
        json.dump(data, file, indent=4)

def main():
    driver = setup_driver()
    navigate_to_holders_tab(driver)
    addresses = scrape_addresses(driver)
    save_addresses_to_json(addresses)
    print("Addresses scraped and saved to JSON.")
    driver.quit()

if __name__ == "__main__":
    main()
