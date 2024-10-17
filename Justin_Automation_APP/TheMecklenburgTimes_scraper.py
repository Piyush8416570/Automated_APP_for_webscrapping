from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def scrape_mecktimes_data():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the target website
    driver.get("https://publicnotices.mecktimes.com/search/results.aspx?stid=53")

    # Prepare a list to hold extracted data
    data = []

    # Loop through all pages
    while True:
        try:
            # Wait for the table to be present
            wait = WebDriverWait(driver, 10)
            table = wait.until(EC.presence_of_element_located((By.ID, "MainContent_InnerMainContent_srGrid1")))

            # Extract table rows
            rows = table.find_elements(By.TAG_NAME, "tr")

            # Extract data from each row, skipping the header row
            for row in rows[1:]:
                columns = row.find_elements(By.TAG_NAME, "td")
                
                # Check if the row has the expected number of columns
                if len(columns) >= 10:
                    try:
                        address = columns[4].text.strip()
                        city = columns[5].text.strip()
                        zip_code = columns[6].text.strip()
                        county = columns[7].text.strip()
                        auction_date = columns[8].text.strip()
                        posted_date = columns[9].text.strip()

                        # Append extracted data to the list
                        data.append({
                            "Address": address,
                            "City": city,
                            "Zip Code": zip_code,
                            "County": county,
                            "Auction Date": auction_date,
                            "Posted Date": posted_date
                        })
                    except IndexError as e:
                        print(f"Row data extraction error: {e}")
                else:
                    print(f"Row skipped due to insufficient columns: {len(columns)} columns found.")

            # Check for the next page
            pagination = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".grid-pager ul")))
            next_buttons = pagination.find_elements(By.TAG_NAME, 'a')

            # If there is a next page, click on it
            if next_buttons and "aspNetDisabled" not in next_buttons[-1].get_attribute("class"):
                driver.execute_script("arguments[0].scrollIntoView(true);", next_buttons[-1])
                driver.execute_script("arguments[0].click();", next_buttons[-1])
                time.sleep(2)
            else:
                print("No more pages to scrape.")
                break

        except Exception as e:
            print("Error finding the next button or clicking it:", e)
            break

    # Close the browser
    driver.quit()

    return data

