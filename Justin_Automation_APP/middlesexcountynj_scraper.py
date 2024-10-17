import requests
from bs4 import BeautifulSoup
import pandas as pd
from geopy.geocoders import Nominatim
import re

# Function to extract city, state, and ZIP from address using geopy
def get_location_details(address):
    geolocator = Nominatim(user_agent="middlesex_foreclosure")
    location = geolocator.geocode(address)
    
    if location:
        # Extract details using regex for simplicity
        match = re.match(r"(.+), ([A-Z]{2}) (\d{5})", location.address)
        if match:
            city = match.group(1)
            state = match.group(2)
            zip_code = match.group(3)
            return city, state, zip_code, "USA"
    return None, None, None, None

# Function to extract required data
def extract_foreclosure_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    table = soup.find("table", class_="front_end_widget listtable")

    if not table:
        print("No table found on the webpage.")
        return data

    rows = table.find("tbody").find_all("tr")

    for row in rows:
        defendant = row.find("td", {"data-th": "Defendant"}).get_text(strip=True)
        sale_date = row.find("td", {"data-th": "Sale Date"}).get_text(strip=True)
        address = row.find("td", {"data-th": "Address"}).find("a").get_text(strip=True)
        
        city, state, zip_code, country = get_location_details(address)

        data.append({
            "Defendant": defendant,
            "Address": address,
            "City": city,
            "State": state,
            "ZIP Code": zip_code,
            "Country": country,
            "Sale Date": sale_date
        })

    return data

# URL of the foreclosure data page
url = "https://www.middlesexcountynj.gov/government/departments/department-of-public-safety-and-health/office-of-the-county-sheriff/foreclosures"

# Extracting data
foreclosure_data = extract_foreclosure_data(url)

# Save data to a CSV file
df = pd.DataFrame(foreclosure_data)
df.to_csv("middlesex_foreclosures.csv", index=False)

print("Data has been successfully extracted and saved to 'middlesex_foreclosures.csv'.")
