import streamlit as st
import pandas as pd
from io import BytesIO
from legalnews_scraper import scrape_foreclosure_data, scrape_probate_data
from salesweb_scraper import scrape_addresses_from_county
from TheMecklenburgTimes_scraper import scrape_mecktimes_data
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import requests
import time
from selenium.webdriver.common.by import By

geocode_cache = {}

def geocode_address(address, retries=2):
    if address in geocode_cache:
        return geocode_cache[address]  # Return cached result

    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {'User-Agent': 'JustinPickellForeclosureApp/1.0 (http://localhost:8501/)'}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data:
                print(f"Geocoding successful for address: {address}")
                geocode_cache[address] = data[0]['address']  # Cache the result
                return data[0]['address']
            else:
                print(f"No geocoding results for address: {address}")
        except requests.RequestException as e:
            print(f"Geocoding request failed for address: {address} with error: {e}")
        except ValueError:
            print(f"Failed to parse JSON response for address: {address}")

        # Wait before retrying
        time.sleep(3)

    return None





def split_address(full_address):
    # Extract parts of the address
    parts = full_address.rsplit(" ", 3)  # Split the address into parts
    street = " ".join(parts[:-3])
    city = parts[-3]
    state = parts[-2]
    zipcode = parts[-1]
    return street, city, state, zipcode, "United States"

def main():
    st.title("Foreclosure and Probate Data Scraper")

    source = st.selectbox("Select Source", options=["LegalNews", "SalesWeb", "TheMecklenburgTimes"])

    if source == "LegalNews":
        county = st.selectbox(
            "Select County",
            options=[
                "All Counties"
            ]
        )

        notice_type = st.selectbox("Select Notice Type", options=["Foreclosure", "Probate"])
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

        if st.button("Scrape Legal News Data"):
            if start_date and end_date:
                with st.spinner("Scraping data... This may take a few minutes."):
                    if notice_type == "Foreclosure":
                        addresses = scrape_foreclosure_data(
                            start_date.strftime("%d-%m-%Y"),
                            end_date.strftime("%d-%m-%Y"),
                            county
                        )
                    else:
                        data = scrape_probate_data(
                            start_date.strftime("%d-%m-%Y"), 
                            end_date.strftime("%d-%m-%Y")
                        )

                if notice_type == "Foreclosure":
                    st.success(f"Scraped {len(addresses)} addresses.")
                    with st.spinner("Geocoding addresses..."):
                        geocoded_data = []
                        for address in addresses:
                            location_data = geocode_address(address)
                            if location_data:
                                geocoded_data.append({
                                    'Address': address,
                                    'State': location_data.get('state', ''),
                                    'Zipcode': location_data.get('postcode', ''),
                                    'Country': location_data.get('country', '')
                                })
                            time.sleep(1)
                    if geocoded_data:
                        df = pd.DataFrame(geocoded_data)
                        st.dataframe(df)
        
                        excel_file = BytesIO()
                        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Addresses')
                        st.download_button(
                            label="Download Excel file",
                            data=excel_file.getvalue(),
                            file_name="addresses.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.warning("No data to display or download.")
                
                else:
                    df = pd.DataFrame(data)
                    st.dataframe(df)

                    excel_file = BytesIO()
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name="Probate Notices", index=False)
                    st.download_button(
                        label="Download data as Excel",
                        data=excel_file.getvalue(),
                        file_name='Probate_Notice_Descriptions.xlsx'
                    )
    elif source == "SalesWeb":
        # List to hold county names
        county_names = []

        # Setting up headless Chrome to get county links
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://salesweb.civilview.com/")

        # Extract all county links for dropdown
        county_links = driver.find_elements(By.XPATH, "//div[@class='table-responsive']//a")
        for link in county_links:
            county_names.append(link.text)

        

        driver.quit()  # Close the driver after fetching county names

        # Dropdown for county selection
        selected_county = st.selectbox("Select a County", options=county_names)

        if st.button("Scrape Addresses"):
            county_index = county_names.index(selected_county)  # Get index of selected county

            with st.spinner("Scraping addresses..."):
                addresses = scrape_addresses_from_county(county_index)

            st.success(f"Scraped {len(addresses)} addresses.")

            # Prepare data for displaying and downloading
            if addresses:
                geocoded_data = []
                for full_address in addresses:
                    street, city, state, zipcode, country = split_address(full_address)
                    # Geocode to fill in missing parts if needed
                    if city == "" or state == "" or zipcode == "":
                        location_data = geocode_address(full_address)
                        if location_data:
                            city = location_data.get('city', city)
                            state = location_data.get('state', state)
                            zipcode = location_data.get('postcode', zipcode)
                            country = location_data.get('country', country)

                    geocoded_data.append({
                        'Street': street,
                        'City': city,
                        'State': state,
                        'Zipcode': zipcode,
                        'Country': country
                    })

                df = pd.DataFrame(geocoded_data)

                st.dataframe(df)

                # Create Excel file
                excel_file = BytesIO()
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Addresses')

                st.download_button(
                    label="Download Excel file",
                    data=excel_file.getvalue(),
                    file_name="addresses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No addresses found for the selected county.")

    elif source == "TheMecklenburgTimes":
        if st.button("Scrape Meck Times Data"):
            with st.spinner("Scraping data from Meck Times..."):
                data = scrape_mecktimes_data()
                st.success(f"Scraped {len(data)} records.")

            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)

                excel_file = BytesIO()
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Meck Times Data')

                st.download_button(
                    label="Download Excel file",
                    data=excel_file.getvalue(),
                    file_name="meck_times_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data found for the selected time period.")

if __name__ == "__main__":
    main()
