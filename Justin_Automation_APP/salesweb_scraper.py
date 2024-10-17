from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def scrape_addresses_from_county(county_index):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the website
    driver.get("https://salesweb.civilview.com/")

    # Optional: wait for the page to load completely
    time.sleep(3)

    # Extract all county links
    county_links = driver.find_elements(By.XPATH, "//div[@class='table-responsive']//a")

    # Check if the county_index is valid
    if county_index < 0 or county_index >= len(county_links):
        driver.quit()
        return []

    # Click on the selected county link
    county_links[county_index].click()

    # Optional: wait for the page to load completely
    time.sleep(3)  # Adjust sleep time if necessary

    # Wait for the table to be present in the DOM
    wait = WebDriverWait(driver, 20)
    table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table-striped')))

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Extract addresses (assuming address is in the 6th column, index 5)
    addresses = []
    for row in rows[1:]:  # Skip header row
        cells = row.find_elements(By.TAG_NAME, 'td')
        if len(cells) > 5:
            address = cells[5].text
            addresses.append(address)

    # Close the browser
    driver.quit()

    return addresses
