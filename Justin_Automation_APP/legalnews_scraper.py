from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from llm import extract_information
def scrape_foreclosure_data(start_date, end_date,county):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)
  
    # Open the website
    driver.get("https://legalnews.com/Home/PublicNotices")

    # Wait for the page to load and click on the 'Advanced Search' button
    wait = WebDriverWait(driver, 20)
    advanced_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Advanced Search')]")))
    advanced_search_button.click()

    # Click the second 'Advanced Search' button
    second_advanced_search_button = wait.until(EC.element_to_be_clickable((By.ID, "advancedsearchbutton")))
    second_advanced_search_button.click()

    # Wait for the advanced search page to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='advancedSearchLeft']//input[@id='probates']")))

    # Select 'Foreclosures' checkbox
    foreclosures_checkbox = driver.find_element(By.XPATH, "//input[@id='foreclosures']")
    foreclosures_checkbox.click()
    if county != "All Counties":
        county_dropdown = wait.until(EC.presence_of_element_located((By.ID, "drpcounty")))
        for option in county_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == county:
                option.click()
                break
    # Input the date range
    first_date = driver.find_element(By.XPATH, "//input[@name='first_date_published']")
    first_date.clear()
    first_date.send_keys(start_date)

    last_date = driver.find_element(By.XPATH, "//input[@name='first_date_published_thru']")
    last_date.clear()
    last_date.send_keys(end_date)

    # Click on the search button
    search_button = driver.find_element(By.XPATH, "//div[@id='advancedSearchSubmit']//input[@class='searchSubmit']")
    search_button.click()

    addresses = []
    while True:
        # Wait for the search results page to load
        wait.until(EC.presence_of_element_located((By.ID, "pagination")))

        # Find and extract addresses from the result items
        results = driver.find_elements(By.XPATH, "//div[@class='result-item']//h3/a")
        for result in results:
            address_text = result.text.strip()
            if address_text:  # Check if address is not empty
                addresses.append(address_text)
                print(f"Scraped address: {address_text}")  # Log the scraped address

        # Try to find the 'Next' link, and if not present, break the loop
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next ≫")
            next_button.click()
            time.sleep(3)  # Increased wait time for page to load
        except Exception as e:
            print(f"No more pages or error encountered: {e}")
            break

    # Close the browser
    driver.quit()

    return addresses

def scrape_probate_data(start_date, end_date):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://legalnews.com/Home/PublicNotices")
    
    wait = WebDriverWait(driver, 10)
    advanced_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Advanced Search')]")))
    advanced_search_button.click()

    second_advanced_search_button = wait.until(EC.element_to_be_clickable((By.ID, "advancedsearchbutton")))
    second_advanced_search_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='advancedSearchLeft']//input[@id='probates']")))
    probates_checkbox = driver.find_element(By.XPATH, "//input[@id='probates']")
    probates_checkbox.click()

    first_date = driver.find_element(By.XPATH, "//input[@name='first_date_published']")
    first_date.clear()
    first_date.send_keys(start_date)

    last_date = driver.find_element(By.XPATH, "//input[@name='first_date_published_thru']")
    last_date.clear()
    last_date.send_keys(end_date)

    search_button = driver.find_element(By.XPATH, "//div[@id='advancedSearchSubmit']//input[@class='searchSubmit']")
    search_button.click()


# Function to collect notice links from the current page
    def collect_notice_links():
        results = driver.find_elements(By.XPATH, "//div[@class='result-item']//h3/a[contains(@href, '/Home/PublicNoticesDetails')]")
        return [result.get_attribute('href') for result in results]

# List to store all notice links
    notice_links = []

# Loop through pages by constructing the URL
    current_page = 1

    while True:
    # Collect links from the current page
        notice_links.extend(collect_notice_links())
    
        print(f"Collected links from page {current_page}: {len(notice_links)}")
    
    # Check if there is a next page by finding a next page link with the current page number incremented
        next_page_url = f"https://legalnews.com/Home/PublicNotices?page={current_page + 1}"
        driver.get(next_page_url)
        time.sleep(2)  # Wait for the next page to load
    
    # Check if the page contains results
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-item")))
            current_page += 1  # Increment page counter if there are more results
        except Exception as e:
            print("No more pages or an error occurred:", str(e))
            break  # Exit the loop if there are no more results or an error occurs

# Print total results collected
    print(f"Total notice links collected: {len(notice_links)}")

# Now open each notice link to extract the description and save to a text file
    notice_descriptions = []
    for link in notice_links:
        driver.get(link)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "noticeDescription")))
            notice_description = driver.find_element(By.ID, "noticeDescription").text
        
            # If no description, indicate it
            if not notice_description:
                notice_description = "No notice description available."
            
            notice_descriptions.append(notice_description)
        
        except Exception as e:
            print(f"Error loading details for link: {link}. Exception: {str(e)}")
            notice_descriptions.append("Error loading notice description.")

# Save all notice descriptions to a text file
    with open("Notices_Document.txt", "w") as doc_file:
        for description in notice_descriptions:
            doc_file.write(description + "\n\n")

# Process each notice description with the LLM and gather extracted data
    
    extracted_data = []
    for notice in notice_descriptions:
        extracted_info = extract_information(notice)
        if extracted_info and extracted_info.get("Address") != "N/A":  # Check if the Address field is valid
            extracted_data.append(extracted_info)

    df = pd.DataFrame(extracted_data)
    df = df.applymap(lambda x: x.replace('"', '').replace(',', '').replace('.', '') if isinstance(x, str) else x)
    df.to_excel("Probate_Notice_Descriptions.xlsx", index=False)

    driver.quit()
    return extracted_data